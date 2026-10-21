/* Offline-first UI. All gameplay and tests use VectorShiftCore, no remote requests. */
(function(){'use strict';
const core=window.VectorShiftCore, levels=window.LEVELS||LEVELS, CHANNEL=window.VS_CHANNEL||'demo';
const LOCALE=CHANNEL==='demo'?'zh':'en';
const $=id=>document.getElementById(id);
const STORE='vector-shift-v05-progress', TELEMETRY_STORE='vector-shift-v05-playtest';
const RUN_STORE='vector-shift-active-run-v1';
const SOUND_STORE='vector-shift-v05-sound', ONBOARD_STORE='vector-shift-v05-onboarded';
const PHASE_TIP_STORE='vector-shift-v05-phase-tip', HINT_TIP_STORE='vector-shift-v05-hint-tip';
const SETTINGS_STORE='vector-shift-v05-settings', DAILY_STORE='vector-shift-v05-daily';
const BUILD='1.0.0-phase-shift';
const TOTAL=levels.length;
const STR={
en:{
 helpBtn:'Help', settingsBtn:'Settings', dailyBtn:'Daily',
 remain:'Left', moves:'Moves', phase:'Phase', legendCyan:'Phase', legendGold:'Fixed',
 mistakes:'Misses', seconds:'Time', hints:'Hints', streak:'Day streak', share:'Share result', copied:'Result copied.',
 zoomOut:'Zoom out', zoomIn:'Zoom in', zoomReset:'Reset view', visualizer:'Show all exits', hideVisualizer:'Hide exit guide',
 exitCampaign:'Campaign', stars:'STARS', dailyStatus:'TODAY',
 dailyRecord:(moves,elapsed)=>`Best ${moves} moves · ${formatTime(elapsed)}`,
 bestNone:'Clear the board', bestFmt:(m,t)=>`Best ${m} / ${t} shifts`,
 prev:'←', levels:'Levels', next:'→',
 phaseTitle:'Phase', phaseDetail:p=>`→ ${p}`, undo:'Undo', reset:'Retry',
 hint:'Hint', feedbackStart:'Tap an arrow.',
 exportBtn:'Export log', soundOn:'Sound: On', soundOff:'Sound: Off',
 footerL:'Vector Shift © 2026', footerR:'',
 footerDemoL:'Vector Shift · demo', footerDemoR:'',
 dir:['up','right','down','left'],
 ariaBlue:(r,c,d)=>`Phase arrow, row ${r} column ${c}, facing ${d}`,
 ariaGold:(r,c,d)=>`Fixed arrow, row ${r} column ${c}, facing ${d}`,
 blocked:'Blocked — clear the path or shift phase.',
 blockedSoft:'Still blocked. Hint shows a safe move.',
 removed:'Sliding off…',
 toggled:p=>`Phase ${p}. Blue arrows turned.`,
 undid:'Undone.', restarted:'Restarted.',
 dead:'No solution here — Undo or Retry.', already:'Already clear.',
 hintToggle:'Hint: shift phase.', hintCell:(r,c)=>`Hint: arrow at row ${r}, column ${c}.`,
 startEasy:'Clear path? Tap it.', startLater:'Find the leaving order.',
 dailyStart:'Daily challenge — same puzzle all day (local).',
 teachFallbackEarly:'Arrows slide off when the path ahead is clear.',
 teachFallbackLate:'Some stages need more than one phase shift.',
 winSub:(last,n,daily)=>daily?'DAILY CLEAR':(last?`ALL ${TOTAL} CLEAR`:`LEVEL ${n}`),
 winTitle:(last,daily)=>daily?'Daily board cleared.':(last?'All levels cleared.':'Nice clear.'),
 winBody:(moves,toggles,delta)=>`You used <strong>${moves}</strong> moves and <strong>${toggles}</strong> phase shifts.${delta===0?' Shortest known path.':` ${delta} above shortest.`}`,
 showOptimal:'Show shortest path', hideOptimal:'Hide path',
 optimalLabel:'Shortest known path:',
 replay:'Again', viewAll:'All levels', cont:'Next →', close:'Close',
 levelsSub:'LEVELS', levelsTitle:`${TOTAL} stages`,
 levelsBlurb:'Finish a stage to unlock the next. Progress stays on this device.',
 done:'Done', unlocked:'Open', locked:'Locked',
 helpSub:'HOW TO PLAY', helpTitle:'Three rules.',
 help1:'<strong>① Tap an arrow</strong> when the path from its head to the board edge (or silhouette edge) is empty — the whole snake slides off.',
 help2:'<strong>② Phase</strong> rotates every blue arrow (and its body) 90°. Gold stays fixed.',
 help3:'<strong>③ Clear the board</strong>. Order matters. Undo, Retry, or Hint anytime.',
 helpKeys:'Zoom with the controls or pinch. At 100% you can drag to pan. Desktop: Space = phase, Z = undo, R = retry.',
 helpGo:'Play',
 onboardSub:'QUICK START', onboardTitle:'Level 1 in three steps',
 onboard1:'Arrows leave only if nothing sits on their path to the edge.',
 onboard2:'Tap a clear arrow — body follows the head off the board.',
 onboard3:'Empty the board. Later levels add Phase for blue arrows.',
 onboardNext:'Next', onboardGo:'Got it',
 phaseTip:'Blue arrows rotate together when you shift Phase.',
 phaseTipDismiss:'Got it',
 hintCoach:'Stuck? Hint shows one safe next move.',
 hintCoachDismiss:'OK',
 settingsSub:'SETTINGS', settingsTitle:'Preferences',
 setSound:'Sound effects', setQuietHints:'Quieter hints', setHaptics:'Vibration feedback',
 setShowOptimal:'Offer “show shortest path” after a win',
 setClear:'Clear progress…', setClearConfirm:'Erase unlocked stages and best scores on this device?',
 setYes:'Yes, reset', setCancel:'Cancel', setDone:'Done',
 setCleared:'Progress cleared.',
 dailySub:'DAILY', dailyTitle:(ymd)=>`Challenge · ${ymd}`,
 dailyBlurb:'One shared daily board. Your time, misses and streak stay on this device.',
 dailyPlay:'Play today', dailyBack:'Back',
 dailyDone:'Already cleared today.',
 chapterCampaign:'LEVEL', chapterDaily:'DAILY'
},
zh:{
 helpBtn:'说明', settingsBtn:'设置', dailyBtn:'每日',
 remain:'剩余', moves:'步数', phase:'相位', legendCyan:'可变', legendGold:'固定',
 mistakes:'误点', seconds:'用时', hints:'提示', streak:'连续天数', share:'分享成绩', copied:'成绩已复制。',
 zoomOut:'缩小棋盘', zoomIn:'放大棋盘', zoomReset:'恢复棋盘视图', visualizer:'显示全部出口', hideVisualizer:'收起出口指引',
 exitCampaign:'返回关卡', stars:'星级', dailyStatus:'今日挑战',
 dailyRecord:(moves,elapsed)=>`最佳 ${moves} 步 · ${formatTime(elapsed)}`,
 bestNone:'清空棋盘', bestFmt:(m,t)=>`最佳 ${m} 步 / ${t} 次`,
 prev:'←', levels:'关卡', next:'→',
 phaseTitle:'相位', phaseDetail:p=>`→ ${p}`, undo:'撤销', reset:'重开',
 hint:'提示', feedbackStart:'点选一个箭头。',
 exportBtn:'导出记录', soundOn:'音效：开', soundOff:'音效：关',
 footerL:'相位箭头 © 2026', footerR:'',
 footerDemoL:'相位箭头 · 演示', footerDemoR:'',
 dir:['上','右','下','左'],
 ariaBlue:(r,c,d)=>`相位箭头，第${r}行第${c}列，向${d}`,
 ariaGold:(r,c,d)=>`固定箭头，第${r}行第${c}列，向${d}`,
 blocked:'前方有阻挡。先清开路，或切换相位。',
 blockedSoft:'还是被挡住了。可点「提示」。',
 removed:'滑出中…',
 toggled:p=>`相位 ${p}。蓝色箭头已转向。`,
 undid:'已撤销。', restarted:'已重开。',
 dead:'死局 — 请撤销或重开。', already:'已经清空。',
 hintToggle:'提示：先切换相位。', hintCell:(r,c)=>`提示：第 ${r} 行、第 ${c} 列。`,
 startEasy:'前方畅通？点它。', startLater:'找出离开的顺序。',
 dailyStart:'每日挑战——同一天同一道本地关卡。',
 teachFallbackEarly:'箭头前方畅通时会整条滑出棋盘。',
 teachFallbackLate:'有些关卡需要多次切换相位。',
 winSub:(last,n,daily)=>daily?'每日完成':(last?`全部 ${TOTAL} 关`:`第 ${n} 关`),
 winTitle:(last,daily)=>daily?'今日已清空。':(last?'全部通关。':'漂亮。'),
 winBody:(moves,toggles,delta)=>`用了 <strong>${moves}</strong> 步，相位 <strong>${toggles}</strong> 次。${delta===0?'已是最短。':`距最短差 ${delta} 步。`}`,
 showOptimal:'显示最短路径', hideOptimal:'收起',
 optimalLabel:'最短路径：',
 replay:'再来', viewAll:'全部关卡', cont:'下一关 →', close:'关闭',
 levelsSub:'关卡', levelsTitle:`${TOTAL} 关`,
 levelsBlurb:'通关解锁下一关。进度保存在本机。',
 done:'完成', unlocked:'可玩', locked:'锁定',
 helpSub:'玩法', helpTitle:'三条规则。',
 help1:'<strong>① 点击箭头</strong>：从头到棋盘/剪影边缘畅通时，整条蛇形箭头滑出。',
 help2:'<strong>② 相位</strong>：蓝色箭头（含身体）旋转 90°；金色不变。',
 help3:'<strong>③ 清空棋盘</strong>。顺序很重要。可撤销、重开或提示。',
 helpKeys:'可用按钮缩放或双指缩放；放大后拖动棋盘。快捷键：Space 相位，Z 撤销，R 重开。',
 helpGo:'开始',
 onboardSub:'上手', onboardTitle:'第 1 关三步',
 onboard1:'只有朝向边界的路径畅通时，箭头才能离场。',
 onboard2:'点击畅通箭头，身体会跟着头部滑出。',
 onboard3:'清空棋盘即通关。稍后会引入蓝色相位。',
 onboardNext:'下一步', onboardGo:'明白了',
 phaseTip:'切换相位时，蓝色箭头会一起旋转。',
 phaseTipDismiss:'知道了',
 hintCoach:'卡住了？提示会标出一步安全操作。',
 hintCoachDismiss:'好的',
 settingsSub:'设置', settingsTitle:'偏好',
 setSound:'音效', setQuietHints:'减少提示文案', setHaptics:'触觉反馈',
 setShowOptimal:'通关后可显示最短路径',
 setClear:'清除进度…', setClearConfirm:'确定清除本机进度？',
 setYes:'确认', setCancel:'取消', setDone:'完成',
 setCleared:'已清除。',
 dailySub:'每日', dailyTitle:(ymd)=>`挑战 · ${ymd}`,
 dailyBlurb:'每天一道共同挑战。用时、误点与连续天数只保存在本机。',
 dailyPlay:'今日挑战', dailyBack:'返回',
 dailyDone:'今日已通关。',
 chapterCampaign:'关卡', chapterDaily:'每日'
}
};
const t=STR[LOCALE];
let progress={unlocked:1,completed:[],best:{},dailyCleared:{}};
let settings={quietHints:false,showOptimal:true,haptics:true};
let telemetry=[],current=0,state=null,sound=false,qa=false;
let blockedTimer=0,completionScheduled=false,crazyReady=false,gameplayStarted=false,onboardStep=0;
let blockedStreak=0,mode='campaign',dailyIndex=null,particles=[],visualizer=false;
let animating=false,pressId=null;
let hintsUsed=0,mistakes=0,elapsedBeforePause=0,runStartedAt=Date.now(),zoom=1,pan={x:0,y:0},framePointers=new Map(),frameGesture=null,suppressedClicks=new Set(),modalReturnFocus=null;

try{
 progress={...progress,...JSON.parse(localStorage.getItem(STORE)||'{}')};
 progress.unlocked=Math.max(1,Math.min(levels.length,progress.unlocked||1));
 if(!Array.isArray(progress.completed))progress.completed=[];
 if(!progress.best||typeof progress.best!=='object')progress.best={};
 if(!progress.dailyCleared||typeof progress.dailyCleared!=='object')progress.dailyCleared={};
 progress.dailyStreak=Math.max(0,Number(progress.dailyStreak)||0);
 progress.dailyDates=Array.isArray(progress.dailyDates)?progress.dailyDates.filter(x=>/^\d{4}-\d{2}-\d{2}$/.test(x)):[];
 telemetry=JSON.parse(localStorage.getItem(TELEMETRY_STORE)||'[]');
 if(!Array.isArray(telemetry))telemetry=[];
 sound=localStorage.getItem(SOUND_STORE)==='1';
 settings={...settings,...JSON.parse(localStorage.getItem(SETTINGS_STORE)||'{}')};
}catch{}
if(CHANNEL==='demo')qa=new URLSearchParams(location.search).has('qa');
document.documentElement.lang=LOCALE==='zh'?'zh-CN':'en';

function persist(){try{localStorage.setItem(STORE,JSON.stringify(progress))}catch{}}
function persistSound(){try{localStorage.setItem(SOUND_STORE,sound?'1':'0')}catch{}}
function persistSettings(){try{localStorage.setItem(SETTINGS_STORE,JSON.stringify(settings))}catch{}}
function runElapsed(){return elapsedBeforePause+Math.max(0,Date.now()-runStartedAt)}
function runStoreKey(target=mode){return RUN_STORE+(target==='daily'?'-daily':'-campaign')}
function saveRun(){
 if(!state||qa)return;
 try{localStorage.setItem(runStoreKey(),JSON.stringify({version:1,mode,current,dailyIndex,dailyDate:mode==='daily'?todayKey():null,state,hintsUsed,mistakes,elapsed:runElapsed()}))}catch{}
}
function restoreRun(target=mode){
 try{
  const saved=JSON.parse(localStorage.getItem(runStoreKey(target))||'null');
  if(!saved||saved.version!==1||saved.mode!==target)return false;
  if(target==='daily'&&saved.dailyDate!==todayKey())return false;
  if(!Number.isInteger(saved.current)||saved.current<0||saved.current>=levels.length)return false;
  if(target==='campaign'&&!qa&&saved.current+1>progress.unlocked)return false;
  const index=target==='daily'?saved.dailyIndex:saved.current;
  if(!Number.isInteger(index)||index<0||index>=levels.length)return false;
  const lv=levels[index],s=saved.state,ids=lv.arrows.map(a=>a.id);
  if(!s||![0,1].includes(s.phase)||!Array.isArray(s.remaining)||!Array.isArray(s.history)||!Number.isInteger(s.moves)||!Number.isInteger(s.toggles))return false;
  if(new Set(s.remaining).size!==s.remaining.length||s.remaining.some(id=>!ids.includes(id)))return false;
  if(s.history.some(h=>![0,1].includes(h.phase)||!Array.isArray(h.remaining)||h.remaining.some(id=>!ids.includes(id))))return false;
  if(!Array.isArray(s.history)||s.history.some(h=>!Array.isArray(h.remaining)||new Set(h.remaining).size!==h.remaining.length||h.remaining.some(id=>!ids.includes(id))||!Number.isInteger(h.moves)||!Number.isInteger(h.toggles)))return false;
  if(s.remaining.length+s.moves-s.toggles!==ids.length||s.history.length!==s.moves||s.history.some((h,i)=>h.moves!==i||h.toggles<0||h.toggles>h.moves))return false;
  mode=target;current=saved.current;dailyIndex=mode==='daily'?index:null;state=s;
  hintsUsed=Math.max(0,Number(saved.hintsUsed)||0);mistakes=Math.max(0,Number(saved.mistakes)||0);
  elapsedBeforePause=Math.max(0,Number(saved.elapsed)||0);runStartedAt=Date.now();
  return true;
 }catch{return false}
}
function log(event,detail={}){if(CHANNEL==='coolmath')return;const item={event,at:new Date().toISOString(),level:mode==='daily'?('daily:'+todayKey()):(current+1),phase:state?.phase??0,mode,...detail};telemetry.push(item);if(telemetry.length>1000)telemetry.shift();try{localStorage.setItem(TELEMETRY_STORE,JSON.stringify(telemetry))}catch{}}
function level(){return mode==='daily'&&dailyIndex!=null?levels[dailyIndex]:levels[current]}
function teachingText(){
 const lv=level();
 if(mode==='daily')return t.dailyStart;
 if(LOCALE==='en'&&lv.teachingEn)return lv.teachingEn;
 if(LOCALE==='zh'&&lv.teaching)return lv.teaching;
 if(LOCALE==='en'&&lv.teaching)return lv.teaching;
 return current>=28?t.teachFallbackLate:t.teachFallbackEarly;
}
function message(text,tone=''){const el=$('feedback');el.textContent=text;el.className='response'+(tone?' '+tone:'')}
function reducedMotion(){return matchMedia('(prefers-reduced-motion: reduce)').matches}
function haptic(pattern){if(!settings.haptics||typeof navigator.vibrate!=='function')return;try{navigator.vibrate(pattern)}catch{}}
function todayKey(){
 const d=new Date();
 return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`;
}
function formatTime(ms){const total=Math.floor(Math.max(0,ms)/1000);return `${String(Math.floor(total/60)).padStart(2,'0')}:${String(total%60).padStart(2,'0')}`}
function previousDate(key){const [y,m,d]=key.split('-').map(Number),date=new Date(Date.UTC(y,m-1,d-1));return `${date.getUTCFullYear()}-${String(date.getUTCMonth()+1).padStart(2,'0')}-${String(date.getUTCDate()).padStart(2,'0')}`}
function recordDailyClear(key){
 if(progress.dailyCleared[key])return;
 const yesterday=previousDate(key);
 progress.dailyStreak=progress.lastDailyDate===yesterday?progress.dailyStreak+1:1;
 progress.lastDailyDate=key;
 progress.dailyDates=Array.isArray(progress.dailyDates)?progress.dailyDates:[];
 progress.dailyDates.push(key);if(progress.dailyDates.length>400)progress.dailyDates=progress.dailyDates.slice(-400);
 progress.dailyCleared[key]=true;
}
function dailyLevelIndex(){
 const key=todayKey();let h=2166136261;
 for(let i=0;i<key.length;i++){h^=key.charCodeAt(i);h=Math.imul(h,16777619)}
 const poolStart=Math.min(20,levels.length-1);
 return poolStart+(Math.abs(h)%(levels.length-poolStart));
}

function cellMetrics(){
 const board=$('board');
 const size=level().size;
 const width=board.clientWidth,height=board.clientHeight;
 const styles=getComputedStyle(board);
 const gap=parseFloat(styles.gap)||3;
 const cell=(width-(size-1)*gap)/size;
 return {cell,gap,pad:0,size,width,height};
}
function cellCenter(x,y,m){
 return {cx:x*(m.cell+m.gap)+m.cell/2, cy:y*(m.cell+m.gap)+m.cell/2};
}
function polylinePoints(cells,m){
 return cells.map(([x,y])=>{const p=cellCenter(x,y,m);return `${p.cx},${p.cy}`}).join(' ');
}
function headTriangle(hx,hy,d,m,scale=0.64){
 const p=cellCenter(hx,hy,m);
 const s=m.cell*scale;
 const tips=[
  [[0,-s],[-s*0.72,s*0.62],[s*0.72,s*0.62]],
  [[s,0],[-s*0.62,-s*0.72],[-s*0.62,s*0.72]],
  [[0,s],[-s*0.72,-s*0.62],[s*0.72,-s*0.62]],
  [[-s,0],[s*0.62,-s*0.72],[s*0.62,s*0.72]]
 ][d];
 return tips.map(([dx,dy])=>`${p.cx+dx},${p.cy+dy}`).join(' ');
}
const BLUE_PAL=['#2ec4d6','#3d9bff','#5b8def','#00bfa6','#7c6cf0','#20c997','#4cc9f0','#4361ee'];
const GOLD_PAL=['#ff9f1c','#ff7a59','#f4a261','#ffa62b','#ffb703','#fb8500','#ef476f','#06d6a0'];
function snakeColors(a){
 const pal=a.color==='gold'?GOLD_PAL:BLUE_PAL;
 const fill=pal[Math.abs(a.id|0)%pal.length];
 const deep=a.color==='gold'?'#b45309':'#0e7490';
 return {fill,deep,outline:'#14202c',hi:'#ffffff'};
}
function offsetPolyline(cells,m,ox,oy){
 return cells.map(([x,y])=>{const p=cellCenter(x,y,m);return `${p.cx+ox},${p.cy+oy}`}).join(' ');
}
function headChevron(hx,hy,d,m,scale=0.72){
 const p=cellCenter(hx,hy,m);
 const s=m.cell*scale;
 const tips=[
  [[0,-s*1.05],[-s*0.78,s*0.55],[0,s*0.18],[s*0.78,s*0.55]],
  [[s*1.05,0],[-s*0.55,-s*0.78],[-s*0.18,0],[-s*0.55,s*0.78]],
  [[0,s*1.05],[-s*0.78,-s*0.55],[0,-s*0.18],[s*0.78,-s*0.55]],
  [[-s*1.05,0],[s*0.55,-s*0.78],[s*0.18,0],[s*0.55,s*0.78]]
 ][d];
 return tips.map(([dx,dy])=>`${p.cx+dx},${p.cy+dy}`).join(' ');
}
function eyePair(hx,hy,d,m,bodyW){
 const p=cellCenter(hx,hy,m);
 const back=[-m.cell*0.08,-m.cell*0.18,m.cell*0.08,m.cell*0.18][d]||0;
 // eyes sit slightly behind tip, spaced perpendicular to facing
 const along=[[0,-1],[1,0],[0,1],[-1,0]][d];
 const perp=[[1,0],[0,1],[-1,0],[0,-1]][d];
 const base={cx:p.cx+along[0]*m.cell*0.02, cy:p.cy+along[1]*m.cell*0.02};
 const spread=bodyW*0.22;
 const r=Math.max(3.2, bodyW*0.16);
 const pupil=r*0.42;
 const eyes=[];
 for(const sign of [-1,1]){
  const cx=base.cx+perp[0]*spread*sign - along[0]*m.cell*0.12;
  const cy=base.cy+perp[1]*spread*sign - along[1]*m.cell*0.12;
  eyes.push({cx,cy,r,px:cx+along[0]*pupil*0.35,py:cy+along[1]*pupil*0.35,pr:pupil});
 }
 return eyes;
}

function applyChrome(){
 if($('helpButton'))$('helpButton').textContent='?';
 if($('settingsButton'))$('settingsButton').textContent=t.settingsBtn;
 if($('dailyButton'))$('dailyButton').textContent=t.dailyBtn;
 if($('labelRemain'))$('labelRemain').textContent=t.remain;
 if($('labelMistakes'))$('labelMistakes').textContent=t.mistakes;
 if($('labelMoves'))$('labelMoves').textContent=t.moves;
 if($('labelPhase'))$('labelPhase').textContent=t.phase;
 if($('legendCyan'))$('legendCyan').textContent=t.legendCyan;
 if($('legendGold'))$('legendGold').textContent=t.legendGold;
 $('prevButton').textContent=t.prev;
 if($('levelMenuButton'))$('levelMenuButton').setAttribute('aria-label',t.levels);
 $('nextButton').textContent=t.next;
 $('phaseBtnTitle').textContent=t.phaseTitle;
 if($('undoLabel'))$('undoLabel').textContent=t.undo;
 if($('resetLabel'))$('resetLabel').textContent=t.reset;
 $('hintLabel').textContent=t.hint;
 if($('exportButton'))$('exportButton').textContent=t.exportBtn;
 if($('soundButton'))$('soundButton').textContent=sound?t.soundOn:t.soundOff;
 if($('footerLeft'))$('footerLeft').textContent=CHANNEL==='demo'?t.footerDemoL:t.footerL;
 if($('footerRight'))$('footerRight').textContent=CHANNEL==='demo'?t.footerDemoR:t.footerR;
 if(CHANNEL==='coolmath'){if($('exportButton'))$('exportButton').style.display='none'}
 if($('gearButton'))$('gearButton').setAttribute('aria-label',t.settingsBtn);
 for(const [id,label] of [['zoomOutButton',t.zoomOut],['zoomInButton',t.zoomIn],['zoomResetButton',t.zoomReset],['visualizerButton',visualizer?t.hideVisualizer:t.visualizer]]){
  if($(id)){$(id).setAttribute('aria-label',label);$(id).title=label}
 }
}

function clearRays(){const ray=$('rayLayer');if(ray)ray.innerHTML=''}
function drawRay(id,tone,global=false){
 const lv=level(),a=core.arrow(lv,id);if(!a)return;
 const m=cellMetrics();
 const rayCells=core.exitRayCells(lv,state,id);
 const blocked=core.blockers(lv,state,id);
 const isClear=blocked&&blocked.length===0;
 const cls=global?'global':(tone||(isClear?'clear':'blocked'));
 const host=$('rayLayer');
 for(const [x,y] of rayCells){
  const el=document.createElement('div');
  el.className='exit-cell '+(global?'global '+(isClear?'clear':'blocked'):cls);
  if(global)el.style.setProperty('--ray-color',isClear?'#16885e':'#d94b55');
  const p=cellCenter(x,y,m);
  const w=m.cell*(global?0.34:0.78);
  el.style.left=(p.cx-w/2)+'px';
  el.style.top=(p.cy-w/2)+'px';
  el.style.width=w+'px';
  el.style.height=w+'px';
  host.appendChild(el);
  if(!global&&cls==='blocked'){
   const occ=core.occupancyMap(lv,state);
   const hit=occ.get(x+','+y);
   if(hit!==undefined&&hit!==id)break;
  }
 }
 if(isClear&&!global){
  const d=core.direction(a,state.phase);
  const cells=core.cellsAtPhase(a,state.phase);
  const head=cells[cells.length-1];
  const base=rayCells.length?rayCells[rayCells.length-1]:head;
  const p=cellCenter(base[0],base[1],m);
  const tip=document.createElement('div');
  tip.className='exit-cell clear';
  const w=m.cell*0.55;
  tip.style.left=(p.cx+core.DX[d]*m.cell*0.55-w/2)+'px';
  tip.style.top=(p.cy+core.DY[d]*m.cell*0.55-w/2)+'px';
  tip.style.width=w+'px';tip.style.height=w+'px';tip.style.opacity='0.55';
  host.appendChild(tip);
 }
 return host.lastElementChild;
}

function display(opts={}){
 if(animating&&!opts.force)return;
 const lv=level(),board=$('board'),size=lv.size;
 board.style.gridTemplateColumns=`repeat(${size},minmax(0,1fr))`;
 board.innerHTML='';
 board.dataset.shape=lv.shape||'square';
 for(let y=0;y<size;y++)for(let x=0;x<size;x++){
  const cell=document.createElement('div');
  const playable=core.isPlayable(lv,x,y);
  cell.className=playable?'grid-cell':'grid-cell void';
  cell.dataset.x=String(x);cell.dataset.y=String(y);
  if(!playable)cell.setAttribute('aria-hidden','true');
  board.appendChild(cell);
 }
 requestAnimationFrame(()=>paintSnakes(opts));

 if(mode==='daily'){
  $('levelChip').textContent='★ '+todayKey().slice(5);
  $('prevButton').disabled=true;$('nextButton').disabled=true;
 }else{
  $('levelChip').textContent=`${current+1} / ${TOTAL}`;
  $('prevButton').disabled=current===0;
  $('nextButton').disabled=current>=levels.length-1||(!qa&&!progress.completed.includes(current+1)&&current+1>=progress.unlocked);
 }
 if($('phaseBadge'))$('phaseBadge').textContent=String(state.phase);
 if($('phaseBtnDetail'))$('phaseBtnDetail').textContent=t.phaseDetail(state.phase);
 $('remainingStat').textContent=String(state.remaining.length);
 if($('movesStat'))$('movesStat').textContent=String(state.moves);
 if($('togglesStat'))$('togglesStat').textContent=String(state.toggles);
 if($('timerStat'))$('timerStat').textContent=formatTime(runElapsed());
 if($('mistakeStat'))$('mistakeStat').textContent=String(mistakes);
 $('undoButton').disabled=!state.history.length;
 const bestKey=mode==='daily'?('d:'+todayKey()):String(current+1);
 const best=progress.best[bestKey];
 if($('bestStat'))$('bestStat').textContent=best?t.bestFmt(best.moves,best.toggles):t.bestNone;
 $('missionText').textContent=settings.quietHints&&current>3&&mode!=='daily'?t.startLater:teachingText();
 if($('visualizerButton')){$('visualizerButton').setAttribute('aria-pressed',String(visualizer));$('visualizerButton').textContent=visualizer?'◉':'◎';$('visualizerButton').setAttribute('aria-label',visualizer?t.hideVisualizer:t.visualizer);$('visualizerButton').title=visualizer?t.hideVisualizer:t.visualizer}
 document.body.classList.toggle('visual-mode',visualizer);
 maybePhaseTip();maybeHintCoach();maybeGameplayStart();sizeFxCanvas();
 saveRun();
}

function paintSnakes(opts={}){
 const lv=level(),svg=$('arrowLayer');if(!svg)return;
 const m=cellMetrics();
 svg.setAttribute('viewBox',`0 0 ${m.width} ${m.height}`);
 svg.innerHTML='';
 clearRays();
 // Keep adjacent paths legible at phone width; the invisible SVG stroke is the only hit target.
 const bodyW=Math.max(12,m.cell*0.68);
 const outlineW=bodyW+Math.max(3,m.cell*0.12);
 const shadeW=Math.max(9,m.cell*0.60);
 const hiW=Math.max(2.4,m.cell*0.11);
 for(const id of state.remaining){
  const a=core.arrow(lv,id);if(!a)continue;
  const cells=core.cellsAtPhase(a,state.phase);
  const d=core.direction(a,state.phase);
  const head=cells[cells.length-1];
  const cols=snakeColors(a);
  const g=document.createElementNS('http://www.w3.org/2000/svg','g');
  g.setAttribute('class','snake-group'+(opts.rotateBlue&&a.color==='blue'?' rotating':''));
  g.setAttribute('data-snake-id',String(a.id));
  const pts=polylinePoints(cells,m);
  const shadePts=offsetPolyline(cells,m,m.cell*0.04,m.cell*0.07);
  const hiPts=offsetPolyline(cells,m,-m.cell*0.09,-m.cell*0.12);
  const mk=(tag,attrs)=>{const el=document.createElementNS('http://www.w3.org/2000/svg',tag);for(const k in attrs)el.setAttribute(k,attrs[k]);return el};
  if(cells.length===1){
   const p=cellCenter(cells[0][0],cells[0][1],m);
   const r=bodyW*0.48;
   g.appendChild(mk('circle',{cx:p.cx,cy:p.cy,r:String(r+m.cell*0.08),fill:cols.outline}));
   g.appendChild(mk('circle',{cx:p.cx,cy:p.cy,r:String(r),fill:cols.fill}));
   g.appendChild(mk('ellipse',{cx:String(p.cx-r*0.18),cy:String(p.cy-r*0.38),rx:String(r*0.48),ry:String(r*0.30),fill:'#ffffff',opacity:'0.72'}));
  }else{
   const mkPoly=(cls,points,sw,stroke,op)=>{
    const pl=mk('polyline',{class:cls,points:points,'stroke-width':String(sw),stroke:stroke,fill:'none','stroke-linecap':'round','stroke-linejoin':'round'});
    if(op!=null)pl.setAttribute('opacity',String(op));
    return pl;
   };
   g.appendChild(mkPoly('snake-outline',pts,outlineW,cols.outline,0.98));
   g.appendChild(mkPoly('snake-shade',shadePts,shadeW,cols.deep,0.42));
   g.appendChild(mkPoly('snake-body',pts,bodyW,cols.fill,1));
   g.appendChild(mkPoly('snake-hi-mid',hiPts,Math.max(5,m.cell*0.32),'#ffffff',0.28));
   g.appendChild(mkPoly('snake-hi',hiPts,hiW,'#ffffff',0.78));
  }
  // Chevron tip (clear arrow head)
  const chev=mk('polygon',{class:'snake-head',points:headChevron(head[0],head[1],d,m,0.52),fill:cols.fill,stroke:cols.outline,'stroke-width':String(Math.max(1.6,m.cell*0.04)),'stroke-linejoin':'round'});
  g.appendChild(chev);
  const tip=mk('polygon',{class:'snake-head tip',points:headChevron(head[0],head[1],d,m,0.30),fill:cols.deep,opacity:'0.45'});
  g.appendChild(tip);
  // Cartoon eyes on head
  for(const e of eyePair(head[0],head[1],d,m,bodyW)){
   g.appendChild(mk('circle',{class:'snake-eye-white',cx:String(e.cx),cy:String(e.cy),r:String(e.r),fill:'#ffffff',stroke:cols.outline,'stroke-width':'1.2'}));
   g.appendChild(mk('circle',{class:'snake-eye-pupil',cx:String(e.px),cy:String(e.py),r:String(e.pr),fill:'#1a2430'}));
  }
  svg.appendChild(g);
  const hitCells=cells.length===1?[cells[0],[cells[0][0]+core.DX[d]*0.28,cells[0][1]+core.DY[d]*0.28]]:cells;
  const hit=mk('polyline',{class:'snake-hit',points:polylinePoints(hitCells,m),fill:'none',stroke:'transparent','stroke-linecap':'round','stroke-linejoin':'round','stroke-width':String(Math.max(bodyW,m.cell*0.76)),'pointer-events':'stroke','data-piece-id':String(a.id),'data-testid':'piece-'+a.id,'data-snake-id':String(a.id),tabindex:'0',role:'button'});
  const dWord=t.dir[d];
  hit.setAttribute('aria-label',a.color==='blue'?t.ariaBlue(head[1]+1,head[0]+1,dWord):t.ariaGold(head[1]+1,head[0]+1,dWord));
  hit.addEventListener('pointerenter',()=>{if(!animating&&!visualizer){clearRays();drawRay(a.id)}});
  hit.addEventListener('pointerleave',()=>{if(pressId!==a.id&&!visualizer)clearRays()});
  hit.addEventListener('pointerdown',()=>{pressId=a.id;if(!visualizer){clearRays();drawRay(a.id)}});
  hit.addEventListener('pointerup',()=>{pressId=null});
  hit.addEventListener('click',e=>{if(suppressedClicks.delete(e.pointerId))return;remove(a.id)});
  hit.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();remove(a.id)}});
  svg.appendChild(hit);
 }
 if(visualizer){for(const id of state.remaining)drawRay(id,null,true)}
 else if(pressId!=null)drawRay(pressId);
}

function tone(kind){
 if(!sound)return;
 try{
  const Audio=window.AudioContext||window.webkitAudioContext;if(!Audio)return;
  const ctx=tone.ctx||(tone.ctx=new Audio()),now=ctx.currentTime;
  const beep=(freq,dur,type,vol,delay)=>{
   const osc=ctx.createOscillator(),gain=ctx.createGain();
   osc.type=type||'sine';osc.frequency.setValueAtTime(freq,now+delay);
   gain.gain.setValueAtTime(Math.max(0.0001,vol),now+delay);
   gain.gain.exponentialRampToValueAtTime(.001,now+delay+dur);
   osc.connect(gain);gain.connect(ctx.destination);osc.start(now+delay);osc.stop(now+delay+dur+.02);
  };
  if(kind==='remove'){beep(520,.06,'triangle',.055,0);beep(780,.08,'sine',.045,.045)}
  else if(kind==='toggle'){beep(300,.07,'sine',.045,0);beep(420,.09,'triangle',.05,.06)}
  else if(kind==='blocked'){beep(170,.1,'square',.035,0);beep(130,.12,'square',.03,.07)}
  else if(kind==='win'){beep(523,.09,'sine',.055,0);beep(659,.1,'sine',.05,.09);beep(784,.12,'triangle',.048,.2)}
  else beep(650,.07,'sine',.045,0);
 }catch{}
}

function setZoom(next){
 const old=zoom;zoom=Math.max(1,Math.min(2.2,Math.round(next*100)/100));
 if(zoom===1)pan={x:0,y:0};else if(old>0)pan={x:pan.x*zoom/old,y:pan.y*zoom/old};
 applyBoardTransform();
}
function zoomAt(next,clientX,clientY){
 const frame=$('boardFrame'),r=frame.getBoundingClientRect(),cx=r.left+r.width/2,cy=r.top+r.height/2;
 const old=zoom;next=Math.max(1,Math.min(2.2,Math.round(next*100)/100));
 const worldX=(clientX-cx-pan.x)/old,worldY=(clientY-cy-pan.y)/old;
 zoom=next;pan=zoom===1?{x:0,y:0}:{x:clientX-cx-worldX*zoom,y:clientY-cy-worldY*zoom};
 applyBoardTransform();
}
function applyBoardTransform(){
 const frame=$('boardFrame'),scene=$('boardScene');if(!scene)return;
 scene.style.setProperty('--zoom',String(zoom));scene.style.setProperty('--pan-x',`${pan.x}px`);scene.style.setProperty('--pan-y',`${pan.y}px`);
 if($('zoomReadout'))$('zoomReadout').textContent=`${Math.round(zoom*100)}%`;
 const max=Math.max(0,(scene.clientWidth*zoom-(frame.clientWidth-22))/2);
 pan={x:Math.max(-max,Math.min(max,pan.x)),y:Math.max(-max,Math.min(max,pan.y))};
 scene.style.setProperty('--pan-x',`${pan.x}px`);scene.style.setProperty('--pan-y',`${pan.y}px`);
}
function setupBoardGestures(){
 const frame=$('boardFrame');if(!frame)return;
 frame.addEventListener('wheel',e=>{if(e.ctrlKey||e.deltaY!==0){e.preventDefault();zoomAt(zoom*(e.deltaY<0?1.12:1/1.12),e.clientX,e.clientY)}},{passive:false});
 frame.addEventListener('pointerdown',e=>{
  if(e.pointerType==='mouse'&&e.button!==0)return;
  if(!framePointers.size)suppressedClicks.delete(e.pointerId);
  framePointers.set(e.pointerId,{x:e.clientX,y:e.clientY});
  if(framePointers.size===2){
   const pts=[...framePointers.values()],mid={x:(pts[0].x+pts[1].x)/2,y:(pts[0].y+pts[1].y)/2};
   for(const id of framePointers.keys())suppressedClicks.add(id);
   frameGesture={kind:'pinch',distance:Math.max(1,Math.hypot(pts[0].x-pts[1].x,pts[0].y-pts[1].y)),zoom,pan:{...pan},mid};
   try{frame.setPointerCapture(e.pointerId)}catch{}
  }else if(framePointers.size===1&&zoom>1&&!e.target.closest('.snake-hit')){
   frameGesture={kind:'pan',pointerId:e.pointerId,start:{x:e.clientX,y:e.clientY},pan:{...pan},moved:false};
   try{frame.setPointerCapture(e.pointerId)}catch{}
  }
 },{passive:true});
 frame.addEventListener('pointermove',e=>{
  if(!framePointers.has(e.pointerId))return;
  framePointers.set(e.pointerId,{x:e.clientX,y:e.clientY});
  if(!frameGesture)return;
  if(frameGesture.kind==='pinch'&&framePointers.size>=2){
   const pts=[...framePointers.values()].slice(0,2),distance=Math.max(1,Math.hypot(pts[0].x-pts[1].x,pts[0].y-pts[1].y));
   const mid={x:(pts[0].x+pts[1].x)/2,y:(pts[0].y+pts[1].y)/2};
   const r=frame.getBoundingClientRect(),cx=r.left+r.width/2,cy=r.top+r.height/2;
   const factor=Math.max(1,Math.min(2.2,frameGesture.zoom*distance/frameGesture.distance));
   const wx=(frameGesture.mid.x-cx-frameGesture.pan.x)/frameGesture.zoom,wy=(frameGesture.mid.y-cy-frameGesture.pan.y)/frameGesture.zoom;
   zoom=factor;pan=zoom===1?{x:0,y:0}:{x:mid.x-cx-wx*zoom,y:mid.y-cy-wy*zoom};applyBoardTransform();
   if(Math.abs(distance-frameGesture.distance)>6)frameGesture.moved=true;
  }else if(frameGesture.kind==='pan'){
   const dx=e.clientX-frameGesture.start.x,dy=e.clientY-frameGesture.start.y;
   if(Math.hypot(dx,dy)>5){frameGesture.moved=true;suppressedClicks.add(frameGesture.pointerId);pan={x:frameGesture.pan.x+dx,y:frameGesture.pan.y+dy};applyBoardTransform()}
  }
 },{passive:true});
 const end=e=>{framePointers.delete(e.pointerId);if(!framePointers.size)frameGesture=null};
 frame.addEventListener('pointerup',end);frame.addEventListener('pointercancel',end);
}
function sizeFxCanvas(){
 const canvas=$('fxCanvas'),scene=$('boardScene');
 if(!canvas||!scene)return;
 const width=scene.clientWidth,height=scene.clientHeight;
 const dpr=Math.min(2,window.devicePixelRatio||1);
 canvas.width=Math.floor(width*dpr);canvas.height=Math.floor(height*dpr);
 canvas.style.width=width+'px';canvas.style.height=height+'px';
}
function spawnBurst(clientX,clientY,color){
 if(reducedMotion())return;
 const canvas=$('fxCanvas'),scene=$('boardScene'),frame=$('boardFrame');
 if(!canvas||!frame||!scene)return;
 const fr=frame.getBoundingClientRect(),z=zoom;
 const x=(clientX-(fr.left+fr.width/2)-pan.x)/z+scene.clientWidth/2;
 const y=(clientY-(fr.top+fr.height/2)-pan.y)/z+scene.clientHeight/2;
 for(let i=0;i<8;i++){
  const ang=Math.random()*Math.PI*2,sp=30+Math.random()*60;
  particles.push({x,y,vx:Math.cos(ang)*sp,vy:Math.sin(ang)*sp,life:0.3+Math.random()*0.2,age:0,color,r:1.5+Math.random()*2});
 }
 if(!spawnBurst.raf)spawnBurst.raf=requestAnimationFrame(tickFx);
}
function tickFx(ts){
 const canvas=$('fxCanvas');if(!canvas){spawnBurst.raf=0;return}
 const ctx=canvas.getContext('2d');
 const dpr=Math.min(2,window.devicePixelRatio||1);
 ctx.clearRect(0,0,canvas.width,canvas.height);
 const last=tickFx.last||ts;const dt=Math.min(0.05,(ts-last)/1000);tickFx.last=ts;
 particles=particles.filter(p=>{
  p.age+=dt;if(p.age>=p.life)return false;
  p.x+=p.vx*dt;p.y+=p.vy*dt;p.vy+=50*dt;
  const a=1-p.age/p.life;
  ctx.globalAlpha=a*0.65;ctx.fillStyle=p.color;
  ctx.beginPath();ctx.arc(p.x*dpr,p.y*dpr,p.r*dpr,0,Math.PI*2);ctx.fill();
  return true;
 });
 ctx.globalAlpha=1;
 if(particles.length)spawnBurst.raf=requestAnimationFrame(tickFx);
 else{spawnBurst.raf=0;tickFx.last=0}
}

function slideOff(a,done){
 const g=document.querySelector(`[data-snake-id="${a.id}"]`);
 const d=core.direction(a,state.phase);
 const m=cellMetrics();
 const dist=m.width*1.35;
 const dx=core.DX[d]*dist,dy=core.DY[d]*dist;
 clearRays();
 drawRay(a.id,'clear');
 if(reducedMotion()||!g){done();return}
 animating=true;
 if(!reducedMotion()&&g.parentNode){
  const clone=g.cloneNode(true);
  clone.removeAttribute('data-snake-id');
  clone.style.opacity='0.35';
  clone.style.pointerEvents='none';
  g.parentNode.appendChild(clone);
  requestAnimationFrame(()=>{
   clone.style.transition='opacity 280ms ease-out,transform 360ms ease-out';
   clone.style.opacity='0';
   clone.style.transform=`translate(${dx*0.55}px,${dy*0.55}px)`;
   setTimeout(()=>clone.remove(),380);
  });
 }
 g.classList.add('sliding');
 g.style.setProperty('--slide-ms','360ms');
 g.style.transform=`translate(${dx}px,${dy}px)`;
 g.style.opacity='0';
 const btn=document.querySelector(`[data-piece-id="${a.id}"]`);
 if(btn){btn.style.transition='opacity .28s';btn.style.opacity='0'}
 setTimeout(()=>{clearRays();animating=false;done()},reducedMotion()?0:380);
}

function remove(id){
 if(completionScheduled||animating||!state.remaining.includes(id))return;
 const b=core.blockers(level(),state,id);if(b===null)return;
 if(b.length){
  mistakes++;saveRun();if($('mistakeStat'))$('mistakeStat').textContent=String(mistakes);
  blockedStreak++;
  log('blocked_click',{id,blockedBy:b,streak:blockedStreak});
  message((!settings.quietHints&&blockedStreak>=3)?t.blockedSoft:t.blocked,'warn');
  tone('blocked');haptic(12);
  clearRays();drawRay(id,'blocked');
  const g=document.querySelector(`[data-snake-id="${id}"]`);g?.classList.add('blocked');
  for(const hit of b){
   const cells=core.cellsAtPhase(core.arrow(level(),hit),state.phase);
   for(const [x,y] of cells){
    const el=document.querySelector(`[data-x="${x}"][data-y="${y}"]`);
    el?.classList.add('hit-cell');
   }
  }
  blockedTimer++;const seq=blockedTimer;
  setTimeout(()=>{
   if(seq!==blockedTimer)return;
   document.querySelectorAll('.hit-cell').forEach(el=>el.classList.remove('hit-cell'));
   g?.classList.remove('blocked');clearRays();
  },620);
  return;
 }
 blockedStreak=0;
 const a=core.arrow(level(),id);
  const hit=document.querySelector(`[data-piece-id="${id}"]`);
  if(hit){const r=hit.getBoundingClientRect();spawnBurst(r.left+r.width/2,r.top+r.height/2,snakeColors(a).fill)}
 message(t.removed,'good');tone('remove');haptic(7);
 slideOff(a,()=>{
  state=core.transition(level(),state,{type:'remove',id});
  log('arrow_removed',{id,remaining:state.remaining.length});
  display({force:true});
  if(state.remaining.length===0)complete();
 });
}
function toggle(){
 if(completionScheduled||animating)return;
 state=core.transition(level(),state,{type:'toggle'});
 log('phase_toggle',{phase:state.phase});
 message(t.toggled(state.phase),'good');tone('toggle');haptic([7,25,7]);
 display({force:true,rotateBlue:true});
}
function undo(){if(completionScheduled||animating||!state.history.length)return;state=core.transition(level(),state,{type:'undo'});log('undo');message(t.undid);display({force:true})}
function reset(){if(completionScheduled||animating)return;state=core.newState(level());blockedStreak=0;log('level_restart');message(t.restarted);display({force:true})}
function hint(){
 if(completionScheduled||animating)return;const result=core.solve(level(),state);log('hint_requested',{solvable:!!result.actions});
 if(!result.actions){message(t.dead,'warn');return}
 if(result.actions.length===0){message(t.already,'good');return}
 hintsUsed++;saveRun();
 const a=result.actions[0];
 if(a.type==='toggle'){$('phaseButton').focus();message(t.hintToggle,'good')}
 else{
  const arrow=core.arrow(level(),a.id);
  const cells=core.cellsAtPhase(arrow,state.phase);
  const head=cells[cells.length-1];
  for(const [x,y] of cells){document.querySelector(`[data-x="${x}"][data-y="${y}"]`)?.classList.add('hint-cell')}
  document.querySelector(`[data-piece-id="${a.id}"]`)?.focus();
  drawRay(a.id,'clear');
  message(t.hintCell(head[1]+1,head[0]+1),'good');
  setTimeout(()=>{document.querySelectorAll('.hint-cell').forEach(el=>el.classList.remove('hint-cell'));clearRays()},1500);
 }
}
function openDialog(html){modalReturnFocus=document.activeElement;$('modal').innerHTML=html;$('overlay').inert=false;$('overlay').classList.remove('hidden');$('overlay').setAttribute('aria-hidden','false');$('modal').querySelector('button,input')?.focus()}
function closeDialog(){$('overlay').classList.add('hidden');$('overlay').setAttribute('aria-hidden','true');$('overlay').inert=true;$('modal').innerHTML='';if(modalReturnFocus?.isConnected)modalReturnFocus.focus();modalReturnFocus=null}

function formatOptimal(actions){
 return actions.map(a=>{
  if(a.type==='toggle')return LOCALE==='zh'?'相位':'Phase';
  const ar=core.arrow(level(),a.id);
  const h=core.headCell(ar);
  return `(${h.y+1},${h.x+1})`;
 }).join(' → ');
}

function complete(){
 completionScheduled=true;
 const opt=level().metrics.minSteps;
 const delta=state.moves-opt;
 log('level_complete',{moves:state.moves,toggles:state.toggles,optimal:opt,mode});
 const key=mode==='daily'?('d:'+todayKey()):String(current+1);
 const old=progress.best[key];
 if(!old||state.moves<old.moves||state.moves===old.moves&&state.toggles<old.toggles)progress.best[key]={moves:state.moves,toggles:state.toggles};
 const clearedAt=todayKey();
 if(mode==='daily'){recordDailyClear(clearedAt);progress.dailyStats={...(progress.dailyStats||{}),[clearedAt]:{moves:state.moves,toggles:state.toggles,elapsed:runElapsed(),mistakes,hints:hintsUsed}}}
 else{
  if(!progress.completed.includes(current+1))progress.completed.push(current+1);
  progress.unlocked=Math.min(levels.length,Math.max(progress.unlocked,current+2));
  const stars=delta===0?3:delta<=2?2:1;progress.stars={...(progress.stars||{}),[current+1]:Math.max(progress.stars?.[current+1]||0,stars)};
 }
 persist();try{localStorage.removeItem(runStoreKey())}catch{}tone('win');
 if(!reducedMotion()){
  const board=document.querySelector('.board-frame');
  if(board){const r=board.getBoundingClientRect();spawnBurst(r.left+r.width/2,r.top+r.height/2,'#2ec4d6')}
 }
 const last=mode!=='daily'&&current===levels.length-1;
 const delay=reducedMotion()?0:420;
 const daily=mode==='daily';
 setTimeout(()=>{
  const optBtn=settings.showOptimal?`<button id="showOptBtn" type="button">${t.showOptimal}</button>`:'';
  const shareBtn=`<button class="share-copy" id="shareResult" type="button">${t.share}</button>`;
  const stats=[['moves',state.moves],['seconds',formatTime(runElapsed())],['mistakes',mistakes],['hints',hintsUsed],...(daily?[["streak",progress.dailyStreak]]:[])];
  const summary=stats.map(([label,value])=>`<div><small>${t[label]}</small><strong>${value}</strong></div>`).join('');
  const mark=daily?`<div class="result-mark">✓</div>`:`<div class="result-mark" aria-label="${t.stars}">${'★'.repeat(delta===0?3:delta<=2?2:1)}${'☆'.repeat(delta===0?0:delta<=2?1:2)}</div>`;
  openDialog(`<button class="close-button" id="modalClose" type="button" aria-label="${t.close}">×</button><div class="modal-sub">${t.winSub(last,current+1,daily)}</div>${mark}<h2 id="modalTitle">${t.winTitle(last,daily)}</h2><p>${t.winBody(state.moves,state.toggles,delta)}</p><div class="result-stats">${summary}</div><div id="optBox" class="opt-box hidden"></div><div class="modal-actions">${shareBtn}${optBtn}<button id="replayWin" type="button">${t.replay}</button>${daily?`<button class="main-button" id="dailyBackWin" type="button">${t.dailyBack}</button>`:(last?`<button class="main-button" id="viewLevelsWin" type="button">${t.viewAll}</button>`:`<button class="main-button" id="continueWin" type="button">${t.cont}</button>`)}</div>`);
  $('modalClose').onclick=()=>{completionScheduled=false;closeDialog()};
  $('shareResult').onclick=async()=>{
   const line=`Vector Shift ${daily?'Daily '+clearedAt:`Level ${current+1}`} · ${state.moves} ${LOCALE==='zh'?'步':'moves'} · ${formatTime(runElapsed())} · ${mistakes} ${LOCALE==='zh'?'误点':'misses'}${daily?` · ${progress.dailyStreak} ${LOCALE==='zh'?'天连续':'day streak'}`:''}`;
   try{if(navigator.share)await navigator.share({text:line});else{await navigator.clipboard.writeText(line);message(t.copied,'good')}}catch{}
  };
  $('replayWin').onclick=()=>{completionScheduled=false;closeDialog();reset()};
  if($('showOptBtn'))$('showOptBtn').onclick=()=>{
   const box=$('optBox');
   if(box.classList.contains('hidden')){
    const solved=core.solve(level(),core.newState(level()));
    box.innerHTML=`<div class="opt-label">${t.optimalLabel}</div><code>${formatOptimal(solved.actions||[])}</code>`;
    box.classList.remove('hidden');$('showOptBtn').textContent=t.hideOptimal;
   }else{box.classList.add('hidden');$('showOptBtn').textContent=t.showOptimal}
  };
  if(daily)$('dailyBackWin').onclick=()=>{completionScheduled=false;closeDialog();exitDaily()};
  else if(last)$('viewLevelsWin').onclick=()=>{completionScheduled=false;closeDialog();openLevels()};
  else $('continueWin').onclick=()=>{completionScheduled=false;closeDialog();select(current+1)};
 },delay);
}

function select(index){
 if(index<0||index>=levels.length||(!qa&&index+1>progress.unlocked))return;
 mode='campaign';dailyIndex=null;completionScheduled=false;animating=false;current=index;state=core.newState(level());blockedStreak=0;hintsUsed=0;mistakes=0;elapsedBeforePause=0;runStartedAt=Date.now();log('level_start');
 zoom=1;pan={x:0,y:0};visualizer=false;applyBoardTransform();
 message(index<=3?t.startEasy:t.startLater);closeDialog();display({force:true});window.scrollTo({top:0,behavior:'auto'});
}
function exitDaily(){completionScheduled=false;if(restoreRun('campaign'))display({force:true});else select(Math.min(current,progress.unlocked-1))}
function openDaily(){
 const ymd=todayKey();const idx=dailyLevelIndex();const cleared=!!progress.dailyCleared[ymd];
 const record=progress.dailyStats?.[ymd];
 const details=[cleared?t.dailyDone:'',`${t.streak}: ${progress.dailyStreak||0}`,record?t.dailyRecord(record.moves,record.elapsed):'',`#${String(idx+1).padStart(2,'0')}`].filter(Boolean).join(' · ');
 openDialog(`<button class="close-button" id="modalClose" type="button" aria-label="${t.close}">×</button><div class="modal-sub">${t.dailySub}</div><h2 id="modalTitle">${t.dailyTitle(ymd)}</h2><p>${t.dailyBlurb}</p><p class="daily-meta">${details}</p><div class="modal-actions"><button class="main-button" id="dailyGo" type="button">${t.dailyPlay}</button><button id="dailyCancel" type="button">${t.setCancel}</button></div>`);
 $('modalClose').onclick=closeDialog;$('dailyCancel').onclick=closeDialog;
 $('dailyGo').onclick=()=>{
  mode='daily';dailyIndex=idx;completionScheduled=false;animating=false;
  if(!restoreRun('daily')){state=core.newState(level());hintsUsed=0;mistakes=0;elapsedBeforePause=0;runStartedAt=Date.now()}
  blockedStreak=0;zoom=1;pan={x:0,y:0};visualizer=false;
  log('daily_start',{ymd,index:idx+1});message(progress.dailyCleared[ymd]?t.dailyDone:t.dailyStart);closeDialog();display({force:true});
 };
}
function openLevels(){
 if(mode==='daily')exitDaily();
 const tiles=levels.map((l,i)=>{
  const unlocked=qa||i+1<=progress.unlocked,done=progress.completed.includes(i+1),stars=progress.stars?.[i+1]||0;
  return `<button type="button" ${unlocked?'':'disabled'} data-go="${i}" class="${i===current&&mode==='campaign'?'current ':''}${done?'done ':''}${unlocked?'':'locked'}"><span>${String(i+1).padStart(2,'0')}</span><small>${done?`${stars}★`:unlocked?t.unlocked:t.locked}</small></button>`;
 }).join('');
 openDialog(`<button class="close-button" id="modalClose" aria-label="${t.close}">×</button><div class="modal-sub">${t.levelsSub}</div><h2 id="modalTitle">${t.levelsTitle}</h2><p>${t.levelsBlurb}</p><div class="level-tiles">${tiles}</div>`);
 $('modalClose').onclick=closeDialog;$('modal').querySelectorAll('[data-go]').forEach(b=>b.onclick=()=>select(Number(b.dataset.go)));
}
function help(){
 openDialog(`<button class="close-button" id="modalClose" aria-label="${t.close}">×</button><div class="modal-sub">${t.helpSub}</div><h2 id="modalTitle">${t.helpTitle}</h2><p>${t.help1}</p><p>${t.help2}</p><p>${t.help3}</p><p>${t.helpKeys}</p><div class="modal-actions"><button class="main-button" id="closeHelp">${t.helpGo}</button></div>`);
 $('modalClose').onclick=closeDialog;$('closeHelp').onclick=closeDialog;
}
function openSettings(){
 openDialog(`<button class="close-button" id="modalClose" aria-label="${t.close}">×</button><div class="modal-sub">${t.settingsSub}</div><h2 id="modalTitle">${t.settingsTitle}</h2>
<label class="set-row"><input type="checkbox" id="setSound" ${sound?'checked':''}> <span>${t.setSound}</span></label>
<label class="set-row"><input type="checkbox" id="setQuiet" ${settings.quietHints?'checked':''}> <span>${t.setQuietHints}</span></label>
<label class="set-row"><input type="checkbox" id="setHaptics" ${settings.haptics?'checked':''}> <span>${t.setHaptics}</span></label>
<label class="set-row"><input type="checkbox" id="setOpt" ${settings.showOptimal?'checked':''}> <span>${t.setShowOptimal}</span></label>
<div class="modal-actions"><button id="clearProgress" type="button">${t.setClear}</button><button class="main-button" id="settingsDone" type="button">${t.setDone}</button></div>`);
 $('modalClose').onclick=closeDialog;$('settingsDone').onclick=()=>{closeDialog();display({force:true})};
 $('setSound').onchange=e=>{sound=e.target.checked;persistSound();if($('soundButton'))$('soundButton').textContent=sound?t.soundOn:t.soundOff;if(sound)tone('ui')};
 $('setQuiet').onchange=e=>{settings.quietHints=e.target.checked;persistSettings();display({force:true})};
 $('setHaptics').onchange=e=>{settings.haptics=e.target.checked;persistSettings()};
 $('setOpt').onchange=e=>{settings.showOptimal=e.target.checked;persistSettings()};
 $('clearProgress').onclick=()=>{
  openDialog(`<div class="modal-sub">${t.settingsSub}</div><h2 id="modalTitle">${t.setClear}</h2><p>${t.setClearConfirm}</p><div class="modal-actions"><button id="confirmClear" type="button">${t.setYes}</button><button class="main-button" id="cancelClear" type="button">${t.setCancel}</button></div>`);
  $('cancelClear').onclick=openSettings;
  $('confirmClear').onclick=()=>{
   progress={unlocked:1,completed:[],best:{},dailyCleared:{},dailyStreak:0,dailyDates:[],stars:{}};persist();
   try{localStorage.removeItem(ONBOARD_STORE);localStorage.removeItem(PHASE_TIP_STORE);localStorage.removeItem(HINT_TIP_STORE);localStorage.removeItem(runStoreKey('campaign'));localStorage.removeItem(runStoreKey('daily'))}catch{}
   message(t.setCleared,'good');closeDialog();select(0);
  };
 };
}
function showOnboarding(){
 let seen=false;try{seen=localStorage.getItem(ONBOARD_STORE)==='1'}catch{}
 if(seen||current!==0||mode!=='campaign')return;
 onboardStep=0;renderOnboard();
}
function renderOnboard(){
 const steps=[t.onboard1,t.onboard2,t.onboard3];
 const last=onboardStep>=2;
 openDialog(`<div class="modal-sub">${t.onboardSub}</div><h2 id="modalTitle">${t.onboardTitle}</h2><p class="onboard-step">${steps[onboardStep]}</p><div class="onboard-dots" aria-hidden="true"><i class="${onboardStep===0?'on':''}"></i><i class="${onboardStep===1?'on':''}"></i><i class="${onboardStep===2?'on':''}"></i></div><div class="modal-actions"><button class="main-button" id="onboardNext" type="button">${last?t.onboardGo:t.onboardNext}</button></div>`);
 $('onboardNext').onclick=()=>{
  if(last){try{localStorage.setItem(ONBOARD_STORE,'1')}catch{}closeDialog();maybeL1Coach()}
  else{onboardStep++;renderOnboard()}
 };
}
function maybeL1Coach(){
 if(current!==0||mode!=='campaign'||settings.quietHints)return;
 const lv=level();
 const clear=lv.arrows.find(a=>core.clearPath(lv,state,a.id));
 if(!clear)return;
 const cells=core.cellsAtPhase(clear,state.phase);
 for(const [x,y] of cells)document.querySelector(`[data-x="${x}"][data-y="${y}"]`)?.classList.add('hint-cell');
 drawRay(clear.id,'clear');
 setTimeout(()=>{document.querySelectorAll('.hint-cell').forEach(el=>el.classList.remove('hint-cell'));clearRays()},2200);
}
function maybePhaseTip(){
 if(settings.quietHints||current!==2||mode!=='campaign')return;
 let seen=false;try{seen=localStorage.getItem(PHASE_TIP_STORE)==='1'}catch{}
 if(seen)return;
 const coach=$('coach');const btn=$('phaseButton');if(!btn||!coach)return;
 const r=btn.getBoundingClientRect();
 coach.innerHTML=`<div class="coach-card" style="top:${Math.max(12,r.top-88)}px;left:${Math.min(innerWidth-280,Math.max(12,r.left))}px"><p>${t.phaseTip}</p><button type="button" id="phaseTipOk">${t.phaseTipDismiss}</button></div>`;
 coach.classList.remove('hidden');coach.setAttribute('aria-hidden','false');
 btn.classList.add('phase-spotlight');
 const dismiss=()=>{try{localStorage.setItem(PHASE_TIP_STORE,'1')}catch{}coach.classList.add('hidden');coach.setAttribute('aria-hidden','true');coach.innerHTML='';btn.classList.remove('phase-spotlight')};
 $('phaseTipOk').onclick=dismiss;
}
function maybeHintCoach(){
 if(settings.quietHints||current!==4||mode!=='campaign')return;
 let seen=false;try{seen=localStorage.getItem(HINT_TIP_STORE)==='1'}catch{}
 if(seen)return;
 const coach=$('coach');const btn=$('hintButton');if(!btn||!coach||!$('coach').classList.contains('hidden'))return;
 let phaseSeen=false;try{phaseSeen=localStorage.getItem(PHASE_TIP_STORE)==='1'}catch{}
 if(current===2&&!phaseSeen)return;
 const r=btn.getBoundingClientRect();
 coach.innerHTML=`<div class="coach-card" style="top:${Math.max(12,r.top-96)}px;left:${Math.min(innerWidth-280,Math.max(12,r.left))}px"><p>${t.hintCoach}</p><button type="button" id="hintTipOk">${t.hintCoachDismiss}</button></div>`;
 coach.classList.remove('hidden');coach.setAttribute('aria-hidden','false');
 const dismiss=()=>{try{localStorage.setItem(HINT_TIP_STORE,'1')}catch{}coach.classList.add('hidden');coach.setAttribute('aria-hidden','true');coach.innerHTML=''};
 $('hintTipOk').onclick=dismiss;
}
function downloadTelemetry(){
 if(CHANNEL==='coolmath')return;
 log('telemetry_exported');
 const data={build:BUILD,channel:CHANNEL,optIn:false,localOnly:true,createdAt:new Date().toISOString(),events:telemetry};
 const blob=new Blob([JSON.stringify(data,null,2)],{type:'application/json'}),href=URL.createObjectURL(blob),a=document.createElement('a');
 a.href=href;a.download='vector-shift-playtest.json';a.click();setTimeout(()=>URL.revokeObjectURL(href),500);
}
function maybeGameplayStart(){
 if(CHANNEL!=='crazygames-basic'||!crazyReady||gameplayStarted)return;
 try{window.CrazyGames.SDK.game.gameplayStart();gameplayStarted=true}catch{}
}
function initCrazySdk(){
 if(CHANNEL!=='crazygames-basic')return;
 const run=async()=>{
  try{
   if(!window.CrazyGames||!window.CrazyGames.SDK)return;
   await window.CrazyGames.SDK.init();
   crazyReady=true;maybeGameplayStart();
  }catch{}
 };
 if(window.CrazyGames&&window.CrazyGames.SDK)run();
 else{
  let tries=0;const timer=setInterval(()=>{tries++;if(window.CrazyGames&&window.CrazyGames.SDK){clearInterval(timer);run()}else if(tries>40)clearInterval(timer)},100);
 }
}

function openGear(){
 openDialog(`<button class="close-button" id="modalClose" aria-label="${t.close}">×</button><div class="modal-sub">${t.settingsSub}</div><h2 id="modalTitle">${t.settingsTitle}</h2>
<div class="gear-menu">
<button type="button" id="gearDaily">${t.dailyBtn}</button>
<button type="button" id="gearSettings">${t.settingsBtn}</button>
<button type="button" id="gearHelp">${t.helpBtn}</button>
<button type="button" id="gearSound">${sound?t.soundOn:t.soundOff}</button>
${CHANNEL==='coolmath'?'':`<button type="button" id="gearExport">${t.exportBtn}</button>`}
</div>
<div class="modal-actions"><button class="main-button" id="gearDone" type="button">${t.setDone}</button></div>`);
 $('modalClose').onclick=closeDialog;$('gearDone').onclick=closeDialog;
 $('gearDaily').onclick=()=>{closeDialog();openDaily()};
 $('gearSettings').onclick=()=>{closeDialog();openSettings()};
 $('gearHelp').onclick=()=>{closeDialog();help()};
 $('gearSound').onclick=()=>{sound=!sound;persistSound();$('gearSound').textContent=sound?t.soundOn:t.soundOff;if($('soundButton'))$('soundButton').textContent=sound?t.soundOn:t.soundOff;tone('ui')};
 if($('gearExport'))$('gearExport').onclick=()=>{downloadTelemetry();closeDialog()};
}
applyChrome();
$('phaseButton').onclick=toggle;$('undoButton').onclick=undo;$('resetButton').onclick=reset;$('hintButton').onclick=hint;
$('zoomOutButton').onclick=()=>setZoom(zoom-0.15);
$('zoomInButton').onclick=()=>setZoom(zoom+0.15);
$('zoomResetButton').onclick=()=>{zoom=1;pan={x:0,y:0};applyBoardTransform()};
$('visualizerButton').onclick=()=>{visualizer=!visualizer;display({force:true});log('visualizer_toggle',{enabled:visualizer})};
setupBoardGestures();applyBoardTransform();
$('prevButton').onclick=()=>select(current-1);$('nextButton').onclick=()=>select(current+1);
$('levelMenuButton').onclick=openLevels;if($('helpButton'))$('helpButton').onclick=help;
if($('gearButton'))$('gearButton').onclick=openGear;
if($('settingsButton'))$('settingsButton').onclick=openSettings;
if($('dailyButton'))$('dailyButton').onclick=openDaily;
if($('exportButton'))$('exportButton').onclick=downloadTelemetry;
if($('soundButton'))$('soundButton').onclick=()=>{sound=!sound;persistSound();$('soundButton').textContent=sound?t.soundOn:t.soundOff;tone('ui')};
$('overlay').addEventListener('click',e=>{if(e.target===$('overlay')&&!completionScheduled)closeDialog()});
document.addEventListener('keydown',e=>{
 if(!$('overlay').classList.contains('hidden')){
  if(e.key==='Escape'&&!completionScheduled)closeDialog();
  if(e.key==='Tab'){
   const focusable=[...$('modal').querySelectorAll('button:not(:disabled),input:not(:disabled),[tabindex="0"]')];
   if(focusable.length){const first=focusable[0],last=focusable[focusable.length-1];if(e.shiftKey&&document.activeElement===first){e.preventDefault();last.focus()}else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first.focus()}}
  }
  return
 }
 if(e.target.matches('input,textarea,select'))return;
 if(e.code==='Space'){e.preventDefault();toggle()}else if(e.key.toLowerCase()==='z')undo();else if(e.key.toLowerCase()==='r')reset();
});
window.addEventListener('resize',()=>{applyBoardTransform();sizeFxCanvas();display({force:true})});

const qp=new URLSearchParams(location.search),requested=Math.max(1,Math.min(levels.length,Number(qp.get('level'))||1));
if(CHANNEL==='demo')window.VectorShiftDebug={getLevel:()=>level(),levels,getState:()=>JSON.parse(JSON.stringify(state)),getProgress:()=>({...progress,completed:[...progress.completed]}),getTelemetry:()=>[...telemetry],getSolution:()=>core.solve(level(),state),setLevel:(n)=>{mode='campaign';select(n-1)},solveAndPlay:()=>{const s=core.solve(level(),state);if(!s.actions)return;animating=false;for(const a of s.actions){if(a.type==='toggle'){state=core.transition(level(),state,{type:'toggle'})}else{state=core.transition(level(),state,{type:'remove',id:a.id})}}display({force:true});if(state.remaining.length===0)complete()},getMode:()=>mode,getDailyIndex:()=>dailyIndex};
log('session_start',{qa,channel:CHANNEL,locale:LOCALE,build:BUILD,levels:TOTAL});
initCrazySdk();
const restored=CHANNEL==='demo'&&!qa&&!qp.has('level')&&restoreRun('campaign');
if(restored){display({force:true});message(LOCALE==='zh'?'已恢复上次进度。':'Run restored.','good');log('run_restored')}
else select((qa||requested<=progress.unlocked)?requested-1:progress.unlocked-1);
setInterval(()=>{if(state&&$('timerStat'))$('timerStat').textContent=formatTime(runElapsed())},1000);
setTimeout(showOnboarding,reducedMotion()?0:280);
})();
