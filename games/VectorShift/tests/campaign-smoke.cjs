const assert = require("node:assert/strict"),
  fs = require("node:fs"),
  path = require("node:path"),
  http = require("node:http");
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || "playwright");
const root = path.resolve(__dirname, ".."),
  out = path.join(root, "artifacts/campaign");
fs.mkdirSync(out, { recursive: true });
const server = http.createServer((req, res) => {
  const url = new URL(req.url, "http://local"),
    channel = url.pathname.startsWith("/coolmath")
      ? "coolmath"
      : url.pathname.startsWith("/crazygames")
        ? "crazygames-basic"
        : "demo";
  res.writeHead(200, { "Content-Type": "text/html;charset=utf-8" });
  res.end(fs.readFileSync(path.join(root, "dist", channel, "index.html")));
});
const state = (p) => p.evaluate(() => VectorShiftDenseDebug.getState());
async function tap(p, id) {
  const point = await p.evaluate(
    (id) => VectorShiftDenseDebug.pointFor(id),
    id,
  );
  await p.mouse.click(point.x, point.y);
}
async function solve(p) {
  const ids = await p.evaluate(() =>
    VectorShiftDenseDebug.getSolution().actions.map((a) => a.id),
  );
  for (const id of ids) await tap(p, id);
  await p.locator("#nextPattern").waitFor();
}
async function layout(p, w, h) {
  await p.setViewportSize({ width: w, height: h });
  await p.waitForTimeout(70);
  const boxes = await p.evaluate(() => ({
    width: innerWidth,
    scroll: document.documentElement.scrollWidth,
    footer: document
      .querySelector(".game-footer")
      .getBoundingClientRect()
      .toJSON(),
    buttons: [
      ...document.querySelectorAll(
        ".game-controls button,.game-top button,#zoomButton",
      ),
    ]
      .filter((b) => !b.hidden)
      .map((b) => b.getBoundingClientRect().toJSON()),
  }));
  assert.ok(boxes.scroll <= w);
  assert.ok(boxes.footer.bottom <= h + 1);
  for (const b of boxes.buttons)
    assert.ok(
      b.width >= 40 && b.height >= 40 && b.x >= 0 && b.right <= w + 1,
      JSON.stringify(boxes),
    );
  await p.screenshot({ path: path.join(out, `layout-${w}x${h}.png`) });
}
async function main() {
  await new Promise((r) => server.listen(0, "127.0.0.1", r));
  const base = `http://127.0.0.1:${server.address().port}`;
  const browser = await chromium.launch({
    executablePath: process.env.CHROMIUM_PATH || undefined,
  });
  const errors = [],
    checks = [];
  let count = 0;
  try {
    const ctx = await browser.newContext({
        viewport: { width: 390, height: 844 },
        deviceScaleFactor: 2,
      }),
      p = await ctx.newPage();
    p.on("pageerror", (e) => errors.push(e.message));
    await p.goto(base + "/?mode=journey");
    assert.equal(
      await p.evaluate(() => VectorShiftDenseDebug.levels.length),
      120,
    );
    assert.equal(
      await p.evaluate(() => VectorShiftDenseDebug.getProgress().unlocked),
      1,
    );
    assert.equal((await state(p)).remaining.length, 4);
    assert.ok(await p.locator("#cutButton").isDisabled());
    for (const [w, h] of [
      [360, 800],
      [390, 844],
      [412, 915],
      [320, 568],
      [844, 390],
      [1440, 1000],
    ])
      await layout(p, w, h);
    await p.setViewportSize({ width: 390, height: 844 });
    await p.locator("#collectionButton").click();
    assert.equal(await p.locator("[data-level]").count(), 12);
    assert.equal(await p.locator("[data-level]:disabled").count(), 11);
    await p.screenshot({ path: path.join(out, "chapter-01.png") });
    await p.locator("#nextChapter").click();
    assert.equal(await p.locator("[data-level]:disabled").count(), 12);
    await p.keyboard.press("Escape");
    checks.push(
      "120 levels, initial locking, 12-item chapter pagination, six viewport layouts",
    );
    // Exercise actual forward progression and reload, including the skill introduction.
    await p.evaluate(() => VectorShiftDenseDebug.setReduced(true));
    for (let n = 1; n <= 5; n++) {
      await solve(p);
      assert.equal(
        await p.evaluate(() => VectorShiftDenseDebug.getProgress().unlocked),
        n + 1,
      );
      await p.locator("#nextPattern").click();
    }
    assert.equal(
      await p.evaluate(() => VectorShiftDenseDebug.getLevel().number),
      6,
    );
    assert.ok(await p.locator("#cutButton").isEnabled());
    await p.reload();
    assert.equal(
      await p.evaluate(() => VectorShiftDenseDebug.getLevel().number),
      6,
    );
    let id = await p.evaluate(() => {
      const d = VectorShiftDenseDebug,
        s = d.getState(),
        l = d.getLevel();
      return s.remaining.find(
        (id) => VectorShiftDenseCore.blockers(l, s, id).length,
      );
    });
    const before = await state(p);
    await p.locator("#cutButton").click();
    await tap(p, id);
    assert.ok(await p.locator("#confirmCut").isVisible());
    await p.locator("#cancelCut").click();
    assert.deepEqual(await state(p), before);
    await p.locator("#cutButton").click();
    await tap(p, id);
    await p.locator("#confirmCut").click();
    assert.equal((await state(p)).cuts, 1);
    assert.equal(
      (await state(p)).remaining.length,
      before.remaining.length - 1,
    );
    assert.ok(await p.locator("#cutButton").isDisabled());
    await p.reload();
    assert.equal((await state(p)).cuts, 1);
    await p.locator("#undoButton").click();
    assert.deepEqual(await state(p), before);
    assert.ok(await p.locator("#cutButton").isEnabled());
    // Real timed cut: body stays in the rule state until its own fade completes.
    await p.evaluate(() => VectorShiftDenseDebug.setReduced(false));
    await p.locator("#cutButton").click();
    await tap(p, id);
    await p.locator("#confirmCut").click();
    assert.equal((await state(p)).cuts, 0);
    await p.screenshot({ path: path.join(out, "scissors-moving.png") });
    await p.waitForFunction(() => VectorShiftDenseDebug.getState().cuts === 1);
    await p.locator("#undoButton").click();
    assert.equal((await state(p)).cuts, 0);
    // Undo a pending cut and refresh: no spend and no missing snake.
    await p.locator("#cutButton").click();
    await tap(p, id);
    await p.locator("#confirmCut").click();
    await p.locator("#undoButton").click();
    await p.reload();
    assert.equal((await state(p)).cuts, 0);
    assert.equal((await state(p)).remaining.length, before.remaining.length);
    await p.locator("#cutButton").click();
    await tap(p, id);
    await p.screenshot({ path: path.join(out, "scissors-confirm.png") });
    await p.keyboard.press("Escape");
    await p.evaluate(() => VectorShiftDenseDebug.setReduced(true));
    await solve(p);
    assert.equal(
      await p.evaluate(
        () =>
          VectorShiftDenseDebug.getProgress().completed["journey-006"].stars,
      ),
      3,
    );
    await p.locator("#playAgain").click();
    await p.locator("#hintButton").click();
    await solve(p);
    assert.equal(
      await p.evaluate(
        () =>
          VectorShiftDenseDebug.getProgress().completed["journey-006"].stars,
      ),
      3,
    );
    await p.locator("#playAgain").click();
    await p.locator("#cutButton").click();
    await tap(p, id);
    await p.locator("#confirmCut").click();
    await solve(p);
    assert.equal(
      await p.locator(".win-stars").getAttribute("aria-label"),
      "1 stars",
    );
    await p.keyboard.press("Escape");
    checks.push(
      "real progression to level 6, locking/next/reload, scissors cancel/confirm/fade/undo/pending undo/persistence, best stars never downgrade",
    );
    // Gallery remains independently selectable and keeps its non-skill collision rules.
    await p.locator("#collectionButton").click();
    await p.locator('[data-mode="samples"]').click();
    assert.equal(await p.locator("[data-level]").count(), 5);
    await p.locator('[data-level="1"]').click();
    assert.equal(
      await p.evaluate(() => VectorShiftDenseDebug.getLevel().id),
      "dense-02",
    );
    assert.ok(await p.locator("#cutButton").isHidden());
    await p.locator("#collectionButton").click();
    await p.locator('[data-mode="journey"]').click();
    await p.keyboard.press("Escape");
    checks.push("gallery/campaign mode switch and independent old board state");
    // All 120 through actual head pointer taps. Reduced motion isolates hit/flow coverage.
    await p.evaluate(() => VectorShiftDenseDebug.setReduced(true));
    for (let n = 1; n <= 120; n++) {
      await p.evaluate((n) => VectorShiftDenseDebug.setLevel(n), n);
      const length = (await state(p)).remaining.length;
      await solve(p);
      count += length;
      assert.equal((await state(p)).cuts, 0);
      assert.equal((await state(p)).remaining.length, 0);
      if ([1, 12, 36, 60, 84, 108, 120].includes(n))
        await p.screenshot({
          path: path.join(out, `win-${String(n).padStart(3, "0")}.png`),
        });
      await p.keyboard.press("Escape");
      if (n % 12 === 0)
        console.log(`Pointer replay: ${n}/120 (${count} snakes)`);
    }
    assert.equal(count, 3268);
    assert.equal(
      await p.evaluate(() => VectorShiftDenseDebug.getProgress().unlocked),
      120,
    );
    await p.reload();
    assert.equal(
      await p.evaluate(
        () =>
          Object.keys(VectorShiftDenseDebug.getProgress().completed).filter(
            (k) => k.startsWith("journey"),
          ).length,
      ),
      120,
    );
    await p.locator("#collectionButton").click();
    assert.equal(await p.locator("[data-level]:disabled").count(), 0);
    await p.screenshot({ path: path.join(out, "chapter-10-cleared.png") });
    await p.keyboard.press("Escape");
    checks.push(
      "all 120 boards / 3268 real head taps without skills; complete journey persisted",
    );
    // Representative live animation in every chapter plus 56-snake final board.
    await p.evaluate(() => VectorShiftDenseDebug.setReduced(false));
    const normal = [];
    for (const n of [12, 60, 108, 120]) {
      await p.evaluate((n) => VectorShiftDenseDebug.setLevel(n), n);
      await p.evaluate(() => document.activeElement?.blur());
      await p.screenshot({
        path: path.join(out, `board-${String(n).padStart(3, "0")}.png`),
      });
      const started = Date.now();
      let guard = 0;
      while ((await state(p)).remaining.length) {
        if (++guard > 600) throw Error("Normal motion stalled " + n);
        const launchable = await p.evaluate(() =>
          VectorShiftDenseDebug.getLaunchable(),
        );
        if (launchable.length) await tap(p, launchable[0]);
        else await p.waitForTimeout(50);
      }
      await p.locator("#nextPattern").waitFor();
      await p.keyboard.press("Escape");
      normal.push({ level: n, ms: Date.now() - started });
      console.log(`Normal motion complete: ${n}`);
    }
    checks.push(
      "default-motion complete boards at levels 12, 60, 108 and 120, including the final large board",
    );
    // English candidate builds, public UI only (no debug hooks).
    for (const channel of ["coolmath", "crazygames"]) {
      const c = await browser.newContext(),
        q = await c.newPage();
      q.on("pageerror", (e) => errors.push(e.message));
      await q.route("**/crazygames-sdk-v3.js", (r) =>
        r.fulfill({
          body: "window.CrazyGames={SDK:{init:async()=>{},game:{gameplayStart:()=>{}}}}",
        }),
      );
      await q.goto(base + "/" + channel + "/");
      assert.equal(await q.locator("html").getAttribute("lang"), "en");
      assert.equal(
        await q.evaluate(() => typeof window.VectorShiftDenseDebug),
        "undefined",
      );
      await q.locator("#collectionButton").click();
      assert.equal(await q.locator("[data-level]").count(), 12);
      await q.screenshot({ path: path.join(out, channel + "-english.png") });
      await c.close();
    }
    const bad = await browser.newContext();
    await bad.addInitScript(() =>
      localStorage.setItem(
        "vector-shift-dense-v1",
        JSON.stringify({
          version: 2,
          mode: "journey",
          index: 119,
          completed: { "journey-001": "bad" },
          runs: {
            "journey-001": {
              state: { remaining: [], moves: 999, cuts: -3, history: [] },
            },
          },
        }),
      ),
    );
    const q = await bad.newPage();
    q.on("pageerror", (e) => errors.push(e.message));
    await q.goto(base);
    assert.equal(
      await q.evaluate(() => VectorShiftDenseDebug.getProgress().unlocked),
      1,
    );
    assert.equal((await state(q)).remaining.length, 4);
    await bad.close();
    checks.push(
      "English public builds without debug, corrupted campaign save recovery",
    );
    const legacy = await browser.newContext();
    await legacy.addInitScript(() =>
      localStorage.setItem(
        "vector-shift-dense-v1",
        JSON.stringify({
          version: 1,
          index: 1,
          runs: {
            "dense-02": {
              state: { remaining: ["s01"], moves: 999, history: [] },
            },
          },
        }),
      ),
    );
    const oldPage = await legacy.newPage();
    oldPage.on("pageerror", (e) => errors.push(e.message));
    await oldPage.goto(base);
    assert.equal(
      await oldPage.evaluate(() => VectorShiftDenseDebug.getLevel().id),
      "dense-02",
    );
    assert.equal((await state(oldPage)).remaining.length, 32);
    await legacy.close();
    checks.push(
      "legacy five-board save stays in the gallery and illegal old-rule histories recover",
    );
    assert.deepEqual(errors, []);
    fs.writeFileSync(
      path.join(out, "browser-report.json"),
      JSON.stringify(
        {
          date: "2026-10-22",
          checks,
          realPointerTaps: count,
          normalMotion: normal,
          errors,
          limits:
            "Local Chromium and emulated viewports; physical-device and human difficulty calibration pending.",
        },
        null,
        2,
      ) + "\n",
    );
    await ctx.close();
    console.log("PASS campaign browser checks");
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
