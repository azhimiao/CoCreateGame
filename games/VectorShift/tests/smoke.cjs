const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const http = require('node:http');

let playwright;
try { playwright = require(process.env.PLAYWRIGHT_MODULE || 'playwright'); }
catch { playwright = require(process.env.PLAYWRIGHT_MODULE || 'playwright-core'); }
const root = path.resolve(__dirname, '..');
const html = fs.readFileSync(path.join(root, 'dist/demo/phase.html'), 'utf8');
const releases = {
  '/coolmath': fs.readFileSync(path.join(root, 'dist/coolmath/phase.html'), 'utf8'),
  '/crazygames': fs.readFileSync(path.join(root, 'dist/crazygames-basic/phase.html'), 'utf8'),
};
const server = http.createServer((req, res) => {
  const body = releases[new URL(req.url, 'http://localhost').pathname] || html;
  res.writeHead(200, { 'content-type': 'text/html; charset=utf-8' });
  res.end(body);
});

async function tapPath(page, id) {
  const locator = page.getByTestId(`piece-${id}`);
  const point = await locator.evaluate(el => {
    const p = el.getPointAtLength(el.getTotalLength() * 0.55);
    const screen = new DOMPoint(p.x, p.y).matrixTransform(el.getScreenCTM());
    return { x: screen.x, y: screen.y };
  });
  await page.mouse.click(point.x, point.y);
}

async function main() {
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const address = server.address();
  const base = `http://127.0.0.1:${address.port}`;
  const executablePath = process.env.CHROMIUM_PATH || undefined;
  const browser = await playwright.chromium.launch({ headless: true, executablePath });
  const failures = [];
  try {
    const context = await browser.newContext({ viewport: { width: 1440, height: 1000 } });
    await context.addInitScript(() => {
      for (const key of Object.keys(localStorage)) localStorage.removeItem(key);
      localStorage.setItem('vector-shift-v05-onboarded', '1');
    });
    const page = await context.newPage();
    page.on('pageerror', error => failures.push(String(error)));
    await page.goto(`${base}/?qa=1`);
    await page.locator('[data-testid="piece-0"]').waitFor({ state: 'attached' });
    assert.equal(await page.locator('.snake-hit').count(), 2);
    assert.equal(await page.locator('.grid-cell').count(), 25);

    const initial = await page.evaluate(() => window.VectorShiftDebug.getState());
    const clearId = await page.evaluate(() => {
      const { getLevel, getState } = window.VectorShiftDebug;
      return getLevel().arrows.find(a => window.VectorShiftCore.clearPath(getLevel(), getState(), a.id)).id;
    });
    await tapPath(page, clearId);
    await page.waitForFunction(n => window.VectorShiftDebug.getState().remaining.length === n - 1, initial.remaining.length);

    await page.evaluate(() => window.VectorShiftDebug.setLevel(20));
    await page.locator('.snake-hit').first().waitFor({ state: 'attached' });
    const beforeMistake = await page.evaluate(() => window.VectorShiftDebug.getState());
    const blockedId = await page.evaluate(() => {
      const { getLevel, getState } = window.VectorShiftDebug;
      return getLevel().arrows.find(a => window.VectorShiftCore.blockers(getLevel(), getState(), a.id)?.length).id;
    });
    await tapPath(page, blockedId);
    await page.waitForFunction(() => document.querySelector('#mistakeStat').textContent === '1');
    assert.deepEqual(await page.evaluate(() => window.VectorShiftDebug.getState()), beforeMistake);
    await page.locator('#phaseButton').click();
    assert.equal(await page.evaluate(() => window.VectorShiftDebug.getState().phase), 1);
    await page.locator('#undoButton').click();
    assert.equal(await page.evaluate(() => window.VectorShiftDebug.getState().phase), 0);
    await page.locator('#hintButton').click();
    assert.ok((await page.locator('#feedback').innerText()).length > 0);

    await page.locator('#zoomInButton').click();
    assert.equal(await page.locator('#zoomReadout').innerText(), '115%');
    assert.match(await page.locator('#boardScene').getAttribute('style'), /--zoom: 1\.15/);
    await page.locator('#visualizerButton').click();
    assert.equal(await page.locator('#visualizerButton').getAttribute('aria-pressed'), 'true');
    await page.locator('.exit-cell.global').first().waitFor({ state: 'attached' });
    assert.ok(await page.locator('.exit-cell.global').count() > 0);
    await page.locator('#zoomResetButton').click();
    assert.equal(await page.locator('#zoomReadout').innerText(), '100%');

    await page.locator('#gearButton').click();
    await page.locator('#gearDaily').click();
    await page.locator('#dailyGo').click();
    assert.equal(await page.evaluate(() => window.VectorShiftDebug.getMode()), 'daily');
    await page.evaluate(() => window.VectorShiftDebug.solveAndPlay());
    await page.locator('#dailyBackWin').waitFor({ timeout: 5000 });
    assert.equal(await page.locator('.result-stats div').count(), 5);
    assert.ok(await page.locator('#shareResult').isVisible());
    assert.equal((await page.locator('.result-stats').innerText()).includes('1'), true);
    await page.screenshot({ path: path.join(root, 'artifacts/daily-result-desktop.png'), fullPage: true });
    await page.setViewportSize({ width: 390, height: 844 });
    const modalBox = await page.locator('#modal').boundingBox();
    assert.ok(modalBox.height < 844 * 0.92, JSON.stringify(modalBox));
    await page.screenshot({ path: path.join(root, 'artifacts/daily-result-mobile.png'), fullPage: true });
    await page.setViewportSize({ width: 1440, height: 1000 });
    await page.locator('#dailyBackWin').click();
    await page.evaluate(() => { window.VectorShiftDebug.setLevel(1); window.VectorShiftDebug.solveAndPlay(); });
    await page.locator('#continueWin').waitFor();
    assert.equal(await page.locator('.result-stats div').count(), 4);
    assert.match(await page.locator('.result-mark').innerText(), /★/);
    await page.locator('#continueWin').click();
    await page.evaluate(() => window.VectorShiftDebug.setLevel(20));
    await page.screenshot({ path: path.join(root, 'artifacts/level20-desktop.png'), fullPage: true });
    await page.evaluate(() => { window.VectorShiftDebug.setLevel(52); window.VectorShiftDebug.solveAndPlay(); });
    await page.locator('#viewLevelsWin').waitFor();
    assert.ok(await page.evaluate(() => window.VectorShiftDebug.getProgress().completed.includes(52)));
    assert.equal(await page.evaluate(() => window.VectorShiftDebug.getState().remaining.length), 0);
    await page.locator('#viewLevelsWin').click();
    await page.locator('#modalTitle').waitFor();
    await page.locator('#modalClose').click();
    assert.deepEqual(failures, []);
    await context.close();

    const resumeContext = await browser.newContext({ viewport: { width: 390, height: 844 } });
    await resumeContext.addInitScript(() => localStorage.setItem('vector-shift-v05-onboarded', '1'));
    const resume = await resumeContext.newPage();
    resume.on('pageerror', error => failures.push(String(error)));
    await resume.goto(base);
    await resume.locator('.snake-hit').first().waitFor({ state: 'attached' });
    const resumeInitial = await resume.evaluate(() => window.VectorShiftDebug.getState().remaining.length);
    const resumeClearId = await resume.evaluate(() => {
      const { getLevel, getState } = window.VectorShiftDebug;
      return getLevel().arrows.find(a => window.VectorShiftCore.clearPath(getLevel(), getState(), a.id)).id;
    });
    await tapPath(resume, resumeClearId);
    await resume.waitForFunction(n => window.VectorShiftDebug.getState().remaining.length === n - 1, resumeInitial);
    await resume.reload();
    await resume.waitForFunction(() => document.querySelector('#feedback').textContent.includes('恢复'));
    assert.equal(await resume.evaluate(() => window.VectorShiftDebug.getState().remaining.length), resumeInitial - 1);
    await resume.locator('#gearButton').click();
    await resume.locator('#gearDaily').click();
    await resume.locator('#dailyGo').click();
    const dailyInitial = await resume.evaluate(() => window.VectorShiftDebug.getState().remaining.length);
    const dailyClearId = await resume.evaluate(() => {
      const { getLevel, getState } = window.VectorShiftDebug;
      return getLevel().arrows.find(a => window.VectorShiftCore.clearPath(getLevel(), getState(), a.id)).id;
    });
    await tapPath(resume, dailyClearId);
    await resume.waitForFunction(n => window.VectorShiftDebug.getState().remaining.length === n - 1, dailyInitial);
    await resume.reload();
    await resume.waitForFunction(() => document.querySelector('#feedback').textContent.includes('恢复'));
    await resume.locator('#gearButton').click();
    await resume.locator('#gearDaily').click();
    await resume.locator('#dailyGo').click();
    assert.equal(await resume.evaluate(() => window.VectorShiftDebug.getMode()), 'daily');
    assert.equal(await resume.evaluate(() => window.VectorShiftDebug.getState().remaining.length), dailyInitial - 1);
    await resume.screenshot({ path: path.join(root, 'artifacts/mobile.png'), fullPage: true });
    await resumeContext.close();

    const denseMobile = await browser.newPage({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true });
    await denseMobile.goto(`${base}/?qa=1`);
    await denseMobile.evaluate(() => window.VectorShiftDebug.setLevel(20));
    await denseMobile.locator('.snake-hit').first().waitFor({ state: 'attached' });
    await denseMobile.screenshot({ path: path.join(root, 'artifacts/level20-mobile.png'), fullPage: true });
    const bounds = await denseMobile.locator('#boardFrame').boundingBox();
    const cdp = await denseMobile.context().newCDPSession(denseMobile);
    await cdp.send('Input.dispatchTouchEvent', { type: 'touchStart', touchPoints: [
      { id: 1, x: bounds.x + bounds.width * 0.35, y: bounds.y + bounds.height * 0.45 },
      { id: 2, x: bounds.x + bounds.width * 0.65, y: bounds.y + bounds.height * 0.45 },
    ] });
    await cdp.send('Input.dispatchTouchEvent', { type: 'touchMove', touchPoints: [
      { id: 1, x: bounds.x + bounds.width * 0.25, y: bounds.y + bounds.height * 0.45 },
      { id: 2, x: bounds.x + bounds.width * 0.75, y: bounds.y + bounds.height * 0.45 },
    ] });
    await cdp.send('Input.dispatchTouchEvent', { type: 'touchEnd', touchPoints: [] });
    await denseMobile.waitForFunction(() => Number(getComputedStyle(document.querySelector('#boardScene')).getPropertyValue('--zoom').trim()) > 1.05);
    await denseMobile.locator('#zoomResetButton').click();
    const phoneBlocked = await denseMobile.evaluate(() => {
      const { getLevel, getState } = window.VectorShiftDebug;
      return getLevel().arrows.find(a => window.VectorShiftCore.blockers(getLevel(), getState(), a.id)?.length).id;
    });
    const phonePoint = await denseMobile.getByTestId(`piece-${phoneBlocked}`).evaluate(el => {
      const p = el.getPointAtLength(el.getTotalLength() * 0.55);
      const screen = new DOMPoint(p.x, p.y).matrixTransform(el.getScreenCTM());
      return { x: screen.x, y: screen.y };
    });
    await denseMobile.touchscreen.tap(phonePoint.x, phonePoint.y);
    await denseMobile.waitForFunction(() => document.querySelector('#mistakeStat').textContent === '1');
    await denseMobile.close();

    for (const viewport of [
      { width: 1440, height: 1000 },
      { width: 390, height: 844 },
      { width: 320, height: 568 },
      { width: 844, height: 390 },
    ]) {
      const p = await browser.newPage({ viewport });
      p.on('pageerror', error => failures.push(String(error)));
      await p.goto(`${base}/?qa=1`);
      await p.locator('.snake-hit').first().waitFor({ state: 'attached' });
      const layout = await p.evaluate(() => ({
        width: document.documentElement.scrollWidth,
        innerWidth,
        header: document.querySelector('.play-top').getBoundingClientRect().toJSON(),
        levelChip: document.querySelector('.level-chip').getBoundingClientRect().toJSON(),
        board: document.querySelector('.board-frame').getBoundingClientRect().toJSON(),
        height: innerHeight,
      }));
      assert.ok(layout.width <= layout.innerWidth + 1, `horizontal overflow at ${viewport.width}: ${layout.width}`);
      assert.ok(layout.board.width > 0 && layout.board.left >= -1 && layout.board.right <= layout.innerWidth + 1, JSON.stringify(layout));
      assert.ok(layout.header.height < 100 && layout.levelChip.width > 45, `header collapsed at ${viewport.width}: ${JSON.stringify(layout.header)}`);
      if (viewport.width === 320) await p.screenshot({ path: path.join(root, 'artifacts/responsive-320.png'), fullPage: true });
      if (viewport.width === 844) await p.screenshot({ path: path.join(root, 'artifacts/responsive-landscape.png'), fullPage: true });
      await p.close();
    }

    for (const [route, expectedSdk] of [['/coolmath', false], ['/crazygames', true]]) {
      const release = await browser.newPage({ viewport: { width: 375, height: 812 } });
      await release.route('https://**', handler => handler.abort());
      await release.goto(base + route);
      assert.equal(await release.evaluate(() => typeof window.VectorShiftDebug), 'undefined');
      assert.equal(await release.locator('html').getAttribute('lang'), 'en');
      assert.ok(await release.locator('.snake-hit').count() >= 2);
      assert.equal(await release.evaluate(() => document.documentElement.scrollWidth > innerWidth + 1), false);
      if (expectedSdk) assert.match(await release.locator('script[src]').evaluateAll(nodes => nodes.map(n => n.src).join('\n')), /crazygames-sdk/);
      else assert.doesNotMatch(await release.content(), /crazygames-sdk/);
      await release.close();
    }
    assert.deepEqual(failures, []);
    for (const [source, target] of [
      ['level20-desktop.png', 'level20.png'],
      ['level20-mobile.png', 'mobile.png'],
    ]) fs.copyFileSync(path.join(root, 'artifacts', source), path.join(root, 'artifacts', target));
    fs.copyFileSync(path.join(root, 'artifacts/level20-desktop.png'), path.join(root, 'submission/assets/desktop.png'));
    fs.copyFileSync(path.join(root, 'artifacts/level20-mobile.png'), path.join(root, 'submission/assets/mobile.png'));
    fs.copyFileSync(path.join(root, 'artifacts/daily-result-desktop.png'), path.join(root, 'artifacts/daily-result.png'));
    console.log('PASS path hit targets, touch/pinch, blocked feedback, zoom, exit guide, daily result, local resume, four viewports, two release builds');
  } finally {
    await browser.close();
    server.close();
  }
}

main().catch(error => { console.error(error); process.exitCode = 1; }).finally(() => server.close());
