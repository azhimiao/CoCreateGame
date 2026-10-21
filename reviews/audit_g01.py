"""Independent finite-data audit, not a game implementation. Writes reviews only."""
from pathlib import Path
from datetime import datetime
from collections import deque
import copy, hashlib, importlib.util, json, re, shutil, subprocess, sys
from jsonschema import Draft202012Validator

BASE = Path(__file__).resolve().parent
SOURCE = BASE.parent / 'games/G01'
DEST = BASE / 'G01-checks'
SNAP = BASE / 'G01-final-snapshot'

def dump(p, d):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

def read(p): return json.loads(p.read_text(encoding='utf-8'))

def gate_values(l, removed):
    return {g['id']: bool(g['initial_open'] ^ (sum(g['id'] in a['toggles'] for a in l['arrows'] if a['id'] in removed) % 2)) for g in l['gates']}

def hit_distance(direction, body, point):
    """Analytic collinear separation, independently of translated-cell union."""
    distances=[]
    for x,y in body:
        px,py=point
        if direction=='E' and py==y and px>x: distances.append(px-x)
        if direction=='W' and py==y and px<x: distances.append(x-px)
        if direction=='S' and px==x and py>y: distances.append(py-y)
        if direction=='N' and px==x and py<y: distances.append(y-py)
    return min(distances) if distances else None

def reason(l, removed, aid):
    arrows={a['id']:a for a in l['arrows']}
    if aid not in arrows or aid in removed: return 'UNKNOWN_OR_REMOVED'
    a=arrows[aid]
    if l['manifest'] and a['direction']!=l['manifest'][len(removed)]: return 'MANIFEST_MISMATCH'
    groups=[('ARROW_COLLISION',[(p,b['id']) for b in l['arrows'] if b['id']!=aid and b['id'] not in removed for p in b['cells']]),
            ('WALL_COLLISION',[(p,'wall') for p in l['walls']]),
            ('CLOSED_GATE',[(p,g['id']) for g in l['gates'] if not gate_values(l,removed)[g['id']] for p in g['cells']])]
    for label,points in groups:
        if any(hit_distance(a['direction'],a['cells'],p) is not None for p,_ in points): return label
    return None

def graph(l):
    empty=frozenset(); full=frozenset(a['id'] for a in l['arrows'])
    paths={empty:[]}; edges={}; q=deque([empty])
    while q:
        s=q.popleft(); edges[s]=[]
        for aid in sorted(full-s):
            if reason(l,s,aid) is None:
                nxt=s|{aid}; edges[s].append((aid,nxt))
                if nxt not in paths: paths[nxt]=paths[s]+[aid]; q.append(nxt)
    counts={}
    for s in sorted(paths,key=len,reverse=True): counts[s]=1 if s==full else sum(counts[n] for _,n in edges[s])
    return paths,edges,counts

def main():
    assert SOURCE.is_dir()
    files=[]
    # Keep all audit inputs; long original web extracts remain in original baseline only.
    for p in SOURCE.rglob('*'):
        if not p.is_file() or any(x in p.parts for x in ['__pycache__','raw']): continue
        if p.suffix not in ['.md','.json','.py','.txt']: continue
        rel=p.relative_to(SOURCE); dst=SNAP/rel; dst.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(p,dst)
        files.append({'path':rel.as_posix(),'sha256':hashlib.sha256(dst.read_bytes()).hexdigest()})
    dump(SNAP/'audit-manifest.json',{'captured_at':datetime.now().astimezone().isoformat(),'files':files})
    spec=read(SNAP/'game-spec.json'); tasks=read(SNAP/'tasks.json')
    for stem in ['game-spec','tasks']:
        schema=read(SNAP/(stem+'.schema.json')); Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(read(SNAP/(stem+'.json')))
    modspec=importlib.util.spec_from_file_location('g01_author',SNAP/'tools/validate.py')
    author=importlib.util.module_from_spec(modspec);modspec.loader.exec_module(author)
    rows=[]; all_checks=0; reachable_checks=0; report=read(SNAP/'validation/report.json')
    traces={t['level_id']:t['steps'] for t in read(SNAP/'validation/solution-traces.json')}
    report_rows={x['id']:x for x in report['levels']}
    for l in spec['levels']:
        ids=[a['id'] for a in l['arrows']]; paths,edges,counts=graph(l)
        assert counts[frozenset()]>0
        for mask in range(1<<len(ids)):
            removed=frozenset(ids[i] for i in range(len(ids)) if mask & (1<<i))
            assert gate_values(l,removed)==author.gate_state(l,mask)
            assert reason(l,removed,'_unknown')=='UNKNOWN_OR_REMOVED'
            for i,aid in enumerate(ids):
                assert reason(l,removed,aid)==author.reason(l,mask,i),(l['id'],mask,aid)
                all_checks+=1
                if removed in paths: reachable_checks+=1
        removed=frozenset(); trace=[]
        for action in l['solution']:
            aid=action['arrow_id']; assert reason(l,removed,aid) is None
            before=sum(1<<i for i,x in enumerate(ids) if x in removed); removed=removed|{aid}
            trace.append(dict(arrow_id=aid,mask_before=before,mask_after=sum(1<<i for i,x in enumerate(ids) if x in removed),gate_open_after=gate_values(l,removed),manifest_cursor_after=len(removed) if l['manifest'] else 0))
        assert len(removed)==len(ids) and trace==traces[l['id']]
        dead=[s for s in paths if len(s)<len(ids) and not edges[s]]
        rr=report_rows[l['id']]
        stats={'reachable_states':len(paths),'winning_solution_count':counts[frozenset()], 'deadlock_states':len(dead), 'losing_states':sum(v==0 for v in counts.values())}
        assert all(rr[k]==v for k,v in stats.items()),(l['id'],stats,rr)
        if rr['deadlock_witness']:
            history=rr['deadlock_witness']['accepted_exits']; s=frozenset()
            for aid in history: assert reason(l,s,aid) is None; s=s|{aid}
            assert s in dead and gate_values(l,s)==rr['deadlock_witness']['gate_open']
            assert sorted(set(ids)-s)==sorted(rr['deadlock_witness']['remaining'])
        ablation={}
        for name in ['remove_gates','remove_manifest','remove_both']:
            x=copy.deepcopy(l)
            if name in ['remove_gates','remove_both']:
                x['gates']=[]
                for a in x['arrows']: a['toggles']=[]
            if name in ['remove_manifest','remove_both']: x['manifest']=[]
            pp,ee,cc=graph(x)
            ablation[name]={'reachable_states':len(pp),'solutions':cc[frozenset()],'losing_states':sum(v==0 for v in cc.values())}
        choices=[{'history':paths[s],'winning':[aid for aid,n in edges[s] if counts[n]>0], 'losing':[aid for aid,n in edges[s] if counts[n]==0]} for s in paths if counts[s]>0 and any(counts[n]==0 for _,n in edges[s])]
        rows.append(dict(id=l['id'],arrows=len(ids),witness=[a['arrow_id'] for a in l['solution']],**stats,trap_choices=choices,ablation=ablation))
    projections=[]
    for block in re.findall(r'```json\s*(.*?)\s*```',(SNAP/'05_Levels_Economy.md').read_text(encoding='utf-8'),re.S):
        item=json.loads(block); actual=next(l for l in spec['levels'] if l['id']==item['id'])
        assert all(actual[k]==v for k,v in item.items()),item['id']; projections.append(item['id'])
    assert projections==spec['progression']['order']
    byid={t['id']:t for t in tasks['tasks']}
    def ancestors(tid):
        found=set();q=list(byid[tid]['depends_on'])
        while q:
            x=q.pop(); assert x in byid
            if x not in found:found.add(x);q.extend(byid[x]['depends_on'])
        assert tid not in found
        return found
    for t in tasks['tasks']:
        a=ancestors(t['id'])
        if t['stage'] in ['AFTER_HUMAN_BUILD_APPROVAL','AFTER_FULL_INVITATION']:assert {'T01','T02'}<=a
    manifest_hashes={f:hashlib.sha256((SNAP/f).read_bytes()).hexdigest() for f in report['inputs_sha256']}
    assert manifest_hashes==report['inputs_sha256']
    cases={}
    x=copy.deepcopy(spec);x['levels'][-1]['id']='L19';x['progression']['order'][-1]='L19';cases['duplicate_campaign_id']=('game-spec.json',x)
    x=copy.deepcopy(spec);x['rules']['commit_order']=list(reversed(x['rules']['commit_order']));cases['reversed_commit_order']=('game-spec.json',x)
    x=copy.deepcopy(tasks);next(t for t in x['tasks'] if t['id']=='T04')['depends_on']=[];cases['approval_gate_bypass']=('tasks.json',x)
    x=copy.deepcopy(spec);x['levels'][0]['arrows'][0]['cells'][0]=[-1,1];cases['out_of_bounds']=('game-spec.json',x)
    probes=[]
    for name,(file,data) in cases.items():
        case=DEST/'mutation-probes'/name
        for f in ['game-spec.json','game-spec.schema.json','tasks.json','tasks.schema.json','tools/validate.py']:
            target=case/f;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(SNAP/f,target)
        dump(case/file,data)
        run=subprocess.run([sys.executable,'-X','utf8','-B',str(case/'tools/validate.py')],capture_output=True,text=True,encoding='utf-8')
        probes.append(dict(case=name,accepted=run.returncode==0,returncode=run.returncode,stdout=run.stdout,stderr=run.stderr[-2200:]))
    rerun=DEST/'author-rerun'
    for f in ['game-spec.json','game-spec.schema.json','tasks.json','tasks.schema.json','tools/validate.py']:
        target=rerun/f;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(SNAP/f,target)
    run=subprocess.run([sys.executable,'-X','utf8','-B',str(rerun/'tools/validate.py')],capture_output=True,text=True,encoding='utf-8')
    assert run.returncode==0,run.stderr
    result=dict(result='PASS_CURRENT_LEVELS',scope='Independent finite data only; no game/runtime/browser/player tests',checked_at=datetime.now().astimezone().isoformat(),independent_algorithm='frozenset states; analytic collinear body/obstacle distances',levels=rows,reachable_states=sum(r['reachable_states'] for r in rows),reachable_transition_comparisons=reachable_checks,all_subset_transition_comparisons=all_checks,document_projections=projections,input_hashes_match=True,tasks_acyclic=True,approval_ancestors_valid=True,mutation_probes=probes,author_rerun=dict(returncode=run.returncode,stdout=run.stdout,stderr=run.stderr))
    dump(DEST/'independent-results.json',result)
    print(json.dumps({k:v for k,v in result.items() if k not in ['levels','document_projections','author_rerun']},ensure_ascii=False))

if __name__=='__main__': main()
