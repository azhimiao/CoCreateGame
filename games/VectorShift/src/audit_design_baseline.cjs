/* Product-design evidence, not a difficulty score or a human playtest.
 * Run: node src/audit_design_baseline.cjs [--check]
 * Reads the actual rules and levels; never changes a playable stage.
 */
'use strict';
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const assert = require('node:assert/strict');
const core = require('./game-core.js');
const base = path.resolve(__dirname, '..');
const dataPath = path.join(base, 'data/levels.json');
const outputPath = path.join(base, 'data/design-baseline.json');
const levels = JSON.parse(fs.readFileSync(dataPath, 'utf8'));
const digest = data => crypto.createHash('sha256').update(data).digest('hex');
const histogram = values => values.reduce((out, x) => { out[x] = (out[x] || 0) + 1; return out; }, {});
const round = n => Math.round(n * 10000) / 10000;
function range(values) {
  const sorted = [...values].sort((a, b) => a - b);
  const n = sorted.length;
  return { min: sorted[0], median: (sorted[Math.floor((n - 1) / 2)] + sorted[Math.floor(n / 2)]) / 2,
    max: sorted[n - 1], mean: round(sorted.reduce((a, b) => a + b, 0) / n) };
}
function maskTopology(level) {
  const mask = core.playableSet(level), visited = new Set();
  let components = 0, enclosedVoidRegions = 0;
  const flood = (sx, sy, allowed, seen) => {
    const queue = [[sx, sy]]; seen.add(sx + ',' + sy);
    for (let i = 0; i < queue.length; i++) {
      const [x, y] = queue[i];
      for (let d = 0; d < 4; d++) {
        const nx = x + core.DX[d], ny = y + core.DY[d], key = nx + ',' + ny;
        if (!seen.has(key) && allowed(nx, ny)) { seen.add(key); queue.push([nx, ny]); }
      }
    }
  };
  for (const key of mask) if (!visited.has(key)) {
    components++; const [x, y] = key.split(',').map(Number);
    flood(x, y, (nx, ny) => mask.has(nx + ',' + ny), visited);
  }
  const voidSeen = new Set(), n = level.size;
  const voidAllowed = (x, y) => x >= -1 && y >= -1 && x <= n && y <= n && !mask.has(x + ',' + y);
  flood(-1, -1, voidAllowed, voidSeen);
  for (let y = 0; y < n; y++) for (let x = 0; x < n; x++) {
    if (!mask.has(x + ',' + y) && !voidSeen.has(x + ',' + y)) {
      enclosedVoidRegions++; flood(x, y, voidAllowed, voidSeen);
    }
  }
  return { components, enclosedVoidRegions };
}
function rotationFingerprint(level) {
  const n = level.size;
  const rotate = ([x, y], turns) => {
    for (let i = 0; i < turns; i++) [x, y] = [n - 1 - y, x];
    return [x, y];
  };
  const mask = [...core.playableSet(level)].map(key => key.split(',').map(Number));
  const forms = [0, 1, 2, 3].map(turns => JSON.stringify({ size: n,
    mask: mask.map(c => rotate(c, turns)).sort((a, b) => a[1] - b[1] || a[0] - b[0]),
    arrows: level.arrows.map(a => JSON.stringify([a.color, (a.d + turns) % 4,
      a.cells.map(c => rotate(c, turns))])).sort()
  }));
  return digest(forms.sort()[0]);
}
function enumerateReachable(level) {
  const n = level.arrows.length, full = (1 << n) - 1;
  const blockers = level.arrows.map(a => [0, 1].map(phase => {
    const ids = core.blockers(level, { ...core.newState(level), phase }, a.id);
    return ids.reduce((bits, id) => bits | (1 << level.arrows.findIndex(b => b.id === id)), 0);
  }));
  const start = full * 2, queue = [start], seen = new Set(queue), reverse = new Map();
  const removals = [];
  function edge(from, to, removal) {
    if (!reverse.has(to)) reverse.set(to, []);
    reverse.get(to).push(from);
    if (removal) removals.push([from, to]);
    if (!seen.has(to)) { seen.add(to); queue.push(to); }
  }
  for (let i = 0; i < queue.length; i++) {
    const from = queue[i], mask = Math.floor(from / 2), phase = from % 2;
    // Terminal boards end the run; a post-win phase toggle is not a player decision.
    if (!mask) continue;
    edge(from, mask * 2 + (1 - phase), false);
    for (let j = 0; j < n; j++) if ((mask & (1 << j)) && !(mask & blockers[j][phase])) {
      edge(from, (mask ^ (1 << j)) * 2 + phase, true);
    }
  }
  const winning = new Set([0, 1].filter(x => seen.has(x))), back = [...winning];
  for (let i = 0; i < back.length; i++) for (const from of reverse.get(back[i]) || []) {
    if (!winning.has(from)) { winning.add(from); back.push(from); }
  }
  return { reachableStates: seen.size, winningStates: winning.size,
    legalRemovalTransitions: removals.length,
    losingRemovalTransitions: removals.filter(([from, to]) => winning.has(from) && !winning.has(to)).length };
}
function audit(level) {
  core.validateLevel(level);
  const optimal = core.solve(level, core.newState(level));
  assert.ok(optimal.actions, level.id + ' is unsolvable');
  let state = core.newState(level), toggles = 0, waves = 0;
  const batches = [], actions = [];
  const cycle = new Set();
  while (state.remaining.length) {
    const key = state.phase + ':' + state.remaining.join(',');
    assert.ok(!cycle.has(key), level.id + ' greedy policy is stuck'); cycle.add(key);
    const ids = state.remaining.filter(id => core.clearPath(level, state, id));
    if (!ids.length) {
      state = core.transition(level, state, { type: 'toggle' });
      toggles++; actions.push('toggle'); continue;
    }
    waves++; batches.push({ phase: state.phase, arrows: ids });
    for (const id of ids) {
      state = core.transition(level, state, { type: 'remove', id }); actions.push(id);
    }
  }
  const minToggles = optimal.actions.filter(a => a.type === 'toggle').length;
  const lengths = level.arrows.map(a => a.cells.length);
  const bodyCells = lengths.reduce((a, b) => a + b, 0), maskCells = core.maskCellCount(level);
  return { id: level.id, size: level.size, shape: level.shape || 'square', arrows: lengths.length,
    bodyCells, maskCells, fillRate: round(bodyCells / maskCells), bodyLengths: range(lengths),
    minActions: optimal.actions.length, minToggles,
    initialLegalRemovals: level.arrows.filter(a => core.clearPath(level, core.newState(level), a.id)).length,
    greedy: { solved: true, toggles, matchesMinimum: toggles === minToggles,
      removalWaves: waves, batches, actions },
    topology: maskTopology(level), rotationFingerprint: rotationFingerprint(level),
    ...enumerateReachable(level) };
}
const rows = levels.map(audit);
const grouped = new Map();
for (const row of rows) {
  if (!grouped.has(row.rotationFingerprint)) grouped.set(row.rotationFingerprint, []);
  grouped.get(row.rotationFingerprint).push(row.id);
}
const report = {
  kind: 'DESIGN_BASELINE_EVIDENCE', ruleset: 'existing binary phase / removal only / first void exits',
  limitations: [ 'Not a human difficulty or aesthetic rating.',
    'Reachable states exclude undo/reset and stop at a cleared board.',
    'A removal loses only if its destination cannot reach a cleared board with unlimited toggles.',
    'Rotation fingerprint includes size, mask, semantic colors, facing, ordered body cells; excludes IDs and decoration.',
    'Reflections, shifted padding, and abstract dependency-graph isomorphism are not deduplicated.' ],
  inputs: { levelsSha256: digest(fs.readFileSync(dataPath)),
    coreSha256: digest(fs.readFileSync(path.join(__dirname, 'game-core.js'))) },
  summary: { levels: rows.length, sizeHistogram: histogram(rows.map(r => r.size)),
    shapeHistogram: histogram(rows.map(r => r.shape)), arrows: range(rows.map(r => r.arrows)),
    fillRate: range(rows.map(r => r.fillRate)), minToggleHistogram: histogram(rows.map(r => r.minToggles)),
    greedySolved: rows.filter(r => r.greedy.solved).length,
    greedyMatchesMinimum: rows.filter(r => r.greedy.matchesMinimum).length,
    reachableStates: rows.reduce((s, r) => s + r.reachableStates, 0),
    winningStates: rows.reduce((s, r) => s + r.winningStates, 0),
    legalRemovalTransitions: rows.reduce((s, r) => s + r.legalRemovalTransitions, 0),
    losingRemovalTransitions: rows.reduce((s, r) => s + r.losingRemovalTransitions, 0),
    rotationDuplicateGroups: [...grouped.values()].filter(ids => ids.length > 1) },
  levels: rows
};
const serialized = JSON.stringify(report, null, 2) + '\n';
if (process.argv.includes('--check')) {
  assert.equal(fs.readFileSync(outputPath, 'utf8'), serialized, 'Design evidence is stale: rerun without --check');
} else fs.writeFileSync(outputPath, serialized);
process.stdout.write(JSON.stringify(report.summary, null, 2) + '\n');
