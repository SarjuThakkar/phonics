#!/usr/bin/env python3
"""What a child can read by a given level -- the brief for whoever writes it.

Run this first when authoring a level. It prints, in one screen:

  * the level's assignment straight from the scope and sequence
  * every sound taught so far, with its keyword
  * every sight word taught so far
  * the words earlier lessons already used, so review is spaced and the new
    lesson doesn't reuse the same six words a fourth time

It reads the authored level files, so it stays true as the curriculum is built
out -- which is the point of building levels in order.

Usage:  python3 tools/inventory.py 37
"""

from __future__ import annotations

import json
import pathlib
import sys
import textwrap

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from tools.lexicon import phonemes, sequence, unlocked_through, words_in

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "web" / "data"
LEVELS_DIR = DATA / "levels"


def words_used_before(level: int) -> dict[int, list[str]]:
    """Words each earlier authored lesson put in front of the child."""
    out: dict[int, list[str]] = {}
    for path in sorted(LEVELS_DIR.glob("[0-9][0-9][0-9].json")):
        data = json.loads(path.read_text())
        if data.get("level", 999) >= level:
            continue
        seen: list[str] = []
        for act in data.get("activities", []):
            for key in ("word", "answer"):
                if act.get(key):
                    seen.append(act[key])
            for key in ("words", "choices"):
                seen += [w for w in act.get(key, []) if isinstance(w, str)]
            if act.get("text"):
                seen += words_in(act["text"])
            for line in act.get("lines", []):
                seen += words_in(line)
        out[data["level"]] = sorted({w.lower() for w in seen})
    return out


def wrap(items, width=76, indent="    ") -> str:
    return textwrap.fill(", ".join(items), width=width,
                         initial_indent=indent, subsequent_indent=indent) or indent + "(none)"


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    level = int(sys.argv[1])
    spec = {lvl["level"]: lvl for lvl in sequence()["levels"]}[level]
    unlocked = unlocked_through(level)
    before = unlocked_through(level - 1) if level > 1 else {"graphemes": [], "sightWords": []}
    table = phonemes()

    print(f"╔═ LEVEL {level} — {spec['focus']}")
    print(f"║  stage {spec['stage']['number']}: {spec['stage']['name']}   ·   kind: {spec['kind']}")
    print("╚" + "═" * 70)
    print()
    print("NEW THIS LEVEL (must appear; nothing else new may)")
    for g in spec["graphemes"]:
        e = table[g]
        print(f"    {e['display']:<5} says /{e['say']}/  as in {e['keyword']}"
              f"   [{e['kind']}, {'stretchy' if e['stretchy'] else 'quick — clip it short'}]")
    for w in spec["sightWords"]:
        print(f"    sight word: {w}")
    if not spec["graphemes"] and not spec["sightWords"]:
        print("    nothing new — this is a review level; consolidate, don't introduce")
    if spec["seedWords"]:
        print("\n  words the scope and sequence lists here (use them, and add more):")
        print(wrap(spec["seedWords"]))

    print(f"\nSOUNDS ALREADY TAUGHT ({len(before['graphemes'])})")
    print(wrap([f"{table[g]['display']}" for g in before["graphemes"]]))

    print(f"\nSIGHT WORDS ALREADY TAUGHT ({len(before['sightWords'])})")
    print(wrap(before["sightWords"]))

    used = words_used_before(level)
    total = sorted({w for ws in used.values() for w in ws})
    print(f"\nWORDS EARLIER LESSONS ALREADY USED ({len(total)} across {len(used)} levels)")
    recent = [lv for lv in sorted(used) if lv >= level - 5]
    for lv in recent:
        print(f"  L{lv}: " + ", ".join(used[lv][:24]) + (" …" if len(used[lv]) > 24 else ""))
    if not recent:
        print("    (no earlier lessons authored yet)")

    print("\nCHECK ANY WORD:  python3 tools/lexicon.py %d <word> [<word> …]" % level)
    print("VALIDATE:        python3 tools/validate.py %d" % level)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
