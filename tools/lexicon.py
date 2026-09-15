#!/usr/bin/env python3
"""Decodability: what a child can actually read by a given level.

The single rule this whole curriculum rests on is that a child is never shown a
word they have not been taught how to sound out. A word is legal at level N if
either:

  * it is a SIGHT WORD unlocked at or before N (taught as a whole, on purpose),
    or
  * it SEGMENTS cleanly into graphemes unlocked at or before N.

`segment()` does the second part. It is a small backtracking matcher over the
letter patterns unlocked so far, with two special cases English forces on us:

  * split digraphs -- "time" is t + i_e + m, not t-i-m-e -- handled by a
    silent-e pass that only runs when the matching X_e grapheme is unlocked.
  * doubled consonants -- "hill", "sniff", "class". Once a letter is known its
    double is allowed, which is also how the floss rule is actually taught.

This is deliberately a little lenient: it can pass a word a purist would argue
about, but it cannot pass a word containing a sound that has not been taught.
That is the direction the error should point -- it is a guardrail against a
subagent reaching for "the" on level 4, not a spelling authority.
"""

from __future__ import annotations

import functools
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "web" / "data"

# Graphemes whose id is positional rather than literal: they only match at the
# end of a word. The value is the letters they put on the page.
SUFFIX_PATTERNS = {
    "-s": "s",
    "-ed": "ed",
    "-le": "le",
    "-e": "e",
    "-o": "o",
    "-y": "y",
    "-ey": "y",
    "-ie": "ie",
}

# Split digraphs: id -> the vowel letter that goes before the consonant(s).
SILENT_E = {"a_e": "a", "i_e": "i", "o_e": "o", "u_e": "u", "e_e": "e"}

# Blends are not new letters, only new letter ORDERS, so they contribute their
# letters individually. Listing them here keeps segment() from needing to know
# what a blend is.
VOWELS = set("aeiou")

# Letter pairs that a child WILL read as one sound once taught, which means
# showing them early is a trap: "ship" on level 13 segments happily into
# s-h-i-p and is still an unreadable word, because /sh/ has not been taught.
# So any of these appearing in a word before its level is a rejection, even
# when the individual letters are all known.
#
# Blends (st, fl, nd...) are deliberately NOT here -- they really are read
# letter by letter. Neither is "ge", which would wrongly flag "get", nor the
# suffix spellings, which would wrongly flag "red" ("-ed") and "let" ("-le").
TRAP_KINDS = {"digraph", "team", "silent-letter"}
TRAP_EXCEPTIONS = {"ge", "ll", "zz"}


@functools.lru_cache(maxsize=1)
def sequence() -> dict:
    return json.loads((DATA / "sequence.json").read_text())


@functools.lru_cache(maxsize=1)
def phonemes() -> dict:
    return json.loads((DATA / "phonemes.json").read_text())


def unlocked_through(level: int) -> dict:
    """Everything a child has been taught by the END of `level`."""
    graphemes: list[str] = []
    sight: list[str] = []
    seeds: list[str] = []
    for lvl in sequence()["levels"]:
        if lvl["level"] > level:
            break
        graphemes += lvl["graphemes"]
        sight += [w.lower() for w in lvl["sightWords"]]
        seeds += [w.lower() for w in lvl["seedWords"]]
    return {"graphemes": graphemes, "sightWords": sight, "seedWords": seeds}


def patterns_for(graphemes: list[str]) -> tuple[frozenset[str], frozenset[str], frozenset[str]]:
    """(anywhere, end-only, silent-e vowels) letter patterns for these graphemes."""
    anywhere: set[str] = set()
    end_only: set[str] = set()
    silent_e: set[str] = set()
    table = phonemes()
    for gid in graphemes:
        if gid in SILENT_E:
            silent_e.add(SILENT_E[gid])
            continue
        if gid in SUFFIX_PATTERNS:
            end_only.add(SUFFIX_PATTERNS[gid])
            continue
        letters = table[gid]["display"].replace("-", "")
        anywhere.add(letters)
        # A known single consonant licenses its double (hill, sniff, class).
        if len(letters) == 1 and letters not in VOWELS:
            anywhere.add(letters * 2)
    return frozenset(anywhere), frozenset(end_only), frozenset(silent_e)


def _match(word: str, anywhere: frozenset[str], end_only: frozenset[str]) -> list[str] | None:
    """Backtracking segmentation. Longest patterns first so 'sh' beats 's'+'h'."""
    n = len(word)
    memo: dict[int, list[str] | None] = {}
    ordered = sorted(anywhere, key=len, reverse=True)

    def walk(i: int) -> list[str] | None:
        if i == n:
            return []
        if i in memo:
            return memo[i]
        memo[i] = None  # guard against cycles; patterns are non-empty so this is safe
        for pat in ordered:
            if word.startswith(pat, i):
                rest = walk(i + len(pat))
                if rest is not None:
                    memo[i] = [pat] + rest
                    return memo[i]
        for pat in end_only:
            if word.endswith(pat) and i + len(pat) == n:
                memo[i] = [pat]
                return memo[i]
        memo[i] = None
        return None

    return walk(0)


@functools.lru_cache(maxsize=1)
def all_traps() -> frozenset[str]:
    out = set()
    for gid, entry in phonemes().items():
        letters = entry["display"].replace("-", "")
        if len(letters) < 2 or gid in TRAP_EXCEPTIONS or gid in SUFFIX_PATTERNS:
            continue
        if entry["kind"] in TRAP_KINDS:
            out.add(letters)
    return frozenset(out)


def untaught_trap(word: str, graphemes: list[str]) -> str | None:
    """The first letter team in `word` that hasn't been taught yet, if any.

    An occurrence sitting entirely inside a team that HAS been taught is fine:
    "air" contains "ai", and a child reading "chair" never meets a bare "ai".
    """
    unlocked_letters = {
        phonemes()[g]["display"].replace("-", "") for g in graphemes if g in phonemes()
    }
    traps = all_traps() - unlocked_letters
    if not traps:
        return None

    # Spans covered by multi-letter graphemes the child already knows.
    safe: list[tuple[int, int]] = []
    i = 0
    known = sorted((p for p in unlocked_letters if len(p) > 1), key=len, reverse=True)
    while i < len(word):
        for pat in known:
            if word.startswith(pat, i):
                safe.append((i, i + len(pat)))
                i += len(pat)
                break
        else:
            i += 1

    for trap in sorted(traps, key=len, reverse=True):
        start = word.find(trap)
        while start != -1:
            end = start + len(trap)
            if not any(s <= start and end <= e for s, e in safe):
                return trap
            start = word.find(trap, start + 1)
    return None


def segment(word: str, graphemes: list[str]) -> list[str] | None:
    """Split `word` into unlocked graphemes, or return None if it can't be read."""
    w = word.lower().strip()
    if not w or not re.fullmatch(r"[a-z]+", w):
        return None
    if untaught_trap(w, graphemes):
        return None
    anywhere, end_only, silent_e = patterns_for(graphemes)

    direct = _match(w, anywhere, end_only)
    if direct is not None:
        return direct

    # Silent-e pass: vowel + one or two consonants + final e, e.g. time, plate.
    if len(w) >= 3 and w.endswith("e") and silent_e:
        stem = w[:-1]
        m = re.search(r"([aeiou])([b-df-hj-np-tv-z]{1,2})$", stem)
        if m and m.group(1) in silent_e:
            head, vowel, tail = stem[: m.start()], m.group(1), m.group(2)
            head_ok = _match(head, anywhere, end_only) if head else []
            tail_ok = _match(tail, anywhere, end_only)
            if head_ok is not None and tail_ok is not None:
                return head_ok + [f"{vowel}_e"] + tail_ok
    return None


def check_words(words: list[str], level: int) -> list[tuple[str, str]]:
    """Return [(word, reason)] for every word a child at `level` could not read."""
    unlocked = unlocked_through(level)
    sight = set(unlocked["sightWords"])
    seeds = set(unlocked["seedWords"])
    problems = []
    for raw in words:
        w = raw.lower().strip()
        if not w:
            continue
        if w in sight or w in seeds:
            # Seed words come from the scope and sequence itself: they are
            # sanctioned at their level even when a strict reading of the
            # grapheme set would argue ("here" on the e-e level contains "er").
            continue
        trap = untaught_trap(w, unlocked["graphemes"])
        if trap:
            problems.append((raw, f'contains "{trap}", which is not taught until later'))
        elif segment(w, unlocked["graphemes"]) is None:
            problems.append((raw, f"cannot be sounded out with the letters taught by level {level}"))
    return problems


WORD_RE = re.compile(r"[A-Za-z][A-Za-z']*")


def words_in(text: str) -> list[str]:
    """Pull readable words out of a sentence, dropping possessives/contractions
    markers so "sam's" is checked as "sam" plus a flagged apostrophe."""
    return [m.group(0) for m in WORD_RE.finditer(text)]


if __name__ == "__main__":
    import sys

    level = int(sys.argv[1])
    for word in sys.argv[2:]:
        parts = segment(word, unlocked_through(level)["graphemes"])
        sight = word.lower() in set(unlocked_through(level)["sightWords"])
        print(f"{word:12} {'SIGHT WORD' if sight else (' + '.join(parts) if parts else 'NOT DECODABLE')}")
