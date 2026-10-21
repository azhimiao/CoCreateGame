/* Vector Shift original mechanical logic. Shared by the browser and Node test harness.
 * Arrows are polyomino/snake bodies: cells[0]=tail … cells[last]=head; d = exit facing from head.
 * Blue arrows: phase rotates facing (d+phase)%4 AND body 90° CW around the head (y-down).
 * Optional mask/shape: playable cells form a silhouette. Exit ray that steps into non-playable
 * "void" is CLEAR (Arrow Out irregular-board rule). Absent mask ⇒ full size×size square.
 */
(function(root){
'use strict';
const DX=[0,1,0,-1],DY=[-1,0,1,0];
const playableCache=typeof WeakMap!=='undefined'?new WeakMap():null;

function headCell(a){
  if(a.cells&&a.cells.length){const c=a.cells[a.cells.length-1];return {x:c[0],y:c[1]}}
  return {x:a.x,y:a.y};
}
function normalizeArrow(a){
  if(a.cells&&a.cells.length)return a;
  return {id:a.id,color:a.color,d:a.d,cells:[[a.x,a.y]]};
}
function rotCW(dx,dy){return [-dy,dx]}
function cellsAtPhase(a,phase){
  const base=normalizeArrow(a).cells;
  const cells=base.map(c=>[c[0],c[1]]);
  const turns=(a.color==='blue'?(phase|0):0)%4;
  if(!turns)return cells;
  const hx=cells[cells.length-1][0],hy=cells[cells.length-1][1];
  for(let t=0;t<turns;t++){
    for(let i=0;i<cells.length-1;i++){
      const dx=cells[i][0]-hx,dy=cells[i][1]-hy;
      const r=rotCW(dx,dy);
      cells[i]=[hx+r[0],hy+r[1]];
    }
  }
  return cells;
}
function direction(a,phase){return (a.d+(a.color==='blue'?phase:0))%4}

/** Set of "x,y" keys that are playable. Cached per level object when WeakMap exists. */
function playableSet(level){
  if(playableCache){
    const hit=playableCache.get(level);
    if(hit)return hit;
  }
  const set=new Set();
  if(level.mask&&level.mask.length){
    for(const c of level.mask)set.add(c[0]+','+c[1]);
  }else{
    for(let y=0;y<level.size;y++)for(let x=0;x<level.size;x++)set.add(x+','+y);
  }
  if(playableCache)playableCache.set(level,set);
  return set;
}
function isPlayable(level,x,y){
  return playableSet(level).has(x+','+y);
}
function maskCellCount(level){return playableSet(level).size}

function newState(level){return {phase:0,remaining:level.arrows.map(a=>a.id),moves:0,toggles:0,history:[]}}
function arrow(level,id){return level.arrows.find(a=>a.id===id)}

function occupancyMap(level,state){
  const map=new Map();
  for(const id of state.remaining){
    const a=arrow(level,id);if(!a)continue;
    for(const [x,y] of cellsAtPhase(a,state.phase))map.set(x+','+y,id);
  }
  return map;
}
/**
 * Walk exit ray from head. Stops at foreign occupancy.
 * Stepping onto a non-playable cell (void / off silhouette) ends the ray as CLEAR
 * (that step is not included — void is outside the board).
 */
function blockers(level,state,id){
  const a=arrow(level,id);
  if(!a||!state.remaining.includes(id))return null;
  const d=direction(a,state.phase);
  const cells=cellsAtPhase(a,state.phase);
  const head=cells[cells.length-1];
  let x=head[0]+DX[d],y=head[1]+DY[d];
  const occ=occupancyMap(level,state);
  const found=[];
  const seen=new Set();
  while(isPlayable(level,x,y)){
    const hit=occ.get(x+','+y);
    if(hit!==undefined&&hit!==id&&!seen.has(hit)){seen.add(hit);found.push(hit)}
    x+=DX[d];y+=DY[d];
  }
  return found;
}
function clearPath(level,state,id){const b=blockers(level,state,id);return b!==null&&b.length===0}
function exitRayCells(level,state,id){
  const a=arrow(level,id);
  if(!a||!state.remaining.includes(id))return [];
  const d=direction(a,state.phase);
  const cells=cellsAtPhase(a,state.phase);
  const head=cells[cells.length-1];
  const occ=occupancyMap(level,state);
  const ray=[];
  let x=head[0]+DX[d],y=head[1]+DY[d];
  while(isPlayable(level,x,y)){
    const hit=occ.get(x+','+y);
    if(hit!==undefined&&hit!==id){ray.push([x,y]);break}
    ray.push([x,y]);
    x+=DX[d];y+=DY[d];
  }
  return ray;
}
function transition(level,state,act){
  if(act.type==='reset')return newState(level);
  const s={phase:state.phase,remaining:[...state.remaining],moves:state.moves,toggles:state.toggles,history:state.history.map(h=>({...h,remaining:[...h.remaining]}))};
  if(act.type==='undo'){
    const last=s.history.pop();if(!last)return s;
    Object.assign(s,{phase:last.phase,remaining:[...last.remaining],moves:last.moves,toggles:last.toggles});return s;
  }
  if(act.type==='toggle'||(act.type==='remove'&&clearPath(level,s,act.id))){
    s.history.push({phase:s.phase,remaining:[...s.remaining],moves:s.moves,toggles:s.toggles});
    s.moves++;
    if(act.type==='toggle'){s.phase=1-s.phase;s.toggles++}
    else s.remaining=s.remaining.filter(x=>x!==act.id);
  }
  return s;
}
function solve(level,state,allowToggle=true){
  const ids=level.arrows.map(a=>a.id),lookup=new Map(ids.map((id,i)=>[id,i]));
  if(ids.length>23)throw new Error('Solver supports <=23 arrows');
  const ray=level.arrows.map(()=>[0,0]);
  for(let p=0;p<2;p++){
    const cellOwner=new Map();
    for(let j=0;j<ids.length;j++){
      for(const [x,y] of cellsAtPhase(level.arrows[j],p))cellOwner.set(x+','+y,j);
    }
    for(let i=0;i<ids.length;i++){
      const a=level.arrows[i],d=direction(a,p);
      const cells=cellsAtPhase(a,p);
      const head=cells[cells.length-1];
      let x=head[0]+DX[d],y=head[1]+DY[d];
      while(isPlayable(level,x,y)){
        const j=cellOwner.get(x+','+y);
        if(j!==undefined&&j!==i)ray[i][p]|=(1<<j);
        x+=DX[d];y+=DY[d];
      }
    }
  }
  let mask=0;for(const id of state.remaining){const i=lookup.get(id);if(i===undefined)throw new Error('bad remaining id');mask|=1<<i}
  const init=mask*2+state.phase,queue=[init],visited=new Set([init]),back=new Map();let headQ=0;
  const reconstruct=node=>{let out=[];while(node!==init){let e=back.get(node);out.push(e.action);node=e.prev}return out.reverse()};
  while(headQ<queue.length){
    const node=queue[headQ++],currentMask=Math.floor(node/2),phase=node%2;
    if(currentMask===0)return {actions:reconstruct(node),explored:visited.size};
    for(let i=0;i<ids.length;i++){
      if((currentMask&(1<<i))&&!(currentMask&ray[i][phase])){
        const dest=((currentMask^(1<<i))*2+phase);
        if(!visited.has(dest)){visited.add(dest);back.set(dest,{prev:node,action:{type:'remove',id:ids[i]}});queue.push(dest)}
      }
    }
    if(allowToggle){const dest=currentMask*2+(1-phase);if(!visited.has(dest)){visited.add(dest);back.set(dest,{prev:node,action:{type:'toggle'}});queue.push(dest)}}
  }
  return {actions:null,explored:visited.size};
}
function validateLevel(level){
  if(!level||!Number.isInteger(level.size)||level.size<3||level.size>12||!Array.isArray(level.arrows))throw new Error('invalid level');
  if(level.mask){
    if(!Array.isArray(level.mask)||!level.mask.length)throw new Error('empty mask');
    const seenM=new Set();
    for(const c of level.mask){
      if(!Array.isArray(c)||c.length<2)throw new Error('bad mask cell');
      const x=c[0],y=c[1];
      if(!Number.isInteger(x)||!Number.isInteger(y)||x<0||y<0||x>=level.size||y>=level.size)throw new Error('mask oob');
      const k=x+','+y;if(seenM.has(k))throw new Error('dup mask');seenM.add(k);
    }
  }
  const ids=new Set();
  for(const raw of level.arrows){
    const a=normalizeArrow(raw);
    if(ids.has(a.id)||![0,1,2,3].includes(a.d)||!['blue','gold'].includes(a.color)||!a.cells.length)throw new Error('bad arrow '+JSON.stringify(raw));
    ids.add(a.id);
    for(let i=0;i<a.cells.length;i++){
      const [x,y]=a.cells[i];
      if(!Number.isInteger(x)||!Number.isInteger(y)||!isPlayable(level,x,y))throw new Error('non-playable cell '+JSON.stringify(raw));
      if(i>0){
        const [px,py]=a.cells[i-1];
        if(Math.abs(px-x)+Math.abs(py-y)!==1)throw new Error('non-adjacent body '+JSON.stringify(raw));
      }
    }
  }
  for(const phase of [0,1]){
    const seen=new Set();
    for(const raw of level.arrows){
      const cells=cellsAtPhase(raw,phase);
      for(const [x,y] of cells){
        if(!isPlayable(level,x,y))throw new Error('phase '+phase+' outside mask '+JSON.stringify(raw));
        const k=x+','+y;
        if(seen.has(k))throw new Error('phase '+phase+' overlap at '+k);
        seen.add(k);
      }
    }
  }
  return true;
}
const API={DX,DY,direction,newState,arrow,blockers,clearPath,transition,solve,validateLevel,headCell,cellsAtPhase,normalizeArrow,occupancyMap,exitRayCells,rotCW,isPlayable,playableSet,maskCellCount};
root.VectorShiftCore=API;
if(typeof module!=='undefined'&&module.exports)module.exports=API;
})(typeof window!=='undefined'?window:globalThis);
