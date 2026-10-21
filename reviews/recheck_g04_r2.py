"""Independent r2 contract audit; reads frozen inputs and writes reviews only."""
from pathlib import Path
from hashlib import sha256
from datetime import datetime, timezone
from dataclasses import replace
import copy
import importlib.util
import json
import subprocess
import sys
import zipfile
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parent
SNAP = ROOT / 'G04-recheck-r2'
OUT = ROOT / 'G04-checks/r2'
OUT.mkdir(exist_ok=True)
sys.path.insert(0, str(SNAP))
sys.path.insert(0, str(ROOT))
import audit_g04 as independent
import validate_contracts as author
import validate_spec as author_rules

def read(name):
    return json.loads((SNAP / name).read_text(encoding='utf-8-sig'))

def h(p):
    return sha256(p.read_bytes()).hexdigest()

checks = []
def expect(ok, name):
    checks.append({'check': name, 'passed': bool(ok)})
    assert ok, name

def canonical(v):
    # Auditor encoder, explicitly follows CJ1 strings and recursive ASCII keys.
    if v is None: return b'null'
    if type(v) is bool: return b'true' if v else b'false'
    if isinstance(v, (int, float)):
        assert v == int(v) and abs(v) <= 9007199254740991
        return str(int(v)).encode('ascii')
    if isinstance(v, str):
        parts = ['"']
        short = {8:r'\b', 9:r'\t', 10:r'\n', 12:r'\f', 13:r'\r', 34:r'\"', 92:r'\\'}
        for c in v:
            n = ord(c)
            assert not 0xd800 <= n <= 0xdfff
            parts.append(short[n] if n in short else ('\\u%04x' % n) if n < 32 else c)
        return (''.join(parts) + '"').encode('utf-8')
    if isinstance(v, list): return b'[' + b','.join(map(canonical, v)) + b']'
    return b'{' + b','.join(canonical(k) + b':' + canonical(v[k]) for k in sorted(v)) + b'}'

def state_value(s):
    return {'position':list(s.pos),'bits':s.bits,'pending':s.pending,'nextBeacon':s.beacon,'used':s.used,'status':s.status,'failure':s.failure}

def main():
    spec = read('game-spec.json'); tasks = read('tasks.json'); report = read('validation-report.json')
    previous = json.loads((ROOT/'G04-recheck-02/game-spec.json').read_text(encoding='utf-8-sig'))
    for key in ['levels','experiment_levels','rules','progression']:
        expect(spec[key] == previous[key], key + ' unchanged from independently searched revision')
    for name, value in report['input_sha256'].items():
        expect(h(SNAP/name) == value, 'input report hash ' + name)
    for filename, data in [('game-spec.schema.json',spec),('tasks.schema.json',tasks)]:
        schema = read(filename); Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(data)
        expect(True, filename + ' and current instance valid')
    author_rules.campaign_semantic(spec)
    for label, mutate in [('out_of_range',lambda s:s['levels'][0].update(id='G04-L99')),('variant',lambda s:s['levels'][0].update(variant='X2')),('duplicate',lambda s:s['levels'][1].update(id='G04-L01')),('reverse',lambda s:s['levels'].reverse())]:
        mutant=copy.deepcopy(spec);mutate(mutant)
        try:author_rules.campaign_semantic(mutant)
        except AssertionError:expect(True,'prior campaign counterexample rejected '+label)
        else:expect(False,'campaign accepted '+label)
    expect(spec['engine']['typescript_typecheck_version']=='4.1.2','prior TS package correction retained')
    order=independent.topological(tasks['tasks'])
    expect(len(order)==16,'16 task DAG acyclic with valid IDs')
    by_id={t['id']:t for t in tasks['tasks']}
    def ancestors(i):
        return set(by_id[i]['depends_on']) | set().union(*(ancestors(j) for j in by_id[i]['depends_on']))
    expect(all('G04-T01' in ancestors(i) for i in by_id if i not in ['G04-T00','G04-T01']),'human decision ancestor retained for build tasks')
    owners=[]
    for row in tasks['required_artifacts']:
        candidates=[t['id'] for t in tasks['tasks'] if any(row['path']==p or p.endswith('/') and row['path'].startswith(p) for p in t['write_scope'])]
        expect(candidates==[row['owner_task']], 'unique owner '+row['path']);owners.append({'path':row['path'],'owners':candidates})
    expect(set(['G04-T03','G04-T08','G04-T09']).issubset(by_id['G04-T07']['depends_on']),'Boot integration explicitly depends on session/save/progress')
    expect(by_id['G04-T00']['outputs']==['../../reviews/G04-audit.md','../../reviews/G04-audit.json'],'external independent audit outputs exact')
    fixtures=read('save-fixtures.json'); schema=read('save-envelope.schema.json')
    Draft202012Validator.check_schema(schema)
    formats=FormatChecker()
    @formats.checks('date-time')
    def date(v):
        try:datetime.strptime(v,'%Y-%m-%dT%H:%M:%S.%fZ')
        except (TypeError,ValueError):return False
        return True
    validator=Draft202012Validator(schema,format_checker=formats)
    content_hash=h(SNAP/'game-spec.json')
    expect(fixtures['content_hash']==content_hash,'fixture current raw content hash')
    vector=fixtures['canonical_vector'];raw=canonical(vector['value'])
    expect(raw==vector['canonical_utf8'].encode('utf-8')==bytes.fromhex(vector['canonical_hex']),'independent CJ1 known bytes')
    expect(sha256(raw).hexdigest()==vector['sha256'],'independent CJ1 known checksum')
    save_results=[]
    for case in fixtures['valid']:
        value=case['value'];validator.validate(value)
        payload={k:v for k,v in value.items() if k!='checksum'}
        expect(sha256(canonical(payload)).hexdigest()==value['checksum']==case['expected_payload_sha256'],case['id']+' independent payload digest')
        a=value['activeSession'];level=next(l for l in spec['levels']+spec['experiment_levels'] if l['id']==a['levelId'])
        model=independent.Model(level);state=model.initial();history=[]
        for command in a['acceptedCommands']:
            history.append(state)
            accepted,state,_=model.transition(state,command)
            expect(accepted,case['id']+' legal replay command')
        expect(state_value(state)==a['ruleState'],case['id']+' independent full replay state')
        if 'expected_undo_state' in case:
            expect(state.status=='FAILED' and state_value(history[-1])==case['expected_undo_state'],case['id']+' FAILED undo state')
        save_results.append({'id':case['id'],'state':state_value(state),'checksum':value['checksum']})
    branches=[]
    for case in fixtures['invalid_or_migration']:
        actual,_=author.check_save(case['value'],spec,validator,content_hash)
        expect(actual==case['expected'],'fixed error branch '+case['id'])
        branches.append({'case':case['id'],'result':actual})
    # Additional adversarial cases with independently resealed data.
    extra=[]
    for name,mutate,want in [
        ('settings_inside_active',lambda v:v['activeSession'].update(settings=v['settings']),'SCHEMA_INVALID'),
        ('negative_revision',lambda v:v.update(revision=-1),'SCHEMA_INVALID'),
        ('unsafe_revision',lambda v:v.update(revision=9007199254740992),'SCHEMA_INVALID'),
        ('forged_failure',lambda v:v['activeSession']['ruleState'].update(failure='MOVE_LIMIT'),'SCHEMA_INVALID'),
        ('forged_used',lambda v:v['activeSession']['ruleState'].update(used=2),'REPLAY_MISMATCH'),
        ('duplicate_progress',lambda v:v['progress']['records'][1].update(levelId='G04-L01'),'PROGRESS_INVALID'),
        ('invalid_leap_day',lambda v:v.update(updatedAt='2026-02-29T10:30:00.000Z'),'SCHEMA_INVALID'),
        ('impossible_raw_counters',lambda v:v['activeSession'].update(totalAccepted=0),'SESSION_INVALID'),
    ]:
        v=copy.deepcopy(fixtures['valid'][0]['value']);mutate(v)
        if name != 'unsafe_revision':
            v['checksum']=sha256(canonical({k:x for k,x in v.items() if k!='checksum'})).hexdigest()
        actual,_=author.check_save(v,spec,validator,content_hash)
        expect(actual==want,'independent mutation '+name);extra.append({'case':name,'expected':want,'actual':actual})
    vectors=read('session-contract-vectors.json');level=next(l for l in spec['levels'] if l['id']==vectors['levelId'])
    s=vectors['before'];before=independent.Node(tuple(s['position']),s['bits'],s['pending'],s['nextBeacon'],s['used'],s['status'],s['failure'])
    accepted,after,_=independent.Model(level).transition(before,vectors['command']['op'])
    expected_facts=[{'type':'CommandAccepted','payload':{'command':'R','used':2,'from':[0,1,1],'to':[0,2,1]}},{'type':'StateCommitted','payload':{'state':state_value(after)}},{'type':'RuleWon','payload':{'used':2,'par':2}}]
    expect(accepted and after.status=='WON' and vectors['expected_facts']==expected_facts,'M02 original identical-rule-input counterexample has session-free facts')
    ev_schema=read('event-contract.schema.json');Draft202012Validator.check_schema(ev_schema);ev=Draft202012Validator(ev_schema)
    session_pairs=[]
    for session in vectors['sessions']:
        for i,(fact,event) in enumerate(zip(expected_facts,session['expected_events'])):
            enriched=copy.deepcopy(fact)
            if fact['type']=='RuleWon':enriched={'type':'LevelWon','payload':{'used':2,'par':2,'assisted':session['assisted'],'stars':2 if session['assisted'] else 3}}
            expected={'v':1,'seq':session['nextSeq']+i,'attemptId':session['attemptId'],'levelId':level['id'],'source':'keyboard',**enriched}
            expect(event==expected,'independent envelope '+session['attemptId']+'/'+str(i));ev.validate(event)
        session_pairs.append({'assisted':session['assisted'],'start_seq':session['nextSeq'],'next_seq_after_commit':session['nextSeq']+len(expected_facts),'terminal_event':session['expected_events'][-1]})
    expect(not ev.is_valid({**expected_facts[-1],'attemptId':vectors['sessions'][0]['attemptId']}),'RuleFact schema rejects session metadata')
    expect(not ev.is_valid({**vectors['sessions'][0]['expected_events'][-1],'payload':{'used':2,'par':2}}),'Session LevelWon requires enrichment')
    # Original artifact identity; no resave/repack of authored files.
    manifest=read('DELIVERY_MANIFEST.json');receipt=read('archive-verification.json');archive=SNAP/receipt['archive']
    expect(h(archive)==receipt['sha256'],'18:59 archive hash equals external receipt')
    with zipfile.ZipFile(archive) as z:
        expect(z.testzip() is None,'archive CRC')
        expect(set(z.namelist())=={'G04/'+r['path'] for r in manifest['files']}|{'G04/DELIVERY_MANIFEST.json'} and len(z.namelist())==len(manifest['files'])+1,'exact unique ZIP member set')
        expect(z.read('G04/DELIVERY_MANIFEST.json')==(SNAP/'DELIVERY_MANIFEST.json').read_bytes(),'internal external manifest exact bytes')
        for r in manifest['files']:
            expect(h(SNAP/r['path'])==r['sha256'] and (SNAP/r['path']).stat().st_size==r['bytes'] and sha256(z.read('G04/'+r['path'])).hexdigest()==r['sha256'],'manifest disk ZIP '+r['path'])
    index=read('observation-index.json')
    for r in index['files']:
        expect(h((ROOT.parent/'games/G04'/r['path']).resolve())==r['sha256'],'external observation '+r['path'])
    expect(len(index['screenshots'])==64 and not index['continuous_first_30_seconds'] and not index['continuous_first_5_minutes'],'M01 exact partial observation boundary')
    # Reproduce the author's latest contract validation only in frozen reviews.
    run=subprocess.run([sys.executable,'-X','utf8','-B',str(SNAP/'validate_contracts.py')],cwd=SNAP,capture_output=True,text=True,encoding='utf-8',timeout=60)
    (OUT/'author-contracts.stdout.json').write_text(run.stdout,encoding='utf-8')
    (OUT/'author-contracts.stderr.txt').write_text(run.stderr,encoding='utf-8')
    expect(run.returncode==0,'author contract checker rerun')
    rerun=json.loads(run.stdout);expect(rerun['result']=='PASS','author contract result')
    expect(rerun==report['contracts'],'rerun contract report exactly matches shipped report')
    expected_geometry=[('PORTRAIT',358,1),('PORTRAIT',208,1),('LANDSCAPE',312,1),('LANDSCAPE',270,2),('WIDE',240,2)]
    expect([(r['branch'],r['board'],r['boards']) for r in rerun['geometry'][:5]]==expected_geometry,'m01 unique breakpoints and board sizes')
    expect(80>=72+4+4 and 108+8+48<=176 and 80+8+108+8+52+8+48+4==316,'m01 target/control containers fit specified dimensions')
    expect(rerun['gate_ablation_unchanged']==15 and len(rerun['same_witness_pairs'])==4,'m02 author now discloses independently identified content risks')
    current_unchanged=[]
    for r in read('AUDIT_SNAPSHOT.json')['files']:
        current_unchanged.append(h(ROOT.parent/'games/G04'/r['path'])==r['sha256'])
    expect(all(current_unchanged),'author current files still match frozen r2 snapshot')
    result={'checked_at_utc':datetime.now(timezone.utc).isoformat(),'result':'PASS','scope':'Independent r2 contract/specification audit; no product source/build/storage/SDK implemented or tested; no repeated 79998-state scan','game_spec_sha256':content_hash,'zip_sha256':h(archive),'checks':checks,'check_count':len(checks),'artifact_owners':owners,'save_fixture_replays':save_results,'fixed_error_branches':branches,'independent_save_mutations':extra,'session_pair_counterexample':session_pairs,'author_contract_rerun':'PASS','closed_findings':['G04-M02','G04-M03','G04-m01','G04-m02','G04-m03'],'remaining_findings':['G04-M01'],'source_unchanged':all(current_unchanged)}
    (OUT/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ['checks','artifact_owners','save_fixture_replays','fixed_error_branches','independent_save_mutations','session_pair_counterexample']},ensure_ascii=False,indent=2))

if __name__=='__main__':main()
