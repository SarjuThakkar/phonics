#!/usr/bin/env python3
"""Generate web/data/audio-manifest.json -- which recordings actually exist.

Drop a file into web/audio/human/ named after an id from the speech index
(`sound-sh.mp3`, `word-cat.mp3`, `line-a-fat-rat-did-9f21c3.mp3`) and run this.
The site then plays that recording everywhere the string is spoken, and keeps
using the browser voice for everything not yet recorded.

Any audio format a browser can play works: .mp3, .m4a, .ogg, .wav, .webm.

Run:  python3 tools/build_audio_manifest.py
"""

from __future__ import annotations

import collections
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "web" / "data"
HUMAN = ROOT / "web" / "audio" / "human"
PLAYABLE = {".mp3", ".m4a", ".ogg", ".oga", ".wav", ".webm", ".aac", ".flac"}


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def main() -> None:
    index = json.loads((DATA / "speech-index.json").read_text())
    by_id = {e["id"]: e for e in index["entries"]}

    HUMAN.mkdir(parents=True, exist_ok=True)
    files: dict[str, str] = {}
    unknown: list[str] = []
    for path in sorted(HUMAN.iterdir()):
        if path.name.startswith(".") or path.suffix.lower() not in PLAYABLE:
            continue
        if path.stem in by_id:
            files[path.stem] = path.name
        else:
            unknown.append(path.name)

    # Everything except the letter sounds is matched by what it says, so one
    # recording of "the cat sat" serves every lesson that uses that line.
    text_lookup = {
        normalize(by_id[i]["text"]): i
        for i in files
        if by_id[i]["kind"] != "sound"
    }

    (DATA / "audio-manifest.json").write_text(json.dumps({
        "count": len(files),
        "files": files,
        "text": text_lookup,
    }, indent=2, ensure_ascii=False) + "\n")

    total = len(index["entries"])
    done = collections.Counter(by_id[i]["kind"] for i in files)
    have_sounds = done.get("sound", 0)
    all_sounds = index["counts"].get("sound", 0)
    print(f"{len(files)}/{total} strings recorded"
          + (f"  ({', '.join(f'{k}={v}' for k, v in sorted(done.items()))})" if done else ""))
    print(f"letter sounds: {have_sounds}/{all_sounds}"
          + ("  <- record these first; they are what the browser voice gets worst"
             if have_sounds < all_sounds else "  <- complete"))
    if unknown:
        print(f"\n{len(unknown)} file(s) in web/audio/human/ match no id in the speech index "
              f"and will be ignored:")
        for name in unknown[:10]:
            print(f"    {name}")
        print("    (ids come from web/data/speech-index.json -- see /record.html)")


if __name__ == "__main__":
    main()
