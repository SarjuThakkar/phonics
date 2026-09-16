#!/usr/bin/env python3
"""Exactly what to record to hear one day entirely in a real voice.

    python3 tools/recording_plan.py 1

Recording the whole course is 635 files. Recording one day is usually a dozen,
which is the sensible way to try it: do day 1, play it, decide whether the
approach is right before doing the rest.

Prints them in the order the lesson says them, marks what is already recorded,
and skips anything the player builds on the fly (a few lines splice in a word,
so they can never be a single recording and always fall back to the browser).
"""

from __future__ import annotations

import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "web" / "data"

def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    day = int(sys.argv[1])

    index = json.loads((DATA / "speech-index.json").read_text())
    by_id = {e["id"]: e for e in index["entries"]}
    try:
        recorded = set(json.loads((DATA / "audio-manifest.json").read_text())["files"])
    except Exception:
        recorded = set()

    level_path = DATA / "levels" / f"{day:03d}.json"
    if not level_path.exists():
        print(f"day {day} has not been written yet")
        return 1
    level = json.loads(level_path.read_text())

    wanted = index.get("plans", {}).get(str(day), [])
    if not wanted:
        print("no recording plan for that day -- run tools/build_speech_index.py")
        return 1

    todo = [i for i in wanted if i not in recorded]
    print(f"Day {day} — {level['kidTitle']} ({level['title']})")
    print(f"{len(wanted)} recordings cover this whole lesson; "
          f"{len(recorded & set(wanted))} already done, {len(todo)} to go.\n")

    order = {"sound": 0, "ui": 1, "prompt": 2, "word": 3, "line": 4}
    label = {"sound": "SOUND", "ui": "APP", "prompt": "INSTRUCTION",
             "word": "WORD", "line": "SENTENCE"}
    for entry_id in sorted(wanted, key=lambda i: (order[by_id[i]["kind"]], by_id[i]["text"])):
        e = by_id[entry_id]
        mark = "✓" if entry_id in recorded else " "
        print(f" {mark} [{label[e['kind']]:<11}] {e['id']}")
        print(f"      “{e['text']}”")
        if e.get("how"):
            print(f"      say “{e['how']['say']}” — the sound in "
                  f"{', '.join(e['how']['words'])}. {e['how']['avoid']}")
    print("\nRecord them at /record.html, or drop files into web/audio/human/.")
    print("Anything not recorded keeps using the browser voice, so a part-done "
          "day still works.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
