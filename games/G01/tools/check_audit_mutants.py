"""Run current COMPLETE checker on exact audit deltas and further bad specs.

External reviews are read only. Temporary fixtures/results stay under G01/validation.
This is preparation verification, not production game code.
"""
import copy
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
ROOT=Path(__file__).resolve().parents[1]
REVIEWS=ROOT.parents[1]/'reviews'
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def diff(a,b,path=()):
    if type(a)!=type(b): return [(path,b)]
    if isinstance(a,dict):
        assert a.keys()==b.keys(), 'unexpected reviewer delta shape'
        return [d for key in a for d in diff(a[key],b[key],path+(key,))]
    if isinstance(a,list) and len(a)==len(b):
        return [d for i in range(len(a)) for d in diff(a[i],b[i],path+(i,))]
    return [] if a==b else [(path,b)]
def apply(data,changes):
    for path,value in changes:
        obj=data
        for key in path[:-1]: obj=obj[key]
        obj[path[-1]]=copy.deepcopy(value)
spec=read(ROOT/'game-spec.json'); tasks=read(ROOT/'tasks.json'); cases=[]
for name in ['duplicate_campaign_id','reversed_commit_order','out_of_bounds','approval_gate_bypass']:
    source=REVIEWS/'G01-checks/mutation-probes'/name
    badspec,badtasks=copy.deepcopy(spec),copy.deepcopy(tasks); changes={}
    for filename,current in [('game-spec.json',badspec),('tasks.json',badtasks)]:
        original=REVIEWS/'G01-final-snapshot'/filename; mutated=source/filename
        delta=diff(read(original),read(mutated)); apply(current,delta)
        changes[filename]=dict(source_sha256=sha(mutated),baseline_sha256=sha(original),delta=[dict(path=list(p),value=v) for p,v in delta])
    assert any(x['delta'] for x in changes.values())
    cases.append((name,badspec,badtasks,dict(origin='exact original reviewer delta replayed on current spec; current metadata/session contract retained',sources=changes)))
def extra(name,mutate):
    bad=copy.deepcopy(spec); mutate(bad); cases.append((name,bad,copy.deepcopy(tasks),dict(origin='additional negative fixture')))
extra('missing_campaign_id',lambda x:(x['levels'].pop(),x['progression']['order'].pop()))
extra('wrong_campaign_id',lambda x:(x['levels'][-1].__setitem__('id','L21'),x['progression']['order'].__setitem__(-1,'L21')))
def reorder(x):
    x['levels'][0],x['levels'][1]=x['levels'][1],x['levels'][0]
    x['progression']['order'][0],x['progression']['order'][1]=x['progression']['order'][1],x['progression']['order'][0]
extra('reordered_campaign',reorder)
extra('duplicate_progression_only',lambda x:x['progression']['order'].__setitem__(-1,'L19'))
extra('duplicate_levels_only',lambda x:x['levels'][-1].__setitem__('id','L19'))
extra('missing_commit_phase',lambda x:x['rules']['commit_order'].pop())
extra('reversed_legal_priority',lambda x:x['rules']['legal_order'].reverse())
extra('wrong_publisher',lambda x:x['session_contract'].__setitem__('publisher','Rules.commitExit'))
rows=[]
with tempfile.TemporaryDirectory(prefix='audit-mutants-',dir=ROOT/'validation') as temp:
    fixture=Path(temp).resolve(); assert fixture.is_relative_to((ROOT/'validation').resolve())
    for sub in ['tools','contracts','validation','research']: (fixture/sub).mkdir()
    for name in ['validate.py','contracts.py','check_contracts.py','check_audit_mutants.py','link_observation.py','prepare_data.py','prepare_evidence.py','write_level_catalog.py']:
        shutil.copy2(ROOT/'tools'/name,fixture/'tools'/name)
    for name in ['game-spec.schema.json','tasks.schema.json','save-envelope.schema.json']: shutil.copy2(ROOT/name,fixture/name)
    for name in ['save-vectors.json','session-vectors.json']: shutil.copy2(ROOT/'contracts'/name,fixture/'contracts'/name)
    shutil.copy2(ROOT/'validation/revision-baseline.json',fixture/'validation/revision-baseline.json')
    for name in ['00_Project_Charter.md','01_Market_Evidence.md','02_Benchmark_Playthrough.md','03_Full_GDD.md','04_Systems_and_Data.md','05_Levels_Economy.md','06_UI_Art_Audio.md','07_Tech_Architecture.md','08_OpenSource_Licenses.md','09_Implementation_Plan.md','10_QA_Test_Plan.md','11_Distribution_Business.md','12_Falsifiability.md','README.md','STATUS.md','REVISIONS.md']:
        shutil.copy2(ROOT/name,fixture/name)
    for name in ['README.md','observation-coverage.json']: shutil.copy2(ROOT/'research'/name,fixture/'research'/name)
    shutil.copy2(ROOT/'validation/audit-mutants.json',fixture/'validation/audit-mutants.json')
    for name,badspec,badtasks,meta in [('unmodified_current_data',spec,tasks,dict(origin='positive control'))]+cases:
        for file,value in [('game-spec.json',badspec),('tasks.json',badtasks)]: (fixture/file).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        report=fixture/'validation/report.json'
        if report.exists(): report.unlink()
        run=subprocess.run([sys.executable,'-B',str(fixture/'tools/validate.py')],capture_output=True,text=True,encoding='utf-8')
        passed=run.returncode==0 and report.exists() and read(report)['result']=='PASS'
        if name=='unmodified_current_data':
            assert passed and read(report)['totals']==dict(levels=20,solutions_verified=20,reachable_states=149,transition_checks=645)
        else: assert run.returncode!=0 and not report.exists(), ('BAD_MUTANT_ACCEPTED',name)
        diagnostic=' | '.join(line.strip() for line in run.stderr.splitlines() if 'ValidationError:' in line or 'AssertionError:' in line or 'ValueError:' in line)
        rows.append(dict(case=name,exit_code=run.returncode,accepted=passed,expected='PASS' if name=='unmodified_current_data' else 'REJECT',diagnostic=diagnostic[:1000],**meta))
out=dict(result='PASS',scope='offline current full checker; no Cocos/browser/storage runtime',original_review_mutants_rejected=4,additional_mutants_rejected=8,positive_control='20/20,149 states,645 checks',cases=rows,
    checker_sha256={n:sha(ROOT/n) for n in ['tools/validate.py','tools/contracts.py','tools/check_contracts.py','game-spec.schema.json','tasks.schema.json','save-envelope.schema.json','game-spec.json','tasks.json']})
(ROOT/'validation/audit-mutants.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('PASS: original 4 reviewer mutations and 8 additional negatives rejected by full checker; current 20 levels PASS.')
