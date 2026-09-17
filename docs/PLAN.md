# Build plan

## The shape of the work

The site engine is finished and fixed. What remains is **content**: 118 more
lesson files, each one a `web/data/levels/NNN.json`.

That work is split across many authoring agents, one batch at a time, because
a single context cannot hold 120 lessons and should not try. The pieces that
keep 120 separately-written days coherent are:

1. **`web/data/sequence.json`** — the spine. What each day teaches, fixed in
   advance, transcribed from the published scope and sequence. No author
   invents their own assignment.
2. **`docs/AUTHORING_GUIDE.md`** — the set guide. Every author reads it in full
   and follows it exactly: the same lesson arc, the same nine activity types,
   the same tone.
3. **`tools/inventory.py`** — the per-day brief. Computes, from the sequence and
   from the lessons already written, exactly what the child knows on that day.
   An author never reads the previous lessons; they read this.
4. **`tools/validate.py`** — the gate. Everything the guide says in prose, this
   says in code. A lesson is not done until it validates clean.

### Why sequentially, not in parallel

Each day builds on the days before it: the review activities pull from earlier
levels, and `inventory.py` reports which words earlier lessons already used so
the course doesn't recycle the same six words all week. That report is only
true if the earlier lessons exist. So batches run **in order, one at a time**,
and each one sees everything before it.

### Batch size

**Five days per authoring agent.** Enough that the agent can vary the material
across a week and carry a thread between days; small enough that it never loses
the guide. Batches are sequential: 3–7, then 8–12, then 13–17…

### The prompt each authoring agent gets

Kept current — this is the version that has been producing good days. Swap in
the batch's own days, reference lessons and milestones.

```
You are authoring days N to M of a 120-day phonics course for young children.
The project is at /home/treehouse/services/phonics.

1. Read docs/AUTHORING_GUIDE.md IN FULL. It is the contract. Follow it exactly.
2. Read web/data/levels/<two recent good days>.json as reference lessons — they
   set the standard (mouth-position coaching in the parentNote, minimal pairs
   targeting the error children actually make, prompts that teach rather than
   just instruct).
3. For each day IN ORDER:
   a. `python3 tools/inventory.py <day>` — that is your brief.
   b. Check candidate words with `python3 tools/lexicon.py <day> word1 word2 …`
      BEFORE building activities around them.
   c. Write web/data/levels/<NNN>.json.
   d. `python3 tools/validate.py <day>` — fix every error AND every warning.
4. Then `python3 tools/validate.py` (all must pass), then
   `python3 tools/build_manifest.py`, `python3 tools/build_speech_index.py`
   and `python3 tools/build_audio_manifest.py` -- the last two add whatever
   your lessons newly say to the recording list.

<any milestones falling in this batch: first sentences (13), first stories
(21), capitals (23), the first digraph (22), a review day, a sight-word day>

- Do NOT modify anything outside web/data/levels/. If you think a tool or the
  sequence is wrong, say so in your report instead of changing it.
- Do not commit or push.
- The word checker is a guardrail, not an oracle. Say every word out loud the
  way the letters say it; if that isn't the word, don't use it however green
  the tool goes.

Report: each day's activity count, its sentences and story, and anything you
worked around or think the guide gets wrong.
```

**Read the report, then verify independently** — `tools/validate.py`,
`tools/player_test.sh`, and actually reading a day's activities. Every batch so
far has found a real gap in the tooling or the guide; those get fixed before the
next batch goes out, which is the main reason the days keep improving.

## Status

Remaining batches, in order — this is the schedule, and it is the thing to
pick up if a session is interrupted. Batches 1–12 (days 28–87) are done,
committed, pushed and live.

| Batch | Days | What it teaches |
|---|---|---|
| 13 | 88–92 | you; said; qu says /kw/; x says /ks/; z says /z/ |
| 14 | 93–97 | aw says /aw/; -all says /all/; y at the end says /ie/; wh says /w/; what |
| 15 | 98–102 | where; there, here, of; th says /th/ (unvoiced); could, would, should; any, anywhere, many |
| 16 | 103–107 | oo says /uu/ and /oo/; house, mouse; -ed endings; ow says /ow/; igh and -alk |
| 17 | 108–112 | -le endings; tomorrow, today, father; bye, your, friend; ew says /oo/; again, were |
| 18 | 113–117 | some, horse, hooray; kn and wr (silent letters); air, and our and eyes; y at the end says /ee/; oh, have, put, away |
| 19 | 118–120 | one, whole, worth, able; -ie at the end; soft g says /j/ |

Milestones to call out in the relevant batch prompt, because an author who
isn't told will miss them:

- **day 35** `is` — the first "X is Y" sentence becomes possible, which changes
  what can be written more than most sounds do
- **day 44** `e` — the last short vowel; the whole CVC space is finally open
- **day 52** `i_e` — silent e, the first time a letter changes another letter
- **day 61, 68, 69, 74, 78, 79, 83, 86** — review days, no new sound: longer
  stories, mixed word sets, harder questions
- **day 55** — "the long a sound" has no real English words (its seed words are
  nonsense); write it as ear training for the sound ahead of `a_e` on day 56
- **day 84/85** `-e` and `-o` at the end — "we, be, he", "go, no, so"
- **day 100** unvoiced `th` — the voiced one was day 24
- **day 104 on** — the last stage; stories reach 10–14 lines

### Known drift: consonant clusters before day 27

The scope and sequence keeps days 1–26 to simple CVC words and teaches blends
across days 27–50. In practice every day from 6 onward used four to nine
cluster words (`mast`, `stand`, `snap`, `and`) — decodable, since the letters
are all taught, but a real step harder than the method intends at that point.

`validate.py` now warns above three per lesson, and the guide tells authors to
cap it there. Days 4–17 still carry the warning. Deciding whether to retrofit
those fourteen days is a pedagogical call worth making deliberately: the fix is
one authoring pass, and the cost of leaving it is that the first three weeks are
somewhat harder than designed. Days 18 on are written to the tighter rule.

Progress is also visible on the site itself: unwritten days are dimmed on the
home page, driven by `web/data/levels/manifest.json`.

## Deployment

Static nginx container, part of the `~/services` compose stack.

| | |
|---|---|
| container | `phonics` |
| host port | 8009 |
| hostname | `phonics.sarjuthakkar.com` |
| docroot | `web/` (which is why `data/` lives inside it) |

```bash
cd ~/services/phonics && git pull
cd ~/services && docker compose up -d --build phonics
```

Adding the hostname needed three things, not one: the ingress rule in
`cloudflared/config.yml`, a DNS record pointing the hostname at the tunnel, and
`sudo systemctl restart cloudflared` — the config is a symlink into the repo, so
a pull rewrites routing without applying it.

## The recorded voice

The site plays a human recording wherever one exists and the browser's
synthetic voice everywhere else, and it never synthesises a bare letter sound
at all -- synthesis says the letter *name* for "a", which is the one thing a
phonics course must not teach. Until a sound is recorded the app says the
keyword instead and lets the grown-up model it.

- `web/data/speech-index.json` — every string the site can say, with a stable
  id and filename. **Regenerated at the end of every authoring batch**; a full
  `validate.py` run fails if it is stale, because new lessons add new things to
  say and they have to reach the recording list.
- `/record.html` — records them from the microphone, saving each file already
  named correctly. Nothing is uploaded.
- `web/audio/human/` — drop recordings here, then `build_audio_manifest.py`.

Priority is the 93 `sound-*` files. They are about twenty minutes of work and
worth more than the other 542 recordings together.

## Open questions / later
- **Pictures.** Activities take an optional emoji. Real illustrations would be
  better, particularly for the stories.
- **Day 29's seed word `lump`** needs a `u`, which the sequence itself does not
  teach until day 39 — the one word in the published scope and sequence that a
  child could not read on the day it is listed. `camp` and `chimp` work; skip
  `lump`. `tools/lexicon.py` now catches this class of thing: a seed word is
  allowed to contain a letter team taught later ("here" on the silent-e day),
  but it is not allowed to be unreadable.
- **Day 55** in the source sequence ("the long a sound", seed words *bae, sae,
  hae*) is a sound-introduction day with no real English words — it is written
  as ear training for the long-a sound ahead of `a_e` on day 56.
- **`soundMatch` with two same-sounding choices is a feature, not a bug —
  don't "fix" it.** Several days deliberately put homophone spellings in one
  choice set (`i_e`/`ie` on 52, `oa`/`ow` on 78 and 80, `-e`/`ee` on 84) and
  make the colliding pair the *distractors*, with the prompt carrying the
  question: *"Two of these say oh. Find the one that says ee."* A batch author
  proposed erroring on this in `validate.py`, on the reasonable-sounding theory
  that the site plays one sound so two choices making it is unanswerable —
  checked, and it would have flagged seven correctly-designed activities. The
  real rule is that a collision is only broken when the prompt *doesn't*
  disambiguate, and no validator can judge that. Left alone deliberately.
- **Day 82's seed word `cowboy`** is the same class of bug as day 29's `lump`,
  except permanent rather than deferred: it contains `ow`, and this course
  never teaches `ow` saying /ow/ at all (the sequence's `ow` levels are all
  the /oh/ reading — snow, grow). `boy`, `toy`, `enjoy`, `joy` all work fine;
  skip `cowboy`, or swap it for `tomboy` if a compound word is wanted there.
