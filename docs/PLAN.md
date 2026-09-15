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
4. Then `python3 tools/validate.py` (all must pass) and
   `python3 tools/build_manifest.py`.

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

| Days | Stage | State |
|---|---|---|
| 1–2 | Letters and first words | ✅ written by hand as the reference lessons |
| 3–17 | Letters and first words → sentences | ✅ |
| 18–20 | Letters and first words | 🔄 in progress |
| 21–50 | Letter teams and blends | 🔄 21–22 in progress |
| 51–71 | Long vowels and silent e | ⬜ |
| 72–103 | Vowel teams and tricky spellings | ⬜ |
| 104–120 | On to real books | ⬜ |

Milestones already passed: sentences start on day 13, stories on day 21,
capital letters on day 23.

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

## Open questions / later

- **Real recordings.** Everything is spoken by the browser's built-in voice,
  which is good at words and mediocre at isolated sounds (see the header of
  `tools/build_phonemes.py`). Recording ~90 grapheme sounds in a human voice is
  the single biggest quality win available, and the engine already has the hook
  for it.
- **Pictures.** Activities take an optional emoji. Real illustrations would be
  better, particularly for the stories.
- **Day 55** in the source sequence ("the long a sound", seed words *bae, sae,
  hae*) is a sound-introduction day with no real English words — it is written
  as ear training for the long-a sound ahead of `a_e` on day 56.
