// Record actual animated pointer input and staged board releases; no synthetic video.
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || "playwright");
const path = require("node:path");
const fs = require("node:fs");
const root = path.resolve(__dirname, ".."),
  out = path.join(root, "artifacts");
(async () => {
  const browser = await chromium.launch({
    executablePath: process.env.CHROMIUM_PATH || undefined,
  });
  const context = await browser.newContext({
    viewport: { width: 390, height: 844 },
    recordVideo: {
      dir: path.join(out, "motion"),
      size: { width: 390, height: 844 },
    },
  });
  const p = await context.newPage(),
    errors = [];
  p.on("pageerror", (e) => errors.push(e.message));
  try {
    await p.goto(process.env.CAPTURE_URL || "http://127.0.0.1:4173/?mode=samples&fresh=1");
    await p.waitForFunction(() => !!window.VectorShiftDenseDebug);
    await p.waitForTimeout(900);
    let step = 0;
    const witness = [];
    while (
      (await p.evaluate(
        () => VectorShiftDenseDebug.getState().remaining.length,
      )) > 0
    ) {
      if (step % 7 === 0) {
        await p.evaluate(() => document.activeElement?.blur());
        await p.screenshot({
          path: path.join(out, `dense-release-${28 - step}.png`),
        });
      }
      const id = await p.evaluate(
          () => VectorShiftDenseDebug.getSolution().actions[0].id,
        ),
        point = await p.evaluate(
          (id) => VectorShiftDenseDebug.pointFor(id),
          id,
        );
      await p.mouse.click(point.x, point.y);
      witness.push(id);
      step++;
      await p.waitForFunction(
        () =>
          !VectorShiftDenseDebug.getAnimation().some((a) => a.kind === "exit"),
      );
      await p.waitForTimeout(100);
    }
    if (errors.length) throw new Error(errors.join("\n"));
    await p.locator("#nextPattern").waitFor();
    await p.waitForTimeout(1000);
    await p.locator("#nextPattern").click();
    await p.waitForTimeout(900);
    for (let i = 0; i < 8; i++) {
      const id = await p.evaluate(
          () => VectorShiftDenseDebug.getSolution().actions[0].id,
        ),
        point = await p.evaluate(
          (id) => VectorShiftDenseDebug.pointFor(id),
          id,
        );
      await p.mouse.click(point.x, point.y);
      await p.waitForFunction(
        () =>
          !VectorShiftDenseDebug.getAnimation().some((a) => a.kind === "exit"),
      );
      await p.waitForTimeout(100);
    }
    await p.locator("#collectionButton").click();
    await p.waitForTimeout(900);
    await p.locator('[data-level="2"]').click();
    await p.waitForTimeout(1200);
    fs.writeFileSync(
      path.join(out, "dense-release-witness.json"),
      JSON.stringify(
        {
          level: "dense-01",
          actions: witness,
          screenshotsRemaining: [28, 21, 14, 7],
          method:
            "Actual pointer taps; default animation; stages captured after settled motion.",
        },
        null,
        2,
      ) + "\n",
    );
    const video = p.video();
    await context.close();
    await video.saveAs(path.join(out, "dense-playthrough.webm"));
    await video.delete();
    console.log("PASS animated playthrough + four release stages captured");
  } catch (e) {
    console.error(
      await p.evaluate(() => ({
        state: VectorShiftDenseDebug.getState(),
        stats: VectorShiftDenseDebug.getStats(),
        dialog: document.querySelector("#gameDialog").outerHTML,
      })),
      errors,
    );
    await p.screenshot({ path: path.join(out, "motion/capture-failure.png") });
    throw e;
  } finally {
    await browser.close();
  }
})().catch((e) => {
  console.error(e);
  process.exitCode = 1;
});
