#!/usr/bin/env python3
"""Generate data/phonemes.json -- how every grapheme is displayed and spoken.

Why this file exists
--------------------
The site speaks with the browser's built-in speech synthesis, so there is
nothing to download and no account anywhere. Speech synthesis is very good at
whole words and poor at isolated sounds: ask it to say "d" and it says the
letter NAME, "dee". So each grapheme carries a `say` string -- a spelling that
makes a normal en-US voice land close to the actual sound.

Two consequences are baked into the engine on purpose:

  * Blending audio is built from WORDS wherever possible, not from stitched
    phonemes, because that is what TTS does well.
  * Stop consonants (b, d, g, k, p, t, ch, j) cannot be said alone without a
    little "uh" on the end. They are marked `stretchy: false`, and the parent
    panel says to clip them short -- /t/, not "tuh" -- because a child who
    learns "tuh" will read "cat" as "cuh-a-tuh" and stall.

If real recordings ever get made, drop them in web/audio/<id>.mp3 and list
them in data/audio-manifest.json; the engine prefers a recording over TTS.

Run:  python3 tools/build_phonemes.py
"""

import json
import pathlib

V, C, D, BL, T, SE, SF, SL = (
    "vowel", "consonant", "digraph", "blend", "team", "silent-e", "suffix", "silent-letter",
)

# id, display, say (TTS spelling), keyword, kind, stretchy
# fmt: off
TABLE = [
    ("a",   "a",   "aah",    "apple",   V,  True),
    ("m",   "m",   "mmm",    "moon",    C,  True),
    ("s",   "s",   "sss",    "sun",     C,  True),
    ("t",   "t",   "t",      "top",     C,  False),
    ("f",   "f",   "fff",    "fish",    C,  True),
    ("d",   "d",   "d",      "dog",     C,  False),
    ("g",   "g",   "g",      "goat",    C,  False),
    ("i",   "i",   "ih",     "igloo",   V,  True),
    ("n",   "n",   "nnn",    "nest",    C,  True),
    ("p",   "p",   "p",      "pig",     C,  False),
    ("h",   "h",   "hh",     "hat",     C,  False),
    ("b",   "b",   "b",      "bug",     C,  False),
    ("l",   "l",   "lll",    "leaf",    C,  True),
    ("ll",  "ll",  "lll",    "hill",    C,  True),
    ("j",   "j",   "j",      "jam",     C,  False),
    ("c",   "c",   "k",      "cat",     C,  False),
    ("v",   "v",   "vvv",    "van",     C,  True),
    ("w",   "w",   "wuh",    "web",     C,  False),
    ("r",   "r",   "rrr",    "rat",     C,  True),
    ("k",   "k",   "k",      "kite",    C,  False),
    ("ck",  "ck",  "k",      "duck",    D,  False),
    ("sh",  "sh",  "shh",    "ship",    D,  True),
    ("ch",  "ch",  "ch",     "chip",    D,  False),
    ("th",  "th",  "thh",    "this",    D,  True),
    ("o",   "o",   "awe",    "otter",   V,  True),
    ("u",   "u",   "uh",     "up",      V,  True),
    ("e",   "e",   "eh",     "egg",     V,  True),
    ("y",   "y",   "yuh",    "yak",     C,  False),
    ("x",   "x",   "ks",     "box",     C,  False),
    ("z",   "z",   "zzz",    "zip",     C,  True),
    ("zz",  "zz",  "zzz",    "jazz",    C,  True),
    ("qu",  "qu",  "kw",     "queen",   D,  False),
    ("wh",  "wh",  "wuh",    "whale",   D,  False),
    ("ng",  "ng",  "ng",     "king",    D,  True),
    ("nk",  "nk",  "nk",     "pink",    D,  False),

    ("nd",  "nd",  "nd",     "sand",    BL, False),
    ("mp",  "mp",  "mp",     "camp",    BL, False),
    ("ft",  "ft",  "ft",     "gift",    BL, False),
    ("st",  "st",  "sst",    "stop",    BL, False),
    ("sn",  "sn",  "ssn",    "snack",   BL, False),
    ("sw",  "sw",  "ssw",    "swim",    BL, False),
    ("fl",  "fl",  "ffl",    "flag",    BL, False),
    ("fr",  "fr",  "ffr",    "frog",    BL, False),
    ("sc",  "sc",  "ssk",    "scat",    BL, False),
    ("sk",  "sk",  "ssk",    "skip",    BL, False),
    ("sp",  "sp",  "ssp",    "spin",    BL, False),
    ("bl",  "bl",  "bl",     "block",   BL, False),
    ("cl",  "cl",  "kl",     "club",    BL, False),
    ("pl",  "pl",  "pl",     "plan",    BL, False),
    ("br",  "br",  "br",     "brick",   BL, False),
    ("tr",  "tr",  "tr",     "truck",   BL, False),
    ("cr",  "cr",  "kr",     "crab",    BL, False),
    ("dr",  "dr",  "dr",     "drum",    BL, False),

    ("ie",  "ie",  "eye",    "pie",     T,  True),
    ("oe",  "oe",  "oh",     "toes",    T,  True),
    ("ue",  "ue",  "oo",     "blue",    T,  True),
    ("ee",  "ee",  "ee",     "bee",     T,  True),
    ("ea",  "ea",  "ee",     "sea",     T,  True),
    ("ai",  "ai",  "ay",     "rain",    T,  True),
    ("ay",  "ay",  "ay",     "day",     T,  True),
    ("oa",  "oa",  "oh",     "boat",    T,  True),
    ("ow",  "ow",  "oh",     "snow",    T,  True),
    ("ou",  "ou",  "ow",     "loud",    T,  True),
    ("oi",  "oi",  "oy",     "coin",    T,  True),
    ("oy",  "oy",  "oy",     "toy",     T,  True),
    ("aw",  "aw",  "aw",     "saw",     T,  True),
    ("oo",  "oo",  "oo",     "moon",    T,  True),
    ("ew",  "ew",  "oo",     "flew",    T,  True),
    ("igh", "igh", "eye",    "night",   T,  True),
    ("air", "air", "air",    "chair",   T,  True),

    ("ar",  "ar",  "arr",    "car",     T,  True),
    ("or",  "or",  "or",     "fork",    T,  True),
    ("er",  "er",  "er",     "her",     T,  True),
    ("ir",  "ir",  "er",     "bird",    T,  True),
    ("ur",  "ur",  "er",     "fur",     T,  True),

    ("a_e", "a-e", "ay",     "cake",    SE, True),
    ("i_e", "i-e", "eye",    "kite",    SE, True),
    ("o_e", "o-e", "oh",     "home",    SE, True),
    ("u_e", "u-e", "oo",     "flute",   SE, True),
    ("e_e", "e-e", "ee",     "eve",     SE, True),

    ("all", "all", "all",    "ball",    T,  True),
    ("alk", "alk", "awk",    "walk",    T,  True),
    ("kn",  "kn",  "nnn",    "knock",   SL, True),
    ("wr",  "wr",  "rrr",    "write",   SL, True),
    ("ge",  "ge",  "j",      "cage",    D,  False),

    ("-s",  "-s",  "sss",    "cats",    SF, True),
    ("-ed", "-ed", "ed",     "landed",  SF, False),
    ("-le", "-le", "ul",     "little",  SF, True),
    ("-e",  "-e",  "ee",     "me",      T,  True),
    ("-o",  "-o",  "oh",     "go",      T,  True),
    ("-y",  "-y",  "eye",    "fly",     T,  True),
    ("-ey", "-y",  "ee",     "happy",   T,  True),
    ("-ie", "-ie", "ee",     "cookie",  T,  True),
]
# fmt: on


def main() -> None:
    root = pathlib.Path(__file__).resolve().parent.parent
    sequence = json.loads((root / "web" / "data" / "sequence.json").read_text())

    phonemes = {}
    for gid, display, say, keyword, kind, stretchy in TABLE:
        phonemes[gid] = {
            "id": gid,
            "display": display,
            "say": say,
            "keyword": keyword,
            "kind": kind,
            "stretchy": stretchy,
        }

    used = {g for lvl in sequence["levels"] for g in lvl["graphemes"]}
    missing = sorted(used - set(phonemes))
    if missing:
        raise SystemExit(f"sequence.json uses graphemes with no phoneme entry: {missing}")

    path = root / "web" / "data" / "phonemes.json"
    path.write_text(json.dumps(phonemes, indent=2) + "\n")
    print(f"wrote {path} ({len(phonemes)} graphemes, {len(used)} used by the sequence)")


if __name__ == "__main__":
    main()
