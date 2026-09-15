/* Shared foundations: data loading, speech, progress.
 *
 * No build step, no framework, no network calls beyond fetching our own JSON.
 * The whole site is static files -- which is why it needs no accounts and
 * works on a five-year-old tablet.
 */

/* ---------------------------------------------------------------- data --- */

const Data = {
  _cache: {},
  async get(path) {
    if (!this._cache[path]) {
      this._cache[path] = fetch(path).then((r) => {
        if (!r.ok) throw new Error(`${path}: ${r.status}`);
        return r.json();
      });
    }
    return this._cache[path];
  },
  sequence() { return this.get('data/sequence.json'); },
  phonemes() { return this.get('data/phonemes.json'); },
  level(n) { return this.get(`data/levels/${String(n).padStart(3, '0')}.json`); },
};

/* -------------------------------------------------------------- speech --- */
/* Browser speech synthesis. Good at words, bad at bare sounds -- so every
 * grapheme carries a `say` spelling from data/phonemes.json that lands closer
 * to the real phoneme than the letter name would. See tools/build_phonemes.py.
 *
 * iOS will not speak until speech has been started inside a real tap, which is
 * what Speech.prime() is for: the lesson's opening button calls it. */

const Speech = {
  voice: null,
  ready: false,
  muted: false,

  init() {
    if (!('speechSynthesis' in window)) return;
    const pick = () => {
      const voices = speechSynthesis.getVoices();
      if (!voices.length) return;
      const prefer = [
        (v) => v.lang === 'en-US' && /samantha|jenny|aria|female|natural/i.test(v.name),
        (v) => v.lang === 'en-US' && v.localService,
        (v) => v.lang === 'en-US',
        (v) => v.lang.startsWith('en'),
      ];
      for (const test of prefer) {
        const found = voices.find(test);
        if (found) { this.voice = found; break; }
      }
      this.ready = true;
    };
    pick();
    speechSynthesis.onvoiceschanged = pick;
  },

  supported() { return 'speechSynthesis' in window; },

  prime() {
    if (!this.supported()) return;
    const u = new SpeechSynthesisUtterance(' ');
    u.volume = 0;
    speechSynthesis.speak(u);
  },

  cancel() { if (this.supported()) speechSynthesis.cancel(); },

  /** Speak text. Returns a promise that settles when it finishes. */
  say(text, { rate = 0.85, pitch = 1.05 } = {}) {
    return new Promise((resolve) => {
      if (!this.supported() || this.muted || !text) return resolve();
      speechSynthesis.cancel();
      const u = new SpeechSynthesisUtterance(text);
      if (this.voice) u.voice = this.voice;
      u.lang = 'en-US';
      u.rate = rate;
      u.pitch = pitch;
      u.onend = () => resolve();
      u.onerror = () => resolve();
      // Safari occasionally drops onend; don't let a lesson hang on it.
      const guard = setTimeout(resolve, 1200 + text.length * 120);
      u.onend = () => { clearTimeout(guard); resolve(); };
      speechSynthesis.speak(u);
    });
  },

  /** Say a single sound, given a grapheme entry from phonemes.json. */
  sound(entry, { rate = 0.7 } = {}) {
    if (!entry) return Promise.resolve();
    return this.say(entry.say, { rate, pitch: 1.0 });
  },

  /** Say a word slowly and clearly. */
  word(text) { return this.say(text, { rate: 0.75 }); },

  /** Say a sentence at storytime pace. */
  sentence(text) { return this.say(text, { rate: 0.8 }); },

  /** Spell a word out by letter name -- the one place letter names are right. */
  spell(word) { return this.say(word.toUpperCase().split('').join(', '), { rate: 0.7 }); },
};

/* ------------------------------------------------------------ progress --- */
/* Everything a family does stays in their own browser. There is no account,
 * no server, nothing to sign into and nothing collected. */

const Progress = {
  KEY: 'phonics.progress.v1',

  read() {
    try {
      return JSON.parse(localStorage.getItem(this.KEY)) || { days: {}, lastDay: null };
    } catch (e) {
      return { days: {}, lastDay: null };
    }
  },

  write(state) {
    try { localStorage.setItem(this.KEY, JSON.stringify(state)); } catch (e) { /* private mode */ }
  },

  day(n) { return this.read().days[String(n)] || null; },

  isDone(n) { const d = this.day(n); return !!(d && d.completed); },

  /** Furthest day finished, so the home page can say where to go next. */
  nextDay() {
    const state = this.read();
    const done = Object.keys(state.days)
      .filter((k) => state.days[k].completed)
      .map(Number);
    if (!done.length) return 1;
    return Math.min(120, Math.max(...done) + 1);
  },

  start(n) {
    const s = this.read();
    s.lastDay = n;
    s.days[String(n)] = Object.assign({ completed: false, step: 0 }, s.days[String(n)], {
      startedAt: (s.days[String(n)] || {}).startedAt || Date.now(),
    });
    this.write(s);
  },

  saveStep(n, step) {
    const s = this.read();
    const d = s.days[String(n)] || { completed: false };
    d.step = step;
    s.days[String(n)] = d;
    s.lastDay = n;
    this.write(s);
  },

  complete(n, stats) {
    const s = this.read();
    const d = s.days[String(n)] || {};
    d.completed = true;
    d.step = 0;
    d.finishedAt = Date.now();
    d.times = (d.times || 0) + 1;
    if (stats) d.stats = stats;
    s.days[String(n)] = d;
    s.lastDay = n;
    this.write(s);
  },

  reset() { this.write({ days: {}, lastDay: null }); },
};

/* ---------------------------------------------------------------- misc --- */

const el = (tag, attrs = {}, ...children) => {
  const node = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === 'class') node.className = v;
    else if (k === 'html') node.innerHTML = v;
    else if (k.startsWith('on') && typeof v === 'function') node.addEventListener(k.slice(2), v);
    else if (v !== null && v !== undefined) node.setAttribute(k, v);
  }
  for (const c of children.flat()) {
    if (c === null || c === undefined || c === false) continue;
    node.append(c.nodeType ? c : document.createTextNode(String(c)));
  }
  return node;
};

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

const shuffle = (arr) => {
  const a = arr.slice();
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
};

/* A short rising chime for "yes", a soft low one for "try again". Generated,
 * so there are no audio files to load. */
const Chime = {
  ctx: null,
  play(kind) {
    try {
      this.ctx = this.ctx || new (window.AudioContext || window.webkitAudioContext)();
      const notes = kind === 'yes' ? [523.25, 659.25, 783.99] : [392.0, 329.63];
      notes.forEach((freq, i) => {
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.type = 'sine';
        osc.frequency.value = freq;
        const t = this.ctx.currentTime + i * 0.09;
        gain.gain.setValueAtTime(0.0001, t);
        gain.gain.exponentialRampToValueAtTime(0.18, t + 0.02);
        gain.gain.exponentialRampToValueAtTime(0.0001, t + 0.22);
        osc.connect(gain).connect(this.ctx.destination);
        osc.start(t);
        osc.stop(t + 0.25);
      });
    } catch (e) { /* audio not available; the visual feedback carries it */ }
  },
};

Speech.init();
