/* The nine activity types.
 *
 * Each renderer returns { node, enter } -- `node` goes on screen, `enter` runs
 * once it is visible (that's where the spoken instruction happens, never
 * before, so nothing talks over the previous screen).
 *
 * Every renderer calls ctx.next() when the child may move on, and ctx.mark(
 * word, ok) whenever a word is read right or found tricky. Tricky words come
 * back at the end of the lesson -- the only "wrong" in the whole site, and it
 * is spelled "let's do that one again".
 *
 * Adding a type here means adding it to SCHEMA in tools/validate.py too, or
 * authors can write lessons the player silently drops.
 */

const Activities = {};

/* Utilities shared by the renderers ---------------------------------------- */

const speakBtn = (label, fn) => el('button', { class: 'btn', onclick: fn }, '🔊 ', label);
const nextBtn = (label, ctx) => el('button', { class: 'btn btn-go btn-big', onclick: () => ctx.next() }, label, ' →');

/** A sentence whose every word can be tapped to hear it on its own. */
function tappableText(text) {
  const frag = el('span');
  for (const token of text.split(/(\s+)/)) {
    if (!token.trim()) { frag.append(token); continue; }
    const bare = token.replace(/[^A-Za-z']/g, '');
    const span = el('span', { class: 'tapword' }, token);
    if (bare) {
      span.addEventListener('click', async () => {
        span.classList.add('lit');
        await Speech.word(bare);
        span.classList.remove('lit');
      });
    }
    frag.append(span);
  }
  return frag;
}

function screen(instruction, ...content) {
  return el('div', { class: 'act' },
    instruction ? el('p', { class: 'instruction' }, instruction) : null,
    ...content);
}


/** "first sound" / "last sound" / just "sound", depending on where the letters
 * actually sit in the keyword. ck and ll only ever appear at the end of a word,
 * so calling that the first sound was simply wrong. */
function wherePhrase(letters, keyword) {
  const k = keyword.toLowerCase(), l = letters.toLowerCase();
  if (k.startsWith(l)) return 'first sound';
  if (k.endsWith(l)) return 'last sound';
  return 'sound';
}

/* soundIntro --------------------------------------------------------------- */

Activities.soundIntro = (act, ctx) => {
  const entry = ctx.phon[act.grapheme] || { display: act.grapheme, say: act.grapheme, keyword: '' };
  const keyword = act.keyword || entry.keyword;
  const instruction = act.prompt || 'This one says…';

  const glyph = el('div', { class: 'grapheme', onclick: () => Speech.sound(entry) }, entry.display);
  const node = screen(instruction,
    glyph,
    el('div', { class: 'keyword' },
      act.picture ? el('span', { class: 'pic' }, act.picture) : null,
      keyword ? `like the ${wherePhrase(entry.display, keyword)} in “${keyword}”` : null),
    act.mouthCue ? el('p', { class: 'instruction' }, act.mouthCue) : null,
    el('div', { class: 'actions' },
      speakBtn('Hear it again', () => Speech.sound(entry)),
      nextBtn('My turn', ctx)));

  const enter = async () => {
    if (Speech.hasSound(entry)) {
      await Speech.say('This one says');
      await Speech.sound(entry);
      if (keyword) { await sleep(180); await Speech.say(`like in ${keyword}`); }
    } else if (keyword) {
      // Nobody has recorded this sound yet, so the app doesn't pretend to make
      // it -- it gives the child the word and lets the grown-up say the sound.
      await Speech.say(`Listen to the ${wherePhrase(entry.display, keyword)} in`);
      await Speech.word(keyword);
      await sleep(120);
      await Speech.word(keyword);
    }
  };
  return { node, enter };
};

/* soundMatch --------------------------------------------------------------- */

Activities.soundMatch = (act, ctx) => {
  const target = ctx.phon[act.target];
  const choices = shuffle(act.choices);
  const instruction = act.prompt || 'Which one says this sound?';
  const tiles = el('div', { class: 'tiles' });

  // With a recording, this plays the bare sound. Without one it plays the
  // keyword, and "which letter does 'moon' start with?" is still a real
  // exercise -- just an easier one.
  const ask = () => Speech.sound(target, { rate: 0.6 });
  const askLead = () => (Speech.hasSound(target)
    ? Promise.resolve()
    : Speech.say(`Which one starts ${target.keyword}?`));

  for (const gid of choices) {
    const entry = ctx.phon[gid] || { display: gid };
    const tile = el('button', { class: 'tile' }, entry.display);
    tile.addEventListener('click', async () => {
      if (gid === act.target) {
        tile.classList.add('right');
        Chime.play('yes');
        await Speech.say('Yes!');
        await sleep(250);
        ctx.next();
      } else {
        tile.classList.add('wrong');
        Chime.play('no');
        setTimeout(() => tile.classList.remove('wrong'), 500);
        await Speech.say('Not that one. Listen again.');
        await ask();
      }
    });
    tiles.append(tile);
  }

  const node = screen(instruction, tiles,
    el('div', { class: 'actions' }, speakBtn('Play the sound', ask)));
  return {
    node,
    enter: async () => { await Speech.say(instruction); await askLead(); await ask(); },
  };
};

/* blend -- the heart of the whole thing ------------------------------------ */

Activities.blend = (act, ctx) => {
  const word = el('div', { class: 'word' });
  const parts = act.parts.map((p) => {
    const span = el('span', { class: 'part' }, p);
    word.append(span);
    return span;
  });
  const instruction = act.prompt || 'Sound it out, then say it fast.';
  let running = false;

  const soundOut = async () => {
    if (running) return;
    running = true;
    word.classList.remove('together');
    for (let i = 0; i < parts.length; i++) {
      parts[i].classList.add('lit');
      const entry = graphemeFor(act.parts[i], ctx.phon, i === parts.length - 1);
      await Speech.sound(entry, { rate: 0.6 });
      await sleep(120);
      parts[i].classList.remove('lit');
    }
    await sleep(160);
    word.classList.add('together');
    parts.forEach((p) => p.classList.add('lit'));
    await sleep(220);
    await Speech.word(act.word);
    parts.forEach((p) => p.classList.remove('lit'));
    running = false;
  };

  const node = screen(instruction,
    act.picture ? el('div', { class: 'keyword' }, el('span', { class: 'pic' }, act.picture)) : null,
    word,
    el('div', { class: 'actions' },
      speakBtn('Sound it out', soundOut),
      el('button', { class: 'btn', onclick: () => Speech.word(act.word) }, '⚡ Say it fast'),
      nextBtn('Next', ctx)));

  return { node, enter: async () => { await Speech.say(instruction); await soundOut(); } };
};

/** Best phoneme entry for a chunk of a blended word.
 *
 * `atEnd` is what makes "fly" work. A blend's `parts` must spell the word
 * exactly (validate.py enforces it), so a grapheme that only exists at the end
 * of a word has to be written as its bare letters -- "fly" is ["f","l","y"].
 * Looked up plainly that finds consonant y, the /y/ of "yak", and the app says
 * "f-l-yuh" on the very day it teaches that final y says /eye/. phonemes.json
 * already carries those final-position sounds as separate "-x" entries, so in
 * final position try that first: -y (fly), -e (me), -o (go), -ie (pie).
 *
 * Only `team` entries are consulted, never the `suffix` ones, and that is
 * deliberate rather than tidiness: "-le" would hijack the silent-e chunk in
 * whale ["wh","a","le"] and say "wh-a-ul". "-s" and "-ed" say the same thing
 * as their bare letters anyway, so nothing is lost by leaving them out.
 *
 * Known limit: a final y is /eye/ in a one-syllable word (fly) but /ee/ in a
 * longer one (happy) -- phonemes.json has both, as -y and -ey, and letters
 * alone cannot tell them apart. Every y-final blend written so far is the
 * /eye/ kind. A "happy" blend would need its grapheme named in the data.
 */
function graphemeFor(part, phon, atEnd = false) {
  const p = part.toLowerCase();
  if (atEnd) {
    const positional = phon[`-${p}`];
    if (positional && positional.kind === 'team') return positional;
  }
  if (phon[p]) return phon[p];
  // "a_e" style chunks arrive as plain letters; fall back to saying the letters.
  return { display: part, say: p, stretchy: true };
}

/* readWord ----------------------------------------------------------------- */

Activities.readWord = (act, ctx) => {
  const instruction = act.prompt || 'Your turn. Read this word.';
  const word = el('div', { class: 'word together', onclick: () => Speech.word(act.word) }, act.word);
  let checked = false;

  const check = async () => { checked = true; await Speech.word(act.word); };

  const node = screen(instruction,
    act.picture ? el('div', { class: 'keyword' }, el('span', { class: 'pic' }, act.picture)) : null,
    word,
    el('div', { class: 'actions' },
      speakBtn('Check it', check),
      el('button', {
        class: 'btn btn-go btn-big',
        onclick: () => { ctx.mark(act.word, true); ctx.next(); },
      }, '✓ Got it'),
      el('button', {
        class: 'btn btn-quiet',
        onclick: async () => {
          ctx.mark(act.word, false);
          if (!checked) await check();
          ctx.next();
        },
      }, 'Tricky one — come back to it')));

  return { node, enter: () => Speech.say(instruction) };
};

/* chooseWord --------------------------------------------------------------- */

Activities.chooseWord = (act, ctx) => {
  const instruction = act.prompt || 'Which word is this?';
  const tiles = el('div', { class: 'tiles' });
  const ask = () => Speech.word(act.answer);

  for (const choice of shuffle(act.choices)) {
    const tile = el('button', { class: 'tile word-tile' }, choice);
    tile.addEventListener('click', async () => {
      if (choice === act.answer) {
        tile.classList.add('right');
        Chime.play('yes');
        ctx.mark(act.answer, true);
        await Speech.say(`Yes, ${act.answer}.`);
        await sleep(200);
        ctx.next();
      } else {
        tile.classList.add('wrong');
        Chime.play('no');
        ctx.mark(act.answer, false);
        setTimeout(() => tile.classList.remove('wrong'), 500);
        await Speech.say('Listen again.');
        await ask();
      }
    });
    tiles.append(tile);
  }

  const node = screen(instruction, tiles,
    el('div', { class: 'actions' }, speakBtn('Say it again', ask)));
  return { node, enter: async () => { await Speech.say(instruction); await sleep(150); await ask(); } };
};

/* sentence ----------------------------------------------------------------- */

Activities.sentence = (act, ctx) => {
  const instruction = act.prompt || 'Read it out loud. Tap any word you get stuck on.';
  const node = screen(instruction,
    el('p', { class: 'sentence' }, tappableText(act.text)),
    el('div', { class: 'actions' },
      speakBtn('Read it to me', () => Speech.sentence(act.text)),
      nextBtn('Next', ctx)));
  return { node, enter: () => Speech.say(instruction) };
};

/* story -------------------------------------------------------------------- */

Activities.story = (act, ctx) => {
  const questions = act.questions || [];
  const node = el('div', { class: 'act' });
  let asked = 0;

  const showStory = () => {
    node.replaceChildren(screen(act.prompt || 'Read the story. Tap a word for help.',
      el('h2', { style: 'font-size:1.5rem;margin:0 0 14px' }, act.title),
      el('div', { class: 'story-lines' }, act.lines.map((line) => el('p', { class: 'sentence' }, tappableText(line)))),
      el('div', { class: 'actions' },
        speakBtn('Read it to me', async () => { for (const l of act.lines) await Speech.sentence(l); }),
        el('button', {
          class: 'btn btn-go btn-big',
          onclick: () => (questions.length ? showQuestion() : ctx.next()),
        }, questions.length ? 'I read it →' : 'Next →'))));
  };

  const showQuestion = () => {
    const q = questions[asked];
    const tiles = el('div', { class: 'tiles' });
    for (const choice of q.choices) {
      const tile = el('button', { class: 'tile word-tile' }, choice);
      tile.addEventListener('click', async () => {
        if (choice === q.answer) {
          tile.classList.add('right');
          Chime.play('yes');
          await Speech.say('That’s right!');
          asked += 1;
          await sleep(200);
          if (asked < questions.length) showQuestion(); else ctx.next();
        } else {
          tile.classList.add('wrong');
          Chime.play('no');
          setTimeout(() => tile.classList.remove('wrong'), 500);
          await Speech.say('Have another look at the story.');
        }
      });
      tiles.append(tile);
    }
    node.replaceChildren(screen(null,
      el('p', { class: 'question' }, q.prompt),
      tiles,
      el('div', { class: 'actions' },
        el('button', { class: 'btn btn-quiet', onclick: showStory }, '← Read the story again'))));
    Speech.sentence(q.prompt);
  };

  // Build the story immediately rather than inside enter(): a renderer that
  // returns an empty node and fills it later is one missed call away from a
  // blank screen.
  showStory();
  return { node, enter: () => Speech.say(act.prompt || 'Here is a story.') };
};

/* sightWord ---------------------------------------------------------------- */

Activities.sightWord = (act, ctx) => {
  const instruction = act.prompt || 'This one we just remember.';
  const node = screen(instruction,
    el('div', { class: 'sight-card' },
      el('span', { class: 'heart' }, '💜'),
      el('div', { class: 'word together', onclick: () => Speech.word(act.word) }, act.word)),
    act.sentence ? el('p', { class: 'sentence', style: 'margin-top:22px' }, tappableText(act.sentence)) : null,
    el('div', { class: 'actions' },
      speakBtn('Say it', () => Speech.word(act.word)),
      el('button', { class: 'btn', onclick: () => Speech.spell(act.word) }, '🔤 Spell it'),
      nextBtn('Got it', ctx)));

  return {
    node,
    enter: async () => {
      await Speech.say(`This word is ${act.word}.`);
      await Speech.spell(act.word);
      await Speech.say(`${act.word}. We remember this one by heart.`);
    },
  };
};

/* review ------------------------------------------------------------------- */

Activities.review = (act, ctx) => {
  const instruction = act.prompt || act.label || 'Read them all. Tap each one when you’ve said it.';
  const grid = el('div', { class: 'review-grid' });
  const remaining = new Set(act.words);
  const go = nextBtn('Done', ctx);
  go.disabled = true;

  for (const word of act.words) {
    const tile = el('button', { class: 'tile word-tile' }, word);
    tile.addEventListener('click', async () => {
      tile.classList.add('checked');
      remaining.delete(word);
      if (!remaining.size) { go.disabled = false; Chime.play('yes'); }
      await Speech.word(word);
    });
    grid.append(tile);
  }

  const node = screen(instruction, grid,
    el('div', { class: 'actions' }, go,
      el('button', { class: 'btn btn-quiet', onclick: () => ctx.next() }, 'Skip ahead')));
  return { node, enter: () => Speech.say(instruction) };
};
