const fs = require('fs');
const path = require('path');
const readline = require('readline');
const { chromium } = require('F:/beautiful/node_modules/playwright-core');
const root = path.resolve(__dirname);
const runtime = path.join(root, 'runtime');
const pages = new Map();
const sessionFile = path.join(root, 'session.json');
const journal = fs.existsSync(sessionFile) ? JSON.parse(fs.readFileSync(sessionFile,'utf8')) : [];
let ctx;
async function main() {
  ctx = await chromium.launchPersistentContext(path.join(runtime,'profile'), {
    executablePath:'C:/Users/whipa/AppData/Local/ms-playwright/chromium-1228/chrome-win64/chrome.exe',
    headless:true, viewport:{width:1365,height:900},
    env:{...process.env,TEMP:runtime,TMP:runtime},
    downloadsPath:runtime, acceptDownloads:false,
    args:['--no-first-run','--disable-default-apps','--disable-background-networking','--use-angle=swiftshader']
  });
  console.log(JSON.stringify({ready:true,version:ctx.browser().version()}));
  const rl=readline.createInterface({input:process.stdin});
  for await (const line of rl) {
    let cmd;
    try {
      cmd=JSON.parse(line);
      if(cmd.op==='quit'){
        await ctx.close();
        journal.push({op:'quit',wall_clock:new Date().toISOString(),research_accessed_at:'2026-10-21',context_close_completed:true});
        fs.writeFileSync(sessionFile,JSON.stringify(journal,null,2));
        rl.close();
        break;
      }
      let p=pages.get(cmd.id);
      const entry={...cmd,wall_clock:new Date().toISOString(),research_accessed_at:'2026-10-21'};
      if(cmd.op==='open'){
        p=await ctx.newPage();pages.set(cmd.id,p);
        entry.errors=[];p.on('pageerror',e=>entry.errors.push(e.message.slice(0,300)));
        try {const r=await p.goto(cmd.url,{waitUntil:'domcontentloaded',timeout:30000});entry.http_status=r?.status();}catch(e){entry.navigation_error=e.message;}
      }
      await p.bringToFront();
      if(cmd.op==='click')await p.mouse.click(cmd.x,cmd.y);
      if(cmd.op==='textclick')await p.getByText(cmd.text,{exact:true}).first().click({timeout:5000});
      if(cmd.op==='press')await p.keyboard.press(cmd.key);
      if(cmd.op==='hold'){await p.keyboard.down(cmd.key);await p.waitForTimeout(cmd.ms);await p.keyboard.up(cmd.key);}
      if(cmd.op==='drag'){await p.mouse.move(cmd.x,cmd.y);await p.mouse.down();await p.mouse.move(cmd.to_x,cmd.to_y,{steps:10});await p.mouse.up();}
      if(cmd.wait_ms)await p.waitForTimeout(Math.min(cmd.wait_ms,15000));
      entry.url=p.url();entry.title=await p.title();
      entry.frames=p.frames().map(f=>({name:f.name(),url:f.url()}));
      entry.buttons=await p.locator('button').allTextContents();
      entry.canvases=[];
      for(const f of p.frames()){
        try {for(const c of await f.locator('canvas').all())entry.canvases.push({frame:f.url(),box:await c.boundingBox()});}catch{}
      }
      entry.body_excerpt=(await p.locator('body').innerText()).slice(0,1800);
      if(cmd.shot){entry.screenshot='screenshots/'+cmd.shot+'.png';await p.screenshot({path:path.join(root,entry.screenshot),fullPage:false});}
      journal.push(entry);fs.writeFileSync(sessionFile,JSON.stringify(journal,null,2));
      console.log(JSON.stringify({op:entry.op,id:entry.id,url:entry.url,shot:entry.screenshot,canvas_count:entry.canvases.length,wall_clock:entry.wall_clock}));
    } catch(e){console.log(JSON.stringify({cmd,error:e.message}));}
  }
}
main().catch(e=>{console.error(e);process.exitCode=1;});
