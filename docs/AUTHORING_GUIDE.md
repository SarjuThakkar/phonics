# How to write one day of this course

**Read this whole file before writing anything.** Every day of the course is
written by a different author working alone, and this guide is the only thing
that makes 120 separately-written days feel like one course. Follow it exactly,
including the parts that feel over-specified — they are over-specified on
purpose.

Your job is to write **one JSON file**: `web/data/levels/NNN.json`.

---

## 1. Who you are writing for

A child between three and six, sitting on a sofa next to a parent, holding a
tablet. They cannot read the interface. They can't read anything yet — that is
the point. Everything they need to hear is spoken aloud by the site; everything
they need to see is enormous.

The parent is the second audience, and they get exactly one paragraph from you:
`parentNote`. Assume they have never taught reading and are slightly worried
they will do it wrong.

A lesson is **15–30 minutes**. That is 14–20 activities. Less is better than
padding; a bored child is a child who doesn't come back tomorrow.

---

## 2. The three rules you cannot break

**1. Never show a word the child cannot yet read.** Not in a sentence, not in a
story, not in a comprehension question, not as a wrong answer in a multiple
choice. If `sh` is taught on day 22, the word "ship" cannot appear on day 21 —
not even as a distractor, not even spoken. A child who meets an unreadable word
learns that reading is guessing.

There is exactly one exception, and it is deliberate: **sight words**, which are
taught whole on their own day because English spells them unreasonably. Once
taught, they may be used freely.

**2. Teach only what this day teaches.** Your level introduces the sounds listed
in the scope and sequence — no more, no fewer. Don't reach ahead because a
better story would be possible with one more sound. Someone else is writing that
day.

**3. Blending is the skill.** Not letter names, not the alphabet song, not
memorising word shapes. Sounding out letters is easy and pushing the sounds
together into a word is hard, so blending is what gets drilled. Every phonics
level needs at least three `blend` activities and they belong early, right after
the new sound is introduced.

---

## 3. Your workflow

```bash
cd ~/services/phonics

# 1. Your brief: what's new, what's already taught, what earlier days used.
python3 tools/inventory.py 37

# 2. Check any word you're considering, before you build a story around it.
python3 tools/lexicon.py 37 king sang thing wish

# 3. Write web/data/levels/037.json

# 4. This must pass with zero errors. It is not advisory.
python3 tools/validate.py 37
```

`tools/inventory.py` is the brief. It prints the day's assignment, every sound
and sight word taught so far, and the words the last five days already used —
read that last part, because reusing the same six words for the fourth day
running is the most common way these lessons go stale.

`tools/validate.py` enforces everything in section 2 mechanically. **Do not
report a level as finished until it validates clean.** Warnings are worth
fixing; errors are not negotiable.

---

## 4. The shape of a lesson

Follow this arc. It is the same every day, because a four-year-old who knows
what comes next spends their attention on reading instead of on the interface.

| Part | What it does | Activities |
|---|---|---|
| **Meet the sound** | Introduce the new grapheme by itself | 1 × `soundIntro`, then 1–2 × `soundMatch` |
| **Build words with it** | The new sound inside words, sounded out | 3–5 × `blend` |
| **Read words alone** | Same words, no scaffolding | 3–4 × `readWord`, 1–2 × `chooseWord` |
| **Read connected text** | Words in a real sentence | 2–3 × `sentence` (from day 13) |
| **Read a story** | Sustained reading + comprehension | 1 × `story` (required from day 21) |
| **Look back** | Spaced review of older sounds | 1 × `review` |

Variations by kind of day (`tools/inventory.py` tells you which you have):

- **`sight` days** — a sight word day still needs a full lesson. Open with the
  `sightWord` activity, then put the new word to work: it should appear in most
  of the sentences and all through the story. Fill the rest of the lesson with
  review of recent phonics, since there is no new sound to drill. Skip the
  `blend` block (sight words don't blend — that's why they're sight words) and
  blend *review* words instead.
- **`review` days** — no new sound at all. This is the day to use longer
  stories, mixed word sets from across the last two stages, and harder
  comprehension questions. Two stories is a good use of a review day.
  **Before day 13 this doesn't apply**: there is no connected text yet, so an
  early review day is word-level only — blends and minimal pairs that make the
  child track left to right rather than recognise a word by its shape.
- **From day 21 on** — every single day ends with a story. Stories get longer
  as the course goes: 3–4 lines around day 21, 6–8 lines by day 60, 10–14 by
  day 100.
- **Days 5–12 have no connected text at all**, since sentences start on day 13.
  They are still full lessons, not short ones: spend the space the sentences
  and story would have taken on more `blend` and `chooseWord` work, and close
  with a `soundMatch` hunt for the day's sound. Day 7 is the model.

---

## 5. The file

```jsonc
{
  "level": 37,
  "title": "ng says /ng/",              // the concept, for grown-ups. Match the scope and sequence.
  "kidTitle": "Meet ng",                // what the child sees on the start screen. 2-4 warm words.
  "parentNote": "…",                    // see §7
  "newGraphemes": ["ng"],               // EXACTLY what inventory.py says. Validator checks this.
  "newSightWords": [],
  "activities": [ … ]                   // 12-30; aim for 14-20
}
```

---

## 6. The nine activity types

Every field not listed is ignored by the player. `prompt` is optional on all of
them and overrides the default spoken instruction — write one when the default
would be confusing, leave it out when it wouldn't.

### `soundIntro` — meet the new sound
```json
{ "type": "soundIntro", "grapheme": "ng", "keyword": "king", "picture": "👑",
  "mouthCue": "The back of your tongue lifts up, like the end of a hum." }
```
**One per new grapheme**, first in the lesson — so a day that introduces two
(day 14 teaches `l` and `ll`) gets two, each with its own keyword and mouth
cue. `grapheme` must be a key in `web/data/phonemes.json`.
`keyword` defaults to the one in that file; override it only if yours is more
concrete for a small child. `picture` is a single emoji and is worth including.
`mouthCue` is optional and lovely — one short sentence about what the mouth
does. Skip it rather than write a vague one.

### `soundMatch` — hear it, find it
```json
{ "type": "soundMatch", "target": "ng", "choices": ["ng", "n", "m"] }
```
The site plays the target sound; the child taps the letter. Choices must all be
already-taught graphemes, and must be genuinely confusable — `["ng","n","m"]`
teaches something, `["ng","a","t"]` teaches nothing.

### `blend` — sound it out, then say it fast
```json
{ "type": "blend", "word": "king", "parts": ["k", "i", "ng"], "picture": "👑" }
```
The core activity. `parts` must spell `word` exactly and must split it into
**sounds, not letters**. Maximum 3 letters per part.

- Digraphs and teams stay whole: `["sh","o","p"]`, never `["s","h","o","p"]`;
  `["k","i","ng"]`, `["r","ai","n"]`, `["st","o","p"]`.
- **Silent-e words keep the silent e attached to the consonant before it**, so
  the child never sounds it out on its own: `{"word": "hope", "parts": ["h",
  "o", "pe"]}`, `{"word": "time", "parts": ["t", "i", "me"]}`, `{"word":
  "snake", "parts": ["sn", "a", "ke"]}`. Never `["h","o","p","e"]`.
- Blends at the start of a word may be one part or two — `["fl","a","g"]` and
  `["f","l","a","g"]` are both defensible. Use two parts on the day the blend
  is introduced (so the child hears both sounds), one part afterwards.

Order blends easy to hard: start with a word built from the day's clearest
sounds, end with the longest one.

### `readWord` — read it with no help
```json
{ "type": "readWord", "word": "sang", "picture": "🎤" }
```
The child reads it aloud, then taps to check. They can mark it tricky, and
tricky words come back at the end of the lesson automatically.

### `chooseWord` — hear it, pick the spelling
```json
{ "type": "chooseWord", "answer": "wink", "choices": ["wink", "wing", "win"] }
```
The site says the word; the child picks it from 2–4 choices. **Distractors must
be minimal pairs** — differ from the answer by one sound, ideally the sound the
day is teaching. `["wink","wing","win"]` forces the child to actually hear the
ending. `["wink","cat","sun"]` is a free point and a wasted activity.

### `sentence` — connected text
```json
{ "type": "sentence", "text": "The king sang a long song." }
```
From day 13 on. 3–8 words early, up to 12 later. Every word tappable to hear.
Must be a real sentence a person might say — "The pig is in the mud" is fine,
"Sam sat. Sam sat. Sam sat." is not.

### `story` — sustained reading with comprehension
```json
{ "type": "story", "title": "The King's Song",
  "lines": ["The king sang a song.", "The song was long.", "…"],
  "questions": [
    { "prompt": "What did the king do?", "choices": ["Sang a song", "Ran fast"],
      "answer": "Sang a song" }
  ] }
```
Required from day 21. At least 3 lines and at least one question. One idea per
line. **The question must need the story to answer** — a question answerable
from the picture on the box, or from general knowledge, teaches guessing.
Questions and choices obey the decodability rule too: the child reads them.

Give the story a shape: something wants something, something goes wrong, it
resolves. Even in five words. Animals doing slightly silly things work at every
level; jokes land from about day 40.

### `sightWord` — the words we just remember
```json
{ "type": "sightWord", "word": "the", "sentence": "the cat sat on the mat" }
```
Only for words the scope and sequence introduces on this day. The site says it,
spells it by letter name (the one place letter names are correct), and shows it
in your sentence.

### `review` — spaced practice
```json
{ "type": "review", "label": "Words from last week",
  "words": ["shop", "chat", "fish", "much", "ship"] }
```
3–8 words, from **earlier** levels, not this one. This is the only place old
material comes back, so choose deliberately: something from 2–3 days ago,
something from a week ago, and one thing from the previous stage.

---

## 7. `parentNote`

Two to four sentences, written to a parent who is not a teacher. Say:

- what the child is learning today, in plain words;
- the one thing that usually goes wrong here, specifically;
- what to do about it.

Good:

> Today is /ng/, the sound at the end of "king". Children often say the letters
> separately — "n-g" — which makes "sing" come out as "sinn-guh". Say the whole
> word yourself first and let them hear it as one sound. If they're tired, stop
> after the story; the review can wait until tomorrow.

Bad:

> Today your child will learn the ng digraph. Encourage and praise their
> efforts! Learning to read is a journey.

Never mention accounts, points, streaks or levels-as-achievement. Never imply
a child is behind.

---

## 8. Writing the words themselves

- **Lowercase until day 23.** Capital letters are taught on day 23; before
  that, everything — including names — is lowercase, because a child who has
  only met `a` should not be asked to recognise `A`. From day 23, sentences
  start with a capital and names are capitalised normally. The validator
  enforces both directions.
- **Punctuation:** every sentence and story line ends with `.`, `!` or `?` —
  the validator checks this. Full stops from day 13; question marks and
  exclamation marks from day 23; commas from about day 50. No apostrophes until
  they are taught — contractions and possessives are not decodable and the
  validator will reject them.
- **Before day 27, prefer simple consonant-vowel-consonant words.** Consonant
  blends (`st`, `nd`, `fl`, `sn`…) are not taught until days 27–50. A word like
  "stand" or "snap" is decodable earlier — the letters are all known — but it is
  a genuine step harder than "sat", and a lesson built out of them is harder
  than this point in the course intends. Two or three cluster words per lesson
  is fine, used as the deliberate stretch at the end of the blend block and
  always blended before they turn up in a sentence. More than three and the
  validator will say so.
- **Names:** short decodable ones only — sam, jim, pam, tim, meg, dan. A name is
  a free real-world word and children love seeing them; use them.
- **No filler.** "Sam sat. Sam sat on a mat. Sam is sad." is three sentences
  with one idea. Give each sentence something to happen in it.
- **Vary the sentence frame.** If every sentence you write is `<name> <verb> a
  <noun>`, the child is learning a pattern, not reading. Ask questions. Start
  with the object. Use two characters.
- **Emoji pictures** (`picture`) are welcome on concrete nouns and nowhere else.
  One emoji, never a sequence.
- **Check every word you write with `tools/lexicon.py` before building on it.**
  It takes two seconds and saves rewriting a story.
- **`lexicon.py` is a guardrail, not an oracle.** It knows which letters have
  been taught; it does not know how English actually sounds. It will pass a
  word whose letters are all taught but whose sound is not — "as" and "is" end
  in /z/, "sign" has a silent g. Those specific ones are now on a blocklist in
  the tool, but the list is not exhaustive and never will be. **The real check
  is your own ear: say the word the way the letters say it.** If that isn't
  the word, don't use it, however green the tool goes.

---

## 9. Tone

Warm, plain, a little funny. Never babyish, never sing-song, never
congratulatory about nothing. The child is doing hard work and the site should
sound like it knows that.

No competition, no timers, no scores, no streaks, no "oh no!". A wrong answer
gets "listen again", never "wrong".

---

## 10. Before you report your day as done

```bash
python3 tools/validate.py NNN     # zero errors
```

Then read your own story out loud. If it is boring to read out loud, it is
boring to read, and a parent will be reading it four times.

State in your report: the day number, the activity count, what the story is
about, and anything you had to work around. If the scope and sequence gave you
something impossible (a day whose seed words you can't build a sentence from,
say), say so plainly rather than bending rule 1.
