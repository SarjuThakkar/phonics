/* The recording studio.
 *
 * Walks the speech index, records each line from the microphone, and saves it
 * under the right id. With the upload passphrase it posts straight to the Pi
 * and the recording is live on the site immediately; without one it falls back
 * to downloading each take to the device, to be copied across by hand.
 *
 * Deliberately plain. It is a tool for one person, not part of the course.
 */

const app = document.getElementById('app');
const state = {
  entries: [],
  recorded: {},
  kind: 'sound',
  i: 0,
  recorder: null,
  chunks: [],
  lastBlob: null,
  lastUrl: null,
  stream: null,
  token: null,
  saving: false,
  saved: '',
};

const KINDS = [
  ['sound', 'Letter sounds', 'The ones that matter most — synthesis cannot do these at all.'],
  ['ui', 'What the app says', 'The fixed lines the app speaks in every lesson.'],
  ['word', 'Words', 'Every word the course puts in front of a child.'],
  ['prompt', 'Instructions', 'The spoken instruction on each activity.'],
  ['line', 'Sentences and stories', 'Read these warmly, at storytime pace.'],
];

const dayFilter = parseInt(new URLSearchParams(location.search).get('day') || '', 10) || null;

/* With ?day=N the studio shows only what that lesson says -- about a dozen
 * files -- which is the sensible way to try the whole idea before committing
 * to all 635. The app's own fixed lines come along because every lesson uses
 * them. */
let dayPlan = null;   // set from speech-index.json's plans at boot
const inScope = (e) => !dayFilter || !dayPlan || dayPlan.has(e.id);

const list = () => state.entries.filter((e) => e.kind === state.kind && inScope(e));

/* ------------------------------------------------------------- recording -- */

async function ensureMic() {
  if (state.stream) return state.stream;
  state.stream = await navigator.mediaDevices.getUserMedia({
    audio: { channelCount: 1, echoCancellation: true, noiseSuppression: true },
  });
  return state.stream;
}

function pickMime() {
  for (const t of ['audio/mp4', 'audio/webm;codecs=opus', 'audio/webm', 'audio/ogg']) {
    if (window.MediaRecorder && MediaRecorder.isTypeSupported(t)) return t;
  }
  return '';
}

async function startRec() {
  const stream = await ensureMic();
  state.chunks = [];
  const mimeType = pickMime();
  state.recorder = new MediaRecorder(stream, mimeType ? { mimeType } : undefined);
  state.recorder.ondataavailable = (e) => e.data.size && state.chunks.push(e.data);
  state.recorder.onstop = () => {
    state.lastBlob = new Blob(state.chunks, { type: state.recorder.mimeType });
    if (state.lastUrl) URL.revokeObjectURL(state.lastUrl);
    state.lastUrl = URL.createObjectURL(state.lastBlob);
    render();
    new Audio(state.lastUrl).play().catch(() => {});
  };
  state.recorder.start();
  render();
}

function stopRec() {
  if (state.recorder && state.recorder.state === 'recording') state.recorder.stop();
}

function extFor(blob) {
  const t = (blob.type || '').toLowerCase();
  if (t.includes('mp4')) return 'm4a';
  if (t.includes('ogg')) return 'ogg';
  return 'webm';
}

/** Post the take to the Pi, where it is live on the site immediately. Falls
 * back to a plain download if there's no token or the upload fails, so a
 * recording is never lost to a flaky connection. */
async function save() {
  const entry = list()[state.i];
  if (!state.lastBlob || !entry) return;

  if (state.token) {
    state.saving = true;
    render();
    try {
      const body = new FormData();
      body.append('file', state.lastBlob, `${entry.id}.${extFor(state.lastBlob)}`);
      const res = await fetch(`api/recordings/${entry.id}`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${state.token}` },
        body,
      });
      if (!res.ok) throw new Error(`${res.status} ${await res.text()}`);
      const out = await res.json();
      entry.done = true;
      state.saved = `Saved — live on the site now (${out.recorded} recorded)`;
    } catch (err) {
      state.saved = `Upload failed (${err.message}). Saved to this device instead.`;
      download(entry);
    } finally {
      state.saving = false;
    }
  } else {
    download(entry);
    state.saved = 'Saved to this device.';
  }

  state.recorded[entry.id] = true;
  try {
    localStorage.setItem('phonics.recorded.v1', JSON.stringify(state.recorded));
  } catch (e) { /* ignore */ }
  next();
}

function download(entry) {
  const a = document.createElement('a');
  a.href = state.lastUrl;
  a.download = `${entry.id}.${extFor(state.lastBlob)}`;
  a.click();
}

async function askToken() {
  const token = prompt('Upload passphrase (from phonics-upload.env on the Pi).\n\n'
    + 'Leave blank to just save recordings to this device instead.');
  if (!token) return;
  const res = await fetch('api/check', {
    method: 'POST', headers: { Authorization: `Bearer ${token}` },
  });
  if (res.ok) {
    state.token = token;
    try { localStorage.setItem('phonics.token.v1', token); } catch (e) { /* ignore */ }
    state.saved = 'Connected. Recordings now save straight to the site.';
  } else {
    state.saved = 'That passphrase was not accepted.';
  }
  render();
}

function next() {
  state.lastBlob = null;
  state.i = Math.min(state.i + 1, list().length - 1);
  render();
}

/* ---------------------------------------------------------------- render -- */

function render() {
  const entries = list();
  const entry = entries[state.i];
  const recording = state.recorder && state.recorder.state === 'recording';
  const doneHere = entries.filter((e) => state.recorded[e.id] || e.done).length;

  app.replaceChildren(
    el('div', { class: 'rec-tabs' }, KINDS.map(([k, label]) =>
      el('button', {
        class: 'btn' + (k === state.kind ? ' btn-primary' : ''),
        onclick: () => { state.kind = k; state.i = 0; state.lastBlob = null; render(); },
      }, label, ' ', el('span', { class: 'rec-count' },
        `${state.entries.filter((e) => e.kind === k && inScope(e) && (state.recorded[e.id] || e.done)).length}/${state.entries.filter((e) => e.kind === k && inScope(e)).length}`)))),

    dayFilter ? el('p', { class: 'rec-dayfilter' },
      `Showing only what day ${dayFilter} says — `,
      el('b', {}, `${state.entries.filter(inScope).length} recordings cover that whole lesson`),
      '. ', el('a', { href: 'record.html' }, 'Show everything →')) : null,

    el('p', { class: 'blurb' }, KINDS.find(([k]) => k === state.kind)[2]),

    el('div', { class: 'rec-dest' },
      state.token
        ? el('span', {}, '\u2713 Saving straight to the site.')
        : el('span', {}, 'Saving to this device only. '),
      el('button', { class: 'btn btn-quiet', onclick: askToken },
        state.token ? 'Change passphrase' : 'Connect to the site \u2192'),
      state.saved ? el('span', { class: 'rec-saved' }, state.saved) : null),

    entry ? el('div', { class: 'rec-card' },
      el('div', { class: 'rec-progress' }, `${state.i + 1} of ${entries.length} · ${doneHere} recorded`),
      el('div', { class: 'rec-text' }, entry.text),
      entry.how ? el('div', { class: 'rec-how' },
        el('div', { class: 'rec-say' }, 'Say: ', el('b', {}, entry.how.say)),
        el('div', { class: 'rec-words' }, 'It\u2019s the sound in ',
          entry.how.words.map((w, i) => el('span', {},
            i ? ', ' : '', el('b', {}, w))),
          ' \u2014 say those three out loud and listen for the bit they share.'),
        entry.how.avoid ? el('div', { class: 'rec-avoid' }, entry.how.avoid) : null)
        : el('p', { class: 'rec-script' }, entry.script),
      el('p', { class: 'rec-file' }, entry.file,
        entry.done ? el('span', { class: 'rec-have' }, ' · already recorded') : null,
        entry.days && entry.days.length
          ? el('span', {}, ` · used on day${entry.days.length > 1 ? 's' : ''} ${entry.days.slice(0, 8).join(', ')}${entry.days.length > 8 ? '…' : ''}`)
          : null),

      el('div', { class: 'actions' },
        el('button', {
          class: 'btn btn-big ' + (recording ? 'btn-rec' : 'btn-go'),
          onclick: () => (recording ? stopRec() : startRec()),
        }, recording ? '⏹ Stop' : '⏺ Record'),
        state.lastBlob ? el('button', { class: 'btn', onclick: () => new Audio(state.lastUrl).play() }, '▶ Play back') : null,
        state.lastBlob ? el('button', {
          class: 'btn btn-primary btn-big',
          onclick: save,
        }, state.saving ? 'Saving…' : (state.token ? '✓ Save & next' : '⬇ Save & next')) : null),

      el('div', { class: 'actions' },
        el('button', {
          class: 'btn btn-quiet',
          onclick: () => { state.i = Math.max(0, state.i - 1); state.lastBlob = null; render(); },
        }, '← Back'),
        el('button', { class: 'btn btn-quiet', onclick: next }, 'Skip →'),
        el('button', {
          class: 'btn btn-quiet',
          onclick: () => {
            const first = entries.findIndex((e) => !(state.recorded[e.id] || e.done));
            state.i = first < 0 ? 0 : first;
            state.lastBlob = null;
            render();
          },
        }, 'Jump to first unrecorded'))) : el('p', {}, 'Nothing here.'),

    el('details', { class: 'parents' },
      el('summary', {}, 'How this works'),
      el('div', {
        class: 'body',
        html: `
        <p>Each take downloads as a file already named correctly — <code>${entry ? entry.file.replace(/\\.mp3$/, '.webm') : 'sound-a.webm'}</code>
        or similar, depending on what your browser records. Copy the files onto
        the Pi into <code>~/services/phonics/web/audio/human/</code> and run:</p>
        <pre>python3 tools/build_audio_manifest.py
cd ~/services &amp;&amp; docker compose up -d --build phonics</pre>
        <p>The site then uses your voice everywhere that string is spoken, and
        the browser voice everywhere else. You can stop at any point — partial
        coverage works fine.</p>
        <p><b>Start with the letter sounds.</b> All 93 of them take about twenty
        minutes and they are the ones synthesis gets outright wrong: it reads
        "a" as its letter <em>name</em>, which is exactly what a child must not
        learn. Say the sound, not the name, and keep the stops clean —
        /t/, not "tuh".</p>
        <p>Nothing is uploaded. The recordings never leave your device until you
        copy them yourself.</p>`,
      })),
  );
}

/* ------------------------------------------------------------------ boot -- */

(async function boot() {
  try {
    state.recorded = JSON.parse(localStorage.getItem('phonics.recorded.v1')) || {};
    state.token = localStorage.getItem('phonics.token.v1') || null;
  } catch (e) { state.recorded = {}; }

  const [index, manifest] = await Promise.all([
    Data.get('data/speech-index.json'),
    // Ask the server, not the cached manifest: this is the page that changes it.
    fetch('api/recordings').then((r) => r.json())
      .catch(() => Data.get('data/audio-manifest.json').catch(() => ({ files: {} }))),
  ]);
  state.entries = index.entries.map((e) => ({ ...e, done: !!manifest.files[e.id] }));
  if (dayFilter && index.plans && index.plans[dayFilter]) {
    dayPlan = new Set(index.plans[dayFilter]);
  }

  if (!navigator.mediaDevices || !window.MediaRecorder) {
    app.replaceChildren(el('div', { class: 'rec-card' },
      el('p', {}, 'This browser cannot record audio. Safari on iOS and Chrome on ' +
        'desktop both work; the page also needs to be served over https, which ' +
        'phonics.sarjuthakkar.com is.'),
      el('p', {}, 'You can still see the full list of what needs recording below.')));
  }
  render();
})();
