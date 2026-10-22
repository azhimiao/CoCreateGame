'use strict';
const {chromium}=require('F:/beautiful/node_modules/playwright');
const fs=require('node:fs'),path=require('node:path');
const results=[];function record(name,data){results.push({name,data});console.log(JSON.stringify({name,data}));fs.writeFileSync(path.join(__dirname,'motion-results.json'),JSON.stringify(results,null,2));}
const wait=ms=>new Promise(r=>setTimeout(r,ms));
(async()=>{
const browser=await chromium.launch({headless:true,executablePath:'C:/Users/whipa/AppData/Local/ms-playwright/chromium_headless_shell-1228/chrome-headless-shell-win64/chrome-headless-shell.exe'});
try{
const context=await browser.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true,deviceScaleFactor:1});
const p=await context.newPage();await p.goto('http://127.0.0.1:4173/');await p.waitForFunction(()=>!!window.VectorShiftDenseDebug);
const levels=await p.evaluate(()=>VectorShiftDenseDebug.levels.map(l=>({id:l.id,pieces:l.arrows.length})));
record('levels-under-test',levels);
// All legal pieces are tapped using real touchscreen input, alternating head/body.
for(let i=0;i<levels.length;i++){
 await p.evaluate(n=>{VectorShiftDenseDebug.setLevel(n);VectorShiftDenseDebug.setReduced(true)},i+1);
 const failures=[];
 for(let k=0;k<levels[i].pieces;k++){
  const info=await p.evaluate(k=>{const D=VectorShiftDenseDebug,id=D.getSolution().actions[0].id;return{id,point:k%2?D.bodyPointFor(id):D.pointFor(id),before:D.getState().remaining}},k);
  await p.touchscreen.tap(info.point.x,info.point.y);
  const after=await p.evaluate(()=>VectorShiftDenseDebug.getState());
  if(after.remaining.includes(info.id)||after.remaining.length!==info.before.length-1){failures.push({step:k,info,after});break;}
 }
 await p.waitForSelector('#nextPattern');
 record(`touch-entire-level-${i+1}`,{failures,remaining:await p.locator('#remainingCount').innerText(),progress:await p.locator('#progressTrack').getAttribute('aria-valuenow'),win:await p.locator('#dialogContent').innerText()});
 await p.keyboard.press('Escape');
}
// Reproduce the heart's s04 body crossing its exit clipping plane.
await p.evaluate(()=>{const D=VectorShiftDenseDebug;D.setLevel(2);D.setReduced(true);for(const a of D.getSolution().actions){if(a.id==='s04')break;D.tap(a.id)}D.setReduced(false)});
const pre=await p.evaluate(()=>{
 const D=VectorShiftDenseDebug,C=VectorShiftDenseCore,l=D.getLevel(),a=l.arrows.find(a=>a.id==='s04'),cv=document.querySelector('#puzzleCanvas'),r=cv.getBoundingClientRect(),s=D.getDisplay().s;
 return {id:a.id,d:a.d,cells:a.cells,head:D.pointFor(a.id),clear:C.clearPath(l,D.getState(),a.id),samples:a.cells.map(([x,y])=>({x:r.x+(18+(x+.5)*32)*s,y:r.y+(18+(y+.5)*32)*s}))};
});
await p.screenshot({path:path.join(__dirname,'heart-s04-before.png')});
// Hold RAF only so the screenshot catches the first paint, not the final state.
await p.evaluate(()=>{window.__originalRAF=requestAnimationFrame;window.__reviewCallbacks=[];window.requestAnimationFrame=cb=>{window.__reviewCallbacks.push(cb);return 99999}});
await p.touchscreen.tap(pre.head.x,pre.head.y);
await p.screenshot({path:path.join(__dirname,'heart-s04-first-frame.png')});
record('heart-clip-first-frame',{pre,animation:await p.evaluate(()=>VectorShiftDenseDebug.getAnimation())});
await p.evaluate(()=>{window.requestAnimationFrame=window.__originalRAF;VectorShiftDenseDebug.render()});
await wait(700);
// Hidden-page timer can be observed without changing app clocks. This page stays
// backgrounded while a second page is active; Chromium headless visibility differs.
const visibility=await p.evaluate(()=>({hidden:document.hidden,state:document.visibilityState,stats:VectorShiftDenseDebug.getStats()}));
record('visibility-environment',visibility);
// Capture actual malformed keyboard labels and canvas-to-button focus loss.
await p.evaluate(()=>VectorShiftDenseDebug.setLevel(1));
record('keyboard-names',await p.locator('#keyboardLayer button').allTextContents());
await p.locator('#puzzleCanvas').focus();await p.keyboard.press('ArrowRight');await p.keyboard.press('Enter');
record('canvas-keyboard-focus',await p.evaluate(()=>({active:document.activeElement.id,remaining:VectorShiftDenseDebug.getState().remaining.length})));
// Existing state is validated. A forged clear is rejected and replaced by fresh.
await p.evaluate(()=>{let store=JSON.parse(localStorage.getItem('vector-shift-dense-v1'));store.runs[VectorShiftDenseDebug.getLevel().id].state={remaining:[],moves:0,history:[]};localStorage.setItem('vector-shift-dense-v1',JSON.stringify(store))});
const forged=await context.newPage();await forged.goto('http://127.0.0.1:4173/');await forged.waitForFunction(()=>!!window.VectorShiftDenseDebug);
record('forged-clear-rejected',await forged.evaluate(()=>VectorShiftDenseDebug.getState()));
// Finite stats must be shape-checked too: array containers accept state writes but
// JSON.stringify([]) drops string level keys, silently losing all progress.
const acontext=await browser.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true});
await acontext.addInitScript(()=>{if(!sessionStorage.getItem('array-seeded')){localStorage.setItem('vector-shift-dense-v1',JSON.stringify({runs:[],completed:[]}));sessionStorage.setItem('array-seeded','1')}});
const ap=await acontext.newPage();await ap.goto('http://127.0.0.1:4173/');await ap.waitForFunction(()=>!!window.VectorShiftDenseDebug);
const apoint=await ap.evaluate(()=>{const D=VectorShiftDenseDebug;return D.pointFor(D.getSolution().actions[0].id)});await ap.touchscreen.tap(apoint.x,apoint.y);
const arrayBefore=await ap.evaluate(()=>({moves:VectorShiftDenseDebug.getState().moves,saved:JSON.parse(localStorage.getItem('vector-shift-dense-v1'))}));
await ap.reload();await ap.waitForFunction(()=>!!window.VectorShiftDenseDebug);
record('array-run-save-loss',{before:arrayBefore,after:await ap.evaluate(()=>VectorShiftDenseDebug.getState().moves)});
}finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
