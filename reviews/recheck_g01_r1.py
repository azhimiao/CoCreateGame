"""Independent G01 audit-r1 recheck. All writes remain in reviews/."""
from pathlib import Path
from hashlib import sha256
from datetime import datetime, timezone
import copy
import importlib.util
import json
import shutil
import subprocess
import sys
from jsonschema import Draft202012Validator
import audit_g01 as model

BASE=Path(__file__).resolve().parent
SNAP=BASE/'G01-recheck-r1-final'
RUN=BASE/'G01-r1-exec'
OUT=BASE/'G01-checks/r1'
OUT.mkdir(exist_ok=True)
MAX=9007199254740991
checks=[]
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def expect(ok,name):
    checks.append({'check':name,'passed':bool(ok)})
    assert ok,name
def digest(p):return sha256(p.read_bytes()).hexdigest()
def parse(raw):
    def unique(pairs):
        d={}
        for k,v in pairs:
            if k in d:raise ValueError('duplicate')
            d[k]=v
        return d
    return json.loads(raw,object_pairs_hook=unique,parse_constant=lambda v:(_ for _ in ()).throw(ValueError(v)))

def classify(raw,spec,schema):
    if len(raw.encode('utf-8'))>65536:return 'REJECT_OVERSIZE',None
    try:v=parse(raw)
    except ValueError:return 'REJECT_JSON',None
    if not isinstance(v,dict):return 'REJECT_SCHEMA',None
    if type(v.get('version')) is int and v['version']>1:return 'READ_ONLY_NEWER_VERSION',None
    if v.get('version')==1 and v.get('content_version')!='1.0.0':return 'RECOVERY_CONTENT_VERSION',None
    if not schema.is_valid(v) or type(v['revision']) is not int:return 'REJECT_SCHEMA',None
    ids=[f'L{i:02}' for i in range(1,21)]
    if v['completed']!=ids[:len(v['completed'])]:return 'REJECT_COMPLETED_PREFIX',None
    if ids.index(v['active_level'])>len(v['completed']):return 'REJECT_LOCKED_ACTIVE',None
    level=spec['levels'][ids.index(v['active_level'])];removed=frozenset()
    for aid in v['accepted_exits']:
        if model.reason(level,removed,aid) is not None:return 'REJECT_REPLAY',None
        removed|={aid}
    output=copy.deepcopy(v)
    if len(removed)==len(level['arrows']) and level['id'] not in v['completed']:
        if v['revision']==MAX:return 'RECOVERY_REVISION_EXHAUSTED',None
        output['completed'].append(level['id']);output['revision']+=1
        return 'ACCEPT_REPAIR_COMPLETION',output
    return 'ACCEPT',output

def main():
    spec=read(SNAP/'game-spec.json');tasks=read(SNAP/'tasks.json');report=read(SNAP/'validation/report.json')
    before=read(BASE/'G01-final-snapshot/game-spec.json');freeze=read(SNAP/'validation/revision-baseline.json')
    expect([l['id'] for l in spec['levels']]==[f'L{i:02}' for i in range(1,21)],'current exact campaign IDs/order')
    for a,b in zip(before['levels'],spec['levels']):
        expect(all(a[k]==b[k] for k in freeze['layout_fields']),'unchanged geometry/rules/solution '+b['id'])
    for p,value in report['inputs_sha256'].items():expect(digest(SNAP/p)==value,'authored report input hash '+p)
    for name,data in [('game-spec',spec),('tasks',tasks)]:
        schema=read(SNAP/(name+'.schema.json'));Draft202012Validator.check_schema(schema);Draft202012Validator(schema).validate(data)
        expect(True,'schema/current '+name)
    schema=read(SNAP/'save-envelope.schema.json');Draft202012Validator.check_schema(schema);sv=Draft202012Validator(schema)
    baseline=[]
    # The already searched graph is unchanged; this small replay checks all supplied
    # witnesses against the independent analytic collision model, without another search.
    for l in spec['levels']:
        removed=frozenset()
        for command in l['solution']:
            aid=command['arrow_id'];expect(model.reason(l,removed,aid) is None,'independent witness '+l['id']+'/'+aid);removed|={aid}
        expect(len(removed)==len(l['arrows']),'independent full clear '+l['id']);baseline.append(l['id'])
    saves=read(SNAP/'contracts/save-vectors.json');save_results=[]
    for c in saves['cases']:
        raw=c.get('raw_json',json.dumps(c.get('envelope'),ensure_ascii=False,separators=(',',':')))
        status,normalized=classify(raw,spec,sv)
        expect(status==c['expected_status'],'independent save classification '+c['id'])
        if 'expected_normalized' in c:expect(normalized==c['expected_normalized'],'independent save normalization '+c['id'])
        if status=='ACCEPT_REPAIR_COMPLETION':
            again,second=classify(json.dumps(normalized),spec,sv)
            expect(again=='ACCEPT' and second==normalized,'completion repair idempotent')
        save_results.append({'id':c['id'],'independent_status':status})
    vectors=read(SNAP/'contracts/session-vectors.json');session_results=[];all_events=set()
    for case in vectors['cases']:
        ctx=copy.deepcopy(case['initial_context']);requested=set();acknowledged=set();steps=[]
        for step in case['steps']:
            generated=[];snapshot=None;start=copy.deepcopy(ctx)
            if step['kind'] in ['EXIT_FACT','UNDO_FACT']:
                level=next(l for l in spec['levels'] if l['id']==ctx['level_id']);ids=[a['id'] for a in level['arrows']]
                removed=frozenset(ctx['accepted_exits']);mask=lambda s:sum(1<<i for i,aid in enumerate(ids) if aid in s)
                expect(step['attempt_before']['accepted_exits']==ctx['accepted_exits'] and step['attempt_before']['revision']==ctx['revision'],'session attempt agrees '+case['id'])
                if step['kind']=='EXIT_FACT':
                    aid=step['rule_fact']['arrow_id'];expect(model.reason(level,removed,aid) is None,'session fact legal '+case['id'])
                    target=removed|{aid};old=model.gate_values(level,removed);new=model.gate_values(level,target)
                    changes=[{'id':k,'was_open':old[k],'is_open':new[k]} for k in sorted(old) if old[k]!=new[k]]
                    won=len(target)==len(ids);dead=not won and not any(model.reason(level,target,x) is None for x in ids)
                    fact={'kind':'ExitAccepted','level_id':level['id'],'arrow_id':aid,'from_mask':mask(removed),'to_mask':mask(target),'gate_changes':changes,'manifest_cursor':len(target) if level['manifest'] else 0,'won':won,'deadlocked':dead}
                    expect(fact==step['rule_fact'],'independent session-free RuleFact '+case['id'])
                    generated.append(('ExitCommitted',{'arrowId':aid,'fromMask':mask(removed),'toMask':mask(target),'gatesChanged':changes,'cursor':fact['manifest_cursor']}));ctx['accepted_exits'].append(aid)
                    if won:
                        first=level['id'] not in ctx['completed']
                        if first:ctx['completed'].append(level['id'])
                        generated.append(('LevelCompleted',{'levelId':level['id'],'firstClear':first,'stampCount':len(ctx['completed'])}))
                else:
                    ctx['accepted_exits'].pop();target=frozenset(ctx['accepted_exits']);won=len(target)==len(ids);dead=not won and not any(model.reason(level,target,x) is None for x in ids)
                    fact={'kind':'UndoAccepted','level_id':level['id'],'from_mask':mask(removed),'to_mask':mask(target),'won':won,'deadlocked':dead}
                    expect(fact==step['rule_fact'],'independent UndoFact '+case['id']);generated.append(('UndoCommitted',{'fromMask':mask(removed),'toMask':mask(target)}))
                ctx['revision']+=1;expect(ctx['revision'] not in requested,'one save per newly accepted revision')
                requested.add(ctx['revision']);generated.append(('SaveRequested',{'snapshotRevision':ctx['revision']}))
                snapshot={'version':1,'content_version':'1.0.0','revision':ctx['revision'],'completed':ctx['completed'].copy(),'active_level':ctx['level_id'],'accepted_exits':ctx['accepted_exits'].copy(),'tutorial_seen':['base'],'settings':{'language':'en','sound':True,'music':False,'reducedMotion':False}}
                expect(classify(json.dumps(snapshot),spec,sv)[0]=='ACCEPT','session snapshot consistent with save protocol')
            elif step['kind']=='SAVE_ACK':
                rev=step['ack_revision'];expect(rev in requested,'ack has request')
                if rev not in acknowledged:acknowledged.add(rev);generated.append(('SaveSucceeded',{'snapshotRevision':rev}))
            elif step['kind']=='STALE_COMMAND':
                expect(step['expected_revision']!=ctx['revision'],'stale command actually stale');generated.append(('ExitRejected',{'arrowId':step['arrow_id'],'reason':'STALE_REVISION'}))
            elif step['kind']=='ANIMATION_INTERRUPTED':expect(step['expected_new_save_requests']==0 and not step['expected_gameplay_or_save_events'],'interruption no recommit')
            else:raise AssertionError(step['kind'])
            events=[]
            for name,payload in generated:
                event_id=ctx['session_id']+':'+str(ctx['next_seq']);ctx['next_seq']+=1;expect(event_id not in all_events,'unique event '+event_id);all_events.add(event_id)
                events.append({'name':name,'eventId':event_id,'revision':ctx['revision'],'payload':payload})
            expect(events==step['expected_events'],'independent exact published events '+case['id']+'/'+step['kind'])
            expect(snapshot==step.get('expected_save_snapshot'),'independent save requests '+case['id']+'/'+step['kind'])
            expect(ctx==step['expected_context'],'independent context '+case['id']+'/'+step['kind'])
            steps.append({'kind':step['kind'],'events':len(events),'revision':ctx['revision'],'new_save_requests':int(snapshot is not None)})
        session_results.append({'id':case['id'],'save_revisions':sorted(requested),'steps':steps})
    byid={t['id']:t for t in tasks['tasks']}
    def ancestors(i,trail=()):
        expect(i not in trail,'no DAG cycle '+i)
        return set(byid[i]['depends_on']) | set().union(*(ancestors(j,trail+(i,)) for j in byid[i]['depends_on']))
    # Avoid dozens of repeated ancestor diagnostics while checking all task gates.
    def get_anc(i):
        seen=set();stack=byid[i]['depends_on'].copy()
        while stack:
            p=stack.pop();assert p in byid and p!=i
            if p not in seen:seen.add(p);stack.extend(byid[p]['depends_on'])
        return seen
    for t in tasks['tasks']:
        a=get_anc(t['id'])
        if t['stage'] in ['AFTER_HUMAN_BUILD_APPROVAL','AFTER_FULL_INVITATION']:expect({'T01','T02'}<=a,'approval ancestors '+t['id'])
    owner_paths=['future/rules/RuleFacts.ts','future/session/SessionCoordinator.ts','future/app-state/AppStateMachine.ts','future/events/SessionBus.ts','future/scenes/Boot.scene','future/save/SaveCoordinator.ts','future/progress/ProgressPolicy.ts','future/integration/CompositionRoot.ts']
    owners=[]
    for path in owner_paths:
        who=[t['id'] for t in tasks['tasks'] if any(path.startswith(p) for p in t['files'] if p.endswith('/'))]
        expect(len(who)==1,'unique contract module owner '+path);owners.append({'path':path,'task':who[0]})
    # Execute frozen author scripts on a separate reviews copy; their reports can
    # change there while the audit snapshot and authored reports remain untouched.
    shutil.copytree(SNAP,RUN,ignore=shutil.ignore_patterns('raw','__pycache__','AUDIT_SNAPSHOT.json'))
    commands=[]
    for file in ['tools/validate.py','tools/check_audit_mutants.py']:
        run=subprocess.run([sys.executable,'-X','utf8','-B',str(RUN/file)],cwd=RUN,capture_output=True,text=True,encoding='utf-8',timeout=60)
        (OUT/(Path(file).stem+'.stdout.txt')).write_text(run.stdout,encoding='utf-8');(OUT/(Path(file).stem+'.stderr.txt')).write_text(run.stderr,encoding='utf-8')
        expect(run.returncode==0,'author isolated rerun '+file);commands.append({'script':file,'returncode':run.returncode,'stdout':run.stdout.strip()})
    rerun=read(RUN/'validation/report.json');expect(rerun==report,'entire authored validator report reproduced exactly')
    mutants=read(RUN/'validation/audit-mutants.json');expect(mutants==read(SNAP/'validation/audit-mutants.json'),'entire mutation report reproduced exactly')
    expect(len(mutants['cases'])==13 and all(not r['accepted'] for r in mutants['cases'][1:]),'positive baseline and 12 rejected mutations')
    source=BASE.parent/'games/G01'
    unchanged=[r['path'] for r in read(SNAP/'AUDIT_SNAPSHOT.json')['files'] if digest(source/r['path'])!=r['sha256']]
    expect(not unchanged,'frozen authored files unchanged')
    result={'checked_at_utc':datetime.now(timezone.utc).isoformat(),'result':'PASS','scope':'Independent audit-r1 specification/contract recheck; no product code, engine, browser storage or SDK execution','game_spec_sha256':digest(SNAP/'game-spec.json'),'frozen_source_files_unchanged':not unchanged,'check_count':len(checks),'checks':checks,'witnesses_replayed':20,'full_graph_search_repeated':False,'original_level_model':'149 reachable states / 645 reachable actions / 2344 subset comparisons; layout/rule equality retained','independent_save_classifications':save_results,'independent_session_sequences':session_results,'module_owners':owners,'author_script_reruns':commands,'mutations_rejected':12,'closed_findings':['G01-M02','G01-M03','G01-m01','G01-m02'],'remaining_findings':['G01-M01']}
    (OUT/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ['checks','independent_save_classifications','independent_session_sequences','module_owners']},ensure_ascii=False,indent=2))

if __name__=='__main__':main()
