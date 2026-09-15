#!/usr/bin/env python3
"""Validate authored lesson files in data/levels/.

This is the contract between the authoring guide and the site. Every rule the
guide states in prose, this file states in code -- so a lesson that reads fine
but shows a child a word they cannot decode fails here rather than on the rug
at bedtime.

Usage:
    python3 tools/validate.py            # every level that exists
    python3 tools/validate.py 7 8 9      # just these
    python3 tools/validate.py --quiet    # exit code only
"""

from __future__ import annotations

import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from tools.lexicon import (check_words, consonant_clusters, phonemes, sequence,
                           unlocked_through, words_in)

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "web" / "data"
LEVELS_DIR = DATA / "levels"

MAX_ACTIVITIES = 30
CAPITALS_FROM = 23   # the day capital letters are taught
BLENDS_FROM = 27     # the day consonant blends start being taught


def min_activities(level: int) -> int:
    """The first days have almost no material to work with -- day 1 is one
    letter and no words at all -- so a full-length lesson there would be
    padding. From day 5 there is enough to fill a proper sitting."""
    return 8 if level <= 4 else 12

# type -> (required fields, optional fields)
SCHEMA = {
    "soundIntro":  ({"grapheme"},            {"keyword", "say", "prompt", "mouthCue", "picture"}),
    "soundMatch":  ({"target", "choices"},   {"prompt"}),
    "blend":       ({"word", "parts"},       {"prompt", "picture"}),
    "readWord":    ({"word"},                {"prompt", "picture"}),
    "chooseWord":  ({"answer", "choices"},   {"prompt"}),
    "sentence":    ({"text"},                {"prompt"}),
    "story":       ({"title", "lines"},      {"questions", "prompt"}),
    "sightWord":   ({"word"},                {"sentence", "prompt"}),
    "review":      ({"words"},               {"label", "prompt"}),
}


class Report:
    def __init__(self, level: int):
        self.level = level
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)


def _text_of(activity: dict) -> list[str]:
    """Every word this activity puts in front of a child."""
    t = activity.get("type")
    out: list[str] = []
    if t in ("blend", "readWord", "sightWord"):
        out.append(activity.get("word", ""))
    if t == "chooseWord":
        out += list(activity.get("choices", []))
    if t == "sentence":
        out += words_in(activity.get("text", ""))
    if t == "story":
        for line in activity.get("lines", []):
            out += words_in(line)
        for q in activity.get("questions", []) or []:
            out += words_in(q.get("prompt", ""))
            for c in q.get("choices", []):
                out += words_in(c)
    if t == "review":
        out += list(activity.get("words", []))
    if t == "sightWord" and activity.get("sentence"):
        out += words_in(activity["sentence"])
    return [w for w in out if w]


def validate_level(path: pathlib.Path) -> Report:
    spec = {lvl["level"]: lvl for lvl in sequence()["levels"]}
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        r = Report(0)
        r.error(f"{path.name}: not valid JSON -- {exc}")
        return r

    level = data.get("level")
    r = Report(level if isinstance(level, int) else 0)

    if not isinstance(level, int) or level not in spec:
        r.error(f"{path.name}: 'level' must be an integer 1-120")
        return r
    if path.stem != f"{level:03d}":
        r.error(f"{path.name}: filename should be {level:03d}.json")

    want = spec[level]
    for field in ("title", "kidTitle", "parentNote", "activities"):
        if not data.get(field):
            r.error(f"missing required field '{field}'")
    if r.errors:
        return r

    if sorted(data.get("newGraphemes", [])) != sorted(want["graphemes"]):
        r.error(f"newGraphemes must be {want['graphemes']} (from the scope and sequence)")
    if sorted(w.lower() for w in data.get("newSightWords", [])) != sorted(want["sightWords"]):
        r.error(f"newSightWords must be {want['sightWords']} (from the scope and sequence)")
    if len(data.get("parentNote", "")) < 80:
        r.warn("parentNote is very short -- it is the only coaching a parent gets")

    activities = data["activities"]
    if not isinstance(activities, list):
        r.error("'activities' must be a list")
        return r
    floor = min_activities(level)
    if not floor <= len(activities) <= MAX_ACTIVITIES:
        r.error(f"{len(activities)} activities; must be {floor}-{MAX_ACTIVITIES}")

    known_graphemes = set(phonemes())
    unlocked = unlocked_through(level)
    kinds: list[str] = []
    shown_words: list[str] = []

    for i, act in enumerate(activities, start=1):
        where = f"activity {i}"
        if not isinstance(act, dict) or "type" not in act:
            r.error(f"{where}: must be an object with a 'type'")
            continue
        t = act["type"]
        kinds.append(t)
        if t not in SCHEMA:
            r.error(f"{where}: unknown type '{t}' (allowed: {', '.join(sorted(SCHEMA))})")
            continue
        required, optional = SCHEMA[t]
        missing = required - set(act)
        if missing:
            r.error(f"{where} ({t}): missing {sorted(missing)}")
            continue
        extra = set(act) - required - optional - {"type"}
        if extra:
            r.warn(f"{where} ({t}): unrecognised fields {sorted(extra)} will be ignored")

        if t == "soundIntro":
            if act["grapheme"] not in known_graphemes:
                r.error(f"{where}: '{act['grapheme']}' is not in data/phonemes.json")
            elif act["grapheme"] not in unlocked["graphemes"]:
                r.error(f"{where}: grapheme '{act['grapheme']}' is not taught by level {level}")
        if t == "soundMatch":
            choices = act["choices"]
            if not 2 <= len(choices) <= 4:
                r.error(f"{where}: needs 2-4 choices")
            if act["target"] not in choices:
                r.error(f"{where}: target '{act['target']}' is not among the choices")
            if act["target"] not in unlocked["graphemes"]:
                r.error(f"{where}: target '{act['target']}' is not taught by level {level}")
            for g in choices:
                # Distractors may be letters the child has not met. Nobody is
                # asked to READ them -- this is telling one shape from another,
                # which is exactly the job on the early days when there is only
                # one taught letter to choose between.
                if g not in known_graphemes:
                    r.error(f"{where}: choice '{g}' is not in data/phonemes.json")
        if t == "blend":
            word, parts = act["word"].lower(), act["parts"]
            if "".join(p.lower() for p in parts) != word:
                r.error(f"{where}: parts {parts} do not spell '{word}'")
            if len(parts) < 2:
                r.error(f"{where}: a blend needs at least 2 parts")
            if any(len(p) > 3 for p in parts):
                r.error(f"{where}: part longer than 3 letters -- split it into sounds")
        if t == "chooseWord":
            choices = act["choices"]
            if not 2 <= len(choices) <= 4:
                r.error(f"{where}: needs 2-4 choices")
            if act["answer"] not in choices:
                r.error(f"{where}: answer '{act['answer']}' is not among the choices")
            if len(set(c.lower() for c in choices)) != len(choices):
                r.error(f"{where}: duplicate choices")
        if t == "story":
            lines = act["lines"]
            if len(lines) < 3:
                r.error(f"{where}: a story needs at least 3 lines")
            questions = act.get("questions") or []
            if not questions:
                r.error(f"{where}: a story needs at least one comprehension question")
            for q in questions:
                if not q.get("prompt") or not q.get("choices"):
                    r.error(f"{where}: every question needs a prompt and choices")
                elif q.get("answer") not in q["choices"]:
                    r.error(f"{where}: question answer '{q.get('answer')}' is not among its choices")
        if t == "sightWord":
            if act["word"].lower() not in unlocked["sightWords"]:
                r.error(f"{where}: '{act['word']}' is not a sight word taught by level {level}")
        if t == "review":
            if len(act["words"]) < 3:
                r.error(f"{where}: a review needs at least 3 words")

        shown_words += _text_of(act)

    # --- the rule that matters most -------------------------------------
    for word, reason in check_words(shown_words, level):
        r.error(f"'{word}': {reason}")

    # --- connected text is punctuated ------------------------------------
    for text in [a.get("text", "") for a in activities if a.get("type") == "sentence"] + \
                [ln for a in activities if a.get("type") == "story" for ln in a.get("lines", [])]:
        if text.strip() and text.strip()[-1] not in ".!?":
            r.error(f'"{text}": a sentence ends with . ! or ?')

    # --- clusters are a step the sequence delays until day 27 -------------
    # Blends (st, nd, fl...) are taught from day 27 on. Before that a cluster
    # word is decodable but genuinely harder than the CVC words these days are
    # built from, so a lesson full of them is harder than intended.
    if level < BLENDS_FROM:
        hard = sorted({w.lower() for w in shown_words if consonant_clusters(w, level)})
        if len(hard) > 3:
            r.warn(f"{len(hard)} cluster words before day {BLENDS_FROM} ({', '.join(hard[:6])}"
                   f"{'…' if len(hard) > 6 else ''}) -- prefer simple consonant-vowel-consonant "
                   f"words here and keep clusters to a couple of stretch words")

    # --- capital letters are themselves a lesson, on day 23 --------------
    # Before then a child has only ever seen lowercase forms, so an "A" is a
    # letter they have not met. After, sentences are capitalised normally.
    sentences = [a.get("text", "") for a in activities if a.get("type") == "sentence"]
    sentences += [ln for a in activities if a.get("type") == "story" for ln in a.get("lines", [])]
    if level < CAPITALS_FROM:
        for word in shown_words:
            if any(c.isupper() for c in word):
                r.error(f"'{word}': capital letters are not taught until day {CAPITALS_FROM}")
    else:
        for text in sentences:
            first = text.strip()[:1]
            if first and not first.isupper():
                r.error(f'"{text}": sentences start with a capital letter from day {CAPITALS_FROM}')

    # --- shape of the lesson ---------------------------------------------
    if want["graphemes"] and "soundIntro" not in kinds:
        r.error("a level that introduces a new sound must start with a soundIntro")
    if want["sightWords"] and "sightWord" not in kinds:
        r.error("a level that introduces sight words must include a sightWord activity")
    if want["kind"] == "phonics" and kinds.count("blend") < 3 and level > 1:
        r.error("phonics levels need at least 3 blend activities -- blending is the skill")
    if level >= 13 and not ({"sentence", "story"} & set(kinds)):
        r.error("from level 13 on, every lesson must include connected text to read")
    if level >= 21 and "story" not in kinds:
        r.error("from level 21 on, every lesson must end with a story")
    if level >= 5 and "review" not in kinds:
        r.warn("no review activity -- old sounds fade fast without one")

    if want["graphemes"] and level > 2:
        focus_letters = {phonemes()[g]["display"].replace("-", "") for g in want["graphemes"]}
        hits = sum(1 for w in shown_words if any(f in w.lower() for f in focus_letters))
        if hits < 5:
            r.warn(f"the new sound only appears in {hits} words -- aim for at least 8")

    return r


def check_speech_index() -> list[str]:
    """Has a new lesson added sounds or phrases nobody has been asked to record?

    Every new word, sentence and instruction is something a human voice will
    eventually say, so the recording list has to grow with the course rather
    than being rebuilt once and forgotten.
    """
    index_path = DATA / "speech-index.json"
    if not index_path.exists():
        return ["web/data/speech-index.json is missing -- run tools/build_speech_index.py"]
    try:
        from tools.build_speech_index import fingerprint
    except Exception:
        return []
    stored = json.loads(index_path.read_text()).get("sourceFingerprint")
    if stored != fingerprint():
        return ["the recording list is out of date -- these lessons say things "
                "nobody has been asked to record yet. Run:\n"
                "        python3 tools/build_speech_index.py && "
                "python3 tools/build_audio_manifest.py"]
    return []


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    quiet = "--quiet" in sys.argv
    if args:
        paths = [LEVELS_DIR / f"{int(a):03d}.json" for a in args]
    else:
        paths = sorted(LEVELS_DIR.glob("[0-9][0-9][0-9].json"))
    if not paths:
        print("no level files found in data/levels/")
        return 0

    failed = 0
    for path in paths:
        if not path.exists():
            print(f"✗ {path.name}: does not exist")
            failed += 1
            continue
        r = validate_level(path)
        if r.errors:
            failed += 1
            if not quiet:
                print(f"✗ level {r.level} ({path.name})")
                for e in r.errors:
                    print(f"    ERROR   {e}")
                for w in r.warnings:
                    print(f"    warn    {w}")
        elif not quiet:
            note = f"  ({len(r.warnings)} warning{'s' if len(r.warnings) != 1 else ''})" if r.warnings else ""
            print(f"✓ level {r.level}{note}")
            for w in r.warnings:
                print(f"    warn    {w}")

    stale = check_speech_index() if not args else []
    if not quiet:
        print(f"\n{len(paths) - failed}/{len(paths)} levels valid")
        for msg in stale:
            print(f"\n!!  {msg}")
    return 1 if (failed or stale) else 0


if __name__ == "__main__":
    raise SystemExit(main())
