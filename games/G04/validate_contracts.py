"""Offline JSON contract models only. No Cocos/TS, browser, SDK or storage I/O."""
from __future__ import annotations
import copy, hashlib, json, math, shutil, subprocess
from datetime import datetime
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker
import validate_spec as rules
ROOT = Path(__file__).resolve().parent
MAX = 9007199254740991

def load(name):
    return strict_json((ROOT/name).read_bytes())

def strict_json(raw):
    assert len(raw) <= 1048576, "offline fixture file too large"
    assert not raw.startswith(b'\xef\xbb\xbf'), "BOM"
    def pairs(items):
        result = {}
        for key, value in items:
            assert key not in result, "duplicate key"
            result[key] = value
        return result
    value = json.loads(raw.decode('utf-8'), object_pairs_hook=pairs,
                       parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))
    safe(value)
    return value

def safe(v):
    if v is None or isinstance(v, bool): return
    if isinstance(v, str):
        assert not any(0xd800 <= ord(c) <= 0xdfff for c in v), "surrogate"
    elif isinstance(v, (int, float)):
        assert (not isinstance(v,float) or math.isfinite(v)) and int(v)==v and abs(v)<=MAX, "unsafe number"
    elif isinstance(v, list):
        for item in v: safe(item)
    elif isinstance(v, dict):
        for key,item in v.items(): safe(key);safe(item)
    else: raise AssertionError(type(v))

def normalize(v):
    if isinstance(v, float): return int(v)
    if isinstance(v, list): return [normalize(x) for x in v]
    if isinstance(v, dict): return {k:normalize(x) for k,x in v.items()}
    return v

def cj1(v):
    safe(v)
    return json.dumps(normalize(v), ensure_ascii=False, sort_keys=True, separators=(',',':')).encode('utf-8')

def manual_cj1(v):
    """Second encoder: no json.dumps, including explicit string escapes."""
    def string(s):
        escapes={'"':'\\"','\\':'\\\\','\b':'\\b','\t':'\\t','\n':'\\n','\f':'\\f','\r':'\\r'}
        return '"'+''.join(escapes.get(c, ('\\u%04x'%ord(c)) if ord(c)<32 else c) for c in s)+'"'
    def walk(x):
        if x is None:return 'null'
        if x is True:return 'true'
        if x is False:return 'false'
        if isinstance(x,str):return string(x)
        if isinstance(x,(int,float)):return str(int(x))
        if isinstance(x,list):return '['+','.join(walk(i) for i in x)+']'
        return '{'+','.join(string(k)+':'+walk(x[k]) for k in sorted(x))+'}'
    safe(v)
    return walk(v).encode('utf-8')

def digest(v):return hashlib.sha256(cj1(v)).hexdigest()
def payload(v):return {k:x for k,x in v.items() if k!='checksum'}
def state_obj(t,reason='OK'):
    return {'position':list(t[:3]),'bits':t[3],'pending':t[4],'nextBeacon':t[5],
            'used':t[6],'status':t[7],'failure':reason if t[7]=='FAILED' else None}

def check_save(v,spec,validator,content_hash,profile='local-qa'):
    # Return a specified error branch, not a boolean that conceals the failure.
    if not isinstance(v,dict):return 'JSON_INVALID',[]
    if v.get('schemaVersion')!=1:return 'UNSUPPORTED_SCHEMA',[]
    if v.get('ruleVersion')!='1.0.0':return 'UNSUPPORTED_RULE',[]
    if not validator.is_valid(v):return 'SCHEMA_INVALID',[]
    if digest(payload(v))!=v['checksum']:return 'CHECKSUM_MISMATCH',[]
    if v['profile']!=profile:return 'PROFILE_MISMATCH',[]
    p=v['progress'];records=p['records']
    if [x['levelId'] for x in records]!=spec['progression']['campaign_order']:return 'PROGRESS_INVALID',[]
    prefix=0
    for x in records:
        if not x['completed']:break
        prefix+=1
    if p['highestUnlocked']!=min(20,prefix+1):return 'PROGRESS_INVALID',[]
    if v['contentHash']!=content_hash:return 'CONTENT_CHANGED',[]
    a=v['activeSession']
    if a is None:return 'OK',[]
    level=next((l for l in spec['levels']+spec['experiment_levels'] if l['id']==a['levelId']),None)
    if level is None or level['name']!=a['levelName'] or level['variant']!=a['variant']:return 'SESSION_INVALID',[]
    if level['variant']!='B0' and profile!='local-qa':return 'SESSION_INVALID',[]
    if level['variant']=='B0':
        index=spec['progression']['campaign_order'].index(level['id'])
        if index+1>p['highestUnlocked'] and not records[index]['completed']:return 'SESSION_INVALID',[]
    if a['totalAccepted']<len(a['acceptedCommands']) or a['undoCount']>a['totalAccepted']:return 'SESSION_INVALID',[]
    st=rules.initial(level);history=[];reason='OK'
    for op in a['acceptedCommands']:
        before=state_obj(st,reason);nxt,reason=rules.step(level,st,op)
        if nxt is None:return 'REPLAY_MISMATCH',[]
        history.append(before);st=nxt
    if state_obj(st,reason)!=a['ruleState'] or st[6]!=len(a['acceptedCommands']):return 'REPLAY_MISMATCH',[]
    return 'OK',history

def select_slots(a,b):
    """Inputs already validated OK; unknown/corrupt slots cannot enter this model."""
    if a['revision']==b['revision']:
        return 'A' if a['checksum']==b['checksum'] else 'SLOT_CONFLICT'
    return 'A' if a['revision']>b['revision'] else 'B'

def raw_facts(level,before,op):
    """Trace model of RuleCore contract; its inputs deliberately contain no Session."""
    t=(*before['position'],before['bits'],before['pending'],before['nextBeacon'],before['used'],before['status'])
    nxt,reason=rules.step(level,t,op)
    if nxt is None:return [{'type':'CommandRejected','payload':{'reason':reason}}]
    pos=nxt[:3];bits=before['bits']^before['pending'];pending=0
    facts=[{'type':'CommandAccepted','payload':{'command':op,'used':nxt[6],'from':before['position'],'to':list(pos)}}]
    if before['pending']:facts.append({'type':'PendingApplied','payload':{'mask':before['pending'],'bits':bits}})
    if rules.supported(level,pos,bits):
        mask=next((x['mask'] for x in level['switches'] if tuple(x['at'])==pos),0)
        if mask:
            if level['variant']=='X2':pending=mask
            else:bits^=mask
            facts.append({'type':'SwitchEntered','payload':{'mask':mask,'mode':'DELAYED' if level['variant']=='X2' else 'IMMEDIATE','bits':bits,'pending':pending}})
        if nxt[5]>before['nextBeacon']:facts.append({'type':'BeaconAdvanced','payload':{'index':before['nextBeacon']}})
    facts.append({'type':'StateCommitted','payload':{'state':state_obj(nxt,reason)}})
    if nxt[-1]=='WON':facts.append({'type':'RuleWon','payload':{'used':nxt[6],'par':level['par']}})
    if nxt[-1]=='FAILED':facts.append({'type':'RuleFailed','payload':{'reason':reason}})
    return facts

def enrich(facts,session,level_id,source):
    events=[]
    for i,f in enumerate(copy.deepcopy(facts)):
        if f['type']=='RuleWon':
            used,par=f['payload']['used'],f['payload']['par']
            stars=3 if used<=par and not session['assisted'] else 2 if used<=par+2 else 1
            f={'type':'LevelWon','payload':{'used':used,'par':par,'assisted':session['assisted'],'stars':stars}}
        elif f['type']=='RuleFailed':f['type']='LevelFailed'
        events.append({'v':1,'seq':session['nextSeq']+i,'attemptId':session['attemptId'],'levelId':level_id,'source':source,**f})
    return events

def ownership(tasks):
    def owners(path):return [t['id'] for t in tasks['tasks'] if any(path==s or (s.endswith('/') and path.startswith(s)) for s in t['write_scope'])]
    for entry in tasks['required_artifacts']:
        assert owners(entry['path'])==[entry['owner_task']], ('missing/duplicate artifact owner',entry)
    for t in tasks['tasks']:
        for path in t['outputs']:assert owners(path)==[t['id']],('output owner',path)
    return [{'path':e['path'],'owner_task':e['owner_task']} for e in tasks['required_artifacts']]

def geometry(w,h):
    w=min(w,1200)
    branch='LANDSCAPE' if w/h>=1.3 else 'WIDE' if w>=700 else 'PORTRAIT'
    if branch=='PORTRAIT':board=min(w-32,h-360,420);count=1;small=board<160
    else:
        side=224 if w<800 else 240;c=w-32-side-16;d=h-88
        small=min(c,d)<160 or h-32<316
        count=2 if min((c-16)/2,d)>=160 else 1
        board=min((c-16)/2,d) if count==2 else min(c,d,420)
    return {'width':w,'height':h,'branch':branch,'board':board,'boards':count,'window_too_small':small,'five_cell_tap_move':board/5>=48}

def validate(spec,tasks):
    report={'scope':'OFFLINE_CONTRACT_MODELS_ONLY','engine_build_executed':False,'browser_storage_executed':False}
    save_schema=load('save-envelope.schema.json');event_schema=load('event-contract.schema.json')
    for sch in (save_schema,event_schema):Draft202012Validator.check_schema(sch)
    formats=FormatChecker()
    @formats.checks('date-time')
    def actual_utc_date(value):
        if not isinstance(value,str):return True
        try:datetime.strptime(value,'%Y-%m-%dT%H:%M:%S.%fZ')
        except ValueError:return False
        return True
    sv=Draft202012Validator(save_schema,format_checker=formats)
    ev=Draft202012Validator(event_schema)
    fixtures=load('save-fixtures.json');h=hashlib.sha256((ROOT/'game-spec.json').read_bytes()).hexdigest()
    assert fixtures['content_hash']==h
    report['saves']=[]
    for case in fixtures['valid']+fixtures['invalid_or_migration']:
        value=case['value'];result,history=check_save(value,spec,sv,h)
        assert result==case['expected'],(case['id'],result,case['expected'])
        if result=='OK':
            assert cj1(payload(value))==manual_cj1(payload(value))
            assert digest(payload(value))==case['expected_payload_sha256']
            assert check_save(strict_json(cj1(value)),spec,sv,h)[0]=='OK'
            if 'expected_undo_state' in case:assert history[-1]==case['expected_undo_state']
        report['saves'].append({'id':case['id'],'result':result,'passed':True})
    vector=fixtures['canonical_vector'];raw=cj1(vector['value'])
    assert raw==manual_cj1(vector['value'])==vector['canonical_utf8'].encode('utf-8')==bytes.fromhex(vector['canonical_hex'])
    assert hashlib.sha256(raw).hexdigest()==vector['sha256']
    escape_value={'s':'中文\u2028\u2029/<>\"\\\x00\b\t\n\f\r','n':-0.0}
    assert cj1(escape_value)==manual_cj1(escape_value)
    report['strict_json_rejections']=[]
    for name,raw in [('duplicate',b'{"a":1,"a":2}'),('surrogate',b'"\\ud800"'),('unsafe_integer',b'9007199254740992'),('fraction',b'1.5'),('nan',b'NaN'),('bom',b'\xef\xbb\xbf{}'),('bad_utf8',b'"\xff"')]:
        try:strict_json(raw)
        except (AssertionError,ValueError,UnicodeError):report['strict_json_rejections'].append(name)
        else:raise AssertionError(('accepted invalid JSON',name))
    legal=fixtures['valid'][0]['value'];other=copy.deepcopy(legal);other['settings']['music']=True;other['checksum']=digest(payload(other))
    assert select_slots(legal,copy.deepcopy(legal))=='A'
    assert select_slots(legal,other)=='SLOT_CONFLICT'
    other['revision']+=1;other['checksum']=digest(payload(other));assert select_slots(legal,other)=='B'
    report['slot_selection']=['same_snapshot_A','equal_revision_conflict','highest_revision_B']
    vectors=load('session-contract-vectors.json');level=next(x for x in spec['levels'] if x['id']==vectors['levelId'])
    facts=raw_facts(level,vectors['before'],vectors['command']['op']);assert facts==vectors['expected_facts']
    for fact in facts:ev.validate(fact)
    report['session_pairs']=[]
    for session in vectors['sessions']:
        assert raw_facts(level,vectors['before'],vectors['command']['op'])==facts
        events=enrich(facts,session,level['id'],vectors['command']['source']);assert events==session['expected_events']
        for event in events:ev.validate(event)
        assert not ev.is_valid({**events[-1],'payload':{'used':2,'par':2}}), 'un-enriched LevelWon accepted'
        report['session_pairs'].append({'attemptId':session['attemptId'],'last_seq':events[-1]['seq'],'stars':events[-1]['payload']['stars'],'passed':True})
    committed=False;commits=publications=0
    for _ in range(vectors['terminal_repeat']['repeated_callbacks']):
        if not committed:committed=True;commits+=1;publications+=1
    assert commits==vectors['terminal_repeat']['expected_commit_win_calls']==1
    assert publications==vectors['terminal_repeat']['expected_level_won_publications']==1
    report['terminal_guard_model']={'commitWin':commits,'LevelWon':publications,'callbacks':3,'note':'Model assertion; future T03/T07 must exercise actual TS/SDK reentry.'}
    report['artifact_owners']=ownership(tasks)
    report['ownership_negative_cases']=[]
    for name in ('missing_boot_owner','duplicate_session_owner'):
        mutant=copy.deepcopy(tasks)
        if name=='missing_boot_owner':mutant['tasks'][7]['write_scope'].remove('implementation/assets/scenes/Boot.scene')
        else:mutant['tasks'][10]['write_scope'].append('implementation/assets/scripts/session/')
        try:ownership(mutant)
        except AssertionError:report['ownership_negative_cases'].append({'case':name,'result':'REJECTED_AS_EXPECTED'})
        else:raise AssertionError(name)
    report['geometry']=[geometry(w,h) for w,h in ((390,844),(320,568),(600,400),(844,390),(768,1024),(320,480))]
    assert [(x['branch'],x['board'],x['boards']) for x in report['geometry'][:5]]==[('PORTRAIT',358,1),('PORTRAIT',208,1),('LANDSCAPE',312,1),('LANDSCAPE',270,2),('WIDE',240,2)]
    assert report['geometry'][-1]['window_too_small']
    report['gate_ablation']=[]
    for level in spec['levels']:
        control=copy.deepcopy(level);control['gates']=[];route,_=rules.shortest(control)
        report['gate_ablation'].append({'id':level['id'],'original_shortest':level['par'],'without_gates_shortest':None if route is None else len(route),'without_gates_solution':route})
    report['gate_ablation_unchanged']=sum(x['original_shortest']==x['without_gates_shortest'] for x in report['gate_ablation'])
    report['same_witness_pairs']=[[a['id'],b['id']] for i,a in enumerate(spec['levels']) for b in spec['levels'][i+1:] if a['solution']==b['solution']]
    report['canonical_sha256']=vector['sha256']
    node=shutil.which('node')
    if node:
        script=r'''const fs=require('fs'),crypto=require('crypto');const f=JSON.parse(fs.readFileSync(process.argv[1],'utf8'));
        function c(x){if(x===null||typeof x!=='object')return JSON.stringify(x);if(Array.isArray(x))return '['+x.map(c).join(',')+']';return '{'+Object.keys(x).sort().map(k=>JSON.stringify(k)+':'+c(x[k])).join(',')+'}'}
        function hash(s){return crypto.createHash('sha256').update(Buffer.from(s,'utf8')).digest('hex')}
        const rows=f.valid.map(x=>{let v={...x.value};delete v.checksum;return [x.id,hash(c(v))]});
        console.log(JSON.stringify({node:process.version,vectorHex:Buffer.from(c(f.canonical_vector.value),'utf8').toString('hex'),vector:hash(c(f.canonical_vector.value)),saves:rows}));'''
        run=subprocess.run([node,'-e',script,str(ROOT/'save-fixtures.json')],capture_output=True,text=True,check=True,timeout=30)
        result=json.loads(run.stdout);assert result['vectorHex']==vector['canonical_hex'] and result['vector']==vector['sha256']
        assert result['saves']==[[x['id'],x['expected_payload_sha256']] for x in fixtures['valid']]
        report['node_cj1_parity']={'result':'PASS',**result,'scope':'Node JSON/crypto only; no Cocos/TypeScript/runtime storage'}
    else:report['node_cj1_parity']={'result':'UNKNOWN','reason':'node not found'}
    report['result']='PASS'
    return report

if __name__=='__main__':
    print(json.dumps(validate(load('game-spec.json'),load('tasks.json')),ensure_ascii=False,indent=2))
