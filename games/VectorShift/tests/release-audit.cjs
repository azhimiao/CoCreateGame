const { chromium } = require(process.env.PLAYWRIGHT_MODULE || "playwright"),
  fs = require("node:fs"),
  path = require("node:path"),
  http = require("node:http"),
  assert = require("node:assert/strict"),
  crypto = require("node:crypto");
const root = path.resolve(__dirname, ".."),
  out = path.join(root, "artifacts/campaign"),
  assets = path.join(root, "submission/assets");
const server = http.createServer((req, res) => {
  const u = new URL(req.url, "http://local"),
    channel = u.pathname.startsWith("/crazygames")
      ? "crazygames-basic"
      : u.pathname.startsWith("/coolmath")
        ? "coolmath"
        : "demo";
  res.writeHead(200, { "Content-Type": "text/html;charset=utf-8" });
  res.end(fs.readFileSync(path.join(root, "dist", channel, "index.html")));
});
async function main() {
  await new Promise((r) => server.listen(0, "127.0.0.1", r));
  const base = `http://127.0.0.1:${server.address().port}`,
    b = await chromium.launch({
      executablePath: process.env.CHROMIUM_PATH || undefined,
    }),
    result = [];
  try {
    for (const channel of ["demo", "coolmath", "crazygames-basic"]) {
      const c = await b.newContext({
          viewport: { width: 390, height: 844 },
          deviceScaleFactor: 2,
          hasTouch: true,
        }),
        p = await c.newPage(),
        errors = [],
        requests = [];
      p.on("pageerror", (e) => errors.push(e.message));
      p.on("request", (r) => requests.push(r.url()));
      await p.route("**/crazygames-sdk-v3.js", (r) =>
        r.fulfill({
          body: 'window.sdkTrace=[];window.CrazyGames={SDK:{init:async()=>sdkTrace.push("init"),game:{gameplayStart:()=>sdkTrace.push("start")}}}',
        }),
      );
      await p.goto(
        base +
          "/" +
          (channel === "crazygames-basic" ? "crazygames" : channel) +
          "/",
      );
      const metrics = await p.evaluate(() => ({
        readyMs: performance.now(),
        lang: document.documentElement.lang,
        canvases: document.querySelectorAll("canvas").length,
        debug: typeof window.VectorShiftDenseDebug,
      }));
      assert.equal(metrics.lang, channel === "demo" ? "zh-CN" : "en");
      assert.equal(metrics.debug, channel === "demo" ? "object" : "undefined");
      assert.equal(metrics.canvases, 1);
      if (channel === "crazygames-basic") {
        await p.waitForFunction(() => window.sdkTrace?.length === 2);
        assert.deepEqual(await p.evaluate(() => sdkTrace), ["init", "start"]);
      } else assert.equal(requests.length, 1);
      await p.screenshot({ path: path.join(out, `${channel}-first.png`) });
      if (channel === "coolmath")
        await p.screenshot({ path: path.join(assets, "mobile.png") });
      await p.locator("#collectionButton").tap();
      await p.locator('[data-mode="samples"]').tap();
      await p.locator('[data-level="1"]').tap();
      await p.screenshot({ path: path.join(out, `${channel}-gallery.png`) });
      if (channel === "coolmath") {
        await p.screenshot({ path: path.join(assets, "gallery-mobile.png") });
        await p.setViewportSize({ width: 1440, height: 1000 });
        await p.screenshot({ path: path.join(assets, "desktop.png") });
      }
      if (channel === "demo") {
        await p.evaluate(() => {
          VectorShiftDenseDebug.setMode("journey");
          VectorShiftDenseDebug.setReduced(true);
          VectorShiftDenseDebug.setLevel(1);
        });
        const ids = await p.evaluate(() =>
          VectorShiftDenseDebug.getSolution().actions.map((a) => a.id),
        );
        for (const id of ids) {
          const point = await p.evaluate(
            (id) => VectorShiftDenseDebug.pointFor(id),
            id,
          );
          await p.mouse.click(point.x, point.y);
        }
        await p.locator("#nextPattern").tap();
        assert.equal(
          await p.locator("#progressTrack").getAttribute("aria-valuenow"),
          "0",
        );
        assert.ok(
          await p
            .locator("#progressFill")
            .evaluate((e) => e.getBoundingClientRect().width <= 1),
        );
      }
      assert.deepEqual(errors, []);
      const file = fs.readFileSync(
        path.join(root, "dist", channel, "index.html"),
      );
      result.push({
        channel,
        bytes: file.length,
        sha256: crypto.createHash("sha256").update(file).digest("hex"),
        ...metrics,
        errors,
        network: requests.map((u) => (u.startsWith(base) ? "local HTML" : u)),
        sdk:
          channel === "crazygames-basic" ? "mock init/start verified" : "none",
      });
      await c.close();
    }
    const legacy = await b.newContext();
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
    await oldPage.goto(base);
    assert.equal(
      await oldPage.evaluate(() => VectorShiftDenseDebug.getLevel().id),
      "dense-02",
    );
    assert.equal(
      await oldPage.evaluate(
        () => VectorShiftDenseDebug.getState().remaining.length,
      ),
      32,
    );
    await legacy.close();
    fs.writeFileSync(
      path.join(out, "release-audit.json"),
      JSON.stringify(
        {
          date: "2026-10-22",
          builds: result,
          regressions: [
            "touch menu/dialog navigation",
            "next-level progress bar resets immediately",
            "legacy gallery mode retained; invalid old history reset",
          ],
          limits:
            "Local Chromium, touch emulation, live platform SDK acceptance and physical phones not verified.",
        },
        null,
        2,
      ) + "\n",
    );
    console.log(JSON.stringify(result, null, 2));
  } finally {
    await b.close();
    server.close();
  }
}
main().catch((e) => {
  console.error(e);
  server.close();
  process.exitCode = 1;
});
