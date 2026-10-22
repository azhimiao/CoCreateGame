/* Classic, non-phase snake rules. Independent of VectorShiftCore.
 * cells run tail -> head; d is 0=N, 1=E, 2=S, 3=W. All bodies block, including self.
 * Rays cross silhouette gaps and end at the full rectangular board boundary.
 * width/height override size independently; size is the square fallback.
 * Input levels are JSON data; validateLevel/validateState return true or throw.
 * State history contains {remaining, moves} snapshots BEFORE each legal remove.
 * moves counts current removals, so undo decrements it and reset clears it.
 */
(function (root, factory) {
  'use strict';
  const api = factory();
  if (typeof module === 'object' && module && module.exports) module.exports = api;
  if (typeof define === 'function' && define.amd) define([], function () { return api; });
  if (root) root.VectorShiftDenseCore = api;
})(typeof globalThis !== 'undefined' ? globalThis : typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  const DX = Object.freeze([0, 1, 0, -1]);
  const DY = Object.freeze([-1, 0, 1, 0]);
  const key = (x, y) => x + ',' + y;
  const validId = id => (typeof id === 'string' && id.trim().length > 0) || Number.isSafeInteger(id);
  const fail = message => { throw new TypeError(message); };

  function record(value, label) {
    if (!value || typeof value !== 'object' || Array.isArray(value)) fail(label + ': expected object');
  }

  // Read data properties only. No eval, action deserialization, or accessor calls.
  function own(value, name, label) {
    const descriptor = Object.getOwnPropertyDescriptor(value, name);
    if (!descriptor) return undefined;
    if (!Object.hasOwn(descriptor, 'value')) fail(label + ': accessors are not data');
    return descriptor.value;
  }

  function fields(value, names, label) {
    record(value, label);
    const keys = Reflect.ownKeys(value);
    if (keys.length !== names.length || keys.some(k => !names.includes(k))) fail(label + ': invalid fields');
    for (const name of names) own(value, name, label);
  }

  function array(value, maximum, label) {
    if (!Array.isArray(value) || value.length > maximum) fail(label + ': invalid array');
    for (let i = 0; i < value.length; i++) {
      const descriptor = Object.getOwnPropertyDescriptor(value, String(i));
      if (!descriptor || !Object.hasOwn(descriptor, 'value')) fail(label + ': sparse/accessor array');
    }
  }

  function dimension(value) {
    return Number.isInteger(value) && value >= 1 && value <= 64;
  }

  function cellKey(cell, width, height, label) {
    array(cell, 2, label);
    if (cell.length !== 2 || !Number.isInteger(cell[0]) || !Number.isInteger(cell[1]) ||
        cell[0] < 0 || cell[1] < 0 || cell[0] >= width || cell[1] >= height) fail(label + ': invalid cell');
    return key(cell[0], cell[1]);
  }

  function geometry(level) {
    const label = 'Invalid level';
    record(level, label);
    const size = own(level, 'size', label);
    const explicitWidth = own(level, 'width', label);
    const explicitHeight = own(level, 'height', label);
    const width = explicitWidth === undefined ? size : explicitWidth;
    const height = explicitHeight === undefined ? size : explicitHeight;
    if (!dimension(width) || !dimension(height) || (size !== undefined && !dimension(size))) {
      fail(label + ': dimensions must be integers in 1..64');
    }
    const mask = own(level, 'mask', label);
    const playable = new Set();
    if (mask !== undefined) {
      array(mask, width * height, label + ' mask');
      if (!mask.length) fail(label + ': empty mask');
      for (const cell of mask) {
        const k = cellKey(cell, width, height, label + ' mask');
        if (playable.has(k)) fail(label + ': duplicate mask cell');
        playable.add(k);
      }
    } else {
      for (let y = 0; y < height; y++) for (let x = 0; x < width; x++) playable.add(key(x, y));
    }
    return { width, height, playable };
  }

  // No mutable caches: editing a level, Set, or Map cannot poison later queries.
  function boardFor(level, options) {
    const board = geometry(level);
    const arrows = own(level, 'arrows', 'Invalid level');
    array(arrows, board.playable.size, 'Invalid level arrows');
    board.ids = [];
    board.byId = new Map();
    board.owners = new Map();
    for (const a of arrows) {
      record(a, 'Invalid level arrow');
      const id = own(a, 'id', 'Invalid level arrow');
      const d = own(a, 'd', 'Invalid level arrow');
      const cells = own(a, 'cells', 'Invalid level arrow');
      if (!validId(id) || board.byId.has(id)) fail('Invalid level: invalid/duplicate arrow ID');
      if (!Number.isInteger(d) || d < 0 || d > 3) fail('Invalid level: invalid direction');
      if (own(a, 'color', 'Invalid level arrow') !== 'gold') fail('Invalid level: classic arrows must be gold');
      array(cells, board.playable.size, 'Invalid level cells');
      if (!cells.length) fail('Invalid level: empty arrow');
      for (let i = 0; i < cells.length; i++) {
        const k = cellKey(cells[i], board.width, board.height, 'Invalid level body');
        if (!board.playable.has(k)) fail('Invalid level: body outside mask');
        if (board.owners.has(k)) fail('Invalid level: repeated/overlapping body cell');
        if (i && Math.abs(cells[i][0] - cells[i - 1][0]) + Math.abs(cells[i][1] - cells[i - 1][1]) !== 1) {
          fail('Invalid level: body must be ordered four-adjacent cells');
        }
        board.owners.set(k, id);
      }
      // A self-facing shape is valid data, but its own body prevents release.
      board.ids.push(id);
      board.byId.set(id, { id, d, cells });
    }
    if (options && options.requireConnectedMask) {
      const first = board.playable.values().next().value;
      const queue = [first];
      const seen = new Set(queue);
      for (let i = 0; i < queue.length; i++) {
        const [x, y] = queue[i].split(',').map(Number);
        for (let d = 0; d < 4; d++) {
          const k = key(x + DX[d], y + DY[d]);
          if (board.playable.has(k) && !seen.has(k)) { seen.add(k); queue.push(k); }
        }
      }
      if (seen.size !== board.playable.size) fail('Invalid level: disconnected mask');
    }
    return board;
  }

  function validateLevel(level, options) {
    boardFor(level, options); // Optional {requireConnectedMask:true}; single-cell arrows are valid.
    return true;
  }

  function playableSet(level) { return geometry(level).playable; }
  function isPlayable(level, x, y) { return playableSet(level).has(key(x, y)); }
  function maskCellCount(level) { return playableSet(level).size; }

  function headCell(a) {
    record(a, 'Invalid arrow');
    const cells = own(a, 'cells', 'Invalid arrow');
    array(cells, 4096, 'Invalid arrow cells');
    if (!cells.length) fail('Invalid arrow: empty body');
    const cell = cells[cells.length - 1];
    cellKey(cell, 64, 64, 'Invalid arrow head');
    return { x: cell[0], y: cell[1] };
  }

  function arrow(level, id) { return level.arrows.find(a => a.id === id); }

  function initialState(board) { return { remaining: board.ids.slice(), moves: 0, history: [] }; }
  function newState(level) { return initialState(boardFor(level)); }

  function ray(board, remaining, id, stopAtBlocker) {
    const a = board.byId.get(id);
    if (!a || !remaining.has(id)) return null;
    const head = a.cells[a.cells.length - 1];
    const cells = [], blocking = [], seen = new Set();
    let x = head[0] + DX[a.d], y = head[1] + DY[a.d];
    while (x >= 0 && y >= 0 && x < board.width && y < board.height) {
      cells.push([x, y]);
      const hit = board.owners.get(key(x, y));
      if (hit !== undefined && remaining.has(hit)) {
        if (!seen.has(hit)) { seen.add(hit); blocking.push(hit); }
        if (stopAtBlocker) break;
      }
      x += DX[a.d]; y += DY[a.d];
    }
    return { cells, blocking };
  }

  function snapshotIds(board, frame, moves) {
    if (!Number.isSafeInteger(frame.moves) || frame.moves !== moves) fail('Invalid state: incoherent moves');
    array(frame.remaining, board.ids.length, 'Invalid state remaining');
    if (frame.remaining.length !== board.ids.length - moves) fail('Invalid state: incoherent remaining count');
    const ids = new Set();
    for (const id of frame.remaining) {
      if (!validId(id) || !board.byId.has(id) || ids.has(id)) fail('Invalid state: invalid/duplicate remaining ID');
      ids.add(id);
    }
    return ids;
  }

  // Validate the entire undo chain from the full board. Reordered ID arrays are fine;
  // missing moves, skipped/blocked removals, resurrection, and forged clears are not.
  // Cost is linear in the supplied history size plus at most 64 ray cells per move.
  function checkedState(board, state) {
    fields(state, ['remaining', 'moves', 'history'], 'Invalid state');
    if (!Number.isSafeInteger(state.moves) || state.moves < 0 || state.moves > board.ids.length) {
      fail('Invalid state: moves out of range');
    }
    array(state.history, board.ids.length, 'Invalid state history');
    if (state.history.length !== state.moves) fail('Invalid state: moves/history mismatch');
    let previous = null;
    for (let i = 0; i <= state.moves; i++) {
      const frame = i === state.moves ? state : state.history[i];
      if (i < state.moves) fields(frame, ['remaining', 'moves'], 'Invalid state snapshot');
      const current = snapshotIds(board, frame, i);
      if (previous) {
        for (const id of current) if (!previous.has(id)) fail('Invalid state: history resurrects an arrow');
        // Counts and unique subsets above guarantee exactly one missing ID.
        let removed;
        for (const id of previous) if (!current.has(id)) { removed = id; break; }
        if (ray(board, previous, removed, true).blocking.length) fail('Invalid state: history removes a blocked arrow');
      }
      previous = current;
    }
    return previous;
  }

  function validateState(level, state) { checkedState(boardFor(level), state); return true; }

  function occupancyMap(level, state) {
    const board = boardFor(level), remaining = checkedState(board, state), result = new Map();
    for (const [cell, id] of board.owners) if (remaining.has(id)) result.set(cell, id);
    return result;
  }

  /** All blocking IDs, nearest first, across gaps to the outer board edge. */
  function blockers(level, state, id) {
    const board = boardFor(level), remaining = checkedState(board, state);
    const result = ray(board, remaining, id, false);
    return result ? result.blocking : null;
  }
  function clearPath(level, state, id) {
    const blocking = blockers(level, state, id);
    return blocking !== null && blocking.length === 0;
  }
  /** Cells AFTER the head, INCLUDING the first blocker and any silhouette gaps. */
  function exitRayCells(level, state, id) {
    const board = boardFor(level), remaining = checkedState(board, state);
    const result = ray(board, remaining, id, true);
    return result ? result.cells : [];
  }

  function copySnapshot(state) { return { remaining: state.remaining.slice(), moves: state.moves }; }
  function copyState(state) { return { ...copySnapshot(state), history: state.history.map(copySnapshot) }; }

  function transition(level, state, action) {
    const board = boardFor(level);
    const type = action && typeof action === 'object' ? own(action, 'type', 'Invalid action') : undefined;
    // Reset can also recover from a rejected saved state.
    if (type === 'reset') return initialState(board);
    const remaining = checkedState(board, state);
    const next = copyState(state);
    if (type === 'undo') {
      const previous = next.history.pop();
      if (previous) { next.remaining = previous.remaining; next.moves = previous.moves; }
    } else if (type === 'remove') {
      const id = own(action, 'id', 'Invalid action');
      const result = ray(board, remaining, id, true);
      if (result && !result.blocking.length) {
        next.history.push(copySnapshot(state));
        next.remaining = next.remaining.filter(value => value !== id);
        next.moves++;
      }
    }
    // Blocked/missing IDs and unsupported actions (including toggle) are pure no-ops.
    return next;
  }

  /** Monotonic dependency peeling, never subset BFS or a bit mask.
   * Build O(body cells + N*64) dependencies, then visit each edge once.
   * waves is an array of ID arrays: all IDs clear BEFORE that wave is removed.
   * IDs in each wave use level order, independent of serialized remaining order.
   * On a dead cycle actions=null; waves still describes any removable prefix,
   * and remainingBlocked lists the cycle plus everything depending on it.
   */
  function solve(level, state) {
    const board = boardFor(level), remaining = checkedState(board, state);
    const ids = board.ids.filter(id => remaining.has(id));
    const order = new Map(ids.map((id, index) => [id, index]));
    const dependents = new Map(ids.map(id => [id, []])), counts = new Map();
    for (const id of ids) {
      const blocking = ray(board, remaining, id, false).blocking;
      counts.set(id, blocking.length);
      for (const blocker of blocking) dependents.get(blocker).push(id);
    }
    let frontier = ids.filter(id => counts.get(id) === 0);
    const actions = [], waves = [];
    while (frontier.length) {
      waves.push(frontier);
      const next = [];
      for (const id of frontier) {
        remaining.delete(id);
        actions.push({ type: 'remove', id });
        for (const dependent of dependents.get(id)) {
          const count = counts.get(dependent) - 1;
          counts.set(dependent, count);
          if (count === 0) next.push(dependent);
        }
      }
      frontier = next.sort((a, b) => order.get(a) - order.get(b));
    }
    const remainingBlocked = ids.filter(id => remaining.has(id));
    const solvable = remainingBlocked.length === 0;
    return { actions: solvable ? actions : null, solvable, remainingBlocked, waves };
  }

  return Object.freeze({
    DX, DY, playableSet, isPlayable, maskCellCount, headCell, arrow, occupancyMap,
    blockers, clearPath, exitRayCells, newState, transition, solve, validateLevel, validateState
  });
});
