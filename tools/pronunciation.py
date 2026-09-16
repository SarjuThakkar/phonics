#!/usr/bin/env python3
"""How to say each sound, written for a person, not a phonetician.

This is what shows up on /record.html while recording. No IPA, no /slashes/ --
just a spelling you can read aloud, three words to find the sound in, and the
mistake to avoid. The single most common mistake is saying the letter's NAME
("ay" for a), which is exactly what a child must not learn, so nearly every
entry names it explicitly.

  say      a spelling to read straight off the screen
  words    three words that contain the sound, in the position it is taught
  avoid    the wrong version, named plainly

The method that works if an entry ever reads oddly: say the three words out
loud and listen for the part they share. That part is the sound.
"""

# gid: (say, words, avoid)
# fmt: off
PRONUNCIATION = {
    # --- short vowels ----------------------------------------------------
    "a":   ("aaa",  ["apple", "ant", "cat"],        "Not 'ay' — that's the letter's name."),
    "i":   ("ih",   ["igloo", "insect", "sit"],     "Not 'eye' — that's the letter's name."),
    "o":   ("ah",   ["otter", "on", "hot"],         "Not 'oh' — that's the letter's name."),
    "u":   ("uh",   ["up", "under", "bus"],         "Not 'you' — that's the letter's name."),
    "e":   ("eh",   ["egg", "elephant", "bed"],     "Not 'ee' — that's the letter's name."),

    # --- consonants you can hold ----------------------------------------
    "m":   ("mmmmm", ["moon", "man", "mud"],        "Lips together and hum. No 'muh'."),
    "s":   ("sssss", ["sun", "sit", "bus"],         "A long hiss. No 'suh'."),
    "f":   ("fffff", ["fish", "fan", "leaf"],       "Teeth on lip, blow. No 'fuh'."),
    "n":   ("nnnnn", ["nest", "net", "sun"],        "Hum through your nose. No 'nuh'."),
    "l":   ("lllll", ["leaf", "lip", "log"],        "Tongue behind top teeth. No 'luh'."),
    "ll":  ("lllll", ["hill", "fill", "bell"],      "Two letters, one sound — same as a single l."),
    "r":   ("rrrrr", ["rat", "run", "red"],         "Like a little growl. No 'ruh'."),
    "v":   ("vvvvv", ["van", "vet", "give"],        "Like an f with your voice on. No 'vuh'."),
    "z":   ("zzzzz", ["zip", "zoo", "buzz"],        "A bee sound. No 'zuh'."),
    "zz":  ("zzzzz", ["jazz", "buzz", "fizz"],      "Two letters, one sound — same as a single z."),
    "sh":  ("shhhh", ["ship", "shop", "fish"],      "The 'be quiet' sound. No 'shuh'."),
    "th":  ("thhhh", ["this", "that", "them"],      "Tongue between your teeth, voice ON — it buzzes."),
    "ng":  ("nnng",  ["king", "sing", "long"],      "The sound at the END of 'sing'. No 'nuh-guh'."),

    # --- quick consonants: clip them short ------------------------------
    "t":   ("t",   ["top", "tap", "cat"],           "As short as you can. NOT 'tuh'."),
    "d":   ("d",   ["dog", "dad", "red"],           "As short as you can. NOT 'duh'."),
    "g":   ("g",   ["goat", "gas", "bag"],          "As short as you can. NOT 'guh'."),
    "p":   ("p",   ["pig", "pan", "top"],           "A tiny puff of air. NOT 'puh'."),
    "b":   ("b",   ["bug", "bat", "cab"],           "As short as you can. NOT 'buh'."),
    "c":   ("k",   ["cat", "can", "cap"],           "The same sound as k. NOT 'kuh'."),
    "k":   ("k",   ["kite", "kid", "kit"],          "As short as you can. NOT 'kuh'."),
    "ck":  ("k",   ["duck", "pack", "sick"],        "Two letters, one sound, always at the end. NOT 'kuh'."),
    "j":   ("j",   ["jam", "jet", "jug"],           "As short as you can. NOT 'juh'."),
    "ch":  ("ch",  ["chip", "chat", "much"],        "Like a train starting. NOT 'chuh'."),
    "h":   ("h",   ["hat", "hop", "hit"],           "Just a breath out. NOT 'huh'."),
    "w":   ("w",   ["web", "wet", "win"],           "Round your lips. As short as you can, not 'wuh'."),
    "y":   ("y",   ["yak", "yes", "yell"],          "The sound that starts 'yes'. Not 'why'."),
    "x":   ("ks",  ["box", "six", "fox"],           "Two sounds run together, k then s. It only comes at the end."),
    "qu":  ("kw",  ["queen", "quick", "quack"],     "k and w run together. Never one without the other."),
    "wh":  ("w",   ["whale", "when", "wheel"],      "Same as w for most people. Don't force a puff."),
    "nk":  ("nk",  ["pink", "bank", "wink"],        "The ending of 'pink'. Say the whole ending, not two sounds."),
    "kn":  ("nnnnn", ["knock", "knee", "knit"],     "The k is silent — this says exactly the same as n."),
    "wr":  ("rrrrr", ["write", "wrap", "wrong"],    "The w is silent — this says exactly the same as r."),
    "ge":  ("j",   ["cage", "gem", "age"],          "A soft g — the same sound as j."),

    # --- letters run together (say both, quickly) ------------------------
    "nd":  ("nd",  ["sand", "hand", "and"],         "Both sounds, run together at the end."),
    "mp":  ("mp",  ["camp", "jump", "lamp"],        "Both sounds, run together at the end."),
    "ft":  ("ft",  ["gift", "lift", "soft"],        "Both sounds, run together at the end."),
    "st":  ("sst", ["stop", "stick", "fast"],       "Hold the s, then the quick t."),
    "sn":  ("ssn", ["snack", "snip", "snow"],       "Hold the s, then slide into n."),
    "sw":  ("ssw", ["swim", "swam", "sweet"],       "Hold the s, then slide into w."),
    "fl":  ("ffl", ["flag", "flip", "flat"],        "Hold the f, then slide into l."),
    "fr":  ("ffr", ["frog", "from", "frost"],       "Hold the f, then slide into r."),
    "sc":  ("ssk", ["scat", "scan", "scab"],        "Hold the s, then the quick k."),
    "sk":  ("ssk", ["skip", "skin", "mask"],        "Hold the s, then the quick k."),
    "sp":  ("ssp", ["spin", "spot", "spill"],       "Hold the s, then the quick p."),
    "bl":  ("bl",  ["block", "blue", "black"],      "Both sounds, run together. Not 'buh-luh'."),
    "cl":  ("kl",  ["club", "clap", "class"],       "Both sounds, run together. Not 'kuh-luh'."),
    "pl":  ("pl",  ["plan", "plus", "plate"],       "Both sounds, run together. Not 'puh-luh'."),
    "br":  ("br",  ["brick", "bring", "brush"],     "Both sounds, run together. Not 'buh-ruh'."),
    "tr":  ("tr",  ["truck", "trip", "tree"],       "Both sounds, run together. Not 'tuh-ruh'."),
    "cr":  ("kr",  ["crab", "crush", "cry"],        "Both sounds, run together. Not 'kuh-ruh'."),
    "dr":  ("dr",  ["drum", "drag", "drink"],       "Both sounds, run together. Not 'duh-ruh'."),

    # --- long vowels and vowel teams -------------------------------------
    "ie":  ("eye", ["pie", "lie", "tie"],           "The word 'eye'."),
    "oe":  ("oh",  ["toes", "doe", "goes"],         "The word 'oh'."),
    "ue":  ("oo",  ["blue", "glue", "true"],        "Like the 'oo' in 'moon'."),
    "ee":  ("eee", ["bee", "tree", "sleep"],        "A long 'ee'. Hold it."),
    "ea":  ("eee", ["sea", "dream", "clean"],       "Same sound as 'ee' — a long 'ee'."),
    "ai":  ("ay",  ["rain", "tail", "wait"],        "Like the letter a's name."),
    "ay":  ("ay",  ["day", "play", "stay"],         "Like the letter a's name."),
    "oa":  ("oh",  ["boat", "soap", "float"],       "The word 'oh'."),
    "ow":  ("oh",  ["snow", "show", "blow"],        "The word 'oh' — this is the 'snow' one, not 'cow'."),
    "ou":  ("ow",  ["loud", "found", "shout"],      "Like 'ouch'."),
    "oi":  ("oy",  ["coin", "oil", "point"],        "Like the word 'oy'."),
    "oy":  ("oy",  ["toy", "boy", "enjoy"],         "Like the word 'oy'."),
    "aw":  ("aww", ["saw", "draw", "claw"],         "Like the start of 'awesome'."),
    "oo":  ("oooo", ["moon", "boot", "pool"],       "The long one, as in 'moon' — not the 'book' one."),
    "ew":  ("oo",  ["flew", "new", "grew"],         "Like the 'oo' in 'moon'."),
    "igh": ("eye", ["night", "light", "high"],      "Three letters, one sound: the word 'eye'."),
    "air": ("air", ["chair", "hair", "fair"],       "The word 'air'."),
    "all": ("all", ["ball", "wall", "small"],       "The word 'all'. The a is not its usual short sound."),
    "alk": ("awk", ["walk", "talk", "chalk"],       "Rhymes with 'hawk'. The l is silent."),

    # --- bossy r ----------------------------------------------------------
    "ar":  ("aaar", ["car", "star", "farm"],        "Like a pirate. Hold it."),
    "or":  ("or",   ["fork", "corn", "storm"],      "The word 'or'."),
    "er":  ("er",   ["her", "sister", "dinner"],    "The sound at the end of 'sister'."),
    "ir":  ("er",   ["bird", "girl", "shirt"],      "The same sound as 'er'."),
    "ur":  ("er",   ["fur", "burn", "hurt"],        "The same sound as 'er'."),

    # --- silent e ---------------------------------------------------------
    "a_e": ("ay",  ["cake", "plane", "snake"],      "The letter a saying its own name."),
    "i_e": ("eye", ["kite", "time", "ride"],        "The letter i saying its own name."),
    "o_e": ("oh",  ["home", "stone", "hope"],       "The letter o saying its own name."),
    "u_e": ("oo",  ["flute", "tune", "June"],       "Like the 'oo' in 'moon'."),
    "e_e": ("eee", ["eve", "here", "Pete"],         "The letter e saying its own name."),

    # --- endings ----------------------------------------------------------
    "-s":  ("sss", ["cats", "naps", "bats"],        "The hiss on the end. No 'suh'."),
    "-ed": ("ed",  ["landed", "wanted", "handed"],  "Just the ending, as in 'land-ed'."),
    "-le": ("ul",  ["little", "bubble", "candle"],  "The mumble at the end of 'little'."),
    "-e":  ("eee", ["me", "we", "she"],             "A long 'ee' at the end of a short word."),
    "-o":  ("oh",  ["go", "no", "hello"],           "The word 'oh' at the end of a word."),
    "-y":  ("eye", ["my", "fly", "try"],            "Like the word 'eye' — this is the 'fly' one."),
    "-ey": ("eee", ["happy", "funny", "baby"],      "A long 'ee' — this is the 'happy' one, not 'fly'."),
    "-ie": ("eee", ["cookie", "movie", "brownie"],  "A long 'ee' at the end."),
}
# fmt: on


def guide(gid: str) -> dict | None:
    """The recording script for one grapheme."""
    entry = PRONUNCIATION.get(gid)
    if not entry:
        return None
    say, words, avoid = entry
    return {"say": say, "words": words, "avoid": avoid}


if __name__ == "__main__":
    import json
    import pathlib
    import sys

    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
    from tools.lexicon import phonemes

    missing = sorted(set(phonemes()) - set(PRONUNCIATION))
    extra = sorted(set(PRONUNCIATION) - set(phonemes()))
    if missing:
        print(f"no pronunciation guide for: {missing}")
    if extra:
        print(f"guide for graphemes that don't exist: {extra}")
    if not missing and not extra:
        print(f"all {len(PRONUNCIATION)} graphemes have a recording script")
    print(json.dumps(guide("a"), indent=2))
