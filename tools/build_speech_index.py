#!/usr/bin/env python3
"""Generate web/data/speech-index.json -- everything the site ever says.

This is the recording list. Every sound, word, sentence and spoken instruction
in the whole course, each with a stable id and filename, so a human voice can
replace the browser's synthetic one a file at a time.

The site plays a recording whenever one exists and falls back to the browser
otherwise, so the list can be worked through in any order and partial coverage
is genuinely useful -- record the 93 letter sounds and the worst of the
synthetic voice is already gone.

Entries are sorted by how much work each recording does: a word used in
fourteen lessons is worth recording before a story line used once.

Run:  python3 tools/build_speech_index.py
"""

from __future__ import annotations

import collections
import hashlib
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from tools.lexicon import phonemes, sequence, words_in

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "web" / "data"
LEVELS = DATA / "levels"


def short(text: str) -> str:
    return hashlib.sha1(text.encode()).hexdigest()[:6]


def fingerprint() -> str:
    """A hash of everything the index is derived from.

    Stored in the index so validate.py can tell when a newly authored lesson
    has added sounds or phrases that nobody has been asked to record yet.
    """
    h = hashlib.sha1()
    for path in sorted(LEVELS.glob("[0-9][0-9][0-9].json")):
        h.update(path.read_bytes())
    for name in ("activities.js", "lesson.js"):
        h.update((ROOT / "web" / "js" / name).read_bytes())
    h.update((DATA / "phonemes.json").read_bytes())
    h.update((DATA / "sequence.json").read_bytes())
    return h.hexdigest()[:16]


def sound_id(gid: str) -> str:
    """A readable, collision-free filename per grapheme.

    "y" and "-y" are different sounds (yak vs happy) and both display as "y",
    so the id has to come from the grapheme id, not what is printed.
    """
    core = gid.replace("_", "-")
    if core.startswith("-"):
        core = "end-" + core[1:]
    return f"sound-{core}"


def slug(text: str, words: int = 4) -> str:
    parts = re.findall(r"[a-z]+", text.lower())[:words]
    return "-".join(parts) or "x"


def ui_phrases() -> list[str]:
    """The fixed things the player says, read straight out of the player.

    Only literal strings: anything built from a template is different every
    time and has to stay synthetic. Reading them from the source keeps this
    list honest when the player changes.
    """
    out = []
    for name in ("activities.js", "lesson.js"):
        src = (ROOT / "web" / "js" / name).read_text()
        for m in re.finditer(r"Speech\.(?:say|sentence|word)\(\s*'((?:[^'\\]|\\.)*)'", src):
            text = m.group(1).replace("\\'", "'")
            if text.strip() and not text.startswith("$"):
                out.append(text)
        # default prompts sit in `const instruction = act.prompt || '...'`
        for m in re.finditer(r"act\.prompt \|\| '((?:[^'\\]|\\.)*)'", src):
            out.append(m.group(1).replace("\\'", "'"))
    return sorted(set(out))


def collect() -> list[dict]:
    entries: dict[str, dict] = {}

    def add(kind: str, id_: str, text: str, script: str, day: int | None):
        e = entries.setdefault(id_, {
            "id": id_, "kind": kind, "text": text, "script": script,
            "file": f"{id_}.mp3", "days": [],
        })
        if day and day not in e["days"]:
            e["days"].append(day)

    # --- the letter sounds: the most valuable recordings in the whole list ---
    # Kept in teaching order, so recording them start to finish walks the
    # course the same way a child does.
    table = phonemes()
    seen: set[str] = set()
    for lvl in sequence()["levels"]:
        for gid in lvl["graphemes"]:
            if gid in seen:
                continue
            seen.add(gid)
            e = table[gid]
            hold = "Hold it for about a second" if e["stretchy"] else \
                   "Keep it short and clean -- /t/, not \"tuh\""
            add("sound", sound_id(gid),
                e["display"],
                f'The SOUND of "{e["display"]}" as in "{e["keyword"]}" -- '
                f'not the letter name. {hold}.',
                lvl["level"])

    # --- words, sentences, story lines, and any prompt an author wrote -------
    for path in sorted(LEVELS.glob("[0-9][0-9][0-9].json")):
        data = json.loads(path.read_text())
        day = data["level"]
        for act in data.get("activities", []):
            for key in ("word", "answer"):
                if act.get(key):
                    w = act[key].lower()
                    add("word", f"word-{w}", w, f'The word "{w}", said clearly and slowly.', day)
            # soundMatch choices are grapheme ids, not words -- they are
            # already covered by the sound recordings above.
            word_keys = ("words",) if act["type"] == "soundMatch" else ("words", "choices")
            for key in word_keys:
                for w in act.get(key, []) or []:
                    if isinstance(w, str) and re.fullmatch(r"[A-Za-z]+", w):
                        add("word", f"word-{w.lower()}", w.lower(),
                            f'The word "{w.lower()}", said clearly and slowly.', day)
            lines = []
            if act.get("text"):
                lines.append(act["text"])
            lines += act.get("lines", []) or []
            for q in act.get("questions", []) or []:
                if q.get("prompt"):
                    lines.append(q["prompt"])
                for choice in q.get("choices", []):
                    if choice and not re.fullmatch(r"[A-Za-z]+", choice):
                        lines.append(choice)
            if act.get("sentence"):
                lines.append(act["sentence"])
            for line in lines:
                add("line", f"line-{slug(line)}-{short(line)}", line,
                    f'Read aloud, warmly, at storytime pace: "{line}"', day)
            if act.get("prompt"):
                add("prompt", f"prompt-{slug(act['prompt'])}-{short(act['prompt'])}",
                    act["prompt"], f'Spoken instruction: "{act["prompt"]}"', day)
            if act.get("mouthCue"):
                add("prompt", f"prompt-{slug(act['mouthCue'])}-{short(act['mouthCue'])}",
                    act["mouthCue"], f'Spoken instruction: "{act["mouthCue"]}"', day)

    # --- the player's own fixed lines ---------------------------------------
    for text in ui_phrases():
        add("ui", f"ui-{slug(text)}-{short(text)}", text,
            f'Spoken by the app itself: "{text}"', None)

    # Sounds first, in teaching order. Everything else by how many lessons the
    # one recording serves, so the most valuable work comes first.
    order = {"sound": 0, "ui": 1, "word": 2, "prompt": 3, "line": 4}
    out = sorted(entries.values(),
                 key=lambda e: (order[e["kind"]],
                                min(e["days"]) if e["kind"] == "sound" and e["days"] else 0,
                                -len(e["days"]), e["text"]))
    for e in out:
        e["days"].sort()
    return out


def main() -> None:
    entries = collect()
    counts = collections.Counter(e["kind"] for e in entries)
    (DATA / "speech-index.json").write_text(json.dumps({
        "note": "Every string the site speaks. Record any of them into "
                "web/audio/human/<id>.mp3 and the site will use the recording "
                "instead of the browser voice.",
        "sourceFingerprint": fingerprint(),
        "counts": dict(counts),
        "entries": entries,
    }, indent=2, ensure_ascii=False) + "\n")
    print(f"wrote speech index: {len(entries)} recordable strings "
          + ", ".join(f"{k}={v}" for k, v in sorted(counts.items())))


if __name__ == "__main__":
    main()
