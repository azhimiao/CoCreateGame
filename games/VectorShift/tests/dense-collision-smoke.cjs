// Regression for visual blocking and in-flight occupancy. A controlled clock
// samples the real renderer while all gameplay activation uses real pointer taps.
const assert = require("node:assert/strict"),
  fs = require("node:fs"),
  path = require("node:path"),
  http = require("node:http");
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || "playwright");
const root = path.resolve(__dirname, ".."),
  out = path.join(root, "artifacts/motion-fix"),
  html = fs.readFileSync(path.join(root, "dist/demo/index.html"), "utf8");
const C = require("../src/dense-core.js"),
  M = require("../src/dense-motion.js"),
  levels = require("../data/dense-levels.json");
const snake = (id, cells, d, skin) => ({ id, cells, d, skin, color: "gold" });
const fixture = (id, arrows, holes = []) => ({
  id,
  title: "路径检查",
  titleEn: "Path check",
  width: 7,
  height: 7,
  size: 7,
  shape: "rounded",
  arrows,
  mask: Array.from({ length: 49 }, (_, i) => [i % 7, Math.floor(i / 7)]).filter(
    (c) => !holes.some((h) => h[0] === c[0] && h[1] === c[1]),
  ),
});
const gap = fixture(
  "gap",
  [
    snake(
      "a",
      [
        [0, 3],
        [1, 3],
      ],
      1,
      0,
    ),
    snake(
      "b",
      [
        [5, 4],
        [5, 3],
      ],
      0,
      3,
    ),
    snake(
      "safe",
      [
        [6, 5],
        [6, 6],
      ],
      2,
      2,
    ),
  ],
  [[3, 3]],
);
const crossing = fixture("crossing", [
  snake(
    "a",
    [
      [0, 3],
      [1, 3],
    ],
    1,
    0,
  ),
  snake(
    "b",
    [
      [4, 6],
      [4, 5],
    ],
    0,
    3,
  ),
  snake(
    "safe",
    [
      [5, 0],
      [6, 0],
    ],
    1,
    2,
  ),
]);
const server = http.createServer((req, res) => {
  const name = new URL(req.url, "http://local").pathname;
  const data =
    name === "/gap" ? [gap] : name === "/crossing" ? [crossing] : levels;
  res.writeHead(200, { "content-type": "text/html;charset=utf-8" });
  res.end(
    html.replace(
      /const DENSE_LEVELS=[^\n]+;/,
      "const DENSE_LEVELS=" + JSON.stringify(data) + ";",
    ),
  );
});
const state = (p) => p.evaluate(() => VectorShiftDenseDebug.getState());
async function tap(p, id) {
  const point = await p.evaluate(
    (id) => VectorShiftDenseDebug.pointFor(id),
    id,
  );
  await p.mouse.click(point.x, point.y);
}
async function step(p, ms) {
  await p.evaluate((ms) => {
    window.qaTime += ms;
    VectorShiftDenseDebug.render(window.qaTime);
  }, ms);
}
async function button(p, id) {
  const box = await p.locator("#" + id).boundingBox();
  await p.mouse.click(box.x + box.width / 2, box.y + box.height / 2);
}
async function main() {
  fs.mkdirSync(out, { recursive: true });
  await new Promise((r) => server.listen(0, "127.0.0.1", r));
  const base = `http://127.0.0.1:${server.address().port}`;
  const browser = await chromium.launch({
    executablePath: process.env.CHROMIUM_PATH || undefined,
  });
  const errors = [],
    checks = [];
  try {
    const context = await browser.newContext({
      viewport: { width: 390, height: 844 },
      deviceScaleFactor: 2,
    });
    await context.addInitScript(() => {
      window.qaTime = 1000;
      performance.now = () => window.qaTime;
      window.requestAnimationFrame = () => 1;
      window.cancelAnimationFrame = () => {};
    });
    const p = await context.newPage();
    p.on("pageerror", (e) => errors.push(e.message));
    await p.goto(base + "/gap?mode=samples");
    const initial = await state(p);
    await tap(p, "a");
    assert.deepEqual(await state(p), initial);
    assert.equal(
      await p.evaluate(
        () =>
          VectorShiftDenseDebug.getAnimation().filter((a) => a.kind === "exit")
            .length,
      ),
      0,
    );
    await p.screenshot({ path: path.join(out, "gap-blocked.png") });
    await step(p, 700);
    await tap(p, "b");
    assert.deepEqual(
      await state(p),
      initial,
      "start of movement must retain occupancy",
    );
    await tap(p, "a");
    assert.equal(
      await p.evaluate(
        () =>
          VectorShiftDenseDebug.getAnimation().filter((a) => a.kind === "exit")
            .length,
      ),
      1,
      "blocked dependent must not join moving snake",
    );
    await tap(p, "b");
    assert.equal(
      await p.evaluate(
        () =>
          VectorShiftDenseDebug.getAnimation().filter((a) => a.kind === "exit")
            .length,
      ),
      1,
      "duplicate press cannot launch twice",
    );
    await tap(p, "safe");
    assert.equal(
      await p.evaluate(
        () =>
          VectorShiftDenseDebug.getAnimation().filter((a) => a.kind === "exit")
            .length,
      ),
      2,
      "independent route should remain responsive",
    );
    await button(p, "undoButton");
    assert.deepEqual(await state(p), initial);
    assert.equal(
      await p.evaluate(
        () =>
          VectorShiftDenseDebug.getAnimation().filter((a) => a.kind === "exit")
            .length,
      ),
      1,
      "undo cancels newest pending flight",
    );
    await step(p, 250);
    await tap(p, "a");
    assert.ok((await state(p)).remaining.includes("a"));
    await p.screenshot({ path: path.join(out, "moving-blocker.png") });
    await p.reload();
    assert.deepEqual(
      await state(p),
      initial,
      "refresh does not save a half-finished release as a completed move",
    );
    await tap(p, "b");
    await step(p, 3000);
    assert.equal((await state(p)).moves, 1);
    await tap(p, "a");
    await step(p, 3000);
    assert.equal((await state(p)).moves, 2);
    await button(p, "undoButton");
    assert.equal((await state(p)).moves, 1);
    checks.push(
      "gap blocker, in-flight body retained, duplicate click, independent concurrency, cancel pending, reload and completed undo",
    );

    await p.goto(base + "/crossing?mode=samples");
    assert.ok(
      C.clearPath(crossing, C.newState(crossing), "a") &&
        C.clearPath(crossing, C.newState(crossing), "b"),
    );
    await tap(p, "a");
    await tap(p, "b");
    assert.equal(
      await p.evaluate(
        () =>
          VectorShiftDenseDebug.getAnimation().filter((a) => a.kind === "exit")
            .length,
      ),
      1,
      "crossing trajectories must serialize",
    );
    await tap(p, "safe");
    assert.equal(
      await p.evaluate(
        () =>
          VectorShiftDenseDebug.getAnimation().filter((a) => a.kind === "exit")
            .length,
      ),
      2,
    );
    await step(p, 3000);
    await tap(p, "b");
    await step(p, 3000);
    await p.locator("#nextPattern").waitFor({ state: "attached" });
    checks.push(
      "two clear but crossing exit rays cannot intersect in flight; win waits for last tail",
    );

    await p.goto(base + "/?mode=samples");
    await tap(p, "s01");
    const duration = await p.evaluate(
      () => VectorShiftDenseDebug.getAnimation()[0].duration,
    );
    for (const [i, t] of [0, 0.12, 0.35, 0.65, 0.9, 1.01].entries()) {
      await p.evaluate(
        ({ time, t, duration }) => {
          window.qaTime = time + duration * t;
          VectorShiftDenseDebug.render(window.qaTime);
        },
        { time: 1000, t, duration },
      );
      await p.screenshot({ path: path.join(out, `smooth-frame-${i}.png`) });
    }
    assert.equal((await state(p)).moves, 1);
    await tap(p, "s23");
    await p.evaluate(() => VectorShiftDenseDebug.setReduced(true));
    assert.equal((await state(p)).moves, 2);
    assert.equal(
      await p.evaluate(
        () =>
          VectorShiftDenseDebug.getAnimation().filter((a) => a.kind === "exit")
            .length,
      ),
      0,
    );
    checks.push(
      "six real rendered frames, full tail completion and reduced-motion change settles safely",
    );
    await context.close();

    // Live-clock sweep: all 128 paths, holding dependent paths until visually clear.
    const live = await browser.newContext({
        viewport: { width: 390, height: 844 },
      }),
      q = await live.newPage();
    q.on("pageerror", (e) => errors.push(e.message));
    await q.goto(base + "/?mode=samples");
    const timings = [];
    for (let i = 0; i < levels.length; i++) {
      await q.evaluate((n) => VectorShiftDenseDebug.setLevel(n), i + 1);
      await q.evaluate(() => {
        window.qaIntervals = [];
        let last = performance.now();
        window.qaRunning = true;
        function frame(now) {
          if (last) qaIntervals.push(now - last);
          last = now;
          if (qaRunning) requestAnimationFrame(frame);
        }
        requestAnimationFrame(frame);
      });
      let guard = 0;
      while ((await state(q)).remaining.length) {
        if (++guard > 300) throw Error("Unfinished animation sweep");
        const ids = await q.evaluate(() =>
          VectorShiftDenseDebug.getLaunchable(),
        );
        if (ids.length) await tap(q, ids[0]);
        else await q.waitForTimeout(50);
      }
      const intervals = await q.evaluate(() => {
        qaRunning = false;
        return qaIntervals;
      });
      intervals.sort((a, b) => a - b);
      timings.push({
        level: levels[i].id,
        frames: intervals.length,
        medianMs: intervals[Math.floor(intervals.length * 0.5)],
        p95Ms: intervals[Math.floor(intervals.length * 0.95)],
        maxMs: Math.max(...intervals),
      });
      await q.locator("#nextPattern").waitFor();
      await q.keyboard.press("Escape");
    }
    checks.push(
      "all five boards / 128 real taps completed with default motion and runtime reservations",
    );
    await live.close();
    assert.deepEqual(errors, []);
    fs.writeFileSync(
      path.join(out, "report.json"),
      JSON.stringify(
        {
          date: "2026-10-22",
          checks,
          timings,
          errors,
          limits:
            "Chromium on this computer, not physical-device or comparative frame-rate proof. Controlled clock used only for deterministic collision/frame regression; timing sweep uses live clock.",
        },
        null,
        2,
      ) + "\n",
    );
    console.log(JSON.stringify({ checks, timings, errors }, null, 2));
  } finally {
    await browser.close();
    server.close();
  }
}
main().catch((e) => {
  console.error(e);
  server.close();
  process.exitCode = 1;
});
