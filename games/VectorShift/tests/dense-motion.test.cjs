const test = require("node:test");
const assert = require("node:assert/strict");
const M = require("../src/dense-motion.js"),
  C = require("../src/dense-core.js"),
  levels = require("../data/dense-levels.json");
const centers = (a) =>
  a.cells.map(([x, y]) => ({ x: 18 + (x + 0.5) * 32, y: 18 + (y + 0.5) * 32 }));
const piece = (id, cells, d) => ({ id, cells, d, color: "gold" });

test("crossing exit rays reserve space even when both static bodies are clear", () => {
  const l = {
      width: 7,
      height: 7,
      arrows: [
        piece(
          "right",
          [
            [0, 3],
            [1, 3],
          ],
          1,
        ),
        piece(
          "up",
          [
            [4, 6],
            [4, 5],
          ],
          0,
        ),
        piece(
          "safe",
          [
            [5, 0],
            [6, 0],
          ],
          1,
        ),
      ],
    },
    s = C.newState(l);
  for (const a of l.arrows) assert.equal(C.clearPath(l, s, a.id), true);
  assert.deepEqual(M.conflicts(l, "up", [{ kind: "exit", id: "right" }]), [
    "right",
  ]);
  assert.deepEqual(M.conflicts(l, "safe", [{ kind: "exit", id: "right" }]), []);
  assert.deepEqual(M.conflicts(l, "up", []), []);
});

test("all four exit directions keep the complete body initially and finish outside the Canvas", () => {
  for (let d = 0; d < 4; d++) {
    const [dx, dy] = [
      [0, -1],
      [1, 0],
      [0, 1],
      [-1, 0],
    ][d];
    const a = piece(
        "snake",
        [
          [3 - dx, 3 - dy],
          [3, 3],
        ],
        d,
      ),
      l = { width: 7, height: 7, arrows: [a] },
      points = centers(a),
      p = M.plan(l, a, points, 0, 32, 18, 25.92);
    assert.deepEqual(M.frame(p, 0).points, points);
    assert.equal(M.frame(p, p.duration).done, true);
    const f = M.frame(p, p.duration - 0.01),
      tail = f.tail;
    assert.ok(
      d === 0
        ? tail.y < -16
        : d === 1
          ? tail.x > 274
          : d === 2
            ? tail.y > 274
            : tail.x < -16,
    );
  }
});

test("a long route uses the same cruise speed, continuous acceleration and no end slowdown inside the board", () => {
  const l = { width: 24, height: 24, arrows: [] },
    a = piece(
      "snake",
      [
        [2, 2],
        [3, 2],
      ],
      1,
    ),
    short = M.plan(l, a, centers(a), 0, 32, 18, 25.92),
    long = M.plan(
      l,
      a,
      [{ x: 30, y: 650 }, { x: 30, y: 98 }, ...centers(a)],
      0,
      32,
      18,
      25.92,
    );
  assert.equal(short.speed, long.speed);
  assert.ok(long.duration > short.duration);
  assert.ok(M.advance(short, 0.1) < 0.001, "no initial velocity jump");
  const t = short.ramp;
  assert.ok(
    Math.abs(
      (M.advance(short, t + 0.01) - M.advance(short, t - 0.01)) / 0.02 -
        short.speed / 1000,
    ) < 0.001,
  );
  let previous = 0;
  for (let t = 0; t <= long.duration; t += 3) {
    const d = M.advance(long, t);
    assert.ok(d >= previous);
    previous = d;
  }
});

test("published witnesses never send a moving head through another live body, including across silhouette gaps", () => {
  for (const l of levels) {
    let state = C.newState(l);
    for (const id of l.solution) {
      const a = l.arrows.find((a) => a.id === id),
        occupied = C.occupancyMap(l, state),
        p = M.plan(l, a, centers(a), 0, 32, 18, 25.92),
        [dx, dy] = [
          [0, -1],
          [1, 0],
          [0, 1],
          [-1, 0],
        ][a.d],
        h = centers(a).at(-1);
      assert.equal(C.clearPath(l, state, id), true);
      // Independently sample the continuous straight head trajectory every 2 world pixels.
      for (let distance = 2; distance <= p.distance - p.length; distance += 2) {
        const x = Math.floor((h.x + dx * distance - 18) / 32),
          y = Math.floor((h.y + dy * distance - 18) / 32),
          owner = occupied.get(x + "," + y);
        assert.ok(
          owner === undefined || owner === id,
          `${l.id}/${id} hits ${owner} at ${x},${y}`,
        );
      }
      state = C.transition(l, state, { type: "remove", id });
    }
    assert.equal(state.remaining.length, 0);
  }
});
