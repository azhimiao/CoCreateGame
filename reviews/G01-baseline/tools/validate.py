"""Small offline finite-data verifier, NOT production game code.

No UI, engine, rendering, SDK, networking, game executable or realtime loop.
Run from any directory: python path/to/G01/tools/validate.py
Requires jsonschema, reports installed version. Writes only G01/validation/.
"""
import copy
import hashlib
import importlib.metadata
import json
import platform
from pathlib import Path
from collections import deque
from jsonschema import Draft202012Validator

ROOT=Path(__file__).resolve().parents[1]
V={'N':(0,-1),'E':(1,0),'S':(0,1),'W':(-1,0)}
def read(name): return json.loads((ROOT/name).read_text(encoding='utf-8'))
def cells(x): return {tuple(p) for p in x}
def inside(l,p): return 0<=p[0]<l['width'] and 0<=p[1]<l['height']

def geometry(l):
    seen=set(); names=set(); gates={g['id'] for g in l['gates']}
    assert len(gates)==len(l['gates'])
    for ar in l['arrows']:
        assert ar['id'] not in names; names.add(ar['id'])
        cc=cells(ar['cells']); assert len(cc)==len(ar['cells'])
        assert all(inside(l,p) for p in cc) and not seen & cc
        seen |= cc
        for a,b in zip(ar['cells'],ar['cells'][1:]): assert abs(a[0]-b[0])+abs(a[1]-b[1])==1
        if len(ar['cells'])>1:
            a,b=ar['cells'][-2:]; assert (b[0]-a[0],b[1]-a[1])==V[ar['direction']]
        assert set(ar['toggles'])<=gates and len(ar['toggles'])==len(set(ar['toggles']))
    for group in [*l['gates'],dict(cells=l['walls'])]:
        cc=cells(group['cells']); assert len(cc)==len(group['cells'])
        assert all(inside(l,p) for p in cc) and not seen & cc
        seen |= cc
    n=len(l['arrows']); assert not l['manifest'] or len(l['manifest'])==n
    assert (l['mode'] in ['RELAY','COMBINED'])==bool(l['gates'])
    assert (l['mode'] in ['MANIFEST','COMBINED'])==bool(l['manifest'])

def gate_state(l,mask):
    gs={g['id']:g['initial_open'] for g in l['gates']}
    for i,a in enumerate(l['arrows']):
        if mask>>i&1:
            for g in a['toggles']: gs[g]=not gs[g]
    return gs

def reason(l,mask,i):
    if mask>>i&1: return 'UNKNOWN_OR_REMOVED'
    a=l['arrows'][i]; cursor=mask.bit_count() if l['manifest'] else 0
    if l['manifest'] and a['direction']!=l['manifest'][cursor]: return 'MANIFEST_MISMATCH'
    dx,dy=V[a['direction']]
    sweep={(x+k*dx,y+k*dy) for x,y in a['cells'] for k in range(1,max(l['width'],l['height'])+1) if inside(l,(x+k*dx,y+k*dy))}
    other=set()
    for j,b in enumerate(l['arrows']):
        if j!=i and not mask>>j&1: other |= cells(b['cells'])
    if sweep&other: return 'ARROW_COLLISION'
    if sweep&cells(l['walls']): return 'WALL_COLLISION'
    gs=gate_state(l,mask)
    if any(not gs[g['id']] and sweep&cells(g['cells']) for g in l['gates']): return 'CLOSED_GATE'
    return None

def reference_legal(l,mask,i):
    """Second formulation: step translation instead of union-of-ray footprint."""
    if mask>>i&1: return False
    a=l['arrows'][i]
    if l['manifest'] and a['direction']!=l['manifest'][mask.bit_count()]: return False
    blocked=cells(l['walls']); gs=gate_state(l,mask)
    for j,b in enumerate(l['arrows']):
        if j!=i and not mask>>j&1: blocked |= cells(b['cells'])
    for g in l['gates']:
        if not gs[g['id']]: blocked |= cells(g['cells'])
    dx,dy=V[a['direction']]; moving=cells(a['cells'])
    for _ in range(max(l['width'],l['height'])):
        moving={(x+dx,y+dy) for x,y in moving}
        if moving&blocked: return False
        if not any(inside(l,p) for p in moving): return True
    raise AssertionError('Exit bound insufficient')

def enumerate_states(l):
    full=(1<<len(l['arrows']))-1; q=deque([0]); seen={0}; edges={}; paths={0:[]}
    while q:
        mask=q.popleft(); edges[mask]=[]
        for i,a in enumerate(l['arrows']):
            legal=reason(l,mask,i) is None
            assert legal==reference_legal(l,mask,i),(l['id'],mask,a['id'],'independent formulations differ')
            if legal:
                nxt=mask|1<<i; edges[mask].append((a['id'],nxt))
                if nxt not in seen: seen.add(nxt); paths[nxt]=paths[mask]+[a['id']]; q.append(nxt)
    assert full in seen,(l['id'],'not solvable')
    counts={full:1}
    for s in sorted(seen,key=int.bit_count,reverse=True):
        if s!=full: counts[s]=sum(counts[t] for _,t in edges[s])
    dead=[s for s in seen if s!=full and not edges[s]]
    first_trap=next((dict(accepted_exits=paths[s],remaining=[a['id'] for i,a in enumerate(l['arrows']) if not s>>i&1],gate_open=gate_state(l,s)) for s in sorted(dead)),None)
    return dict(reachable_states=len(seen),winning_solution_count=counts[0],deadlock_states=len(dead),
                losing_states=sum(counts[s]==0 for s in seen),deadlock_witness=first_trap,
                first_legal=[a for a,_ in edges[0]],first_winning=[a for a,s in edges[0] if counts[s]>0],
                solver_solution=paths[full],transition_checks=sum(len(l['arrows']) for _ in seen))

def schema_checks():
    results=[]
    for f in ['game-spec','tasks']:
        schema=read(f+'.schema.json'); Draft202012Validator.check_schema(schema)
        validator=Draft202012Validator(schema); data=read(f+'.json'); validator.validate(data)
        bad=copy.deepcopy(data); bad['unexpected_property']=True
        assert not validator.is_valid(bad)
        if f=='game-spec':
            bad=copy.deepcopy(data); bad['levels'][0]['arrows'][0]['direction']='NE'; assert not validator.is_valid(bad)
            bad=copy.deepcopy(data); bad['ready_for_build']=True; assert not validator.is_valid(bad)
        else:
            bad=copy.deepcopy(data); bad['tasks'][0]['write_scope']='../'; assert not validator.is_valid(bad)
        results.append(dict(file=f+'.json',valid=True,additional_properties_rejected=True))
    return results

def dag_checks():
    data=read('tasks.json'); ts=data['tasks']; ids={t['id'] for t in ts}; assert len(ids)==len(ts)
    done=[]
    while len(done)<len(ts):
        ready=[t['id'] for t in ts if t['id'] not in done and set(t['depends_on'])<=set(done)]
        assert ready,'cycle or missing task'; done+=ready
    for t in ts:
        assert set(t['depends_on'])<=ids and t['id'] not in t['depends_on']
        assert t['write_scope']=='games/G01/'
        for f in t['files']: assert not f.startswith(('/','\\')) and '..' not in Path(f).parts
    return dict(tasks=len(ts),acyclic=True,topological_order=done,approval_before_build=True)

def adversarial_checks(spec):
    """Meaningful semantic counterexamples, not just replaying claimed solutions."""
    out=[]
    lv={l['id']:l for l in spec['levels']}
    x=lv['L03']; assert reason(x,0,0)=='ARROW_COLLISION'; out.append('BENT_SWEEP_BLOCKED')
    x=lv['L05']; assert reason(x,0,0)=='CLOSED_GATE'; assert reason(x,2,0) is None; out.append('PRESTATE_GATE_THEN_TOGGLE')
    x=lv['L08']; assert gate_state(x,2)['g'] is True and gate_state(x,6)['g'] is False
    assert reason(x,6,0)=='CLOSED_GATE'; assert reason(x,2,0) is None; out.append('DOUBLE_TOGGLE_DEADLOCK_AND_UNDO')
    x=lv['L13']; assert reason(x,0,2)=='MANIFEST_MISMATCH'; assert reason(x,1,2)=='ARROW_COLLISION'; out.append('MANIFEST_SAME_DIRECTION_TRAP')
    x=copy.deepcopy(lv['L05']); x['arrows'][0]['toggles']=['g']; assert reason(x,0,0)=='CLOSED_GATE'; out.append('SELF_OPEN_FORBIDDEN')
    x=copy.deepcopy(lv['L02']); x['walls']=[[4,1]]; assert reason(x,2,0)=='WALL_COLLISION'; out.append('WALL_BLOCKED')
    x=lv['L01']; assert reason(x,1,0)=='UNKNOWN_OR_REMOVED'; out.append('DUPLICATE_EXIT_REJECTED')
    x=copy.deepcopy(lv['L03']); x['arrows'][1]=dict(id='b',direction='N',cells=[[3,1]],toggles=[])
    assert reason(x,0,0)=='ARROW_COLLISION'; out.append('TAIL_SWEEP_NOT_HEAD_RAY')
    x=copy.deepcopy(lv['L01']); x['arrows'][1]['cells']=[[2,1],[2,0]]
    try: geometry(x)
    except AssertionError: out.append('OVERLAP_REJECTED')
    else: raise AssertionError('invalid geometry accepted')
    return out

def main():
    schemas=schema_checks(); spec=read('game-spec.json'); assert len(spec['levels'])==20
    assert [x['id'] for x in spec['levels']]==spec['progression']['order']
    rows=[]; traces=[]
    for l in spec['levels']:
        geometry(l); mask=0; trace=[]; byid={a['id']:i for i,a in enumerate(l['arrows'])}
        for action in l['solution']:
            i=byid[action['arrow_id']]; fail=reason(l,mask,i)
            assert fail is None,(l['id'],action,fail,gate_state(l,mask))
            before=mask; mask |=1<<i
            trace.append(dict(arrow_id=action['arrow_id'],mask_before=before,mask_after=mask,gate_open_after=gate_state(l,mask),manifest_cursor_after=mask.bit_count() if l['manifest'] else 0))
        assert mask==(1<<len(l['arrows']))-1
        stats=enumerate_states(l)
        rows.append(dict(id=l['id'],name=l['name'],arrows=len(l['arrows']),provided_solution_valid=True,**stats))
        traces.append(dict(level_id=l['id'],steps=trace))
    report=dict(result='PASS',scope='offline preparation data only; not Cocos/browser/device/player/business validation',
        recorded_date='2026-10-21',python=platform.python_version(),jsonschema=importlib.metadata.version('jsonschema'),
        design_values='HYPOTHESIS',schemas=schemas,dag=dag_checks(),adversarial_checks=adversarial_checks(spec),levels=rows,
        totals=dict(levels=len(rows),solutions_verified=len(rows),reachable_states=sum(x['reachable_states'] for x in rows),transition_checks=sum(x['transition_checks'] for x in rows)),
        inputs_sha256={f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in ['game-spec.json','tasks.json','game-spec.schema.json','tasks.schema.json']})
    dest=ROOT/'validation'; dest.mkdir(exist_ok=True)
    for name,data in [('report.json',report),('solution-traces.json',traces)]:
        (dest/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(result=report['result'],**report['totals'],adversarial_cases=len(report['adversarial_checks']),schemas=2,tasks=report['dag']['tasks']),ensure_ascii=False))

if __name__=='__main__': main()
