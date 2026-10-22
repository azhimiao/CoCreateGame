// Exercise the real Canvas/pointer UI, including every authored dense-board solution.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const http = require("node:http");
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || "playwright");
const root = path.resolve(__dirname, "..");
const output = path.join(root, "artifacts");
const core = require("../src/dense-core.js");
const levels = require("../data/dense-levels.json");
const errors = [],
  checks = [];
const server = http.createServer((req, res) => {
  const pathname = new URL(req.url, "http://localhost").pathname;
  const channel = pathname.startsWith("/coolmath/")
    ? "coolmath"
    : pathname.startsWith("/crazygames/")
      ? "crazygames-basic"
      : "demo";
  res.writeHead(200, { "content-type": "text/html; charset=utf-8" });
  res.end(
    fs.readFileSync(
      path.join(
        root,
        "dist",
        channel,
        pathname.endsWith("phase.html") ? "phase.html" : "index.html",
      ),
    ),
  );
});
const state = (p) => p.evaluate(() => VectorShiftDenseDebug.getState());
async function tap(p, id, body = false) {
  const point = await p.evaluate(
    ({ id, body }) =>
      VectorShiftDenseDebug[body ? "bodyPointFor" : "pointFor"](id),
    { id, body },
  );
  await p.mouse.click(point.x, point.y);
}
async function layout(p, size) {
  await p.setViewportSize(size);
  const boxes = await p.evaluate(() => ({
    scroll: document.documentElement.scrollWidth,
    width: innerWidth,
    canvas: document
      .querySelector("canvas#puzzleCanvas")
      .getBoundingClientRect()
      .toJSON(),
    controls: [
      ...document.querySelectorAll(".game-controls button,.game-top button"),
    ].map((b) => b.getBoundingClientRect().toJSON()),
    footer: document
      .querySelector(".game-footer")
      .getBoundingClientRect()
      .toJSON(),
  }));
  assert.ok(boxes.scroll <= boxes.width, JSON.stringify(boxes));
  assert.ok(
    boxes.canvas.width > 80 && boxes.canvas.height > 160,
    JSON.stringify(boxes),
  );
  assert.ok(boxes.footer.bottom <= size.height + 1, JSON.stringify(boxes));
  for (const b of boxes.controls)
    assert.ok(
      b.width >= 40 && b.height >= 40 && b.x >= 0 && b.right <= size.width + 1,
      JSON.stringify(boxes),
    );
  await p.screenshot({
    path: path.join(output, `dense-${size.width}x${size.height}.png`),
  });
  checks.push(`layout ${size.width}x${size.height}`);
}
async function main() {
  fs.mkdirSync(output, { recursive: true });
  await new Promise((r) => server.listen(0, "127.0.0.1", r));
  const base = `http://127.0.0.1:${server.address().port}`;
  const browser = await chromium.launch({
    headless: true,
    executablePath: process.env.CHROMIUM_PATH || undefined,
  });
  try {
    const context = await browser.newContext({
      viewport: { width: 390, height: 844 },
      deviceScaleFactor: 2,
    });
    const p = await context.newPage();
    p.on("pageerror", (e) => errors.push(e.message));
    await p.goto(base);
    await p.waitForFunction(() => !!window.VectorShiftDenseDebug);
    const first = await state(p);
    assert.equal(first.remaining.length, 28);
    const display = await p.evaluate(() => ({
      ...VectorShiftDenseDebug.getDisplay(),
      rect: document
        .querySelector("#puzzleCanvas")
        .getBoundingClientRect()
        .toJSON(),
      viewport: { width: innerWidth, height: innerHeight },
    }));
    assert.ok(display.bodyWidthCss >= 15 && display.bodyWidthCss <= 19);
    for (const size of [
      { width: 390, height: 844 },
      { width: 360, height: 800 },
      { width: 412, height: 915 },
      { width: 320, height: 568 },
      { width: 844, height: 390 },
      { width: 1440, height: 1000 },
    ])
      await layout(p, size);
    await p.setViewportSize({ width: 390, height: 844 });

    // A blocked tap preserves pieces/history; its feedback, counter and retry work.
    const blocked = levels[0].arrows.find(
      (a) => !core.clearPath(levels[0], first, a.id),
    ).id;
    await tap(p, blocked, true);
    assert.deepEqual(await state(p), first);
    assert.equal(
      await p.evaluate(() => VectorShiftDenseDebug.getStats().mistakes),
      1,
    );
    await p.screenshot({ path: path.join(output, "dense-blocked.png") });
    await p.locator("#hintButton").click();
    assert.equal(
      await p.evaluate(() => VectorShiftDenseDebug.getStats().hints),
      1,
    );
    await p.locator("#restartButton").click();
    assert.equal(
      await p.evaluate(() => VectorShiftDenseDebug.getStats().mistakes),
      0,
    );
    assert.equal(
      await p.evaluate(() => VectorShiftDenseDebug.getStats().hints),
      0,
    );
    checks.push("blocked tap, hint and retry counters");

    // Hold press, then release a winding body. Another legal piece remains tappable during exit.
    const clear = levels[0].arrows
      .filter((a) => core.clearPath(levels[0], first, a.id))
      .sort((a, b) => b.cells.length - a.cells.length)[0].id;
    const rightPoint = await p.evaluate(
      (id) => VectorShiftDenseDebug.pointFor(id),
      clear,
    );
    await p.mouse.click(rightPoint.x, rightPoint.y, { button: "right" });
    assert.deepEqual(
      await state(p),
      first,
      "right mouse button must not remove a snake",
    );
    const point = await p.evaluate(
      (id) => VectorShiftDenseDebug.bodyPointFor(id),
      clear,
    );
    await p.mouse.move(point.x, point.y);
    await p.mouse.down();
    await p.screenshot({ path: path.join(output, "dense-press.png") });
    await p.mouse.up();
    assert.equal((await state(p)).remaining.length, 27);
    const capture = [];
    for (let i = 0; i < 4; i++) {
      await p.waitForTimeout(i === 0 ? 25 : 80);
      capture.push(
        await p.evaluate(() => VectorShiftDenseDebug.getAnimation()),
      );
      await p
        .locator("#puzzleCanvas")
        .screenshot({ path: path.join(output, `dense-exit-${i}.png`) });
    }
    fs.writeFileSync(
      path.join(output, "dense-motion-samples.json"),
      JSON.stringify(capture, null, 2),
    );
    await p.locator("#undoButton").click();
    assert.deepEqual(await state(p), first);
    await tap(p, clear);
    const next = (await p.evaluate(() => VectorShiftDenseDebug.getSolution()))
      .actions[0].id;
    await tap(p, next);
    assert.equal((await state(p)).remaining.length, 26);
    await p.reload();
    assert.equal((await state(p)).remaining.length, 26);
    await p.locator("#undoButton").click();
    assert.equal((await state(p)).remaining.length, 27);
    checks.push(
      "body press, continuous exit frames, rapid sequential taps, saved run and undo",
    );

    // Real pointer hit testing clears every stage. No debug action is used to remove a snake.
    await p.evaluate(() => VectorShiftDenseDebug.setReduced(true));
    for (let i = 0; i < levels.length; i++) {
      await p.evaluate((n) => VectorShiftDenseDebug.setLevel(n), i + 1);
      if (i < 4) {
        await p.evaluate(() => document.activeElement?.blur());
        await p.waitForTimeout(280);
        await p.screenshot({
          path: path.join(output, `dense-pattern-${i + 1}.png`),
        });
      }
      const solution = (
        await p.evaluate(() => VectorShiftDenseDebug.getSolution())
      ).actions;
      for (const [n, action] of solution.entries()) {
        await tap(p, action.id, n % 2 === 0);
        assert.equal(
          (await state(p)).remaining.length,
          solution.length - n - 1,
          `stage ${i + 1}, step ${n + 1}`,
        );
      }
      await p.locator("#nextPattern").waitFor();
      assert.equal(
        await p.locator(".win-stats strong").first().innerText(),
        String(levels[i].arrows.length),
      );
      if (i === 0)
        await p.screenshot({
          path: path.join(output, "dense-result-mobile.png"),
        });
      await p.keyboard.press("Escape");
    }
    checks.push(
      `all ${levels.length} boards / ${levels.reduce((n, l) => n + l.arrows.length, 0)} snakes solved through head/body pointer input`,
    );
    await p.evaluate(() => VectorShiftDenseDebug.setLevel(1));
    await p.locator("#collectionButton").click();
    assert.equal(await p.locator("[data-level]").count(), levels.length);
    await p.screenshot({ path: path.join(output, "dense-collection.png") });
    await p.locator('[data-level="2"]').click();
    assert.equal(await p.locator("#levelTitle").innerText(), levels[2].title);
    await p.locator("#helpButton").click();
    await p.keyboard.press("Escape");
    assert.equal(
      await p.evaluate(() => document.activeElement.id),
      "helpButton",
    );
    assert.equal(await p.locator("#gameShell").getAttribute("inert"), null);
    checks.push(
      "collection thumbnails, board selection, modal Escape and restored focus",
    );

    const mobile = await browser.newContext({
      viewport: { width: 390, height: 844 },
      hasTouch: true,
      isMobile: true,
      deviceScaleFactor: 2,
    });
    const t = await mobile.newPage();
    t.on("pageerror", (e) => errors.push(e.message));
    await t.goto(base);
    const id = (await t.evaluate(() => VectorShiftDenseDebug.getSolution()))
      .actions[0].id;
    const hp = await t.evaluate((id) => VectorShiftDenseDebug.pointFor(id), id);
    await t.touchscreen.tap(hp.x, hp.y);
    assert.equal((await state(t)).remaining.length, 27);
    await t.locator("#undoButton").tap();
    const session = await mobile.newCDPSession(t);
    const box = await t.locator("#puzzleCanvas").boundingBox(),
      cx = box.x + box.width / 2 - 40,
      cy = box.y + box.height / 2 - 55;
    const points = (span) => [
      { x: cx - span, y: cy, id: 1 },
      { x: cx + span, y: cy, id: 2 },
    ];
    await session.send("Input.dispatchTouchEvent", {
      type: "touchStart",
      touchPoints: points(35),
    });
    await session.send("Input.dispatchTouchEvent", {
      type: "touchMove",
      touchPoints: points(80),
    });
    await session.send("Input.dispatchTouchEvent", {
      type: "touchEnd",
      touchPoints: [],
    });
    assert.ok(
      (await t.evaluate(() => VectorShiftDenseDebug.getView())).zoom > 1.7,
    );
    const pinchView = await t.evaluate(() => VectorShiftDenseDebug.getView());
    assert.ok(
      Math.abs(
        box.x +
          box.width / 2 +
          pinchView.x +
          (cx - box.x - box.width / 2) * pinchView.zoom -
          cx,
      ) < 2,
      "pinch must preserve its focal point",
    );
    assert.equal(
      (await state(t)).remaining.length,
      28,
      "pinch must not release any snakes",
    );
    await session.send("Input.dispatchTouchEvent", {
      type: "touchStart",
      touchPoints: [{ x: cx, y: cy, id: 3 }],
    });
    await session.send("Input.dispatchTouchEvent", {
      type: "touchMove",
      touchPoints: [{ x: cx + 55, y: cy + 35, id: 3 }],
    });
    await session.send("Input.dispatchTouchEvent", {
      type: "touchEnd",
      touchPoints: [],
    });
    assert.ok((await t.evaluate(() => VectorShiftDenseDebug.getView())).x > 20);
    assert.equal((await state(t)).remaining.length, 28);
    await t.locator("#zoomButton").tap();
    await t.waitForFunction(() => VectorShiftDenseDebug.getView().zoom === 1);
    checks.push(
      "emulated touch tap, two-finger pinch, drag and fit; no accidental removals",
    );
    await mobile.close();

    // Untrusted persisted data must recover to a usable game, including a forged history.
    for (const value of [
      "bad json",
      JSON.stringify({
        index: 0,
        runs: {
          "dense-01": { state: { remaining: ["s01"], moves: 27, history: [] } },
        },
      }),
      JSON.stringify({
        index: 0,
        runs: {
          "dense-01": {
            state: core.newState(levels[0]),
            elapsed: "1e309",
            hints: "1e309",
            mistakes: -9,
          },
        },
      }),
    ]) {
      const badContext = await browser.newContext();
      await badContext.addInitScript(
        (value) => localStorage.setItem("vector-shift-dense-v1", value),
        value,
      );
      const badPage = await badContext.newPage();
      badPage.on("pageerror", (e) => errors.push(e.message));
      await badPage.goto(base);
      assert.equal((await state(badPage)).remaining.length, 28);
      assert.ok(
        await badPage.evaluate(() => {
          const s = VectorShiftDenseDebug.getStats();
          return (
            Number.isFinite(s.elapsed) && s.hints === 0 && s.mistakes === 0
          );
        }),
      );
      await badContext.close();
    }
    checks.push("malformed and forged saved-state recovery");
    for (const channel of ["coolmath", "crazygames"]) {
      const release = await context.newPage();
      release.on("pageerror", (e) => errors.push(e.message));
      await release.route("https://sdk.crazygames.com/**", (route) =>
        route.fulfill({
          contentType: "application/javascript",
          body: 'window.sdkCalls=[];window.CrazyGames={SDK:{init:async()=>sdkCalls.push("init"),game:{gameplayStart:()=>sdkCalls.push("start")}}}',
        }),
      );
      await release.goto(`${base}/${channel}/?qa=1&pattern=1&fresh=1`);
      assert.equal(await release.locator("html").getAttribute("lang"), "en");
      assert.equal(
        await release.evaluate(() => typeof window.VectorShiftDenseDebug),
        "undefined",
      );
      assert.equal(
        await release.locator("#levelTitle").innerText(),
        levels[0].titleEn,
      );
      assert.match(
        await release.locator("#puzzleCanvas").getAttribute("aria-label"),
        /Winding paths/,
      );
      await release.locator("#collectionButton").click();
      assert.equal(await release.locator('a[href="phase.html"]').count(), 1);
      await release.keyboard.press("Escape");
      if (channel === "crazygames") {
        await release.waitForFunction(() => window.sdkCalls?.length === 2);
        assert.deepEqual(await release.evaluate(() => window.sdkCalls), [
          "init",
          "start",
        ]);
      }
      await release.close();
    }
    checks.push(
      "English channel builds, debug disabled, phase link, CrazyGames SDK lifecycle with mock",
    );
    assert.deepEqual(errors, []);
    fs.writeFileSync(
      path.join(output, "dense-browser-report.json"),
      JSON.stringify(
        {
          date: "2026-10-22",
          checks,
          errors,
          firstBoard: display,
          limitations: [
            "Chromium browser and touch emulation; physical-device performance and player preference not measured.",
            "SDK lifecycle uses a local mock, not platform approval.",
          ],
        },
        null,
        2,
      ) + "\n",
    );
    console.log(
      `PASS dense browser: ${checks.length} checks; ${errors.length} page errors`,
    );
    checks.forEach((c) => console.log(`  ${c}`));
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
