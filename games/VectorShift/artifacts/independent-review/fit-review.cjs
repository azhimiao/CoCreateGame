const {chromium}=require('F:/beautiful/node_modules/playwright');
const fs=require('fs'),path=require('path');
(async()=>{
const browser=await chromium.launch({headless:true,executablePath:'C:/Users/whipa/AppData/Local/ms-playwright/chromium_headless_shell-1228/chrome-headless-shell-win64/chrome-headless-shell.exe'});
const results=[];
try{
 const context=await browser.newContext({viewport:{width:390,height:844},hasTouch:true,isMobile:true,deviceScaleFactor:2});
 const p=await context.newPage();await p.goto('http://127.0.0.1:4173/');await p.waitForFunction(()=>!!window.VectorShiftDenseDebug);
 await p.evaluate(()=>{
  window.reviewEvents=[];
  for(const type of ['pointerdown','pointerup','pointercancel','touchstart','touchend','click'])document.addEventListener(type,e=>{
   const entry={type,target:e.target.id,time:performance.now(),zoom:VectorShiftDenseDebug.getView().zoom,trusted:e.isTrusted};window.reviewEvents.push(entry);
   if(type==='click')queueMicrotask(()=>window.reviewEvents.push({type:'after-click',target:e.target.id,time:performance.now(),zoom:VectorShiftDenseDebug.getView().zoom}));
  },true);
 });
 const session=await context.newCDPSession(p);
 for(let i=0;i<20;i++){
  await p.evaluate(()=>{VectorShiftDenseDebug.setLevel(1);window.reviewEvents=[]});
  const hp=await p.evaluate(()=>{const D=VectorShiftDenseDebug;return D.pointFor(D.getSolution().actions[0].id)});
  await p.touchscreen.tap(hp.x,hp.y);await p.waitForFunction(()=>VectorShiftDenseDebug.getState().moves===1);
  await p.locator('#undoButton').tap();await p.waitForFunction(()=>VectorShiftDenseDebug.getState().moves===0);
  const box=await p.locator('#puzzleCanvas').boundingBox(),cx=box.x+box.width/2,cy=box.y+box.height/2;
  const points=span=>[{x:cx-span,y:cy,id:1},{x:cx+span,y:cy,id:2}];
  await session.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:points(35)});
  await session.send('Input.dispatchTouchEvent',{type:'touchMove',touchPoints:points(80)});
  await session.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});
  await session.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x:cx,y:cy,id:3}]});
  await session.send('Input.dispatchTouchEvent',{type:'touchMove',touchPoints:[{x:cx+55,y:cy+35,id:3}]});
  await session.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});
  const before=await p.evaluate(()=>VectorShiftDenseDebug.getView());
  await p.locator('#zoomButton').tap();
  const immediate=await p.evaluate(()=>({time:performance.now(),view:VectorShiftDenseDebug.getView(),events:window.reviewEvents.slice(-8)}));
  let failed=false;
  try{await p.waitForFunction(()=>{const v=VectorShiftDenseDebug.getView();return v.zoom===1&&v.x===0&&v.y===0},null,{timeout:1000})}catch{failed=true}
  const settled=await p.evaluate(()=>({time:performance.now(),view:VectorShiftDenseDebug.getView(),events:window.reviewEvents.slice(-8),remaining:VectorShiftDenseDebug.getState().remaining.length}));
  results.push({iteration:i,before,immediate,settled,failed});
  console.log(JSON.stringify({iteration:i,immediateZoom:immediate.view.zoom,settledZoom:settled.view.zoom,delay:settled.time-immediate.time,failed}));
 }
 fs.writeFileSync(path.join(__dirname,'fit-results.json'),JSON.stringify(results,null,2));
 console.log(JSON.stringify({iterations:results.length,staleImmediateReads:results.filter(r=>r.immediate.view.zoom!==1).length,failedFits:results.filter(r=>r.failed).length}));
}finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
