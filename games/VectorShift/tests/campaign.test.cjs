const test = require("node:test"),
  assert = require("node:assert/strict");
const C = require("../src/dense-core.js"),
  levels = require("../data/campaign-levels.json");
const clone = (x) => JSON.parse(JSON.stringify(x));
const fixture = (budget) => ({
  width: 5,
  height: 2,
  cutBudget: budget,
  arrows: [
    {
      id: "a",
      color: "gold",
      d: 1,
      cells: [
        [0, 0],
        [1, 0],
      ],
    },
    {
      id: "b",
      color: "gold",
      d: 0,
      cells: [
        [3, 1],
        [3, 0],
      ],
    },
  ],
});
test("120 distinct boards, complete no-skill solutions, sequential chapters and increasing workload", () => {
  assert.equal(levels.length, 120);
  assert.equal(new Set(levels.map((l) => l.canonicalGeometry)).size, 120);
  const means = [];
  for (let ch = 1; ch <= 10; ch++) {
    const group = levels.filter((l) => l.chapter === ch);
    assert.equal(group.length, 12);
    means.push(group.reduce((s, l) => s + l.workloadScore, 0) / 12);
  }
  for (let i = 1; i < means.length; i++) assert.ok(means[i] > means[i - 1]);
  let total = 0;
  for (const [i, l] of levels.entries()) {
    C.validateLevel(l, { requireConnectedMask: true });
    assert.equal(l.number, i + 1);
    assert.equal(l.cutBudget, +(i >= 5));
    if (l.breather) assert.ok(l.workloadScore < levels[i - 1].workloadScore);
    let s = C.newState(l);
    assert.equal(C.solve(l, s).solvable, true);
    for (const id of l.solution) {
      const n = C.transition(l, s, { type: "remove", id });
      assert.equal(n.moves, s.moves + 1, `${l.id}/${id}`);
      s = n;
      total++;
    }
    assert.deepEqual(s.remaining, []);
    assert.equal(s.cuts, 0);
    C.validateState(l, clone(s));
  }
  assert.equal(total, 3268);
});
test("scissors clear a blocked body once; normal moves retain strict collision; undo/reset restore budget", () => {
  const l = fixture(1),
    s = C.newState(l);
  assert.deepEqual(C.transition(l, s, { type: "remove", id: "a" }), s);
  const cut = C.transition(l, s, { type: "cut", id: "a" });
  assert.equal(cut.cuts, 1);
  assert.deepEqual(cut.remaining, ["b"]);
  assert.equal(C.validateState(l, clone(cut)), true);
  assert.deepEqual(C.transition(l, cut, { type: "cut", id: "b" }), cut);
  assert.deepEqual(C.transition(l, cut, { type: "undo" }), s);
  assert.deepEqual(C.transition(l, cut, { type: "reset" }), s);
  const done = C.transition(l, cut, { type: "remove", id: "b" });
  assert.equal(done.cuts, 1);
  assert.deepEqual(done.remaining, []);
  C.validateState(l, clone(done));
  assert.deepEqual(C.transition(l, done, { type: "undo" }), cut);
  assert.deepEqual(
    C.transition(fixture(0), C.newState(fixture(0)), { type: "cut", id: "a" }),
    C.newState(fixture(0)),
  );
  assert.equal(s.cuts, 0);
  assert.deepEqual(s.history, []);
});
test("forged scissors counts, dropped spend and blocked removals are rejected through the whole history", () => {
  const l = fixture(1),
    s = C.newState(l),
    cut = C.transition(l, s, { type: "cut", id: "a" });
  for (const v of [-1, 2, 0.5, "1", null, Infinity, NaN])
    assert.throws(() => C.validateState(l, { ...cut, cuts: v }));
  assert.throws(() => C.validateState(l, { ...cut, cuts: 0 }), /blocked/);
  const next = C.transition(l, cut, { type: "remove", id: "b" });
  next.cuts = 0;
  assert.throws(() => C.validateState(l, next), /cuts/);
  const corrupt = clone(cut);
  delete corrupt.history[0].cuts;
  assert.throws(() => C.validateState(l, corrupt));
  const bad = fixture(2);
  assert.throws(() => C.validateLevel(bad));
});
test("any one blocked snake may be snipped without making a published board unsolvable", () => {
  for (const l of levels.filter((l) => l.cutBudget)) {
    const s = C.newState(l);
    for (const id of s.remaining.filter((id) => C.blockers(l, s, id).length)) {
      const cut = C.transition(l, s, { type: "cut", id });
      assert.equal(cut.cuts, 1);
      assert.equal(C.solve(l, cut).solvable, true, `${l.id}/${id}`);
    }
  }
});
