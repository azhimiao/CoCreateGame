// Test the rendered alpha at each exit, not just the motion plan's coordinates.
const assert = require("node:assert/strict"),
  fs = require("node:fs"),
  path = require("node:path"),
  http = require("node:http"),
  { chromium } = require(process.env.PLAYWRIGHT_MODULE || "playwright"),
  M = require("../src/dense-motion.js");
const root = path.resolve(__dirname, ".."),
  out = path.join(root, "artifacts/clear-feedback"),
  html = fs.readFileSync(path.join(root, "index.html"), "utf8"),
  directions = [[0, -1], [1, 0], [0, 1], [-1, 0]],
  names = ["up", "right", "down", "left"];
function fixture(d) {
  const [dx, dy] = directions[d];
  return {
    id: "exit-" + d, title: "出口检查", titleEn: "Exit check",
    width: 7, height: 7, size: 7, shape: "rounded",
    mask: Array.from({ length: 49 }, (_, i) => [i % 7, Math.floor(i / 7)]),
    arrows: [
      { id: "target", cells: [[3 - 2 * dx, 3 - 2 * dy], [3 - dx, 3 - dy], [3, 3]], d, skin: 5, color: "gold" },
      { id: "other", cells: [[0, 0], [1, 0]], d: 1, skin: 2, color: "gold" },
    ],
  };
}
const server = http.createServer((req, res) => {
  const url = new URL(req.url, "http://local");
  res.writeHead(200, { "Content-Type": "text/html;charset=utf-8" });
  res.end(url.pathname === "/fixture"
    ? html.replace(/const DENSE_LEVELS=[^\n]+;/,
        "const DENSE_LEVELS=" + JSON.stringify([fixture(Number(url.searchParams.get("d")))]) + ";")
    : html);
});
async function render(page, elapsed) {
  await page.evaluate((elapsed) => {
    window.qaTime = 1000 + elapsed;
    VectorShiftDenseDebug.render(window.qaTime);
  }, elapsed);
}
async function tap(page, id) {
  const p = await page.evaluate((id) => VectorShiftDenseDebug.pointFor(id), id);
  await page.touchscreen.tap(p.x, p.y);
}
async function main() {
  fs.mkdirSync(out, { recursive: true });
  await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM_PATH || undefined }),
    base = "http://127.0.0.1:" + server.address().port,
    checks = [], errors = [];
  try {
    for (const [width, height] of [[390, 844], [844, 390]]) {
      const context = await browser.newContext({
        viewport: { width, height }, deviceScaleFactor: 2, hasTouch: true, isMobile: true,
      });
      await context.addInitScript(() => {
        window.qaTime = 1000;
        performance.now = () => window.qaTime;
        window.requestAnimationFrame = () => 1;
        window.cancelAnimationFrame = () => {};
      });
      const page = await context.newPage();
      page.on("pageerror", (e) => errors.push(e.message));
      for (let d = 0; d < 4; d++) {
        await page.goto(base + "/fixture?mode=samples&fresh&d=" + d);
        await page.evaluate(() => VectorShiftDenseDebug.setReduced(false));
        const l = fixture(d), a = l.arrows[0],
          points = a.cells.map(([x, y]) => ({ x: 18 + (x + 0.5) * 32, y: 18 + (y + 0.5) * 32 })),
          plan = M.plan(l, a, points, 0, 32, 18, 25.92);
        await tap(page, "target");
        assert.equal(await page.locator("#feedback").innerText(), "畅通，出发！");
        assert.equal(await page.evaluate(() => VectorShiftDenseDebug.getState().moves), 0);
        // Put the tail's centre just inside the screen while its body crosses the edge.
        const advance = plan.distance - (25.92 * 0.75 + 4) - 25.92 * 0.2,
          time = advance / plan.speed * 1000 + plan.ramp * 0.5;
        await render(page, time);
        const alpha = await page.evaluate((d) => {
          const debug = VectorShiftDenseDebug, display = debug.getDisplay(),
            canvas = document.querySelector("canvas"), rect = canvas.getBoundingClientRect(),
            p = debug.pointFor("target"), c = canvas.getContext("2d"),
            feather = Math.min(28, 32 * display.s * 0.5),
            offsets = [0.5 / display.dpr, feather * 0.25, feather * 0.5, feather * 0.75];
          return offsets.map((offset) => {
            let x = p.x - rect.left, y = p.y - rect.top;
            if (d === 0) y = offset;
            if (d === 1) x = display.w - offset;
            if (d === 2) y = display.h - offset;
            if (d === 3) x = offset;
            return c.getImageData(Math.floor(x * display.dpr), Math.floor(y * display.dpr), 1, 1).data[3];
          });
        }, d);
        assert.ok(alpha[0] < 32, "exit edge must be transparent: " + alpha);
        assert.ok(alpha[1] > alpha[0] && alpha[2] > alpha[1] && alpha[3] > alpha[2],
          "tail must dissolve continuously rather than terminate on a hard line: " + alpha);
        assert.equal(await page.evaluate(() => VectorShiftDenseDebug.getState().remaining.length), 2,
          "a feathered tail must still reserve its path until the motion completes");
        await page.screenshot({ path: path.join(out, `${width}-${names[d]}-tail.png`) });
        await render(page, plan.duration + 1);
        assert.equal(await page.evaluate(() => VectorShiftDenseDebug.getState().moves), 1);
        assert.equal(await page.locator("#remainingCount").innerText(), "1");
        assert.equal(await page.locator("#feedback.success").innerText(), "漂亮，清掉一条！");
        await render(page, plan.duration + 75);
        if (d === 2) {
          await page.evaluate(() => document.querySelector("#feedback").getAnimations()
            .forEach((animation) => { animation.currentTime = 200; animation.pause(); }));
          await page.screenshot({ path: path.join(out, `${width}-confirmed.png`) });
        }
        await render(page, plan.duration + 300);
        assert.deepEqual(await page.evaluate(() => VectorShiftDenseDebug.getAnimation()), []);
        await page.evaluate(() => VectorShiftDenseDebug.setReduced(true));
        assert.equal(await page.evaluate(() => document.querySelector("#feedback").getAnimations().length), 0);
        await tap(page, "other");
        assert.equal(await page.evaluate(() => VectorShiftDenseDebug.getState().remaining.length), 0);
        assert.deepEqual(await page.evaluate(() => VectorShiftDenseDebug.getAnimation()), []);
        await page.evaluate(() => localStorage.clear());
        checks.push({ viewport: [width, height], direction: names[d], edgeAlpha: alpha,
          completionOnlyFeedback: true, reducedMotion: true });
      }
      await context.close();
    }
    // Real clock, real touch, shipping level and an unedited transition recording.
    const live = await browser.newContext({
      viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, hasTouch: true, isMobile: true,
      recordVideo: { dir: path.join(root, "runtime/clear-video"), size: { width: 390, height: 844 } },
    }), page = await live.newPage();
    page.on("pageerror", (e) => errors.push(e.message));
    await page.goto(base + "/?mode=journey");
    await page.screenshot({ path: path.join(out, "journey-before.png") });
    while ((await page.evaluate(() => VectorShiftDenseDebug.getState().remaining.length)) > 0) {
      const id = await page.evaluate(() => VectorShiftDenseDebug.getSolution().actions[0].id);
      await tap(page, id);
      await page.waitForFunction(() => !VectorShiftDenseDebug.getAnimation().some((a) => a.kind === "exit"));
      await page.waitForTimeout(320);
    }
    await page.locator("#nextPattern").waitFor();
    const video = page.video();
    await live.close();
    await video.saveAs(path.join(out, "journey-clear.webm"));
    await video.delete();
    assert.deepEqual(errors, []);
    fs.writeFileSync(path.join(out, "report.json"), JSON.stringify({
      date: "2026-10-22", checks, liveJourneyLevel: 1, errors,
      method: "Controlled-clock real-touch tail frames and Canvas alpha readback at all four exits, portrait/landscape. Real-clock touch recording on shipping journey level 1.",
      limits: "Desktop Chromium mobile emulation; no physical-phone or subjective satisfaction claim.",
    }, null, 2) + "\n");
    console.log(JSON.stringify({ checks, liveJourneyLevel: 1, errors }, null, 2));
  } finally {
    await browser.close();
    server.close();
  }
}
main().catch((e) => { console.error(e); server.close(); process.exitCode = 1; });
