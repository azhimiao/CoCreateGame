// Research recorder: normal UI input and visible-DOM diagnostics; no game-state access.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),readline=require('node:readline');
const {chromium}=require('F:/beautiful/node_modules/playwright-core');
const {PNG}=require('F:/beautiful/node_modules/pngjs');
const ROOT=path.resolve(__dirname),EXPECTED=path.resolve('F:/CoCreateGame/research/playthroughs/G02');
if(ROOT.toLowerCase()!==EXPECTED.toLowerCase())throw Error('Unexpected evidence root');
const RUNTIME=path.resolve(ROOT,'runtime'),SHOTS=path.join(ROOT,'screenshots');
if(path.dirname(RUNTIME)!==ROOT||path.basename(RUNTIME)!=='runtime')throw Error('Unsafe runtime path');
fs.mkdirSync(SHOTS,{recursive:true});fs.mkdirSync(RUNTIME,{recursive:true});
const session=new Date().toISOString().replace(/[:.]/g,'-');
const allowed={goodsort:'https://playgama.com/game/good-sort-master',screwout:'https://www.crazygames.com/game/screw-out-bolts-and-nuts'};
let context,page,game=null,sequence=0,lastShot=null,attemptStarted=null,deadline=null,timer=null,closed=false;
function url(s){return String(s??'').split('?')[0].split('#')[0].replace(/(\/challenge-platform\/).*/,'$1[omitted]').replace(/[0-9a-f]{8}-[0-9a-f-]{27,}/gi,'[identifier-omitted]');}
function log(event,detail={}){const row={at:new Date().toISOString(),session_id:session,game:game?.id??null,game_elapsed_ms:game?Date.now()-game.started:null,attempt_elapsed_ms:attemptStarted?Date.now()-attemptStarted:null,event,...detail};fs.appendFileSync(path.join(ROOT,'operations.jsonl'),JSON.stringify(row)+'\n');process.stdout.write(JSON.stringify(row)+'\n');return row;}
async function shot(label){
 const name=`${session}-${game?.id??'browser'}-${String(++sequence).padStart(3,'0')}-${String(label).replace(/[^a-zA-Z0-9_-]/g,'_').slice(0,50)}.png`;
 const data=await page.screenshot({path:path.join(SHOTS,name),timeout:6000});let diff=null;
 if(lastShot){const a=PNG.sync.read(lastShot),b=PNG.sync.read(data);if(a.width===b.width&&a.height===b.height){let count=0;for(let k=0;k<b.data.length;k+=4)if(Math.max(Math.abs(a.data[k]-b.data[k]),Math.abs(a.data[k+1]-b.data[k+1]),Math.abs(a.data[k+2]-b.data[k+2]))>20)count++;diff={pixels:count,caveat:'Animation, ads and scrolling may change pixels; not proof of effective game input'};}}
 lastShot=data;return log('screenshot',{label,file:'screenshots/'+name,sha256:crypto.createHash('sha256').update(data).digest('hex'),diff_from_previous:diff});
}
async function inspect(){const frames=[];for(const f of page.frames()){
 const item={url:url(f.url()),name:f.name()};
 const hostOk=/^https:\/\/([^/]*\.)?(playgama\.com|crazygames\.com)\//.test(f.url());
 if(f===page.mainFrame()||hostOk)try{item.ui=await f.evaluate(main=>{
  const visible=e=>{const r=e.getBoundingClientRect(),s=getComputedStyle(e);return r.width>0&&r.height>0&&s.display!=='none'&&s.visibility!=='hidden';};
  return {title:document.title,body_excerpt:main?(document.body?.innerText??'').slice(0,900):'[Subframe body omitted; interface geometry only]',active_element:document.activeElement?.tagName,
   canvases:[...document.querySelectorAll('canvas')].filter(visible).map(e=>({tag:e.tagName,rect:e.getBoundingClientRect().toJSON()})),
   controls:[...document.querySelectorAll('button,a,[role=button],input[type=button]')].filter(visible).map(e=>({text:(e.innerText||e.value||e.getAttribute('aria-label')||'').trim().slice(0,70),rect:e.getBoundingClientRect().toJSON()})).filter(e=>/play|start|continue|retry|next|close|ignore|reject|accept|consent|no thanks|decline/i.test(e.text)).slice(0,25),
   iframes:[...document.querySelectorAll('iframe')].filter(visible).map(e=>({title:e.title,src:e.getAttribute('src'),rect:e.getBoundingClientRect().toJSON()})).slice(0,8)};
 },f===page.mainFrame());if(item.ui?.iframes)for(const i of item.ui.iframes)i.src=url(i.src);}catch(e){item.error=e.message.slice(0,150);}else item.dom_omitted='Auxiliary/external frame: no DOM text or source collected';frames.push(item);
 }return log('inspection',{current_url:url(page.url()),frames});}
async function close(reason='operator-close'){
 if(closed)return;closed=true;if(timer)clearTimeout(timer);log('browser_closing',{reason});
 if(context)await context.close().catch(e=>log('close_error',{error:e.message.slice(0,150)}));
 if(path.dirname(RUNTIME)!==ROOT||path.basename(RUNTIME)!=='runtime')throw Error('Invalid cleanup target');
 try{fs.rmSync(RUNTIME,{recursive:true,force:true,maxRetries:3,retryDelay:250});log('runtime_cleanup',{removed:!fs.existsSync(RUNTIME),path:'runtime'});}catch(e){log('runtime_cleanup',{removed:false,path:'runtime',error:e.message.slice(0,180),exclusion:'Temporary profile/cache excluded from evidence'});}
}
async function command(c){
 const ops=['close','finish','navigate','shot','inspect','note','confirm-input','click','click-text','drag','key','scroll'];
 if(!ops.includes(c.op))throw Error('Use a supported op field');
 if(c.op==='close'){await close();process.exit(0);}
 if(c.op==='finish'){log('game_finished',{status:c.status,summary:c.summary,effective_core_input_confirmed:!!game?.confirmed});game=null;lastShot=null;return;}
 if(c.op==='note')return log('observer_note',{status:c.status??'UNCLASSIFIED',claim:c.claim,evidence:c.evidence??[]});
 if(c.op==='navigate'){
  if(game)throw Error('Finish prior game first');if(!allowed[c.game])throw Error('URL outside authorized set');
  if(!attemptStarted){const prior=fs.readFileSync(path.join(ROOT,'operations.jsonl'),'utf8').trim().split(/\r?\n/).map(JSON.parse).find(r=>r.event==='navigation_start');attemptStarted=prior?Date.parse(prior.at):Date.now();deadline=attemptStarted+480000;timer=setTimeout(async()=>{log('attempt_cap_reached',{cap_ms:480000});await close('eight-minute-wall-clock-cap');process.exit(0);},Math.max(1,deadline-Date.now()));}
  if(Date.now()>=deadline)throw Error('Eight-minute total cap reached');
  game={id:c.game,started:Date.now(),confirmed:false};lastShot=null;
  log('navigation_start',{official_url:allowed[c.game],remaining_attempt_ms:deadline-Date.now()});
  try{const response=await page.goto(allowed[c.game],{waitUntil:'domcontentloaded',timeout:25000});log('navigation_response',{status:response?.status(),final_url:url(page.url())});}catch(e){log('navigation_error',{error:e.message.slice(0,200)});}
  await shot('official-page');await inspect();return;
 }
 if(!game)throw Error('Navigate to a game first');if(Date.now()>=deadline)throw Error('Eight-minute total cap reached');
 if(c.op==='shot')return shot(c.label??'manual');if(c.op==='inspect')return inspect();
 if(c.op==='confirm-input'){if(!c.evidence?.length||!c.description)throw Error('Evidence and visual description required');game.confirmed=true;return log('effective_core_input_confirmed_by_observer',{description:c.description,evidence:c.evidence,continuous_time_coverage:false});}
 await shot('before-'+c.op);log('input_start',{command:c,dispatch_only:true});
 if(c.op==='click')await page.mouse.click(c.x,c.y);
 else if(c.op==='click-text'){const f=c.frame_url_contains?page.frames().find(f=>f.url().includes(c.frame_url_contains)):page.mainFrame();if(!f)throw Error('Frame not found');await f.getByText(c.text,{exact:true}).first().click({timeout:2500});}
 else if(c.op==='drag'){await page.mouse.move(c.from.x,c.from.y);await page.mouse.down();try{await page.mouse.move(c.to.x,c.to.y,{steps:c.steps??16});await page.waitForTimeout(Math.min(c.drop_hold_ms??150,500));}finally{await page.mouse.up();}}
 else if(c.op==='key'){for(const k of c.keys){await page.keyboard.press(k);await page.waitForTimeout(150);}}
 else if(c.op==='scroll')await page.mouse.wheel(c.dx??0,c.dy??400);
 await page.waitForTimeout(Math.min(c.settle_ms??700,2500));await shot('after-'+c.op);log('input_dispatch_complete',{command:c,effectiveness:'UNKNOWN_UNTIL_VISUAL_REVIEW'});
}
(async()=>{
 const executablePath=path.join(process.env.LOCALAPPDATA,'ms-playwright/chromium_headless_shell-1228/chrome-headless-shell-win64/chrome-headless-shell.exe');
 context=await chromium.launchPersistentContext(path.join(RUNTIME,'profile'),{executablePath,headless:true,viewport:{width:1365,height:900},locale:'en-US',timezoneId:'Asia/Shanghai',args:['--disable-dev-shm-usage','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
 page=context.pages()[0]??await context.newPage();page.setDefaultTimeout(2500);
 page.on('pageerror',e=>log('page_error',{error:e.message.slice(0,200)}));
 page.on('requestfailed',r=>{if(r.resourceType()==='document'||(/playgama\.com|crazygames\.com/.test(r.url())&&['script','fetch','xhr'].includes(r.resourceType())))log('request_failed',{url:url(r.url()),resource_type:r.resourceType(),failure:r.failure()?.errorText});});
 page.on('response',r=>{if(r.status()>=400&&r.request().resourceType()==='document')log('http_error',{url:url(r.url()),status:r.status()});});
 log('browser_ready',{browser_version:context.browser()?.version(),executable:executablePath,viewport:{width:1365,height:900},device:{type:'desktop-headless',touch:false,device_scale_factor:1,locale:'en-US',timezone:'Asia/Shanghai',os:process.platform,node:process.version},profile:'runtime/profile',rights:'Third-party screenshots for research only, never own production assets',coverage:'Discrete screenshots; no continuous30s/5min claim',attempt_cap_ms:480000});
 const rl=readline.createInterface({input:process.stdin,crlfDelay:Infinity});for await(const line of rl){if(!line.trim())continue;try{await command(JSON.parse(line));}catch(e){log('command_error',{error:e.message.slice(0,300)});}}await close('stdin-ended');
})().catch(async e=>{log('fatal_error',{error:e.message.slice(0,300)});await close('fatal');process.exitCode=1;});
process.on('SIGINT',()=>close('SIGINT').finally(()=>process.exit(0)));
