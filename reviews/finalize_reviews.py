"""Read-only source consistency and decisions aggregation. Writes only reviews/."""
from pathlib import Path
from hashlib import sha256
from datetime import datetime, timezone
import json
import shutil

BASE=Path(__file__).resolve().parent
ROOT=BASE.parent
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def digest(p):return sha256(p.read_bytes()).hexdigest()
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
checks=[]
def expect(ok,name):
    checks.append({'check':name,'passed':bool(ok)})
    assert ok,name

source_groups=[]
for game,snapshot in [('G01','G01-recheck-r1-final'),('G04','G04-recheck-r2')]:
    frozen=read(BASE/snapshot/'AUDIT_SNAPSHOT.json')
    files=[]
    for row in frozen['files']:
        p=ROOT/'games'/game/row['path']
        expect(p.is_file() and digest(p)==row['sha256'],game+' unchanged '+row['path'])
        files.append({'path':row['path'],'sha256':row['sha256']})
    source_groups.append({'game_id':game,'frozen_files':len(files),'unchanged':True,'files':files})

g02=read(BASE/'G02-rereview-results.json')
expect(g02['result']=='PASS','G02 independent rereview PASS')
for rel,value in g02['source_sha256'].items():
    expect(digest(ROOT/'games/G02'/rel)==value,'G02 unchanged '+rel)
source_groups.append({'game_id':'G02','frozen_files':len(g02['source_sha256']),'unchanged':True,'source_sha256':g02['source_sha256'],'scope':'Jason full independent review; aggregator checks scope, conclusion and current hashes only'})
expected_g02={'G02-audit.md':'e97c6ab62d3fb63f7042cc4acdb5ec1250cf37242c9080a1e86478653ac484bd','G02-audit.json':'e9d394069ea5380a37193e0e2ab171d4a3657e6a241c477df49540063a0ea397'}
for name,value in expected_g02.items():expect(digest(BASE/name)==value,'G02 final reviewer report '+name)
expect(g02['total_reachable']==26483 and len(g02['independent_levels'])==20,'G02 independent level scope')
expect(g02['author_vectors']==31 and len(g02['independent_layout'])==5 and g02['zip_members']==37,'G02 vectors/layout/archive scope')

# Final benchmark change is one metadata line. Do not repeat closed semantic checks.
benchmark=ROOT/'research/benchmarks'
old=BASE/'shared-recheck-03/research/benchmarks/validate_delivery.py'
current=benchmark/'validate_delivery.py'
old_text=old.read_text(encoding='utf-8-sig')
new_text=current.read_text(encoding='utf-8-sig')
line="        'validation_check_count': report['check_count'],\n"
expect(new_text.count(line)==1 and new_text.replace(line,'',1)==old_text,'benchmark validator diff is count metadata line only')
manifest=read(benchmark/'delivery_manifest.json');validation=read(benchmark/'validation.json')
expect(manifest['validation_check_count']==validation['check_count']==622,'benchmark manifest validation count 622')
expect(validation['result']=='PASS' and not validation['missing_references'],'benchmark final report PASS metadata')
for row in manifest['files']:
    p=benchmark/row['path']
    expect(p.stat().st_size==row['bytes'] and digest(p)==row['sha256'],'benchmark final payload metadata '+row['path'])
associated=manifest['associated_read_only']
expect(len(associated)==1 and associated[0]['relative_to']=='research/' and associated[0]['path']=='observation-summary.md' and associated[0]['included_in_this_subpackage'] is False,'benchmark exact readonly associated metadata')
row=associated[0];p=ROOT/'research'/row['path']
expect(p.stat().st_size==row['bytes'] and digest(p)==row['sha256'],'benchmark associated hash')
meta={'checked_at_utc':datetime.now(timezone.utc).isoformat(),'scope':'Final metadata-only update; no repeat of closed SRA-m03 semantic/path checks','result':'PASS','validation_check_count':622,'manifest_payload_count':len(manifest['files']),'associated_read_only_count':len(associated),'validator_change':'Only adds manifest.validation_check_count = report.check_count; readonly path policy unchanged','sha256':{name:digest(benchmark/name) for name in ['validate_delivery.py','validation.json','delivery_manifest.json']},'original_closed_result':'reviews/shared-recheck-03/results.json'}
folder=BASE/'shared-final-metadata'
folder.mkdir(exist_ok=True)
for name in meta['sha256']:shutil.copy2(benchmark/name,folder/name)
write(folder/'results.json',meta)

fields=['game_id','verdict','summary','unresolved_blockers','unresolved_majors']
decisions=[];reports=[]
for game in ['G01','G02','G04']:
    audit=read(BASE/(game+'-audit.json'))
    expect(audit['game_id']==game and audit['verdict']=='REVISE','current verdict '+game)
    expect(not audit['unresolved_blockers'] and len(audit['unresolved_majors'])==1,'only research major '+game)
    expect(all(v['severity']=='MAJOR' and v.get('evidence') and v.get('fix') and v.get('validation') for v in audit['unresolved_majors']),'actionable major evidence '+game)
    decisions.append({k:audit[k] for k in fields})
    reports.append({'game_id':game,'markdown_sha256':digest(BASE/(game+'-audit.md')),'json_sha256':digest(BASE/(game+'-audit.json')),'unresolved_major_ids':[v['id'] for v in audit['unresolved_majors']]})
expect([v['game_id'] for v in decisions]==['G01','G02','G04'],'exact requested decisions membership/order')
write(BASE/'decisions.json',decisions)
expect(read(BASE/'decisions.json')==decisions,'decisions persisted exactly')
result={'checked_at_utc':datetime.now(timezone.utc).isoformat(),'result':'PASS','scope':'Auditor consistency/aggregation only; source read only, no engine or full root delivery verification','check_count':len(checks),'checks':checks,'source_freezes':source_groups,'current_audit_reports':reports,'decisions_sha256':digest(BASE/'decisions.json'),'benchmark_final_metadata':meta,'historical_author_status':'PENDING_RE_REVIEW / RECHECK_PENDING describe frozen handoff; independent audit reports and decisions give current conclusions; no author repack required','counts':{'games':3,'unresolved_blockers':0,'unresolved_majors':3,'verdicts':{'REVISE':3}},'g02_scope_review':'Full independent Jason report covers 00-12, cold workflow/rules/interfaces/save reconstruction, 20 levels, DAG/ownership, originality and falsification, official SDK/license/stats/business segregation, and honest missing play evidence; no duplicate full audit by aggregator.'}
diagnostic=ROOT/'validation/G02-transient-failure.json'
if diagnostic.exists():
    detail=read(diagnostic)
    assert detail['frozen_verifier_sha256']==g02['source_sha256']['tools/verify.py']
    folder=BASE/'execution-diagnostics';folder.mkdir(exist_ok=True)
    shutil.copy2(diagnostic,folder/'G02-transient-failure.json')
    result['execution_diagnostic_boundary']={'source':'validation/G02-transient-failure.json','source_sha256':digest(diagnostic),'reported_error':detail['error_type']+': '+detail['message'],'reported_failed_at':detail['failed_at'],'reported_unchanged_retry_at':detail['unchanged_source_retry_at'],'reported_retry_result':detail['unchanged_source_retry_result'],'cause':'UNKNOWN','bounded_author_probe':'Pending at auditor freeze; no speculative root cause','gameplay_finding_reopened':False,'interpretation':'Independent audit reruns and latest root retry PASS do not explain or erase the earlier reported TypeError. This aggregator read the preserved diagnostic summary, not the original complete failed tool output.'}
write(BASE/'final-integration-checks.json',result)
print(json.dumps({'result':'PASS','consistency_checks':len(checks),'games':3,'unresolved_blockers':0,'unresolved_majors':3,'decisions_sha256':result['decisions_sha256'],'benchmark_final_metadata':meta},ensure_ascii=False,indent=2))
