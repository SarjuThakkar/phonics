#!/usr/bin/env python3
"""Generate data/sequence.json -- the 120-level spine of the whole site.

The table below is transcribed from the Mentava public Scope and Sequence
(https://www.mentava.com/assets/docs/mentava-scope-and-sequence.pdf). It is the
ORDER of concepts, which is a pedagogical fact, not their content: every word,
sentence, story and activity on this site is written from scratch.

Each row is:
    level, kind, focus, graphemes, sight_words, seed_words

  kind        "phonics" | "sight" | "review"
  focus       human label shown in the UI and to authoring subagents
  graphemes   NEW graphemes unlocked at this level, machine-readable. These
              are what tools/inventory.py accumulates and tools/validate.py
              decodes against, so they matter more than the label.
  sight_words NEW sight ("heart") words unlocked at this level
  seed_words  the example words the Mentava sequence lists for this level.
              Authors may use them but are not limited to them -- anything
              that segments cleanly against the unlocked graphemes is fair.

Run:  python3 tools/build_sequence.py
"""

import json
import pathlib

# fmt: off
TABLE = [
    # --- Stage 1: single letters, first words (1-20) -------------------------
    (1,  "phonics", "a says /a/",              ["a"],        [], []),
    (2,  "phonics", "m says /m/",              ["m"],        [], ["am"]),
    (3,  "phonics", "s says /s/",              ["s"],        [], ["sam"]),
    (4,  "phonics", "t says /t/",              ["t"],        [], ["sat", "mat", "at"]),
    (5,  "review",  "Reading left to right",   [],           [], []),
    (6,  "phonics", "f says /f/",              ["f"],        [], ["fat"]),
    (7,  "phonics", "d says /d/",              ["d"],        [], ["sad", "mad"]),
    (8,  "phonics", "g says /g/",              ["g"],        [], ["sag", "gas"]),
    (9,  "phonics", "i says /i/",              ["i"],        [], ["fit", "fig", "sit", "dig", "it"]),
    (10, "phonics", "n says /n/",              ["n"],        [], ["fin", "man", "in", "fan", "an"]),
    (11, "phonics", "p says /p/",              ["p"],        [], ["pig", "nap", "pan", "pit", "pat"]),
    (12, "phonics", "h says /h/",              ["h"],        [], ["hit", "him", "had", "hid", "ham"]),
    (13, "phonics", "b says /b/",              ["b"],        [], ["bag", "big", "bat"]),
    (14, "phonics", "l says /l/",              ["l", "ll"],  [], ["lip", "lap", "lit", "lid", "hill", "fill"]),
    (15, "phonics", "j says /j/",              ["j"],        [], ["jam", "jim"]),
    (16, "phonics", "c says /k/",              ["c"],        [], ["can", "cat", "cab", "cap"]),
    (17, "phonics", "v says /v/",              ["v"],        [], ["van"]),
    (18, "phonics", "w says /w/",              ["w"],        [], ["win", "wig"]),
    (19, "phonics", "r says /r/",              ["r"],        [], ["rat", "rip", "ran"]),
    (20, "phonics", "k says /k/",              ["k"],        [], ["kid", "napkin"]),

    # --- Stage 2: letter teams and blends (21-50) ----------------------------
    (21, "phonics", "ck says /k/",             ["ck"],       [], ["pick", "pack", "lick"]),
    (22, "phonics", "sh says /sh/",            ["sh"],       [], ["ship", "fish", "shack", "wish", "dash"]),
    (23, "phonics", "ch says /ch/",            ["ch"],       [], ["chick", "chip", "rich", "chat"]),
    (24, "phonics", "th says /th/ (voiced)",   ["th"],       [], ["that", "this", "than"]),
    (25, "sight",   "the",                     [],       ["the"], []),
    (26, "phonics", "o says /o/",              ["o"],        [], ["not", "rock", "got", "chop", "shot"]),
    (27, "phonics", "nd blend",                ["nd"],       [], ["pond", "sand", "and", "land"]),
    (28, "phonics", "-s makes it plural",      ["-s"],       [], ["cats", "dogs"]),
    (29, "phonics", "mp blend",                ["mp"],       [], ["chimp", "camp", "lump"]),
    (30, "phonics", "ft blend",                ["ft"],       [], ["gift", "lift", "soft"]),
    (31, "phonics", "st blend (ending)",       ["st"],       [], ["lost", "mist", "fast"]),
    (32, "phonics", "sn blend",                ["sn"],       [], ["snack", "snag", "snip", "sniff", "milk"]),
    (33, "phonics", "sw blend",                ["sw"],       [], ["swim", "swam", "swag"]),
    (34, "phonics", "fl blend",                ["fl"],       [], ["flip", "flap", "flop", "flag", "flat"]),
    (35, "sight",   "is",                      [],        ["is"], []),
    (36, "phonics", "fr blend",                ["fr"],       [], ["frog", "frost"]),
    (37, "phonics", "ng says /ng/",            ["ng"],       [], ["long", "sang", "king", "standing", "digging"]),
    (38, "phonics", "nk says /nk/",            ["nk"],       [], ["bank", "wink", "pink", "tank", "rink"]),
    (39, "phonics", "u says /u/",              ["u"],        [], ["duck", "jump", "muffin", "bus", "fun"]),
    (40, "phonics", "sc and sk blends",        ["sc", "sk"], [], ["skip", "mask", "ask"]),
    (41, "phonics", "st blend (starting)",     [],           [], ["stand", "stuck", "stop", "stick"]),
    (42, "phonics", "sp blend",                ["sp"],       [], ["spin", "spot", "spit"]),
    (43, "phonics", "sk blend (starting)",     [],           [], ["skip", "skunk", "skin", "skim"]),
    (44, "phonics", "e says /e/",              ["e"],        [], ["best", "pet", "left", "hen", "red"]),
    (45, "sight",   "they",                    [],     ["they"], []),
    (46, "phonics", "bl blend",                ["bl"],       [], ["blimp", "black", "block", "blond"]),
    (47, "phonics", "cl blend",                ["cl"],       [], ["clams", "cliff", "club", "cluck", "class"]),
    (48, "phonics", "pl blend",                ["pl"],       [], ["plant", "plum", "plan", "plus", "plot"]),
    (49, "phonics", "br and tr blends",        ["br", "tr"], [], ["bring", "brush", "brick", "truck", "trod", "trip"]),
    (50, "phonics", "cr and dr blends",        ["cr", "dr"], [], ["crush", "crab", "craft", "drink", "drag", "drum"]),

    # --- Stage 3: long vowels and silent e (51-71) ---------------------------
    (51, "phonics", "ie says /ie/",            ["ie"],       [], ["pie", "lie", "ties", "flies", "cries"]),
    (52, "phonics", "i_e (silent e)",          ["i_e"],      [], ["time", "hike", "ride", "slide", "kite"]),
    (53, "phonics", "oe says /oe/",            ["oe"],       [], ["toes", "doe", "goes"]),
    (54, "phonics", "o_e (silent e)",          ["o_e"],      [], ["rode", "home", "stone", "hope", "broke"]),
    (55, "phonics", "the long a sound",        [],           [], []),
    (56, "phonics", "a_e (silent e)",          ["a_e"],      [], ["cake", "plane", "snake", "plate", "came"]),
    (57, "phonics", "ue says /oo/",            ["ue"],       [], ["blue", "glue", "true"]),
    (58, "phonics", "u_e (silent e)",          ["u_e"],      [], ["tune", "flute", "june", "tube", "dune"]),
    (59, "phonics", "ee says /ee/",            ["ee"],       [], ["bee", "tree", "street", "sheep", "sleep"]),
    (60, "phonics", "e_e (silent e)",          ["e_e"],      [], ["pete", "steve", "eve", "here"]),
    (61, "review",  "Review: silent e",        [],           [], []),
    (62, "phonics", "ar says /ar/",            ["ar"],       [], ["car", "art", "star", "shark", "farm"]),
    (63, "sight",   "are",                     [],      ["are"], []),
    (64, "phonics", "or says /or/",            ["or"],       [], ["for", "corn", "fork", "morning", "storm"]),
    (65, "phonics", "er says /er/",            ["er"],       [], ["her", "after", "under", "sister", "dinner"]),
    (66, "phonics", "ir says /er/",            ["ir"],       [], ["girl", "bird", "shirt", "chirp", "stir"]),
    (67, "phonics", "ur says /er/",            ["ur"],       [], ["fur", "hurt", "burn", "surf", "curl"]),
    (68, "review",  "Review: bossy r",         [],           [], []),
    (69, "review",  "Review: silent e + bossy r", [],        [], []),
    (70, "sight",   "I, want",                 [],  ["i", "want"], []),
    (71, "sight",   "to, do",                  [],  ["to", "do"], []),

    # --- Stage 4: vowel teams and tricky spellings (72-103) ------------------
    (72, "phonics", "ay says /ae/",            ["ay"],       [], ["day", "hay", "play", "stay", "spray"]),
    (73, "phonics", "ai says /ae/",            ["ai"],       [], ["rain", "tail", "trail", "wait", "paint"]),
    (74, "review",  "Review: ay and ai",       [],           [], []),
    (75, "phonics", "ea says /ee/",            ["ea"],       [], ["sea", "read", "treat", "dream", "clean"]),
    (76, "phonics", "oa says /oe/",            ["oa"],       [], ["boat", "soap", "toad", "toast", "float"]),
    (77, "phonics", "ow says /oe/",            ["ow"],       [], ["row", "show", "snow", "own", "blow"]),
    (78, "review",  "Review: ea, oa, ow",      [],           [], []),
    (79, "review",  "Review: ay, ai, ea, oa, ow", [],        [], []),
    (80, "phonics", "ou says /ow/",            ["ou"],       [], ["found", "shout", "loud", "ground", "outside"]),
    (81, "phonics", "oi says /oi/",            ["oi"],       [], ["coin", "oil", "boil", "point", "join"]),
    (82, "phonics", "oy says /oi/",            ["oy"],       [], ["boy", "toy", "enjoy", "joy", "cowboy"]),
    (83, "review",  "Review: ou, oi, oy",      [],           [], []),
    (84, "phonics", "e at the end says /ee/",  ["-e"],       [], ["we", "be", "he", "she", "me"]),
    (85, "phonics", "o at the end says /oe/",  ["-o"],       [], ["go", "no", "so", "hippo", "hello"]),
    (86, "review",  "Review: long e and o endings", [],      [], []),
    (87, "phonics", "y says /y/",              ["y"],        [], ["yak", "yes", "yum", "yell", "yard"]),
    (88, "sight",   "you",                     [],      ["you"], []),
    (89, "sight",   "said",                    [],     ["said"], []),
    (90, "phonics", "qu says /kw/",            ["qu"],       [], ["quack", "quick", "squid", "squish", "queen"]),
    (91, "phonics", "x says /ks/",             ["x"],        [], ["box", "six", "fox", "mix", "next"]),
    (92, "phonics", "z says /z/",              ["z", "zz"],  [], ["maze", "zipper", "prize", "froze", "jazz"]),
    (93, "phonics", "aw says /aw/",            ["aw"],       [], ["saw", "draw", "hawk", "claw", "straw"]),
    (94, "phonics", "-all says /all/",         ["all"],      [], ["all", "ball", "wall", "small", "mall"]),
    (95, "phonics", "y at the end says /ie/",  ["-y"],       [], ["my", "by", "shy", "fly", "try"]),
    (96, "phonics", "wh says /w/",             ["wh"],       [], ["why", "whale", "white", "wheel", "when"]),
    (97, "sight",   "what",                    [],     ["what"], []),
    (98, "sight",   "where",                   [],    ["where"], []),
    (99, "sight",   "there, here, of",         [], ["there", "here", "of"], []),
    (100, "phonics", "th says /th/ (unvoiced)", [],          [], ["thing", "thick", "thank", "throw", "thunder"]),
    (101, "sight",  "could, would, should",    [], ["could", "would", "should"], []),
    (102, "sight",  "any, anywhere, many",     [], ["any", "anywhere", "many"], []),
    (103, "phonics", "oo says /uu/ and /oo/",  ["oo"],       [], ["good", "cook", "foot", "wood", "shook", "food", "boot", "goose", "moon", "pool"]),

    # --- Stage 5: on to real books (104-120) ---------------------------------
    (104, "sight",  "house, mouse",            [], ["house", "mouse"], []),
    (105, "phonics", "-ed endings",            ["-ed"],      [], ["opened", "backed", "jumped", "landed"]),
    (106, "phonics", "ow says /ow/",           [],           [], ["how", "down", "brown", "cow", "owl"]),
    (107, "phonics", "igh and -alk",           ["igh", "alk"], ["other", "mother", "brother"], ["high", "night", "bright", "might", "light", "walk", "talk"]),
    (108, "phonics", "-le endings",            ["-le"],      [], ["little", "bubble", "juggle", "puzzle", "turtle", "candle"]),
    (109, "sight",  "tomorrow, today, father", [], ["tomorrow", "today", "father"], []),
    (110, "sight",  "bye, your, friend",       [], ["bye", "your", "friend"], []),
    (111, "phonics", "ew says /oo/",           ["ew"],       [], ["flew", "news", "grew", "chew"]),
    (112, "sight",  "again, were",             [], ["again", "were"], []),
    (113, "sight",  "some, horse, hooray",     [], ["some", "horse", "hooray"], []),
    (114, "phonics", "kn and wr (silent letters)", ["kn", "wr"], [], ["knew", "knit", "knight", "knock", "wrap", "write", "wrong"]),
    (115, "phonics", "air, and our and eyes",  ["air"], ["our", "eyes"], ["air", "airport", "airplane", "chair", "hair"]),
    (116, "phonics", "y at the end says /ee/", ["-ey"], ["who", "was"], ["happy", "baby", "sorry", "pretty", "funny", "every"]),
    (117, "sight",  "oh, have, put, away",     [], ["oh", "have", "put", "away"], []),
    (118, "sight",  "one, whole, worth, able", [], ["one", "done", "whole", "worth", "able", "table"], []),
    (119, "phonics", "-ie at the end",         ["-ie"],      [], ["piggie", "cookie", "brownie", "movie"]),
    (120, "phonics", "soft g says /j/",        ["ge"],       [], ["giraffe", "gentle", "gem", "age", "cage", "gerald"]),
]
# fmt: on

STAGES = [
    (1, 20, "Letters and first words",
     "One letter at a time, and the first words you can sound out."),
    (21, 50, "Letter teams and blends",
     "Two letters that make one sound, and words that start or end with two sounds."),
    (51, 71, "Long vowels and silent e",
     "The letter that sneaks onto the end of a word and changes the vowel."),
    (72, 103, "Vowel teams and tricky spellings",
     "Vowels that work in pairs, and the words English spells oddly."),
    (104, 120, "On to real books",
     "The last common words and endings, then real books."),
]


def stage_for(level: int) -> dict:
    for i, (lo, hi, name, blurb) in enumerate(STAGES, start=1):
        if lo <= level <= hi:
            return {"number": i, "name": name, "range": [lo, hi], "blurb": blurb}
    raise ValueError(level)


def main() -> None:
    root = pathlib.Path(__file__).resolve().parent.parent
    levels = []
    for level, kind, focus, graphemes, sight_words, seed_words in TABLE:
        levels.append({
            "level": level,
            "kind": kind,
            "focus": focus,
            "stage": stage_for(level),
            "graphemes": graphemes,
            "sightWords": sight_words,
            "seedWords": seed_words,
        })

    assert [row["level"] for row in levels] == list(range(1, 121)), "levels must be 1..120"

    out = {
        "source": "Order of concepts follows the public Mentava Scope and Sequence; "
                  "all lesson content on this site is original.",
        "stages": [
            {"number": i, "name": n, "range": [lo, hi], "blurb": b}
            for i, (lo, hi, n, b) in enumerate(STAGES, start=1)
        ],
        "levels": levels,
    }
    path = root / "web" / "data" / "sequence.json"
    path.write_text(json.dumps(out, indent=2) + "\n")
    print(f"wrote {path} ({len(levels)} levels)")


if __name__ == "__main__":
    main()
