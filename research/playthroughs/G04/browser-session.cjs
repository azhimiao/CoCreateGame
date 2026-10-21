// Research-only browser input recorder. Does not copy game code or game assets.
// Run with node, then send one JSON command per stdin line; see README.md.
const fs = require('node:fs');
const path = require('node:path');
const readline = require('node:readline');
const crypto = require('node:crypto');
const { chromium } = require('F:/beautiful/node_modules/playwright-core');
const { PNG } = require('F:/beautiful/node_modules/pngjs');

const ROOT = path.resolve(__dirname);
const EXPECTED = path.resolve('F:/CoCreateGame/research/playthroughs/G04');
if (ROOT.toLowerCase() !== EXPECTED.toLowerCase()) throw new Error('Unexpected evidence root');
const RUNTIME = path.resolve(ROOT, 'runtime');
if (path.dirname(RUNTIME) !== ROOT || path.basename(RUNTIME) !== 'runtime') throw new Error('Unsafe runtime path');
const SHOTS = path.join(ROOT, 'screenshots');
fs.mkdirSync(SHOTS, { recursive: true });
fs.mkdirSync(RUNTIME, { recursive: true });
const LOG = path.join(ROOT, 'operations.jsonl');
const sessionId = new Date().toISOString().replace(/[:.]/g, '-');
let context, page, game = null, sequence = 0, lastShot = null, stopped = false;
const allowed = {
  bloxorz: 'https://www.coolmathgames.com/0-bloxorz',
  liquid2: 'https://www.coolmathgames.com/0-liquid-2',
  paintmaster: 'https://www.coolmathgames.com/0-paint-master',
};
function cleanUrl(s) { try { const u = new URL(s); return u.origin + u.pathname; } catch { return String(s).slice(0, 180); } }
function log(event, detail = {}) {
  const entry = { at: new Date().toISOString(), session_id: sessionId, game: game?.id ?? null,
    elapsed_ms: game ? Date.now() - game.started : null, event, ...detail };
  fs.appendFileSync(LOG, JSON.stringify(entry) + '\n', 'utf8');
  process.stdout.write(JSON.stringify(entry) + '\n');
  return entry;
}
function checkBudget() {
  if (!game) return;
  const anchor = game.observedAt ?? game.started;
  const limit = game.observedAt ? 300000 : 180000;
  if (Date.now() - anchor > limit) throw new Error(game.observedAt ? 'Observation wall-clock cap reached' : 'Troubleshooting wall-clock cap reached; finish this game');
}
async function snapshot(label) {
  const safe = String(label).replace(/[^a-zA-Z0-9_-]/g, '_').slice(0, 60);
  const filename = `${sessionId}-${game?.id ?? 'browser'}-${String(++sequence).padStart(3, '0')}-${safe}.png`;
  const file = path.join(SHOTS, filename);
  const data = await page.screenshot({ path: file, timeout: 8000 });
  let diff = null;
  if (lastShot) {
    const a = PNG.sync.read(lastShot), b = PNG.sync.read(data);
    if (a.width === b.width && a.height === b.height) {
      let pixels = 0, x0 = b.width, y0 = b.height, x1 = -1, y1 = -1;
      for (let y = 0; y < b.height; y++) for (let x = 0; x < b.width; x++) {
        const k = (y * b.width + x) * 4;
        if (Math.max(...[0, 1, 2].map(d => Math.abs(a.data[k+d] - b.data[k+d]))) > 20) {
          pixels++; x0 = Math.min(x0,x); y0 = Math.min(y0,y); x1 = Math.max(x1,x); y1 = Math.max(y1,y);
        }
      }
      diff = { pixels, bounds: pixels ? { x0, y0, x1, y1 } : null,
        caveat: 'Whole-viewport pixel change; animation/ads/scroll can change pixels without effective game input.' };
    }
  }
  lastShot = data;
  return log('screenshot', { label, file: 'screenshots/' + filename, sha256: crypto.createHash('sha256').update(data).digest('hex'), diff_from_previous: diff });
}
async function inspect() {
  const frames = [];
  for (const frame of page.frames()) {
    const item = { url: cleanUrl(frame.url()), name: frame.name() };
    try {
      item.visible_dom = await frame.evaluate(() => {
        const visible = e => { const r = e.getBoundingClientRect(); const s = getComputedStyle(e); return r.width > 0 && r.height > 0 && s.display !== 'none' && s.visibility !== 'hidden'; };
        return {
          title: document.title,
          body_excerpt: (document.body?.innerText ?? '').slice(0, 600),
          active_element: document.activeElement?.tagName,
          canvases: [...document.querySelectorAll('canvas, ruffle-player, embed, object')].filter(visible).map(e => ({ tag: e.tagName, id: e.id, width: e.getBoundingClientRect().width, height: e.getBoundingClientRect().height })),
          controls: [...document.querySelectorAll('button,input[type=button],input[type=submit],a,[role=button]')].filter(visible).map(e => ({ text: (e.innerText || e.value || e.getAttribute('aria-label') || '').trim().slice(0,70), tag: e.tagName, id:e.id })).filter(e => /play|start|skip|continue|reset|retry|next|close|reject|accept|consent/i.test(e.text)).slice(0, 22),
          iframes: [...document.querySelectorAll('iframe')].map(e => ({ id:e.id, title:e.title, src:e.getAttribute('src'), rect: { x:e.getBoundingClientRect().x, y:e.getBoundingClientRect().y, width:e.getBoundingClientRect().width, height:e.getBoundingClientRect().height } })).slice(0, 12)
        };
      });
      item.visible_dom.iframes = item.visible_dom.iframes.map(f => ({...f, src: cleanUrl(f.src ?? '')}));
    } catch (e) { item.inspect_error = e.message.slice(0, 200); }
    frames.push(item);
  }
  return log('inspection', { current_url: cleanUrl(page.url()), frames });
}
async function close() {
  if (stopped) return;
  stopped = true;
  if (context) await context.close().catch(e => log('close_error', { error:e.message.slice(0,200) }));
  // Only remove this explicitly validated, task-owned runtime after the browser closes.
  if (path.dirname(RUNTIME) !== ROOT || path.basename(RUNTIME) !== 'runtime') throw new Error('Cleanup path invalid');
  try { fs.rmSync(RUNTIME, { recursive: true, force: true, maxRetries: 3, retryDelay: 300 }); log('runtime_cleanup', { path:'runtime', removed: !fs.existsSync(RUNTIME) }); }
  catch(e) { log('runtime_cleanup', { path:'runtime', removed:false, error:e.message.slice(0,200), exclusion:'Temporary profile/cache is not evidence or a redistributable asset.' }); }
}
async function command(cmd) {
  if (cmd.op === 'close') { await close(); process.exit(0); }
  if (cmd.op === 'finish') { log('game_finished', { status:cmd.status, summary:cmd.summary, effective_gameplay_started:!!game?.observedAt }); game=null; lastShot=null; return; }
  if (cmd.op === 'navigate') {
    if (!allowed[cmd.game]) throw new Error('Game is outside the authorized reference set');
    if (game) throw new Error('Finish previous game first');
    game = { id:cmd.game, started:Date.now(), observedAt:null };
    log('navigation_start', { official_url:allowed[cmd.game], troubleshooting_cap_ms:180000 });
    try { const response = await page.goto(allowed[cmd.game], { waitUntil:'domcontentloaded', timeout:25000 }); log('navigation_response', { status:response?.status() }); }
    catch(e) { log('navigation_error', { error:e.message.slice(0,300) }); }
    await snapshot('official-page'); await inspect(); return;
  }
  checkBudget();
  if (cmd.op === 'inspect') return await inspect();
  if (cmd.op === 'shot') return await snapshot(cmd.label ?? 'manual');
  if (cmd.op === 'note') return log('observer_note', { claim:cmd.claim, evidence:cmd.evidence ?? [], status:cmd.status ?? 'UNCLASSIFIED' });
  if (cmd.op === 'confirm-input') {
    if (!cmd.evidence?.length || !cmd.description) throw new Error('Visual evidence and description required');
    game.observedAt = Date.now();
    return log('effective_game_input_confirmed_by_observer', { evidence:cmd.evidence, description:cmd.description, observation_cap_ms:300000, caveat:'This marker alone does not claim a complete 30-second or five-minute playthrough.' });
  }
  await snapshot('before-' + cmd.op);
  log('input_start', { command:cmd, dispatch_only:true });
  if (cmd.op === 'click') await page.mouse.click(cmd.x,cmd.y);
  else if (cmd.op === 'key') { for (const key of cmd.keys ?? [cmd.key]) { await page.keyboard.press(key); await page.waitForTimeout(Math.min(cmd.interval_ms ?? 350, 1500)); } }
  else if (cmd.op === 'hold') { await page.keyboard.down(cmd.key); try { await page.waitForTimeout(Math.min(cmd.ms ?? 400,3000)); } finally { await page.keyboard.up(cmd.key); } }
  else if (cmd.op === 'scroll') await page.mouse.wheel(cmd.dx ?? 0,cmd.dy ?? 400);
  else if (cmd.op === 'click-text') {
    const frame = cmd.frame_url_contains ? page.frames().find(f=>f.url().includes(cmd.frame_url_contains)) : page.mainFrame();
    if (!frame) throw new Error('Requested frame not found');
    await frame.getByText(cmd.text,{exact:true}).first().click({timeout:3000});
  }
  else throw new Error('Unknown command');
  await page.waitForTimeout(Math.min(cmd.settle_ms ?? 700, 4000));
  await snapshot('after-' + cmd.op);
  log('input_dispatch_complete', { command:cmd, effectiveness:'UNKNOWN_PENDING_VISUAL_REVIEW' });
}
(async()=>{
  const executablePath = path.join(process.env.LOCALAPPDATA, 'ms-playwright/chromium_headless_shell-1228/chrome-headless-shell-win64/chrome-headless-shell.exe');
  context = await chromium.launchPersistentContext(path.join(RUNTIME,'profile'), { executablePath, headless:true, viewport:{width:1365,height:900}, locale:'en-US', timezoneId:'Asia/Shanghai', args:['--disable-dev-shm-usage','--use-angle=swiftshader','--enable-unsafe-swiftshader'] });
  page = context.pages()[0] ?? await context.newPage();
  page.setDefaultTimeout(3000);
  page.on('pageerror',e=>log('page_error',{error:e.message.slice(0,220)}));
  page.on('requestfailed',r=>{ if (/document|script|fetch|xhr/.test(r.resourceType())) log('request_failed',{url:cleanUrl(r.url()),resource_type:r.resourceType(),failure:r.failure()?.errorText}); });
  page.on('response',r=>{ if (r.status()>=400 && ['document','script','fetch','xhr'].includes(r.request().resourceType())) log('http_error',{url:cleanUrl(r.url()),status:r.status()}); });
  log('browser_ready',{ browser_version:context.browser()?.version(), executable:executablePath, viewport:{width:1365,height:900}, source_access_date:'2026-10-21', profile:'runtime/profile', rights:'Screenshots are third-party research evidence, never own game assets.' });
  const rl = readline.createInterface({input:process.stdin,crlfDelay:Infinity});
  for await (const line of rl) { if (!line.trim()) continue; try { await command(JSON.parse(line)); } catch(e) { log('command_error',{error:e.message.slice(0,500)}); } }
  await close();
})().catch(async e=>{log('fatal_error',{error:e.message.slice(0,500)});await close();process.exitCode=1;});
process.on('SIGINT',()=>{close().finally(()=>process.exit(0));});
