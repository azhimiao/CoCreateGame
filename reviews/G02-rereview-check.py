import copy, hashlib, importlib.metadata, json, platform, sys, types, zipfile
from collections import Counter, deque
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
root = Path(r"F:\CoCreateGame\games\G02")
def read(name):
    return json.loads((root / name).read_text(encoding="utf-8"))
def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
spec = read("game-spec.json")
def initial(level):
    return tuple("".join(t["items"]) for t in level["containers"]), ("",) * len(level["containers"])
def won(level, state):
    return not any(state[0]) and Counter(c for c in state[1] if c) == Counter(level["win"]["sealed_colours"])
def invariant(level, state):
    stacks, sealed = state
    assert len(stacks) == len(sealed) == len(level["containers"])
    total = Counter("".join(stacks))
    for i, tray in enumerate(level["containers"]):
        assert len(stacks[i]) <= tray["capacity"] and set(stacks[i]) <= set(tray["accepts"])
        if sealed[i]:
            assert not stacks[i] and tray["sealable"]
            total[sealed[i]] += level["demand"][sealed[i]]
    assert total == Counter(level["demand"])
    assert len([c for c in sealed if c]) == len(set(c for c in sealed if c))
def edges(level, state):
    stacks, sealed = state
    trays = level["containers"]
    stamps = set(sealed) - {""}
    opened = [i for i, t in enumerate(trays) if not sealed[i] and all(c in stamps for c in t["unlock_after"])]
    out = []
    for i in opened:
        s = stacks[i]
        if s and trays[i]["sealable"] and len(set(s)) == 1 and len(s) == level["demand"][s[0]]:
            ns, nc = list(stacks), list(sealed)
            ns[i], nc[i] = "", s[0]
            out.append((("seal", trays[i]["id"]), (tuple(ns), tuple(nc))))
    for i in opened:
        if not stacks[i]:
            continue
        c = stacks[i][-1]
        for j in opened:
            if i == j or len(stacks[j]) >= trays[j]["capacity"] or c not in trays[j]["accepts"]:
                continue
            if stacks[j] and stacks[j][-1] != c:
                continue
            ns = list(stacks)
            ns[i], ns[j] = ns[i][:-1], ns[j] + c
            out.append((("move", trays[i]["id"], trays[j]["id"]), (tuple(ns), sealed)))
    return out
def action_key(a):
    return ("seal", a["at"]) if a["op"] == "seal" else ("move", a["src"], a["dst"])
def replay(level):
    state = initial(level)
    invariant(level, state)
    for a in level["solution"]:
        choices = dict(edges(level, state))
        assert action_key(a) in choices, (level["id"], a, state)
        state = choices[action_key(a)]
        invariant(level, state)
    assert won(level, state), level["id"]
def graph(level):
    start = initial(level)
    distances, incoming = {start: 0}, {}
    q, wins, deadlocks = deque([start]), [], 0
    while q:
        state = q.popleft()
        invariant(level, state)
        adjacent = edges(level, state)
        if won(level, state):
            wins.append(state)
        elif not adjacent:
            deadlocks += 1
        for _, nxt in adjacent:
            incoming.setdefault(nxt, []).append(state)
            if nxt not in distances:
                distances[nxt] = distances[state] + 1
                q.append(nxt)
    assert wins
    can_win, rq = set(wins), deque(wins)
    while rq:
        for prev in incoming.get(rq.popleft(), []):
            if prev not in can_win:
                can_win.add(prev)
                rq.append(prev)
    return min(distances[s] for s in wins), len(distances), deadlocks, len(distances) - len(can_win)
rows = []
for level in spec["levels"]:
    print("LEVEL_BEGIN", level["id"], flush=True)
    replay(level)
    shortest, count, deadlocks, no_win_path = graph(level)
    assert shortest == level["par_actions"] == len(level["solution"])
    rows.append({"id": level["id"], "shortest": shortest, "reachable": count,
                 "immediate_deadlocks": deadlocks, "no_path_to_win_states": no_win_path})
    if level["id"] in ("L09", "L13"):
        reduced = copy.deepcopy(level)
        reduced["containers"] = reduced["containers"][:-1]
        replay(reduced)
print("INDEPENDENT_FINISHED", flush=True)

# Current independent re-review additions. Historical mutation expectation is NOT run.
import importlib.util, inspect
sys.path.insert(0,str(root/'tools'))
ms=importlib.util.spec_from_file_location('g02_current_author',root/'tools/verify.py')
author=importlib.util.module_from_spec(ms);sys.modules[ms.name]=author;ms.loader.exec_module(author)
normal_vectors=author.rule_vectors()
source=inspect.getsource(author.actions)
needle='or (target and target[-1] != colour)'
assert source.count(needle)==1
namespace={}
exec(compile(source.replace('def actions(', 'def audit_mutated_actions(').replace(needle,'or False'),'<single-clause-mutation>','exec'),author.__dict__,namespace)
original=author.actions;author.actions=namespace['audit_mutated_actions']
try:
    author.rule_vectors()
except AssertionError as error:
    assert str(error)=='same_top_spare_capacity_rejected',str(error)
    mutation={'result':'REJECTED_AS_EXPECTED','failed_vector':str(error),'historical_baseline':'Old version let 24 vectors pass; now expectation is rejection.'}
else:
    raise AssertionError('same-top mutation survived current vectors')
finally:author.actions=original
import check_contracts as contracts
# Directed independent assertions against the author's protocol probe, beyond its tables.
p=contracts.Probe()
cmd={'run_id':'R1','command_epoch':'E1','command_seq':1,'expected_revision':0,'op':'move','src':'T0','dst':'T2'}
first=p.dispatch(cmd,'ACCEPT');receipt=copy.deepcopy(first['receipt'])
retries=[]
for status in ('ANIMATING','PAUSE','WIN','PLAY'):
    p.status=status;before=copy.deepcopy(p.__dict__);again=p.dispatch(cmd,'TARGET_FULL')
    assert again['cached'] and again['receipt']==receipt and before==p.__dict__
    retries.append(status)
p.status='PLAY';conflict=copy.deepcopy(cmd);conflict['dst']='T1';before=copy.deepcopy(p.__dict__)
assert p.dispatch(conflict,'ACCEPT')['reason']=='ID_CONFLICT' and before==p.__dict__
# A consumed rejection stays rejected after status and revision change; no new side effects.
reject={**cmd,'command_seq':2,'expected_revision':1}
p.status='ANIMATING';failed=p.dispatch(reject,'ACCEPT');assert failed['reason']=='BUSY'
p.status='PLAY';before=copy.deepcopy(p.__dict__);again=p.dispatch(reject,'ACCEPT')
assert again['receipt']==failed['receipt'] and before==p.__dict__
old=copy.deepcopy(cmd);preserved=p.snapshot();p.restore('E-audit-new')
assert p.snapshot()==preserved and p.high==0 and not p.cache
before=copy.deepcopy(p.__dict__);assert p.dispatch(old,'ACCEPT')['reason']=='STALE_EPOCH' and before==p.__dict__
new={**cmd,'command_epoch':'E-audit-new','expected_revision':p.revision};assert p.dispatch(new,'ACCEPT')['reason']=='OK'
# Known rule priority and actual undo fixture independently encoded via graph functions.
l=copy.deepcopy(spec['levels'][0]);l['containers']=[{'id':'T0','capacity':2,'items':['B'],'accepts':['A','B'],'unlock_after':[],'sealable':True},{'id':'T1','capacity':2,'items':['A'],'accepts':['A','B'],'unlock_after':[],'sealable':True},{'id':'T2','capacity':2,'items':['A','B'],'accepts':['A','B'],'unlock_after':[],'sealable':True}];l['demand']={'A':2,'B':2};l['win']['sealed_colours']=['A','B']
assert ('move','T0','T1') not in dict(edges(l,initial(l)))
# Recompute all 5 geometry cases from written section 06, including actual top for each occupancy.
layout=[]
for case in read('layout-cases.json')['cases']:
    w,h=case['viewport'];left,top,right,bottom=case['insets'];w-=left+right;h-=top+bottom
    portrait=h>=w;cols=3 if portrait else 6;cw=(w-8-(cols-1)*4)/cols
    assert (portrait and w>=304 and h>=480) or (not portrait and w>=480 and h>=296)
    for i in range(6):
        x,y=4+(i%cols)*(cw+4),84+(i//cols)*162
        assert x>=0 and y+158<=h and x+cw<=w
        for center in (42,66,90):assert y+center+22<=y+114 and x+cw/2-22>=x and x+cw/2+22<=x+cw
    assert (436 if portrait else 252)+44<=h
    layout.append({'case':case['id'],'mode':'portrait' if portrait else 'landscape','safe':[w,h],'min_card_width':cw,'status':'PASS'})
# Portable package: exact set, duplicate prevention, CRC, every manifest hash and actual member bytes.
manifest=read('package-manifest.json');archive=root/'G02_Preparation_2026-10-21.zip'
for entry in manifest['files']:
    pth=root/entry['path'];assert pth.stat().st_size==entry['bytes'] and digest(pth)==entry['sha256']
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    names=z.namelist();assert len(names)==len(set(names))
    assert set(names)=={'G02/'+e['path'] for e in manifest['files']}|{'G02/package-manifest.json'}
    for name in names:
        parts=Path(name).parts;assert parts[0]=='G02' and '..' not in parts
        assert z.read(name)==root.joinpath(*parts[1:]).read_bytes()
stored=read('verification/verification-report.json')
assert stored['overall_status']=='PASS'
assert all(digest(root/n)==h for n,h in stored['input_sha256'].items())
# Validate original research independently, never count mere frame integrity as core play.
e=read('evidence/team-browser-observation-index.json')
research=root.parents[1]/'research/playthroughs/G02'
frames=e['screenshots']
for frame in frames:
    pth=research/frame['file'];assert pth.stat().st_size==frame['bytes'] and digest(pth)==frame['sha256']
assert e['confirmed_effective_core_inputs']==0 and len(frames)==13
hashes={str(p.relative_to(root)).replace('\\','/'):digest(p) for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
result={'scope':'INDEPENDENT_REVIEW_NOT_ENGINE_BUILD','independent_levels':rows,'total_reachable':sum(x['reachable'] for x in rows),'no_path_to_win':sum(x['no_path_to_win_states'] for x in rows),'author_vectors':len(normal_vectors),'same_top_mutation':mutation,'directed_retry_statuses':retries,'cached_rejection_retested':True,'restore_new_epoch_old_retry_rejected':True,'independent_layout':layout,'zip_members':len(names),'manifest_payloads':len(manifest['files']),'zip_sha256':digest(archive),'research_core_inputs':0,'research_screenshots_hashed':13,'source_sha256':hashes,'engine_build_executed':False,'result':'PASS'}
output=Path(r'F:\CoCreateGame\reviews\G02-rereview-results.json')
output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k not in ('source_sha256','independent_levels')},ensure_ascii=False,indent=2))
