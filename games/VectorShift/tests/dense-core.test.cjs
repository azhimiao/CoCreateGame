'use strict';

const assert = require('node:assert/strict');
const test = require('node:test');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const core = require('../src/dense-core.js');

const clone = value => JSON.parse(JSON.stringify(value));
const piece = (id, d, cells, skin = 'coral') => ({ id, d, cells, color: 'gold', skin });
const board = (width, height, arrows, mask) => ({ width, height, arrows, ...(mask === undefined ? {} : { mask }) });
const remove = (level, state, id) => core.transition(level, state, { type: 'remove', id });

function freeze(value) {
  if (value && typeof value === 'object') {
    Object.freeze(value);
    Object.values(value).forEach(freeze);
  }
  return value;
}

// 48 packed, 12-cell snakes: each row of six tiles releases right -> left.
// No external data or level generator is required to run these tests.
function denseFixture() {
  const arrows = [];
  for (let row = 0; row < 8; row++) for (let column = 0; column < 6; column++) {
    const cells = [];
    for (let y = 0; y < 3; y++) for (let i = 0; i < 4; i++) {
      cells.push([column * 4 + (y % 2 ? 3 - i : i), row * 3 + y]);
    }
    arrows.push(piece(`snake-${row * 6 + column}`, 1, cells));
  }
  return board(24, 24, arrows);
}

function chainFixture() {
  return board(6, 2, [
    piece('left', 1, [[0, 1], [1, 1]]),
    piece('middle', 1, [[2, 1], [3, 1]]),
    piece('right', 1, [[4, 1], [5, 1]])
  ]);
}

function replay(level, actions, state = core.newState(level)) {
  for (const action of actions) {
    assert.equal(action.type, 'remove');
    assert.equal(core.clearPath(level, state, action.id), true, `blocked witness ID ${action.id}`);
    const previous = state;
    state = core.transition(level, state, action);
    assert.equal(state.remaining.length, previous.remaining.length - 1);
    assert.equal(core.validateState(level, state), true);
  }
  return state;
}

test('UMD supports Node, browser and AMD without replacing the phase core', () => {
  assert.equal(globalThis.VectorShiftDenseCore, core);
  const source = fs.readFileSync(path.resolve(__dirname, '../src/dense-core.js'), 'utf8');
  for (const amd of [false, true]) {
    const existing = { phase: 'sentinel' };
    let exported;
    const sandbox = { VectorShiftCore: existing };
    if (amd) {
      sandbox.define = (dependencies, factory) => { assert.equal(dependencies.length, 0); exported = factory(); };
      sandbox.define.amd = {};
    }
    vm.runInNewContext(source, sandbox);
    assert.equal(typeof sandbox.VectorShiftDenseCore.solve, 'function');
    assert.equal(sandbox.VectorShiftCore, existing);
    assert.equal(sandbox.VectorShiftDenseCore.validateLevel(chainFixture()), true);
    if (amd) assert.equal(exported, sandbox.VectorShiftDenseCore);
  }
});

test('rectangle dimensions take precedence over square fallback and support 64 cells per side', () => {
  const rectangle = { size: 7, width: 2, height: 7, arrows: [piece('edge', 1, [[1, 5]])] };
  assert.equal(core.validateLevel(rectangle), true);
  assert.equal(core.playableSet(rectangle).size, 14);
  assert.equal(core.isPlayable(rectangle, 2, 5), false);
  assert.deepEqual(core.exitRayCells(rectangle, core.newState(rectangle), 'edge'), []);
  assert.equal(core.validateLevel({ size: 64, arrows: [] }), true);
  assert.equal(core.maskCellCount({ size: 64, arrows: [] }), 4096);
  assert.equal(core.maskCellCount({ size: 3, width: 2, arrows: [] }), 6);
  assert.equal(core.maskCellCount({ size: 3, height: 2, arrows: [] }), 6);
  assert.equal(core.maskCellCount({ size: 3, arrows: [] }), 9);
});

test('48 long snakes solve in six simultaneous waves without a bit mask', () => {
  const level = freeze(denseFixture()), start = freeze(core.newState(level));
  assert.equal(core.validateLevel(level, { requireConnectedMask: true }), true);
  assert.equal(core.occupancyMap(level, start).size, 576);
  const result = core.solve(level, start);
  assert.equal(result.solvable, true);
  assert.equal(result.actions.length, 48);
  assert.equal(new Set(result.actions.map(action => action.id)).size, 48);
  assert.deepEqual(result.remainingBlocked, []);
  assert.deepEqual(result.waves, Array.from({ length: 6 }, (_, wave) =>
    Array.from({ length: 8 }, (_, row) => `snake-${row * 6 + 5 - wave}`)));
  const end = replay(level, result.actions, start);
  assert.equal(end.moves, 48);
  assert.deepEqual(end.remaining, []);
  assert.deepEqual(core.solve(level, end), { actions: [], solvable: true, remainingBlocked: [], waves: [] });
  let state = end;
  for (let i = 0; i < 48; i++) state = core.transition(level, state, { type: 'undo' });
  assert.deepEqual(state, start);
});

test('numeric IDs 0, 31, 32, 40 and 44 stay distinct through dependencies and removal', () => {
  const level = board(45, 1, Array.from({ length: 45 }, (_, id) => piece(id, 1, [[id, 0]])));
  const start = core.newState(level), result = core.solve(level, start);
  assert.deepEqual(core.blockers(level, start, 0), Array.from({ length: 44 }, (_, i) => i + 1));
  assert.deepEqual(result.actions.map(a => a.id), Array.from({ length: 45 }, (_, i) => 44 - i));
  assert.deepEqual(replay(level, result.actions).remaining, []);
});

test('maximum 64x64 board with 4096 single-cell pieces is solvable in 64 waves', () => {
  const arrows = [];
  for (let y = 0; y < 64; y++) for (let x = 0; x < 64; x++) arrows.push(piece(y * 64 + x, 1, [[x, y]]));
  const level = board(64, 64, arrows);
  const result = core.solve(level, core.newState(level));
  assert.equal(result.solvable, true);
  assert.equal(result.actions.length, 4096);
  assert.equal(new Set(result.actions.map(a => a.id)).size, 4096);
  assert.equal(result.waves.length, 64);
  assert.ok(result.waves.every(wave => wave.length === 64));
});

for (const [d, dx, dy] of [[0, 0, -1], [1, 1, 0], [2, 0, 1], [3, -1, 0]]) {
  test(`direction ${d}: ordered blockers, blocker-inclusive ray, and newly cleared paths`, () => {
    const level = board(5, 5, [
      piece('far', d, [[2 + dx * 2, 2 + dy * 2]]),
      piece('target', d, [[2, 2]]),
      piece('near', d, [[2 + dx, 2 + dy]])
    ]);
    const start = core.newState(level);
    assert.deepEqual(core.blockers(level, start, 'target'), ['near', 'far']);
    assert.equal(core.clearPath(level, start, 'target'), false);
    assert.deepEqual(core.exitRayCells(level, start, 'target'), [[2 + dx, 2 + dy]]);
    assert.deepEqual(remove(level, start, 'target'), start);
    const state = replay(level, [{ type: 'remove', id: 'far' }, { type: 'remove', id: 'near' }]);
    assert.deepEqual(core.blockers(level, state, 'target'), []);
    assert.deepEqual(core.exitRayCells(level, state, 'target'), [[2 + dx, 2 + dy], [2 + dx * 2, 2 + dy * 2]]);
    assert.equal(core.clearPath(level, state, 'target'), true);
    assert.deepEqual(core.blockers(level, state, 'near'), null);
    assert.deepEqual(core.exitRayCells(level, state, 'near'), []);
    assert.equal(core.clearPath(level, state, 'missing'), false);
    assert.equal(core.blockers(level, state, 'missing'), null);
  });
}

test('a long blocker intersecting a ray repeatedly appears once at its first intersection', () => {
  const level = board(6, 3, [
    piece('target', 1, [[0, 1]]),
    piece('weave', 0, [[1, 1], [1, 0], [2, 0], [3, 0], [3, 1], [4, 1], [4, 0]]),
    piece('far', 1, [[5, 1]])
  ]);
  const state = core.newState(level);
  assert.deepEqual(core.blockers(level, state, 'target'), ['weave', 'far']);
  assert.deepEqual(core.exitRayCells(level, state, 'target'), [[1, 1]]);
  assert.deepEqual(core.solve(level, state).waves, [['weave', 'far'], ['target']]);
});

test('own body blocks release instead of allowing a snake to pass through itself', () => {
  const level = board(7, 3, [
    piece('curl', 1, [[0, 0], [1, 0], [2, 0], [2, 1], [1, 1], [0, 1]]),
    piece('blocker', 1, [[4, 1]])
  ]);
  const state = core.newState(level);
  assert.equal(core.validateLevel(level), true);
  assert.deepEqual(core.headCell(core.arrow(level, 'curl')), { x: 0, y: 1 });
  assert.equal(core.arrow(level, 'missing'), undefined);
  assert.deepEqual(core.blockers(level, state, 'curl'), ['curl', 'blocker']);
  assert.deepEqual(core.exitRayCells(level, state, 'curl'), [[1, 1]]);
  const next = remove(level, state, 'blocker');
  assert.equal(core.clearPath(level, next, 'curl'), false);
  assert.deepEqual(remove(level, next, 'curl'), next);
  assert.equal(core.solve(level, next).solvable, false);
  assert.deepEqual(core.solve(level, next).remainingBlocked, ['curl']);
});

test('a hole in a silhouette is empty space, not an exit past a visible blocker', () => {
  const mask = [];
  for (let y = 0; y < 3; y++) for (let x = 0; x < 7; x++) if (x !== 3 || y !== 1) mask.push([x, y]);
  const level = board(7, 3, [piece('before', 1, [[1, 1]]), piece('after', 3, [[4, 1]])], mask);
  assert.equal(core.validateLevel(level, { requireConnectedMask: true }), true);
  const state = core.newState(level);
  assert.deepEqual(core.blockers(level, state, 'before'), ['after']);
  assert.deepEqual(core.exitRayCells(level, state, 'before'), [[2, 1], [3, 1], [4, 1]]);
  assert.deepEqual(core.exitRayCells(level, state, 'after'), [[3, 1], [2, 1], [1, 1]]);
  assert.equal(core.solve(level, state).solvable, false);
  assert.deepEqual(remove(level, state, 'before'), state);
  const stale = {remaining:['after'],moves:1,history:[{remaining:['before','after'],moves:0}]};
  assert.throws(()=>core.validateState(level,stale), /blocked/);
});

for (const [d, dx, dy] of [[0, 0, -1], [1, 1, 0], [2, 0, 1], [3, -1, 0]]) {
  test(`direction ${d}: gaps never hide a later blocker, even on separate mask islands`, () => {
    const a=[3,3], b=[3+dx*3,3+dy*3], level=board(7,7,[piece('a',d,[a]),piece('b',d,[b])],[a,b]);
    const start=core.newState(level);
    assert.deepEqual(core.blockers(level,start,'a'),['b']);
    assert.equal(core.clearPath(level,start,'a'),false);
    assert.deepEqual(remove(level,start,'a'),start);
    const next=remove(level,start,'b');
    assert.equal(core.clearPath(level,next,'a'),true);
    assert.equal(core.solve(level,start).solvable,true);
  });
}

test('mask connectivity is optional and uses four-neighbour connectivity', () => {
  const disconnected = board(3, 3, [piece('island', 1, [[0, 0]])], [[0, 0], [1, 1]]);
  assert.equal(core.validateLevel(disconnected), true);
  assert.throws(() => core.validateLevel(disconnected, { requireConnectedMask: true }), /disconnected mask/);
  assert.equal(core.clearPath(disconnected, core.newState(disconnected), 'island'), true);
});

test('returned collections, head coordinates and edited levels never poison cached geometry', () => {
  const level = chainFixture(), state = core.newState(level);
  const mask = core.playableSet(level); mask.clear();
  const occupancy = core.occupancyMap(level, state); occupancy.clear();
  const head = core.headCell(level.arrows[0]); head.x = 999;
  assert.equal(core.playableSet(level).size, 12);
  assert.equal(core.occupancyMap(level, state).size, 6);
  assert.deepEqual(core.headCell(level.arrows[0]), { x: 1, y: 1 });
  level.mask = [[0, 1], [1, 1], [2, 1], [3, 1], [4, 1], [5, 1]];
  assert.equal(core.playableSet(level).size, 6);
  level.mask.pop();
  assert.equal(core.playableSet(level).has('5,1'), false);
  assert.throws(() => core.validateLevel(level), /outside mask/);
});

test('remove, undo, reset and no-ops are immutable, with independent history arrays', () => {
  const level = freeze(chainFixture()), initial = freeze(core.newState(level));
  for (const action of [{ type: 'remove', id: 'left' }, { type: 'remove', id: 'absent' }, { type: 'undo' }, { type: 'toggle' }, null]) {
    const next = core.transition(level, initial, action);
    assert.deepEqual(next, initial);
    assert.notEqual(next, initial);
    assert.notEqual(next.remaining, initial.remaining);
  }
  const one = freeze(remove(level, initial, 'right'));
  const two = freeze(remove(level, one, 'middle'));
  assert.deepEqual(core.transition(level, two, { type: 'undo' }), one);
  assert.deepEqual(core.transition(level, two, { type: 'reset' }), initial);
  assert.deepEqual(core.transition(level, null, { type: 'reset' }), initial);
  const next = remove(level, two, 'left');
  next.history[0].remaining.pop();
  next.history[1].remaining[0] = 'changed';
  assert.deepEqual(two.history[0].remaining, ['left', 'middle', 'right']);
  assert.deepEqual(two.history[1].remaining, ['left', 'middle']);
  assert.deepEqual(core.occupancyMap(level, one), new Map([['0,1', 'left'], ['1,1', 'left'], ['2,1', 'middle'], ['3,1', 'middle']]));
});

test('JSON persistence retains legal undo and supports reordered ID arrays', () => {
  const level = chainFixture();
  const state = replay(level, [{ type: 'remove', id: 'right' }, { type: 'remove', id: 'middle' }]);
  const restored = JSON.parse(JSON.stringify(state));
  restored.history[0].remaining.reverse();
  restored.history[1].remaining.reverse();
  assert.equal(core.validateState(level, restored), true);
  const undo = core.transition(level, restored, { type: 'undo' });
  assert.equal(core.validateState(level, undo), true);
  assert.deepEqual(core.solve(level, undo).actions.map(a => a.id), ['middle', 'left']);
  assert.deepEqual(core.solve(level, state).actions, [{ type: 'remove', id: 'left' }]);
});

test('string and numeric IDs are distinct, including object-property-like strings', () => {
  const level = board(6, 1, ['__proto__', 'constructor', 'toString', 0, '0', '1'].map((id, x) => piece(id, 0, [[x, 0]])));
  const start = core.newState(level);
  assert.equal(core.validateState(level, start), true);
  assert.equal(core.occupancyMap(level, start).get('0,0'), '__proto__');
  const end = replay(level, core.solve(level, start).actions);
  assert.deepEqual(end.remaining, []);
  assert.equal(core.validateState(level, clone(end)), true);
});

test('dead cycles and arrows depending on them are reported after any clear prefix', () => {
  const cycle = board(5, 2, [
    piece('upstream', 1, [[0, 0]]), piece('a', 1, [[1, 0]]), piece('b', 3, [[3, 0]])
  ]);
  assert.deepEqual(core.solve(cycle, core.newState(cycle)), {
    actions: null, solvable: false, remainingBlocked: ['upstream', 'a', 'b'], waves: []
  });
  cycle.arrows.push(piece('free', 2, [[4, 1]]));
  const start = freeze(core.newState(cycle));
  assert.deepEqual(core.solve(cycle, start), {
    actions: null, solvable: false, remainingBlocked: ['upstream', 'a', 'b'], waves: [['free']]
  });
  assert.equal(start.remaining.length, 4);
});

test('an empty level is already solved and still has a valid serializable state', () => {
  const level = board(1, 1, []), state = core.newState(level);
  assert.equal(core.validateState(level, clone(state)), true);
  assert.deepEqual(core.solve(level, state), { actions: [], solvable: true, remainingBlocked: [], waves: [] });
});

test('malformed dimensions, masks, arrows and paths are rejected', () => {
  const invalid = [null, {}, { width: 3, arrows: [] }, { height: 3, arrows: [] }];
  for (const value of [0, -1, 65, 1.5, '4', null, NaN, Infinity]) {
    invalid.push({ width: value, height: 3, arrows: [] });
    invalid.push({ width: 3, height: value, arrows: [] });
    invalid.push({ width: 3, height: 3, size: value, arrows: [] });
  }
  for (const mask of [[], null, 'mask', [[0, 0], [0, 0]], [[-1, 0]], [[3, 0]], [[0, 3]], [[0.5, 0]], [[0]], [[0, 0, 1]], [null], new Array(1)]) {
    invalid.push(board(3, 3, [], mask));
  }
  for (const cells of [[], null, 'cells', [[0, 0], [1, 1]], [[0, 0], [2, 0]], [[0, 0], [1, 0], [0, 0]], [[3, 0]], [[0, 3]], [[0.5, 0]], [[0, 0, 1]], [null], new Array(1)]) {
    invalid.push(board(3, 3, [piece('a', 0, cells)]));
  }
  for (const id of [null, undefined, '', ' ', {}, [], NaN, Infinity, 0.5, Number.MAX_SAFE_INTEGER + 1]) {
    invalid.push(board(3, 3, [piece(id, 0, [[0, 0]])]));
  }
  for (const d of [-1, 4, 1.5, '1', NaN, null, undefined]) invalid.push(board(3, 3, [piece('a', d, [[0, 0]])]));
  invalid.push(board(3, 3, [piece('a', 0, [[0, 0]]), piece('a', 0, [[1, 0]])]));
  invalid.push(board(3, 3, [piece('a', 0, [[0, 0]]), piece('b', 0, [[0, 0]])]));
  invalid.push(board(3, 3, [{ ...piece('a', 0, [[0, 0]]), color: 'blue' }]));
  invalid.push(board(3, 3, [piece('a', 0, [[0, 0]])], [[1, 0]]));
  invalid.push(board(3, 3, new Array(1)));
  invalid.push(board(3, 3, null));
  invalid.push(board(3, 3, [null]));
  for (let i = 0; i < invalid.length; i++) {
    assert.throws(() => core.validateLevel(invalid[i]), TypeError, `malformed fixture ${i}`);
  }
});

test('saved-state guards reject forged counters, subsets, history and illegal removals', () => {
  const level = chainFixture(), initial = core.newState(level);
  const one = remove(level, initial, 'right');
  const two = remove(level, one, 'middle');
  const invalid = [null, [], {}, 'JSON is parsed by the caller',
    { ...initial, remaining: ['left', 'middle'] },
    { ...initial, remaining: ['left', 'left', 'right'] },
    { ...initial, remaining: ['left', 'middle', 'unknown'] },
    { ...initial, remaining: [{}, 'middle', 'right'] },
    { ...initial, remaining: new Array(3) },
    { ...initial, moves: -1 }, { ...initial, moves: 0.5 }, { ...initial, moves: '0' },
    { ...initial, moves: Infinity }, { ...initial, moves: 4 },
    { ...initial, phase: 0 }, { ...initial, history: null },
    { ...one, history: [] }, { ...one, history: [null] }, { ...one, history: new Array(1) },
    { ...one, history: [{ remaining: initial.remaining, moves: 1 }] },
    { ...one, history: [{ remaining: initial.remaining, moves: 0, history: [] }] },
    // Counts look plausible, but the removed left arrow was blocked.
    { ...one, remaining: ['middle', 'right'] },
    { ...two, remaining: ['right'] }, // Reintroduces a previously removed ID.
    { ...two, history: [initial, one] }, // Nested history isn't the snapshot schema.
    { remaining: [], moves: 3, history: [
      { remaining: ['left', 'middle', 'right'], moves: 0 },
      { remaining: ['middle', 'right'], moves: 1 },
      { remaining: ['right'], moves: 2 }
    ] }
  ];
  for (let i = 0; i < invalid.length; i++) {
    const state = invalid[i];
    assert.throws(() => core.validateState(level, state), TypeError, `forged state ${i}`);
    assert.throws(() => core.solve(level, state), TypeError, `solver forged state ${i}`);
    assert.throws(() => core.transition(level, state, { type: 'undo' }), TypeError, `undo forged state ${i}`);
  }
  const otherLevel = clone(level);
  otherLevel.arrows[2].d = 3;
  assert.throws(() => core.validateState(otherLevel, one), /blocked arrow/);
});

test('validation does not invoke getters or execute action-like save data', () => {
  const level = chainFixture(), state = core.newState(level);
  let invoked = false;
  const accessor = { moves: 0, history: [] };
  Object.defineProperty(accessor, 'remaining', { get() { invoked = true; throw new Error('executed'); } });
  assert.throws(() => core.validateState(level, accessor), /accessors are not data/);
  const forged = { ...state, history: [() => { invoked = true; }] };
  assert.throws(() => core.validateState(level, forged), TypeError);
  const action = { type: 'run', execute() { invoked = true; } };
  assert.deepEqual(core.transition(level, state, action), state);
  const payload = JSON.parse('{"remaining":["left","middle","right"],"moves":0,"history":[],"__proto__":{"polluted":true}}');
  assert.throws(() => core.validateState(level, payload), /invalid fields/);
  assert.equal({}.polluted, undefined);
  assert.equal(invoked, false);
});

// Independent, small exhaustive oracle. It uses coordinate comparisons and subsets,
// not the dense core's ray helpers, dependency graph, or transition implementation.
function oracleClear(level, ids, id) {
  const a = level.arrows.find(candidate => candidate.id === id);
  const [dx, dy] = [[0, -1], [1, 0], [0, 1], [-1, 0]][a.d];
  let [x, y] = a.cells[a.cells.length - 1];
  for (;;) {
    x += dx; y += dy;
    if (x < 0 || x >= level.width || y < 0 || y >= level.height) return true;
    if (level.arrows.some(other => ids.includes(other.id) && other.cells.some(cell => cell[0] === x && cell[1] === y))) return false;
  }
}

function oracleSolvable(level) {
  const queue = [level.arrows.map(a => a.id)], seen = new Set();
  for (let i = 0; i < queue.length; i++) {
    const ids = queue[i];
    if (!ids.length) return true;
    for (const id of ids) if (oracleClear(level, ids, id)) {
      const next = ids.filter(other => other !== id), key = JSON.stringify(next);
      if (!seen.has(key)) { seen.add(key); queue.push(next); }
    }
  }
  return false;
}

test('greedy closure agrees with exhaustive search on 100 deterministic small boards', () => {
  let seed = 20771;
  const random = limit => { seed = (Math.imul(seed, 1664525) + 1013904223) >>> 0; return seed % limit; };
  let solved = 0, dead = 0;
  for (let trial = 0; trial < 100; trial++) {
    const mask = [], arrows = [];
    for (let y = 0; y < 3; y++) for (let x = 0; x < 3; x++) {
      if (random(5) === 0) continue;
      mask.push([x, y]);
      arrows.push(piece(`p${x}-${y}`, random(4), [[x, y]]));
    }
    if (!arrows.length) continue;
    const level = board(3, 3, arrows, mask), initial = core.newState(level);
    const result = core.solve(level, initial);
    assert.equal(result.solvable, oracleSolvable(level), `oracle trial ${trial}`);
    let ids = initial.remaining.slice();
    for (const wave of result.waves) {
      const allClear = ids.filter(id => oracleClear(level, ids, id));
      assert.deepEqual(wave, allClear, `wave trial ${trial}`);
      ids = ids.filter(id => !wave.includes(id));
    }
    assert.deepEqual(result.remainingBlocked, ids);
    if (result.solvable) {
      solved++;
      assert.deepEqual(replay(level, result.actions).remaining, []);
      // Any legal greedy choice preserves solvability, including reverse ID order.
      let state = initial;
      while (state.remaining.length) {
        const clear = state.remaining.filter(id => oracleClear(level, state.remaining, id));
        assert.ok(clear.length > 0);
        state = remove(level, state, clear[clear.length - 1]);
      }
    } else {
      dead++;
      assert.equal(result.actions, null);
    }
  }
  assert.ok(solved > 0 && dead > 0, `oracle coverage: ${solved} solved, ${dead} cycles`);
});

const densePath = path.resolve(__dirname, '../data/dense-levels.json');
test('published dense levels validate, solve and replay their stored witnesses', {
  skip: fs.existsSync(densePath) ? false : 'dense-levels.json is not available yet; generated fixtures above run independently'
}, () => {
  const data = JSON.parse(fs.readFileSync(densePath, 'utf8'));
  const levels = Array.isArray(data) ? data : data.levels;
  assert.ok(Array.isArray(levels) && levels.length > 0, 'dense pack must contain levels');
  for (const level of levels) {
    assert.equal(core.validateLevel(level, { requireConnectedMask: true }), true, level.id);
    const state = core.newState(level), result = core.solve(level, state);
    assert.equal(result.solvable, true, `${level.id}: no complete solution`);
    assert.equal(result.actions.length, level.arrows.length, level.id);
    assert.deepEqual(replay(level, result.actions).remaining, []);
    const witness = level.witness ?? level.solution;
    const entries = Array.isArray(witness) ? witness : witness?.actions;
    assert.ok(Array.isArray(entries), `${level.id}: missing stored witness`);
    const actions = entries.map(entry => typeof entry === 'object' && entry !== null ? entry : { type: 'remove', id: entry });
    assert.equal(actions.length, level.arrows.length, `${level.id}: incomplete stored witness`);
    const end = replay(level, actions);
    assert.deepEqual(end.remaining, [], `${level.id}: stored witness failed`);
    assert.equal(core.validateState(level, clone(end)), true);
  }
});
