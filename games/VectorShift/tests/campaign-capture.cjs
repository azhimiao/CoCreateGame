// A real, default-motion journey through levels 1–6 and a scissors use.
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || "playwright");
const path = require("node:path"),
  fs = require("node:fs");
const root = path.resolve(__dirname, ".."),
  out = path.join(root, "artifacts/campaign");
async function main() {
  const b = await chromium.launch({
      executablePath: process.env.CHROMIUM_PATH || undefined,
    }),
    c = await b.newContext({
      viewport: { width: 390, height: 844 },
      deviceScaleFactor: 2,
      recordVideo: {
        dir: path.join(root, "runtime/campaign-video"),
        size: { width: 390, height: 844 },
      },
    }),
    p = await c.newPage(),
    errors = [];
  p.on("pageerror", (e) => errors.push(e.message));
  try {
    await p.goto(
      process.env.CAPTURE_URL || "http://127.0.0.1:4173/?mode=journey",
    );
    await p.waitForTimeout(600);
    for (let n = 1; n <= 5; n++) {
      while (
        (await p.evaluate(
          () => VectorShiftDenseDebug.getState().remaining.length,
        )) > 0
      ) {
        const point = await p.evaluate(() => {
          const d = VectorShiftDenseDebug;
          return d.pointFor(d.getSolution().actions[0].id);
        });
        await p.mouse.click(point.x, point.y);
        await p.waitForFunction(
          () =>
            !VectorShiftDenseDebug.getAnimation().some(
              (a) => a.kind === "exit",
            ),
        );
        await p.waitForTimeout(100);
      }
      await p.locator("#nextPattern").click();
      await p.waitForTimeout(300);
    }
    await p.locator("#cutButton").click();
    const point = await p.evaluate(() => {
      const d = VectorShiftDenseDebug,
        l = d.getLevel(),
        s = d.getState();
      return d.pointFor(
        s.remaining.find(
          (id) => VectorShiftDenseCore.blockers(l, s, id).length,
        ),
      );
    });
    await p.mouse.click(point.x, point.y);
    await p.waitForTimeout(700);
    await p.locator("#confirmCut").click();
    await p.waitForTimeout(700);
    await p.locator("#undoButton").click();
    await p.waitForTimeout(500);
    await p.locator("#collectionButton").click();
    await p.waitForTimeout(700);
    if (errors.length) throw Error(errors.join("\n"));
    const v = p.video();
    await c.close();
    await v.saveAs(path.join(out, "journey-playthrough.webm"));
    await v.delete();
    fs.writeFileSync(
      path.join(out, "capture.json"),
      JSON.stringify(
        {
          date: "2026-10-22",
          method:
            "Real head pointer input, default motion, sequential levels 1–6, blocked-target scissors confirmation and undo.",
          errors,
        },
        null,
        2,
      ) + "\n",
    );
    console.log("PASS journey progression/scissors video captured");
  } finally {
    await b.close();
  }
}
main().catch((e) => {
  console.error(e);
  process.exitCode = 1;
});
