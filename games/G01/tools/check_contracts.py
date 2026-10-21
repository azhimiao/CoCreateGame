"""Offline specification-table checks; no Session, UI, storage or game runtime.

Consumes fixed facts/expected events and validates their consistency against the
written contract. Does not implement commitExit or Web Storage.
"""
import copy
import hashlib
import json
from jsonschema import Draft202012Validator
from contracts import CAMPAIGN_IDS, LEGAL_ORDER, COMMIT_ORDER, SESSION_CONTRACT, RULE_FACT_FIELDS, FORBIDDEN_RULE_FIELDS, MAX_REVISION

def spec_semantics(spec):
    ids=[l['id'] for l in spec['levels']]; order=spec['progression']['order']
    if len(ids)!=20 or len(set(ids))!=20 or set(ids)!=set(CAMPAIGN_IDS):
        raise ValueError('CAMPAIGN_SET: levels must contain each L01..L20 exactly once')
    if ids!=list(CAMPAIGN_IDS) or order!=list(CAMPAIGN_IDS):
        raise ValueError('CAMPAIGN_SEQUENCE: levels and progression.order must both be exact L01..L20')
    if spec['rules']['legal_order']!=list(LEGAL_ORDER):
        raise ValueError('LEGAL_ORDER: fixed rule contract priority differs')
    if spec['rules']['commit_order']!=list(COMMIT_ORDER):
        raise ValueError('COMMIT_ORDER: fixed pre-state/commit/save/animation contract differs')
    if spec['session_contract']!=SESSION_CONTRACT:
        raise ValueError('SESSION_CONTRACT: publisher/fact/history boundary differs')
    return dict(exact_unique_campaign=True,canonical_legal_order=True,canonical_commit_order=True,session_contract_bound=True)

def layout_checks(root,spec):
    baseline=json.loads((root/'validation/revision-baseline.json').read_text(encoding='utf-8'))
    def digest(x): return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf-8')).hexdigest()
    actual={l['id']:digest({k:l[k] for k in baseline['layout_fields']}) for l in spec['levels']}
    if actual!=baseline['level_layout_sha256']: raise ValueError('FROZEN_LAYOUT_OR_SOLUTION_CHANGED')
    return dict(layouts_and_solutions_unchanged=True,level_layout_sha256=actual)

def parse_unique_json(raw):
    def pairs(items):
        out={}
        for k,v in items:
            if k in out: raise ValueError('DUPLICATE_JSON_KEY')
            out[k]=v
        return out
    return json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda _: (_ for _ in ()).throw(ValueError('NONFINITE_JSON')))

def validate_save_table(raw,spec,schema,reason,gate_state):
    """Classify a fixed JSON sample; never read/write storage or migrate files."""
    if len(raw.encode('utf-8'))>65536: return 'REJECT_OVERSIZE',None
    try: envelope=parse_unique_json(raw)
    except (ValueError,json.JSONDecodeError): return 'REJECT_JSON',None
    if not isinstance(envelope,dict): return 'REJECT_SCHEMA',None
    version=envelope.get('version')
    if type(version) is int and version>1: return 'READ_ONLY_NEWER_VERSION',None
    if version==1 and envelope.get('content_version')!='1.0.0': return 'RECOVERY_CONTENT_VERSION',None
    if not Draft202012Validator(schema).is_valid(envelope): return 'REJECT_SCHEMA',None
    # Reject booleans as integers even in implementations whose host type aliases them.
    if type(envelope['revision']) is not int: return 'REJECT_SCHEMA',None
    completed=envelope['completed']; expected=list(CAMPAIGN_IDS[:len(completed)])
    if completed!=expected: return 'REJECT_COMPLETED_PREFIX',None
    active=envelope['active_level']; index=CAMPAIGN_IDS.index(active)
    if index>len(completed): return 'REJECT_LOCKED_ACTIVE',None
    level=spec['levels'][index]; byid={a['id']:i for i,a in enumerate(level['arrows'])}; mask=0
    for aid in envelope['accepted_exits']:
        if aid not in byid or reason(level,mask,byid[aid]) is not None: return 'REJECT_REPLAY',None
        mask|=1<<byid[aid]
    normalized=copy.deepcopy(envelope)
    if mask==(1<<len(level['arrows']))-1 and active not in completed:
        if envelope['revision']==MAX_REVISION: return 'RECOVERY_REVISION_EXHAUSTED',None
        normalized['completed'].append(active); normalized['revision']+=1
        return 'ACCEPT_REPAIR_COMPLETION',normalized
    return 'ACCEPT',normalized

def save_checks(root,spec,reason,gate_state):
    data=json.loads((root/'contracts/save-vectors.json').read_text(encoding='utf-8'))
    schema=json.loads((root/'save-envelope.schema.json').read_text(encoding='utf-8'))
    Draft202012Validator.check_schema(schema); rows=[]
    for v in data['cases']:
        raw=v.get('raw_json')
        if raw is None: raw=json.dumps(v['envelope'],ensure_ascii=False,separators=(',',':'))
        status,normalized=validate_save_table(raw,spec,schema,reason,gate_state)
        if status!=v['expected_status']: raise ValueError(('SAVE_VECTOR',v['id'],status,v['expected_status']))
        if 'expected_normalized' in v and normalized!=v['expected_normalized']: raise ValueError(('SAVE_NORMALIZATION',v['id']))
        if status=='ACCEPT_REPAIR_COMPLETION':
            again,second=validate_save_table(json.dumps(normalized),spec,schema,reason,gate_state)
            if again!='ACCEPT' or second!=normalized: raise ValueError(('SAVE_REPAIR_NOT_IDEMPOTENT',v['id']))
        rows.append(dict(id=v['id'],status=status,matched=True))
    return dict(scope='offline fixed save-envelope samples; no storage fault injection',cases=rows)

def session_checks(root,spec,reason,gate_state):
    data=json.loads((root/'contracts/session-vectors.json').read_text(encoding='utf-8'))
    rows=[]; previous_facts={}; used_events=set()
    for case in data['cases']:
        context=copy.deepcopy(case['initial_context']); save_revisions=set(); successful_acks=set(); rows_steps=[]
        for step in case['steps']:
            before=copy.deepcopy(context)
            generated=[]; save_snapshot=None
            if step['kind'] in ['EXIT_FACT','UNDO_FACT']:
                fact=step['rule_fact']; level=spec['levels'][CAMPAIGN_IDS.index(fact['level_id'])]
                # Facts must be derivable from the supplied Attempt, with no session/progress inputs.
                if step['kind']=='EXIT_FACT':
                    if set(fact)!=set(RULE_FACT_FIELDS) or set(fact)&set(FORBIDDEN_RULE_FIELDS): raise ValueError('RULE_FACT_BOUNDARY')
                    byid={a['id']:i for i,a in enumerate(level['arrows'])}; mask=0
                    for aid in step['attempt_before']['accepted_exits']:
                        if reason(level,mask,byid[aid]) is not None: raise ValueError('VECTOR_REPLAY')
                        mask|=1<<byid[aid]
                    i=byid[fact['arrow_id']]
                    if reason(level,mask,i) is not None: raise ValueError('VECTOR_ILLEGAL_EXIT')
                    target=mask|1<<i; old=gate_state(level,mask); new=gate_state(level,target)
                    changes=[dict(id=k,was_open=old[k],is_open=new[k]) for k in sorted(old) if old[k]!=new[k]]
                    won=target==(1<<len(level['arrows']))-1
                    expected=dict(kind='ExitAccepted',level_id=level['id'],arrow_id=fact['arrow_id'],from_mask=mask,to_mask=target,gate_changes=changes,manifest_cursor=target.bit_count() if level['manifest'] else 0,won=won,deadlocked=not won and not any(reason(level,target,j) is None for j in range(len(level['arrows']))))
                    if fact!=expected: raise ValueError(('RULE_FACT',case['id']))
                    key=json.dumps(step['attempt_before'],sort_keys=True)+fact['arrow_id']
                    if key in previous_facts and previous_facts[key]!=fact: raise ValueError('RULE_FACT_DEPENDS_ON_HISTORY')
                    previous_facts[key]=fact
                    generated.append(('ExitCommitted',dict(arrowId=fact['arrow_id'],fromMask=mask,toMask=target,gatesChanged=changes,cursor=fact['manifest_cursor'])))
                    context['accepted_exits'].append(fact['arrow_id'])
                    if won:
                        first=level['id'] not in before['completed']
                        if first: context['completed'].append(level['id'])
                        generated.append(('LevelCompleted',dict(levelId=level['id'],firstClear=first,stampCount=len(context['completed']))))
                else:
                    if not context['accepted_exits']: raise ValueError('EMPTY_UNDO_VECTOR')
                    context['accepted_exits'].pop()
                    if fact!=dict(kind='UndoAccepted',level_id='L01',from_mask=3,to_mask=1,won=False,deadlocked=False): raise ValueError('UNDO_FACT')
                    generated.append(('UndoCommitted',dict(fromMask=3,toMask=1)))
                if step['attempt_before']['accepted_exits']!=before['accepted_exits'] or step['attempt_before']['revision']!=before['revision']: raise ValueError('ATTEMPT_CONTEXT_MISMATCH')
                context['revision']+=1
                save_snapshot=dict(version=1,content_version='1.0.0',revision=context['revision'],completed=list(context['completed']),active_level=context['level_id'],accepted_exits=list(context['accepted_exits']),tutorial_seen=['base'],settings=dict(language='en',sound=True,music=False,reducedMotion=False))
                if context['revision'] in save_revisions: raise ValueError('DUPLICATE_SAVE_REVISION')
                save_revisions.add(context['revision']); generated.append(('SaveRequested',dict(snapshotRevision=context['revision'])))
            elif step['kind']=='ANIMATION_INTERRUPTED':
                # UI lifecycle is tested separately. It must not replay gameplay/completion/save.
                if step['expected_gameplay_or_save_events']!=[] or step['expected_new_save_requests']!=0: raise ValueError('INTERRUPT_RECOMMITS')
            elif step['kind']=='STALE_COMMAND':
                if step['expected_revision']==context['revision']: raise ValueError('NOT_STALE_VECTOR')
                generated.append(('ExitRejected',dict(arrowId=step['arrow_id'],reason='STALE_REVISION')))
            elif step['kind']=='SAVE_ACK':
                revision=step['ack_revision']
                if revision not in save_revisions: raise ValueError('ACK_WITHOUT_REQUEST')
                if revision not in successful_acks:
                    successful_acks.add(revision); generated.append(('SaveSucceeded',dict(snapshotRevision=revision)))
            else: raise ValueError('UNKNOWN_SESSION_VECTOR_STEP')
            expected_events=[]
            for name,payload in generated:
                event_id=f"{context['session_id']}:{context['next_seq']}"; context['next_seq']+=1
                if event_id in used_events: raise ValueError('DUPLICATE_EVENT_ID')
                used_events.add(event_id)
                expected_events.append(dict(name=name,eventId=event_id,revision=context['revision'],payload=payload))
            if expected_events!=step['expected_events'] or context!=step['expected_context']: raise ValueError(('SESSION_EXPECTED_TABLE',case['id'],step['kind']))
            if save_snapshot!=step.get('expected_save_snapshot'): raise ValueError(('SAVE_SNAPSHOT_TABLE',case['id']))
            rows_steps.append(dict(kind=step['kind'],event_count=len(expected_events),save_requests=sum(n=='SaveRequested' for n,_ in generated),matched=True))
        rows.append(dict(id=case['id'],steps=rows_steps,unique_save_revisions=sorted(save_revisions),matched=True))
    by_id={case['id']:case for case in data['cases']}
    for left,right in data['history_equivalence_pairs']:
        a,b=by_id[left],by_id[right]; x,y=a['steps'][0],b['steps'][0]
        if x['kind']!='EXIT_FACT' or y['kind']!='EXIT_FACT' or x['attempt_before']!=y['attempt_before'] or x['rule_fact']!=y['rule_fact']:
            raise ValueError('HISTORY_PAIR_NOT_SAME_RULE_INPUT_AND_FACT')
        if a['initial_context']['completed']==b['initial_context']['completed']:
            raise ValueError('HISTORY_PAIR_NOT_DIFFERENT_HISTORY')
        p=[e['payload'] for e in x['expected_events'] if e['name']=='LevelCompleted']
        q=[e['payload'] for e in y['expected_events'] if e['name']=='LevelCompleted']
        if p==q: raise ValueError('HISTORY_PAIR_NOT_ENRICHED')
    return dict(scope='offline rule-fact/session expectation tables only; no Session implementation',cases=rows,same_attempt_history_pairs_checked=len(data['history_equivalence_pairs']))

def task_contract_checks(tasks):
    byid={t['id']:t for t in tasks['tasks']}
    required={'T04':(['T03'],['future/rules/','future/tests/rules/']),
              'T06':(['T04','T05'],['future/session/','future/app-state/','future/events/','future/tests/session/']),
              'T07':(['T06'],['future/save/','future/tests/save/']),
              'T08':(['T04','T06','T07'],['future/content/','future/tutorial/','future/progress/','future/integration/','future/tests/campaign/'])}
    for tid,(deps,scopes) in required.items():
        task=byid[tid]
        if not set(deps)<=set(task['depends_on']) or not set(scopes)<=set(task['files']):
            raise ValueError(('TASK_OWNERSHIP_OR_HANDOFF_MISSING',tid))
    return dict(owners=['T04 rules/facts','T06 Session/state machine/bus/SavePort','T07 save transport','T08 progress/integration'],dependency_and_write_scopes_bound=True)
