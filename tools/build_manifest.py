#!/usr/bin/env python3
"""Generate data/levels/manifest.json -- which days actually exist.

The home page needs to know which of the 120 days are written so it can dim
the rest, and it can't ask the filesystem. Regenerate this after authoring.

Run:  python3 tools/build_manifest.py
"""

import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "web" / "data"
LEVELS = DATA / "levels"


def main() -> None:
    entries = []
    for path in sorted(LEVELS.glob("[0-9][0-9][0-9].json")):
        data = json.loads(path.read_text())
        entries.append({
            "level": data["level"],
            "title": data["title"],
            "kidTitle": data["kidTitle"],
            "activities": len(data.get("activities", [])),
        })
    entries.sort(key=lambda e: e["level"])
    out = {"built": [e["level"] for e in entries], "levels": entries}
    (LEVELS / "manifest.json").write_text(json.dumps(out, indent=2) + "\n")
    print(f"wrote manifest: {len(entries)} level(s) built"
          + (f", up to day {entries[-1]['level']}" if entries else ""))


if __name__ == "__main__":
    main()
