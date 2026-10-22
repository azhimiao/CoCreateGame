const {chromium}=require('F:/beautiful/node_modules/playwright');
const fs=require('fs'),path=require('path'),crypto=require('crypto');
(async()=>{
 const b=await chromium.launch({headless:true,executablePath:'C:/Users/whipa/AppData/Local/ms-playwright/chromium_headless_shell-1228/chrome-headless-shell-win64/chrome-headless-shell.exe'});
 try{
 const c=await b.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true});const p=await c.newPage();
 const response=await p.goto('http://127.0.0.1:4173/');const html=await response.text();await p.waitForFunction(()=>!!window.VectorShiftDenseDebug);
 const code=fs.readFileSync('games/VectorShift/src/dense-app.js','utf8');
 const revision={sourceSHA256:crypto.createHash('sha256').update(code).digest('hex'),servedSHA256:crypto.createHash('sha256').update(html).digest('hex'),servedLatestCode:html.replace(/\r\n/g,'\n').includes(code.replace(/\r\n/g,'\n')),servedFocusFix:html.includes('hadFocus=holder.contains'),servedPauseFix:html.includes('paused=true')};
 const D=()=>p.evaluate(()=>{const d=VectorShiftDenseDebug;return{view:d.getView(),stats:d.getStats(),state:d.getState()}});
 let clear=await p.evaluate(()=>{const d=VectorShiftDenseDebug,id=d.getSolution().actions[0].id;return{id,point:d.pointFor(id)}});
 await p.mouse.click(clear.point.x,clear.point.y,{button:'right'});
 const rightClick={target:clear.id,after:await D()};
 await p.evaluate(()=>VectorShiftDenseDebug.retry());
 const native=await c.newCDPSession(p);
 const start=[{x:120,y:330,id:1},{x:180,y:390,id:2}];
 const canvas=await p.locator('#puzzleCanvas').boundingBox();
 await native.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:start});
 await native.send('Input.dispatchTouchEvent',{type:'touchMove',touchPoints:[{x:100,y:310,id:1},{x:200,y:410,id:2}]});
 await native.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});
 const v=(await D()).view,cx=canvas.x+canvas.width/2,cy=canvas.y+canvas.height/2;
 const pinch={stationaryFingersMidpoint:{x:150,y:360},view:v,boardPointNow:{x:cx+(150-cx)*v.zoom+v.x,y:cy+(360-cy)*v.zoom+v.y},moves:(await D()).state.moves};
 await p.locator('#zoomButton').tap();
 clear=await p.evaluate(()=>VectorShiftDenseDebug.getSolution().actions[0].id);await p.locator('#puzzleCanvas').focus();
 for(let i=0;i<50;i++){if(await p.evaluate(()=>document.activeElement.dataset.snakeId)===String(clear))break;await p.keyboard.press('Tab')}
 await p.keyboard.press('Enter');
 const keyboard={active:await p.evaluate(()=>({tag:document.activeElement.tagName,id:document.activeElement.id,snake:document.activeElement.dataset.snakeId})),firstLabel:await p.locator('#keyboardLayer button').first().innerText()};
 // Exercise actual visibility handling through CDP freeze; event observations determine
 // whether this environment can test background time without a DOM mock.
 const lifecycle=[];await p.exposeFunction('reviewVisibility',e=>lifecycle.push(e));
 await p.evaluate(()=>document.addEventListener('visibilitychange',()=>window.reviewVisibility({hidden:document.hidden,time:performance.now(),elapsed:VectorShiftDenseDebug.getStats().elapsed})));
 const beforeFreeze=(await D()).stats.elapsed;
 await native.send('Page.setWebLifecycleState',{state:'frozen'});await new Promise(r=>setTimeout(r,1000));await native.send('Page.setWebLifecycleState',{state:'active'});
 const afterFreeze=(await D()).stats.elapsed;
 const result={revision,rightClick,pinch,keyboard,lifecycle,beforeFreeze,afterFreeze};
 fs.writeFileSync(path.join(__dirname,'final-check.json'),JSON.stringify(result,null,2));console.log(JSON.stringify(result,null,2));
 }finally{await b.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
