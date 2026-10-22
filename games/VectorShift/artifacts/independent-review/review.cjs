'use strict';
const {chromium}=require('F:/beautiful/node_modules/playwright');
const fs=require('node:fs');
const path=require('node:path');
const out=__dirname;
const results=[];
function record(name,data){results.push({name,data}); console.log(JSON.stringify({name,data}));fs.writeFileSync(path.join(out,'results.json'),JSON.stringify(results,null,2));}
const base='http://127.0.0.1:4173/';
const delay=ms=>new Promise(r=>setTimeout(r,ms));
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:'C:/Users/whipa/AppData/Local/ms-playwright/chromium_headless_shell-1228/chrome-headless-shell-win64/chrome-headless-shell.exe'});
 try {
 const ctx=await browser.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true,deviceScaleFactor:1});
 const p=await ctx.newPage(),errors=[];p.on('pageerror',e=>errors.push(e.message));
 await p.goto(base);await p.waitForFunction(()=>!!window.VectorShiftDenseDebug);
 record('loaded',{title:await p.title(),url:p.url(),errors});
 for(const [width,height] of [[320,568],[360,800],[390,844],[412,915],[568,320],[667,375],[844,390]]){
   await p.setViewportSize({width,height});await delay(100);
   const layout=await p.evaluate(()=>({viewport:[innerWidth,innerHeight],scroll:[document.documentElement.scrollWidth,document.documentElement.scrollHeight],display:VectorShiftDenseDebug.getDisplay(),elements:[...document.querySelectorAll('#gameShell,#boardRegion,#puzzleCanvas,.game-controls,#undoButton,#hintButton,#zoomButton,#restartButton,#helpButton')].map(e=>({id:e.id||e.className,x:e.getBoundingClientRect().x,y:e.getBoundingClientRect().y,w:e.getBoundingClientRect().width,h:e.getBoundingClientRect().height}))}));
   record(`layout-${width}-${height}`,layout);await p.screenshot({path:path.join(out,`layout-${width}-${height}.png`),fullPage:true});
 }
 await p.setViewportSize({width:390,height:844});await delay(100);
 const target=()=>p.evaluate(()=>{const D=VectorShiftDenseDebug,id=D.getSolution().actions[0].id;return {id,point:D.pointFor(id),body:D.bodyPointFor(id)}});
 let t=await target();await p.touchscreen.tap(t.body.x,t.body.y);
 record('real-touch-body-remove',await p.evaluate(()=>({state:VectorShiftDenseDebug.getState(),stats:VectorShiftDenseDebug.getStats(),animation:VectorShiftDenseDebug.getAnimation(),remainingText:document.querySelector('#remainingCount').textContent})));
 await p.screenshot({path:path.join(out,'exit-motion.png')});await delay(650);
 const blocked=await p.evaluate(()=>{const D=VectorShiftDenseDebug,C=VectorShiftDenseCore,l=D.getLevel(),s=D.getState(),id=s.remaining.find(id=>!C.clearPath(l,s,id));return{id,point:D.pointFor(id)}});
 await p.touchscreen.tap(blocked.point.x,blocked.point.y);
 record('blocked-touch',await p.evaluate(()=>({state:VectorShiftDenseDebug.getState(),stats:VectorShiftDenseDebug.getStats(),feedback:document.querySelector('#feedback').textContent})));
 await p.locator('#hintButton').tap();const beforeReload=await p.evaluate(()=>({state:VectorShiftDenseDebug.getState(),stats:VectorShiftDenseDebug.getStats()}));
 await p.reload();await p.waitForFunction(()=>!!window.VectorShiftDenseDebug);
 record('restored',{before:beforeReload,after:await p.evaluate(()=>({state:VectorShiftDenseDebug.getState(),stats:VectorShiftDenseDebug.getStats(),feedback:document.querySelector('#feedback').textContent}))});
 await p.locator('#undoButton').tap();record('undo-after-reload',await p.evaluate(()=>({state:VectorShiftDenseDebug.getState(),stats:VectorShiftDenseDebug.getStats()})));
 // A cancelled drag must not turn into a tap, and a zoomed drag must pan.
 t=await target();let moves=await p.evaluate(()=>VectorShiftDenseDebug.getState().moves);
 await p.mouse.move(t.point.x,t.point.y);await p.mouse.down();await p.mouse.move(t.point.x+60,t.point.y+40,{steps:5});await p.mouse.up();
 record('drag-at-fit',{before:moves,after:await p.evaluate(()=>VectorShiftDenseDebug.getState().moves)});
 await p.locator('#zoomButton').tap();t=await target();await p.mouse.move(195,400);await p.mouse.down();await p.mouse.move(230,440,{steps:6});await p.mouse.up();
 record('pan-zoomed',await p.evaluate(()=>VectorShiftDenseDebug.getView()));await p.locator('#zoomButton').tap();
 // CDP sends native touchscreen events, not synthetic DOM handlers.
 const cdp=await ctx.newCDPSession(p);
 const pinchStart=[{x:120,y:330,id:1},{x:180,y:390,id:2}];
 await cdp.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:pinchStart});
 for(let i=1;i<=5;i++)await cdp.send('Input.dispatchTouchEvent',{type:'touchMove',touchPoints:[{x:120-i*4,y:330-i*4,id:1},{x:180+i*4,y:390+i*4,id:2}]});
 await cdp.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});
 record('native-pinch',await p.evaluate(()=>({view:VectorShiftDenseDebug.getView(),moves:VectorShiftDenseDebug.getState().moves})));
 await p.locator('#zoomButton').tap();
 // Right-click is not a release action.
 t=await target();await p.mouse.click(t.point.x,t.point.y,{button:'right'});
 record('right-click',{id:t.id,state:await p.evaluate(()=>VectorShiftDenseDebug.getState())});
 await p.evaluate(()=>VectorShiftDenseDebug.retry());
 // Actual keyboard focuses the hidden controls and activates the clear arrow.
 const clear=await p.evaluate(()=>VectorShiftDenseDebug.getSolution().actions[0].id);
 await p.locator('#puzzleCanvas').focus();
 let tabs=0;for(;tabs<50;tabs++){const id=await p.evaluate(()=>document.activeElement.dataset.snakeId);if(id===String(clear))break;await p.keyboard.press('Tab')}
 const focusedBefore=await p.evaluate(()=>({tag:document.activeElement.tagName,id:document.activeElement.id,snake:document.activeElement.dataset.snakeId}));
 await p.keyboard.press('Enter');
 const focusedAfter=await p.evaluate(()=>({tag:document.activeElement.tagName,id:document.activeElement.id,snake:document.activeElement.dataset.snakeId,moves:VectorShiftDenseDebug.getState().moves}));
 await p.keyboard.press('Tab');
 record('keyboard-release-focus',{tabs,before:focusedBefore,after:focusedAfter,next:await p.evaluate(()=>({tag:document.activeElement.tagName,id:document.activeElement.id,snake:document.activeElement.dataset.snakeId}))});
 // Persisted counter corruption is separate from the validated core state.
 await p.evaluate(()=>{const s=JSON.parse(localStorage.getItem('vector-shift-dense-v1')),id=VectorShiftDenseDebug.getLevel().id;s.runs[id].elapsed='1e309';s.runs[id].hints='1e309';s.runs[id].mistakes='1e309';localStorage.setItem('vector-shift-dense-v1',JSON.stringify(s));});
 // A fresh page preserves the seeded storage; reloading the old page calls save().
 const bad=await ctx.newPage();await bad.goto(base);await bad.waitForFunction(()=>!!window.VectorShiftDenseDebug);
 record('nonfinite-stats',await bad.evaluate(()=>({stats:VectorShiftDenseDebug.getStats(),encoded:[VectorShiftDenseDebug.getStats().elapsed,VectorShiftDenseDebug.getStats().hints].map(String)})));
 await bad.evaluate(()=>{const D=VectorShiftDenseDebug;D.setReduced(true);for(const a of D.getSolution().actions)D.tap(a.id)});await bad.waitForSelector('#nextPattern');
 record('nonfinite-win',{text:await bad.locator('#dialogContent').innerText()});await bad.screenshot({path:path.join(out,'nonfinite-win.png')});
 record('page-errors',errors);
 } finally {await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1});
