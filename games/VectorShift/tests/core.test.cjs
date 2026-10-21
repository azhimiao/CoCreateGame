const assert=require('node:assert/strict');
const fs=require('node:fs');const path=require('node:path');
const core=require('../src/game-core.js');
const levels=JSON.parse(fs.readFileSync(path.resolve(__dirname,'../data/levels.json'),'utf8'));
assert.equal(levels.length,52);
const signs=new Set();let playerActions=0,phaseLevels=0,twoToggle=0;
const steps=[];
for(let i=0;i<levels.length;i++){
 const lv=levels[i];core.validateLevel(lv);
 const hash=JSON.stringify(lv.arrows.map(a=>[a.d,a.color,JSON.stringify(a.cells)]).sort());
 assert.ok(!signs.has(hash),'duplicate '+lv.id);signs.add(hash);
 assert.equal(lv.id,`phase-${String(i+1).padStart(2,'0')}`);
 assert.ok(lv.size>=5&&lv.size<=8,lv.id+' size');
 assert.ok(lv.tag&&typeof lv.tag==='string',lv.id+' missing tag');
 for(const a of lv.arrows){
  assert.ok(Array.isArray(a.cells)&&a.cells.length>=1,lv.id+' missing cells');
  const head=a.cells[a.cells.length-1];
  assert.ok(Number.isInteger(head[0])&&Number.isInteger(head[1]));
 }
 let state=core.newState(lv),r=core.solve(lv,state);
 assert.ok(r.actions,lv.id+' no path');assert.equal(r.actions.length,lv.metrics.minSteps,lv.id+' not shortest');
 let literal=r.actions.map(a=>a.type==='toggle'?'toggle':a.id);
 assert.deepEqual(literal,lv.solution,lv.id+' stored path differs');
 if(i>=2){assert.equal(core.solve(lv,state,false).actions,null,lv.id+' phase not required');phaseLevels++}
 if(i>=38){assert.ok(r.actions.filter(a=>a.type==='toggle').length>=2,lv.id+' not 2-toggle');twoToggle++}
 assert.ok(r.explored<=2**(lv.arrows.length+1),'state bound');
 steps.push(lv.metrics.minSteps);
 const initial=structuredClone(state);
 for(const action of r.actions){
  if(action.type==='remove'){
   assert.ok(core.clearPath(lv,state,action.id));
   const blocked=core.blockers(lv,state,action.id);assert.deepEqual(blocked,[]);
  }
  state=core.transition(lv,state,action);playerActions++;
 }
 assert.equal(state.remaining.length,0,lv.id+' incomplete');
 const historyState=structuredClone(state);let undone=core.transition(lv,state,{type:'undo'});assert.equal(undone.remaining.length,1,lv.id+' undo not restore last');
 assert.deepEqual(state,historyState,lv.id+' mutated original');
 assert.deepEqual(core.transition(lv,state,{type:'reset'}),initial);
 assert.deepEqual(core.solve(lv,state).actions,[],lv.id+' solved wrongly');
 const reachable=lv.arrows.find(a=>!core.clearPath(lv,initial,a.id));
 if(reachable){assert.deepEqual(core.transition(lv,initial,{type:'remove',id:reachable.id}),initial,'blocked changed state')}
 assert.equal(core.direction({d:3,color:'blue'},1),0);
 // Phase rotation keeps both occupancies valid (already in validateLevel)
 const cells0=core.cellsAtPhase(lv.arrows[0],0);
 assert.ok(cells0.length>=1);
}
// Gentle curve: last-third median steps >= first-third median
const first=steps.slice(0,17).sort((a,b)=>a-b)[8];
const last=steps.slice(-17).sort((a,b)=>a-b)[8];
assert.ok(last>=first,`curve ${first} -> ${last}`);
assert.equal(levels[2].tag,'phase_intro');
assert.ok(['phase_read','order_phase'].includes(levels[3].tag)||levels[3].metrics.phaseRequired);
// Fuzz with deterministic action sequences including illegal actions, undo, and restart.
let seed=527923;function rnd(){seed^=seed<<13;seed^=seed>>>17;seed^=seed<<5;return (seed>>>0)/4294967296}
for(let trial=0;trial<100;trial++){
 const lv=levels[Math.floor(rnd()*levels.length)];let s=core.newState(lv);
 for(let k=0;k<40;k++){
  const r=Math.floor(rnd()*5),id=lv.arrows[Math.floor(rnd()*lv.arrows.length)].id;
  const action=r===0?{type:'toggle'}:r===1?{type:'undo'}:r===2?{type:'reset'}:{type:'remove',id};
  const t=core.transition(lv,s,action);
  assert.ok(t.phase===0||t.phase===1);assert.ok(t.remaining.length<=lv.arrows.length&&t.remaining.length>=0);
  assert.ok(t.remaining.every(id=>lv.arrows.some(a=>a.id===id)));
  assert.ok(t.moves>=0&&t.toggles>=0&&t.toggles<=t.moves);
  if(action.type==='remove'&&!core.clearPath(lv,s,id))assert.deepEqual(t,s,'illegal click mutated state');
  s=t;
 }
}

// Shape / mask P0: L10+ at least 40% non-square; mask levels exit into void.
let shapedFrom10=0;
for(let i=9;i<levels.length;i++){
 if((levels[i].shape||'square')!=='square')shapedFrom10++;
}
assert.ok(shapedFrom10/ (levels.length-9) >= 0.4, 'shaped ratio '+shapedFrom10);
const heart=levels.find(l=>l.shape==='heart');
assert.ok(heart&&heart.mask&&heart.mask.length, 'missing heart showcase');
core.validateLevel(heart);
const hState=core.newState(heart);
assert.ok(core.maskCellCount(heart)<heart.size*heart.size, 'heart should be irregular');
// Void exit: a clear arrow's ray stops before leaving mask
for(const a of heart.arrows){
 if(core.clearPath(heart,hState,a.id)){
  const ray=core.exitRayCells(heart,hState,a.id);
  for(const [x,y] of ray)assert.ok(core.isPlayable(heart,x,y));
  break;
}
}
console.log(`PASS ${levels.length} levels, ${phaseLevels} phase-necessary, ${twoToggle} two-toggle stages, ${playerActions} verified moves, 100 fuzz sequences, shaped L10+=${shapedFrom10}`);
