/* Home: 120 days, grouped into the five stages, and nothing else to decide. */

const app = document.getElementById('app');

function dayTile(spec, built, done, isNext) {
  const classes = ['day'];
  if (!built) classes.push('missing');
  else if (done) classes.push('done');
  else if (isNext) classes.push('next');
  else classes.push('todo');

  const inner = [el('span', { class: 'n' }, spec.level), el('span', { class: 'f' }, spec.focus)];
  if (!built) return el('div', { class: classes.join(' '), title: 'Not written yet' }, inner);
  return el('a', {
    class: classes.join(' '),
    href: `lesson.html?day=${spec.level}`,
    'aria-label': `Day ${spec.level}: ${spec.focus}`,
  }, inner);
}

(async function boot() {
  const [sequence, manifest] = await Promise.all([
    Data.sequence(),
    Data.get('data/levels/manifest.json').catch(() => ({ built: [] })),
  ]);
  const built = new Set(manifest.built);
  const next = Progress.nextDay();
  const doneCount = sequence.levels.filter((l) => Progress.isDone(l.level)).length;

  const target = built.has(next) ? next : Math.max(...[...built, 1]);
  const targetSpec = sequence.levels.find((l) => l.level === target);

  const head = el('div', { class: 'continue-card' },
    el('div', {},
      el('div', { class: 'label' }, doneCount ? 'Pick up where you left off' : 'Start here'),
      el('div', { class: 'title' }, `Day ${target} · ${targetSpec.focus}`)),
    el('a', { class: 'btn btn-go btn-big', href: `lesson.html?day=${target}` }, 'Start →'));

  const stages = sequence.stages.map((stage) => {
    const levels = sequence.levels.filter((l) => l.level >= stage.range[0] && l.level <= stage.range[1]);
    const doneHere = levels.filter((l) => Progress.isDone(l.level)).length;
    return el('section', { class: 'stage' },
      el('h2', {}, `${stage.name} `, el('span', { style: 'color:var(--ink-soft);font-weight:600;font-size:1rem' },
        `· days ${stage.range[0]}–${stage.range[1]} · ${doneHere}/${levels.length} done`)),
      el('p', { class: 'blurb' }, stage.blurb),
      el('div', { class: 'days' }, levels.map((l) => dayTile(l, built.has(l.level), Progress.isDone(l.level), l.level === next))));
  });

  const parents = el('details', { class: 'parents' },
    el('summary', {}, 'For grown-ups: how to use this'),
    el('div', { class: 'body', html: `
      <p><b>One day at a time, 15–30 minutes, sitting together.</b> Do one day per
      sitting. If a day is hard, do it again tomorrow — going slower is not falling
      behind. Stop while it is still fun, even mid-lesson; the site remembers.</p>
      <p><b>Blending is the whole game.</b> Sounding out letters is easy; pushing
      the sounds together into a word is the hard part, and it is what the
      "sound it out, then say it fast" activities drill. Say the sounds short and
      clean — /t/, not "tuh" — or "cat" turns into "cuh-a-tuh".</p>
      <p><b>Help early, don't let them struggle.</b> If a word stalls for more than
      a couple of seconds, say it for them and move on. Tap any word in a sentence
      to hear it.</p>
      <p><b>Nothing is stored anywhere but this device.</b> No account, no sign-in,
      no data leaves the browser. Progress lives in this browser only.</p>
      <p><a href="about.html">What this is and where the sequence comes from →</a><br>
      <a href="record.html">Record the voice in your own voice →</a></p>` }));

  const reset = el('div', { style: 'margin-top:30px;text-align:center' },
    el('button', {
      class: 'btn btn-quiet',
      onclick: () => {
        if (confirm('Clear all progress on this device? The lessons stay, the stars go.')) {
          Progress.reset();
          location.reload();
        }
      },
    }, 'Clear progress on this device'));

  app.replaceChildren(head, ...stages, parents, reset);
})();
