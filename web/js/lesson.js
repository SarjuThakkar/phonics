/* The lesson player: one activity on screen at a time, start to finish. */

const params = new URLSearchParams(location.search);
const day = Math.min(120, Math.max(1, parseInt(params.get('day') || '1', 10) || 1));

const app = document.getElementById('app');
const bar = document.getElementById('bar');
const fill = document.getElementById('fill');
const count = document.getElementById('count');
const titleEl = document.getElementById('lesson-title');

const state = { level: null, phon: {}, index: 0, tricky: [], got: 0 };

function setProgress(i, total) {
  fill.style.width = `${Math.round((i / total) * 100)}%`;
  count.textContent = `${Math.min(i + 1, total)}/${total}`;
}

function toast(msg) {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 2200);
}

/* ------------------------------------------------------------- screens --- */

function showStart(level, spec) {
  bar.hidden = true;
  app.replaceChildren(el('div', { class: 'stage-area' },
    el('p', { class: 'instruction' }, `Day ${day} · ${spec.stage.name}`),
    el('h1', { style: 'font-size:clamp(2rem,7vw,3.2rem);margin:0 0 6px' }, level.kidTitle),
    el('p', { class: 'keyword' }, level.title),
    el('div', { class: 'actions' },
      el('button', {
        class: 'btn btn-go btn-big',
        onclick: () => { Speech.prime(); Chime.play('yes'); run(0); },
      }, 'Let’s go!')),
    el('div', { class: 'parent-note' },
      el('h3', {}, 'For the grown-up'),
      level.parentNote),
    el('p', { class: 'instruction', style: 'margin-top:18px;font-size:1rem' },
      `About ${Math.max(10, Math.round(level.activities.length * 1.2))} minutes · ${level.activities.length} activities`)));
}

function showMissing() {
  bar.hidden = true;
  app.replaceChildren(el('div', { class: 'stage-area' },
    el('div', { class: 'grapheme' }, '🚧'),
    el('h1', {}, `Day ${day} isn’t ready yet`),
    el('p', { class: 'instruction' }, 'This day is still being written. Try an earlier day.'),
    el('div', { class: 'actions' },
      el('a', { class: 'btn btn-primary btn-big', href: 'index.html' }, '← All the days'))));
}

async function run(i) {
  const acts = state.level.activities;
  if (i >= acts.length) return finish();

  state.index = i;
  Progress.saveStep(day, i);
  bar.hidden = false;
  setProgress(i, acts.length);

  const act = acts[i];
  const renderer = Activities[act.type];
  if (!renderer) { console.warn('unknown activity type', act.type); return run(i + 1); }

  const ctx = {
    phon: state.phon,
    level: day,
    next: () => run(i + 1),
    mark: (word, ok) => {
      if (ok) state.got += 1;
      else if (!state.tricky.includes(word)) state.tricky.push(word);
    },
  };

  Speech.cancel();
  const { node, enter } = renderer(act, ctx);
  const area = el('div', { class: 'stage-area' }, node);
  app.replaceChildren(area, backRow(i));
  if (enter) enter();
}

function backRow(i) {
  return el('div', { class: 'actions', style: 'margin-top:14px' },
    i > 0 ? el('button', { class: 'btn btn-quiet', onclick: () => { Speech.cancel(); run(i - 1); } }, '← Back') : null,
    el('a', { class: 'btn btn-quiet', href: 'index.html', onclick: () => Speech.cancel() }, 'Stop for now'),
    el('button', {
      class: 'btn btn-quiet',
      onclick: () => { Speech.muted = !Speech.muted; Speech.cancel(); toast(Speech.muted ? 'Sound off' : 'Sound on'); },
    }, '🔇 Sound'));
}

/* The only "wrong" in the site: words the child called tricky come back once,
 * right away, while the sounds are still warm. */
function trickyRound() {
  const words = state.tricky.slice(0, 6);
  bar.hidden = true;
  const ctx = {
    phon: state.phon,
    level: day,
    next: () => { state.tricky = []; finish(true); },
    mark: () => {},
  };
  const { node, enter } = Activities.review({
    type: 'review',
    words,
    prompt: 'One more go at the tricky ones. Tap each when you’ve said it.',
  }, ctx);
  app.replaceChildren(el('div', { class: 'stage-area' }, node));
  if (enter) enter();
}

function finish(skipTricky) {
  if (!skipTricky && state.tricky.length) return trickyRound();

  Progress.complete(day, { got: state.got, tricky: state.tricky.length });
  bar.hidden = true;
  fill.style.width = '100%';
  Chime.play('yes');
  Speech.say('You did it! Great reading.');

  const next = Math.min(120, day + 1);
  app.replaceChildren(el('div', { class: 'stage-area finish' },
    el('div', { class: 'stars' }, '⭐️⭐️⭐️'),
    el('h2', {}, 'You did it!'),
    el('p', {}, `Day ${day} finished.`),
    el('div', { class: 'actions' },
      day < 120 ? el('a', { class: 'btn btn-go btn-big', href: `lesson.html?day=${next}` }, `Day ${next} →`) : null,
      el('a', { class: 'btn', href: 'index.html' }, 'All the days'),
      el('button', { class: 'btn btn-quiet', onclick: () => run(0) }, '↻ Do this day again'))));
}

/* ---------------------------------------------------------------- boot --- */

(async function boot() {
  const [sequence, phon] = await Promise.all([Data.sequence(), Data.phonemes()]);
  state.phon = phon;
  const spec = sequence.levels.find((l) => l.level === day);
  document.title = `Day ${day} · ${spec.focus} · Phonics`;
  titleEl.textContent = `Day ${day}`;

  let level;
  try {
    level = await Data.level(day);
  } catch (e) {
    return showMissing();
  }
  state.level = level;
  Progress.start(day);
  showStart(level, spec);
})();
