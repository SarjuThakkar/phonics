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

```
Write days N..M of the phonics course in ~/services/phonics.

1. Read docs/AUTHORING_GUIDE.md in full. Follow it exactly.
2. Read web/data/levels/001.json and 002.json as reference lessons.
3. For each day in order: run `python3 tools/inventory.py <day>` for your
   brief, write web/data/levels/<NNN>.json, then run
   `python3 tools/validate.py <day>` and fix every error.
4. Do not touch anything outside web/data/levels/. Do not edit the tools, the
   sequence, or the guide. If the sequence looks wrong, say so in your report
   rather than changing it.
5. Report: each day's activity count, what its story is about, and anything
   you had to work around.
```

## Status

| Days | Stage | State |
|---|---|---|
| 1–2 | Letters and first words | ✅ written by hand as the reference lessons |
| 3–20 | Letters and first words | ⬜ |
| 21–50 | Letter teams and blends | ⬜ |
| 51–71 | Long vowels and silent e | ⬜ |
| 72–103 | Vowel teams and tricky spellings | ⬜ |
| 104–120 | On to real books | ⬜ |

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
