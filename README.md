# Learn to Read — 120 days of phonics

A free, account-free phonics course that takes a child from a single letter
sound to reading real books, in 120 short daily lessons. Static site, no
backend, no sign-in, no data collection: every family's progress lives in their
own browser and nowhere else.

Live at **https://phonics.sarjuthakkar.com**

## What it is

120 days, grouped into five stages. Each day is a 15–30 minute lesson done
sitting next to a grown-up: meet a new sound, blend it into words, read those
words alone, then read a sentence and a story that use it. The child taps; the
site talks.

The design rests on three things:

- **Sounds, not letter names.** `m` is /mmm/, never "em".
- **Blending from day 2.** Knowing sounds is easy; pushing them together into a
  word is the hard part, so it is drilled from the first word onward.
- **Nothing appears before it is taught.** Every word in every sentence, story
  and multiple-choice distractor can be sounded out with the letters taught so
  far. This is checked by a script (`tools/validate.py`), not by eye.

## Layout

```
web/                     the entire site — this directory is the docroot
  index.html             the 120 days
  lesson.html            the lesson player
  js/app.js              data loading, speech, progress (localStorage)
  js/activities.js       the nine activity types
  js/lesson.js           the player
  js/home.js             the day grid
  data/sequence.json     the 120-level spine        (generated)
  data/phonemes.json     how each grapheme is shown and spoken  (generated)
  data/levels/NNN.json   one authored lesson per day
tools/                   authoring and checking
docs/AUTHORING_GUIDE.md  how a day is written — read this before writing one
docs/PLAN.md             build order and status
```

## Working on it

```bash
# regenerate the spine (only after editing the tables in tools/)
python3 tools/build_sequence.py
python3 tools/build_phonemes.py

# author a day: brief, write, check
python3 tools/inventory.py 37
python3 tools/lexicon.py 37 king sang wish
python3 tools/validate.py 37

# after adding or changing any lesson
python3 tools/build_manifest.py

# serve it
cd web && python3 -m http.server 8009
```

`tools/validate.py` must pass with zero errors before a lesson is committed. It
enforces the decodability rule, the activity schema, the shape of a lesson and
the capital-letter rule mechanically.

## Where the sequence comes from

The **order** concepts are introduced follows the scope and sequence
[Mentava publishes](https://www.mentava.com/assets/docs/mentava-scope-and-sequence.pdf) —
a sensible ordering of a body of phonics knowledge nobody owns. The order is the
only thing taken: every word, sentence, story, activity and line of code here is
original. Not affiliated with Mentava.

## Deployment

Static nginx container on the Pi, port 8009, behind the Cloudflare tunnel as
`phonics.sarjuthakkar.com`. See `docs/PLAN.md`.
