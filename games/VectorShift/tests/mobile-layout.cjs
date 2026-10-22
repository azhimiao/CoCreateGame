const { chromium } = require(process.env.PLAYWRIGHT_MODULE || "playwright"),
  assert = require("node:assert/strict"),
  fs = require("node:fs"),
  path = require("node:path"),
  http = require("node:http");
const root = path.resolve(__dirname, ".."),
  out = path.join(root, "artifacts/mobile");
fs.mkdirSync(out, { recursive: true });
const server = http.createServer((req, res) => {
  res.writeHead(200, { "Content-Type": "text/html;charset=utf-8" });
  res.end(fs.readFileSync(path.join(root, "index.html")));
});

async function main() {
  await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));
  const browser = await chromium.launch({
      executablePath: process.env.CHROMIUM_PATH || undefined,
    }),
    sizes = [
      [320, 568],
      [360, 640],
      [360, 800],
      [390, 844],
      [412, 915],
      [568, 320],
      [667, 375],
      [844, 390],
    ],
    errors = [];
  try {
    for (const [width, height] of sizes) {
      const context = await browser.newContext({
          viewport: { width, height },
          deviceScaleFactor: 1,
          hasTouch: true,
          isMobile: true,
        }),
        page = await context.newPage();
      page.on("pageerror", (error) => errors.push(error.message));
      await page.goto(
        "http://127.0.0.1:" + server.address().port + "/?mode=journey",
      );
      const layout = await page.evaluate(() => {
        const buttons = [
          ...document.querySelectorAll(
            ".game-top button,.game-controls button,.game-footer button,#zoomButton",
          ),
        ].filter((button) => !button.hidden);
        return {
          width: innerWidth,
          height: innerHeight,
          documentWidth: document.documentElement.scrollWidth,
          documentHeight: document.documentElement.scrollHeight,
          stage: document
            .querySelector("#canvasStage")
            .getBoundingClientRect()
            .toJSON(),
          controls: buttons.map((button) => ({
            id: button.id,
            ...button.getBoundingClientRect().toJSON(),
          })),
        };
      });
      assert.equal(
        layout.documentWidth,
        width,
        "horizontal overflow " + width + "x" + height,
      );
      assert.equal(
        layout.documentHeight,
        height,
        "page overflow " + width + "x" + height,
      );
      assert.ok(layout.stage.x >= 0 && layout.stage.right <= width + 1);
      assert.ok(layout.stage.y >= 0 && layout.stage.bottom <= height + 1);
      for (const button of layout.controls) {
        assert.ok(
          button.width >= 44 && button.height >= 44,
          button.id + " target",
        );
        assert.ok(
          button.x >= 0 &&
            button.y >= 0 &&
            button.right <= width + 1 &&
            button.bottom <= height + 1,
          button.id + " outside " + width + "x" + height,
        );
      }
      await page.screenshot({
        path: path.join(out, "game-" + width + "x" + height + ".png"),
      });

      await page.locator("#collectionButton").tap();
      const modal = await page.evaluate(() => {
        const dialog = document.querySelector("#gameDialog"),
          box = dialog.getBoundingClientRect();
        return {
          open: dialog.open,
          x: box.x,
          y: box.y,
          right: box.right,
          bottom: box.bottom,
          clientHeight: dialog.clientHeight,
          scrollHeight: dialog.scrollHeight,
        };
      });
      assert.ok(modal.open);
      assert.ok(modal.x >= 0 && modal.right <= width);
      assert.ok(modal.y >= 0 && modal.bottom <= height);
      assert.ok(
        modal.bottom >= height - 12,
        "sheet should meet safe bottom: " + JSON.stringify(modal),
      );
      await page.screenshot({
        path: path.join(out, "chapters-" + width + "x" + height + ".png"),
      });
      await page.locator("#gameDialog").evaluate((dialog) => {
        dialog.scrollTop = dialog.scrollHeight;
      });
      const lastStage = await page.locator('[data-level="11"]').boundingBox();
      const dialogBox = await page.locator("#gameDialog").boundingBox();
      assert.ok(
        lastStage.y >= dialogBox.y &&
          lastStage.y + lastStage.height <= dialogBox.y + dialogBox.height,
      );
      const footer = await page.locator(".collection-footer").boundingBox();
      assert.ok(
        footer.y >= dialogBox.y &&
          footer.y + footer.height <= dialogBox.y + dialogBox.height,
        "chapter footer must be reachable by scrolling",
      );
      await page.locator("#gameDialog").evaluate((dialog) => {
        dialog.scrollTop = 0;
      });
      await page.locator('[data-mode="samples"]').tap();
      await page.locator('[data-level="0"]').tap();
      assert.equal(
        await page.evaluate(() => VectorShiftDenseDebug.getLevel().id),
        "dense-01",
      );
      await page.locator("#helpButton").tap();
      const helpDialog = await page.locator("#gameDialog").boundingBox();
      assert.ok(helpDialog.y >= 0 && helpDialog.y + helpDialog.height <= height);
      await page.locator("#helpDone").scrollIntoViewIfNeeded();
      const helpDone = await page.locator("#helpDone").boundingBox();
      assert.ok(
        helpDone.y >= helpDialog.y &&
          helpDone.y + helpDone.height <= helpDialog.y + helpDialog.height,
        "help confirmation must remain reachable",
      );
      await page.locator("#helpDone").tap();
      await context.close();
      console.log("PASS mobile " + width + "x" + height);
    }
    assert.deepEqual(errors, []);
    fs.writeFileSync(
      path.join(out, "report.json"),
      JSON.stringify(
        {
          date: "2026-10-22",
          viewports: sizes.map(([width, height]) => width + "x" + height),
          checks: [
            "No horizontal/page overflow; board and >=44px controls remain inside all eight viewports.",
            "Chapter sheet stays within the safe viewport; all 12 stages remain reachable by scrolling.",
            "Touch can switch to the five-board gallery and enter a selected stage.",
            "Long help content scrolls within the bottom sheet; confirmation remains touch reachable.",
          ],
          errors,
          limitation:
            "Playwright Chromium touch emulation; no physical handset tested.",
        },
        null,
        2,
      ) + "\n",
    );
  } finally {
    await browser.close();
    server.close();
  }
}
main().catch((error) => {
  console.error(error);
  server.close();
  process.exitCode = 1;
});
