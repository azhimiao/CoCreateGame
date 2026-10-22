'use strict';
const {chromium}=require('F:/beautiful/node_modules/playwright');
const fs=require('fs'),path=require('path'),crypto=require('crypto'),assert=require('node:assert/strict');
const results=[];
function record(name,data){results.push({name,data});fs.writeFileSync(path.join(__dirname,'closure-results.json'),JSON.stringify(results,null,2));console.log(JSON.stringify({name,data}));}
const delay=ms=>new Promise(r=>setTimeout(r,ms));
(async()=>{
const browser=await chromium.launch({headless:true,executablePath:'C:/Users/whipa/AppData/Local/ms-playwright/chromium_headless_shell-1228/chrome-headless-shell-win64/chrome-headless-shell.exe'});
try{
const context=await browser.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true,deviceScaleFactor:1});
const p=await context.newPage(),errors=[];p.on('pageerror',e=>errors.push(e.message));
const response=await p.goto('http://127.0.0.1:4173/');const html=await response.text();await p.waitForFunction(()=>!!window.VectorShiftDenseDebug);
const source=fs.readFileSync('games/VectorShift/src/dense-app.js','utf8');
const markers=[/exitDistance:\s*length\s*\+/,/showHead\s*=\s*true/,/const savedNumber\s*=/,/if\s*\(e.button\s*!==\s*0\)\s*return/,/anchorX:/,/number\s*=\s*lv\(\).arrows.indexOf\(a\)\s*\+\s*1/];
for(const marker of markers)assert.match(html,marker,'served app missing targeted fix: '+marker);
record('revision',{servedIncludesAllFiveFixes:true,servedMatchesLatestSource:html.replace(/\r\n/g,'\n').includes(source.replace(/\r\n/g,'\n')),sourceSHA256:crypto.createHash('sha256').update(source).digest('hex'),servedSHA256:crypto.createHash('sha256').update(html).digest('hex')});
await p.evaluate(()=>VectorShiftDenseDebug.setLevel(2));
await p.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
await p.evaluate(()=>VectorShiftDenseDebug.setReduced(true));
const prep=[];
while(await p.evaluate(()=>VectorShiftDenseDebug.getState().remaining.includes('s01'))){
 const target=await p.evaluate(()=>{const D=VectorShiftDenseDebug,C=VectorShiftDenseCore,l=D.getLevel(),s=D.getState();const id=s.remaining.find(id=>id!=='s04'&&C.clearPath(l,s,id));return{id,point:D.pointFor(id)}});
 assert.ok(target.id,'can legally clear s01 while retaining s04');
 await p.touchscreen.tap(target.point.x,target.point.y);await p.waitForFunction(id=>!VectorShiftDenseDebug.getState().remaining.includes(id),target.id,{timeout:2000});prep.push(target.id);
}
record('heart-legal-preparation',{removed:prep,s01Removed:true,s04Retained:true});
await p.evaluate(()=>VectorShiftDenseDebug.setReduced(false));
const info=await p.evaluate(()=>{
 const D=VectorShiftDenseDebug,C=VectorShiftDenseCore,l=D.getLevel(),a=l.arrows.find(a=>a.id==='s04'),cv=document.querySelector('#puzzleCanvas'),r=cv.getBoundingClientRect(),s=D.getDisplay().s;
 const cells=a.cells.slice(0,4);
 window.reviewSamplePixels=()=>cells.map(([x,y])=>{const sx=Math.round((18+(x+.5)*32)*s),sy=Math.round((18+(y+.5)*32)*s);return {cell:[x,y],rgba:[...cv.getContext('2d').getImageData(sx,sy,1,1).data]}});
 return {point:D.pointFor('s04'),clear:C.clearPath(l,D.getState(),'s04'),samples:window.reviewSamplePixels(),remaining:D.getState().remaining.length};
});
assert.equal(info.clear,true);
await p.screenshot({path:path.join(__dirname,'closed-heart-before.png')});
// Hold animation time/RAF solely to inspect the exact initial paint after a native tap.
await p.evaluate(()=>{window.reviewOriginalNow=performance.now.bind(performance);window.reviewTime=performance.now();performance.now=()=>window.reviewTime;window.reviewOriginalRAF=requestAnimationFrame;window.requestAnimationFrame=()=>999999});
await p.touchscreen.tap(info.point.x,info.point.y);
const first=await p.evaluate(()=>({samples:window.reviewSamplePixels(),animation:VectorShiftDenseDebug.getAnimation(),state:VectorShiftDenseDebug.getState()}));
for(const sample of first.samples)assert.ok(sample.rgba[3]>220,`tail ${sample.cell} must remain visible in initial frame`);
assert.equal(first.state.remaining.length,info.remaining-1);
await p.screenshot({path:path.join(__dirname,'closed-heart-first-frame.png')});
record('heart-original-tail-preserved',{before:info.samples,first:first.samples,animation:first.animation,remaining:first.state.remaining.length});
const duration=first.animation[0].duration;
for(const fraction of [.18,.5,1.01]){
 await p.evaluate(({duration,fraction})=>{window.reviewTime+=duration*fraction;VectorShiftDenseDebug.render()}, {duration,fraction});
 await p.screenshot({path:path.join(__dirname,`closed-heart-frame-${fraction}.png`)});
}
await p.evaluate(()=>{performance.now=window.reviewOriginalNow;window.requestAnimationFrame=window.reviewOriginalRAF;VectorShiftDenseDebug.render()});
assert.equal(await p.evaluate(()=>VectorShiftDenseDebug.getAnimation().length),0);

await p.evaluate(()=>VectorShiftDenseDebug.setLevel(1));
const native=await context.newCDPSession(p),box=await p.locator('#puzzleCanvas').boundingBox(),cx=box.x+box.width/2,cy=box.y+box.height/2;
await native.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x:120,y:330,id:1},{x:180,y:390,id:2}]});
await native.send('Input.dispatchTouchEvent',{type:'touchMove',touchPoints:[{x:100,y:310,id:1},{x:200,y:410,id:2}]});
await native.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});
const view=await p.evaluate(()=>VectorShiftDenseDebug.getView());
const anchored={x:cx+(150-cx)*view.zoom+view.x,y:cy+(360-cy)*view.zoom+view.y};
const drift=Math.hypot(anchored.x-150,anchored.y-360);
assert.ok(view.zoom>1.6&&drift<1,JSON.stringify({view,anchored,drift}));
assert.equal(await p.evaluate(()=>VectorShiftDenseDebug.getState().moves),0);
record('offcenter-pinch',{view,expected:{x:150,y:360},actual:anchored,driftCssPixels:drift,moves:0});
// Also ensure one fit tap works after pinch+pan, and is not activated twice.
await native.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x:cx,y:cy,id:3}]});
await native.send('Input.dispatchTouchEvent',{type:'touchMove',touchPoints:[{x:cx+55,y:cy+35,id:3}]});
await native.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});
await p.locator('#zoomButton').tap();await p.waitForFunction(()=>VectorShiftDenseDebug.getView().zoom===1);
await delay(400);assert.deepEqual(await p.evaluate(()=>VectorShiftDenseDebug.getView()),{zoom:1,x:0,y:0});
record('fit-after-pinch-pan',{singleTapWorks:true,noDelayedDoubleActivation:true});

const target=await p.evaluate(()=>{const D=VectorShiftDenseDebug,id=D.getSolution().actions[0].id;return{id,point:D.pointFor(id)}});
await p.mouse.click(target.point.x,target.point.y,{button:'right'});
assert.equal(await p.evaluate(()=>VectorShiftDenseDebug.getState().moves),0);
const zh=await p.locator('#keyboardLayer button').first().innerText();assert.match(zh,/第1条小蛇/);assert.doesNotMatch(zh,/s01/);
const english=await context.newPage();await english.goto('http://127.0.0.1:4173/?lang=en');await english.waitForFunction(()=>!!window.VectorShiftDenseDebug);
const en=await english.locator('#keyboardLayer button').first().innerText();assert.match(en,/Snake 1,/);
record('right-click-and-labels',{rightClickMoves:0,zh,en});

const level=JSON.parse(fs.readFileSync('games/VectorShift/data/dense-levels.json','utf8'))[0];
const validState={remaining:level.arrows.map(a=>a.id),moves:0,history:[]};
const cases=[
 {name:'overflow-strings',elapsed:'1e309',hints:'1e309',mistakes:'1e309',expectedHints:0,expectedMistakes:0},
 {name:'fractional-counts',elapsed:-10,hints:2.9,mistakes:3.7,expectedHints:2,expectedMistakes:3},
 {name:'huge-and-negative',elapsed:1e100,hints:-4,mistakes:1e100,expectedHints:0,expectedMistakes:0}
];
for(const item of cases){
 const c=await browser.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true});
 await c.addInitScript(({validState,item})=>localStorage.setItem('vector-shift-dense-v1',JSON.stringify({index:0,runs:{'dense-01':{state:validState,elapsed:item.elapsed,hints:item.hints,mistakes:item.mistakes}}})),{validState,item});
 const page=await c.newPage();await page.goto('http://127.0.0.1:4173/');await page.waitForFunction(()=>!!window.VectorShiftDenseDebug);
 const stats=await page.evaluate(()=>VectorShiftDenseDebug.getStats());
 assert.ok(Number.isFinite(stats.elapsed)&&stats.elapsed>=0&&stats.elapsed<5000);assert.equal(stats.hints,item.expectedHints);assert.equal(stats.mistakes,item.expectedMistakes);
 record(`saved-stats-${item.name}`,stats);
 if(item.name==='overflow-strings'){
  await page.evaluate(()=>VectorShiftDenseDebug.setReduced(true));
  for(let i=0;i<level.arrows.length;i++){
   const point=await page.evaluate(()=>{const D=VectorShiftDenseDebug;return D.pointFor(D.getSolution().actions[0].id)});await page.touchscreen.tap(point.x,point.y);
  }
  await page.waitForSelector('#nextPattern');const win=await page.locator('#dialogContent').innerText();assert.doesNotMatch(win,/NaN|Infinity/);
  await page.screenshot({path:path.join(__dirname,'closed-normalized-stats-win.png')});record('saved-stats-result',win);
 }
 await c.close();
}
assert.deepEqual(errors,[]);record('completed',{fiveFindingsClosed:true,pageErrors:errors});
}finally{await browser.close()}
})().catch(e=>{record('failure',{message:e.message,stack:e.stack});process.exitCode=1});
