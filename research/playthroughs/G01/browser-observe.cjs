const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const readline = require('readline');
const { chromium } = require('F:/beautiful/node_modules/playwright-core');
const root = __dirname;
const runtime = path.join(root, 'runtime');
const shots = path.join(root, 'screenshots');
fs.mkdirSync(runtime, {recursive:true});
fs.mkdirSync(shots, {recursive:true});
const log = path.join(root, 'operations.jsonl');
const start = process.hrtime.bigint();
const elapsed = () => Number(process.hrtime.bigint() - start) / 1e9;
const record = x => fs.appendFileSync(log, JSON.stringify(x) + '\n');
let context, shuttingDown = false;
const pages = new Map();
async function close(reason) {
  if (shuttingDown) return;
  shuttingDown = true;
  await context?.close();
  const e = {event:'context_closed', reason, at_utc:new Date().toISOString(), elapsed_s:elapsed(), normal_close:true};
  record(e); console.log(JSON.stringify(e));
}
async function main() {
  context = await chromium.launchPersistentContext(path.join(runtime, 'profile'), {
    executablePath:'C:/Users/whipa/AppData/Local/ms-playwright/chromium-1228/chrome-win64/chrome.exe',
    headless:true, viewport:{width:1365,height:900}, deviceScaleFactor:1,
    env:{...process.env,TEMP:runtime,TMP:runtime}, downloadsPath:runtime,
    acceptDownloads:false, locale:'en-US',
    args:['--no-first-run','--disable-default-apps','--disable-background-networking','--use-angle=swiftshader']
  });
  context.setDefaultTimeout(4000);
  record({event:'environment',at_utc:new Date().toISOString(),accessed_at:'2026-10-21',
    browser:context.browser().version(),os:process.platform,viewport:{width:1365,height:900},
    headless:true,device_scale_factor:1,touch_emulated:false,runtime:'runtime/',
    max_attempt_seconds:480,game_state_injection:false,game_source_saved:false,cookies_exported:false});
  console.log(JSON.stringify({ready:true,version:context.browser().version()}));
  const rl = readline.createInterface({input:process.stdin});
  const remaining = Math.max(1000, Math.min(480000, Date.parse('2026-10-21T10:46:35Z') - Date.now()));
  const watchdog = setTimeout(async()=>{try{await close('overall_attempt_limit');}finally{rl.close();process.exit(0);}},remaining);
  try {
    for await (const line of rl) {
      let c, entry;
      try {
        c = JSON.parse(line);
        if (c.op === 'quit') {await close('requested_end');rl.close();break;}
        entry = {event:'operation',...c,started_at_utc:new Date().toISOString(),started_elapsed_s:elapsed()};
        let p = pages.get(c.id);
        if(c.op === 'open') {
          p = await context.newPage();pages.set(c.id,p);
          try {const response=await p.goto(c.url,{waitUntil:'domcontentloaded',timeout:30000});entry.http_status=response?.status();}
          catch(e){entry.navigation_error=e.message.slice(0,500);}
        }
        if(!p)throw Error('Unknown page ID');
        await p.bringToFront();
        if(c.op === 'click')await p.mouse.click(c.x,c.y,{delay:c.delay_ms || 180});
        if(c.op === 'textclick')await p.getByText(c.text,{exact:true}).first().click();
        if(c.op === 'press')await p.keyboard.press(c.key);
        if(c.op === 'hold') {await p.keyboard.down(c.key);await p.waitForTimeout(c.ms);await p.keyboard.up(c.key);}
        if(c.op === 'drag') {await p.mouse.move(c.x,c.y);await p.mouse.down();await p.waitForTimeout(c.hold_ms || 200);await p.mouse.move(c.to_x,c.to_y,{steps:12});await p.mouse.up();}
        if(c.wait_ms)await p.waitForTimeout(Math.min(c.wait_ms,8000));
        entry.final_url=p.url();entry.title=await p.title();
        entry.frames=p.frames().map(f=>({name:f.name(),url_without_query:f.url().split('?')[0].split('#')[0]}));
        entry.canvases=[];
        for(const f of p.frames().filter(f => f === p.mainFrame() || /games\.playgama\.net|crazygames\.com\/gameframe/.test(f.url())).slice(0,12)) {
          try {
            const canvases=f.locator('canvas');const count=await canvases.count();
            for(let i=0;i<Math.min(count,3);i++)entry.canvases.push({frame_url_without_query:f.url().split('?')[0],box:await canvases.nth(i).boundingBox()});
          }catch(e){entry.canvas_metadata_error=e.message.slice(0,200);}
        }
        entry.buttons=await p.locator('button').allTextContents();
        entry.body_excerpt=(await p.locator('body').innerText()).slice(0,700);
        if(c.shot) {
          if(!/^[a-z0-9-]+$/.test(c.shot))throw Error('Invalid screenshot name');
          entry.screenshot='screenshots/'+c.shot+'.png';
          await p.screenshot({path:path.join(root,entry.screenshot),fullPage:false});
          entry.screenshot_sha256=crypto.createHash('sha256').update(fs.readFileSync(path.join(root,entry.screenshot))).digest('hex');
        }
        entry.ended_at_utc=new Date().toISOString();entry.ended_elapsed_s=elapsed();
        record(entry);
        console.log(JSON.stringify({id:c.id,op:c.op,url:entry.final_url,screenshot:entry.screenshot,canvas:entry.canvases,buttons:entry.buttons,elapsed_s:elapsed()}));
      }catch(e){const x={event:'operation_error',command:c,error:e.message,at_utc:new Date().toISOString(),elapsed_s:elapsed()};record(x);console.log(JSON.stringify(x));}
    }
  } finally {clearTimeout(watchdog);await close('input_ended');}
}
main().catch(async e=>{record({event:'fatal_error',error:e.message,at_utc:new Date().toISOString()});try{await close('fatal_error');}finally{process.exitCode=1;}});
