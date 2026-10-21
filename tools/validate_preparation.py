"""Validate preparation artifacts, not a game build or player-experience claim."""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from zoneinfo import ZoneInfo
from jsonschema import validators

ROOT = Path(__file__).resolve().parents[1]
P0 = ('G01', 'G02', 'G04')
DOCS = ('00_Project_Charter.md', '01_Market_Evidence.md', '02_Benchmark_Playthrough.md',
        '03_Full_GDD.md', '04_Systems_and_Data.md', '05_Levels_Economy.md', '06_UI_Art_Audio.md',
        '07_Tech_Architecture.md', '08_OpenSource_Licenses.md', '09_Implementation_Plan.md',
        '10_QA_Test_Plan.md', '11_Distribution_Business.md', '12_Falsifiability.md')

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def task_dag(data):
    tasks = data['tasks'] if isinstance(data, dict) else data
    ids = [x.get('id', x.get('task_id')) for x in tasks]
    if None in ids or len(ids) != len(set(ids)):
        raise ValueError('missing or duplicate task ID')
    deps = {i: t.get('depends_on', t.get('dependencies', [])) for i, t in zip(ids, tasks)}
    if any(d not in deps for ds in deps.values() for d in ds):
        raise ValueError('task refers to unknown dependency')
    visited, active = set(), set()
    def visit(i):
        if i in active: raise ValueError('task dependency cycle')
        if i in visited: return
        active.add(i)
        for d in deps[i]: visit(d)
        active.remove(i)
        visited.add(i)
    for i in ids: visit(i)
    return len(ids)

def main():
    errors, checks, warnings = [], [], []
    projects = read(ROOT/'data/projects.json')
    platforms = read(ROOT/'data/platforms.json')
    if {x['id'] for x in projects} != {f'G{i:02d}' for i in range(1,11)}: errors.append('candidate scope changed')
    if {x['id'] for x in platforms} != {f'P{i:02d}' for i in range(1,7)}: errors.append('channel scope changed')
    checks.append('Frozen six channels and ten project IDs')
    try:
        sources = read(ROOT/'research/official-sources.json')
        claims = read(ROOT/'research/claims.json')
        source_map = {x['source_id']: x for x in sources}
        if len(source_map) != len(sources): raise ValueError('duplicate source ID')
        if len({x['claim_id'] for x in claims}) != len(claims): raise ValueError('duplicate claim ID')
        for c in claims:
            source = source_map[c['source_id']]
            if c['source_url'] != source['url'] or c['platform_id'] != source['platform_id']:
                raise ValueError(f'claim/source mismatch: {c["claim_id"]}')
            if not c.get('metric_definition') or not c.get('source_locator'):
                raise ValueError(f'claim has no metric/locator: {c["claim_id"]}')
        checks.append(f'{len(claims)} claims resolve to {len(sources)} official sources with locators')
        matrix = read(ROOT/'research/adaptation-matrix.json')
        if len(matrix)!=10 or any(set(x['channels'])!={f'P{i:02d}' for i in range(1,7)} for x in matrix):
            raise ValueError('adaptation matrix must cover 10 × 6')
        checks.append('Ten-family adaptation matrix covers all six channels')
    except Exception as exc: errors.append(f'research ledger: {exc}')
    # Catch invalid UTF-8, corrupt JSON and accidental replacement characters.
    json_count = 0
    for path in ROOT.rglob('*.json'):
        if any(x in path.parts for x in ('runtime', 'node_modules', '.git', 'dist')): continue
        try:
            content = path.read_text(encoding='utf-8-sig')
            json.loads(content)
            if '\ufffd' in content: raise ValueError('Unicode replacement character')
            json_count += 1
        except Exception as exc: errors.append(f'{path.relative_to(ROOT)}: {exc}')
    checks.append(f'{json_count} JSON documents parse as UTF-8')
    for gid in P0:
        directory = ROOT/'games'/gid
        for name in DOCS:
            path = directory/name
            if not path.is_file() or path.stat().st_size < 300: errors.append(f'{gid}/{name}: missing or insubstantial')
        for stem in ('game-spec', 'tasks'):
            path, schema_path = directory/f'{stem}.json', directory/f'{stem}.schema.json'
            if not path.is_file() or not schema_path.is_file():
                errors.append(f'{gid}/{stem}: JSON/schema missing')
                continue
            try:
                schema = read(schema_path)
                cls = validators.validator_for(schema)
                cls.check_schema(schema)
                cls(schema).validate(read(path))
                checks.append(f'{gid}/{stem}: schema PASS')
                if stem == 'tasks': checks.append(f'{gid}/tasks: DAG {task_dag(read(path))} tasks PASS')
            except Exception as exc: errors.append(f'{gid}/{stem}: {exc}')
        try:
            spec = read(directory/'game-spec.json')
            levels = spec.get('levels', [])
            if len(levels) < 20: errors.append(f'{gid}: only {len(levels)} levels')
            else: checks.append(f'{gid}: {len(levels)} concrete level records')
        except Exception as exc: errors.append(f'{gid}/levels: {exc}')
    verifiers = [('G01','tools/validate.py',[]), ('G02','tools/verify.py',['--all']), ('G04','validate_spec.py',[])]
    for gid, filename, args in verifiers:
        directory = ROOT/'games'/gid
        path = directory/filename
        if not path.is_file(): errors.append(f'{gid}: verifier {filename} missing'); continue
        try:
            env = dict(os.environ, PYTHONUTF8='1')
            # The author verifiers emit receipts. Run copies so a fresh check does not
            # invalidate the already-reviewed project archives and their manifests.
            staging_parent = (ROOT/'validation/runtime').resolve()
            staging_parent.mkdir(parents=True,exist_ok=True)
            with tempfile.TemporaryDirectory(prefix='foundry-verification-',dir=staging_parent) as staging:
                staging_root = Path(staging).resolve()
                if staging_root.parent != staging_parent:
                    raise ValueError('unexpected verification temporary root')
                snapshot = staging_root/gid
                shutil.copytree(directory,snapshot,ignore=shutil.ignore_patterns('*.zip','runtime','raw','__pycache__','diagnostics'))
                result = subprocess.run([sys.executable,'-X','faulthandler','-B',str(snapshot/filename),*args], cwd=snapshot, env=env,
                                        capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=120)
            target = ROOT/'validation'/f'{gid}-verifier.log'
            target.parent.mkdir(exist_ok=True)
            target.write_text(result.stdout+result.stderr, encoding='utf-8')
            if result.returncode: errors.append(f'{gid}: verifier exited {result.returncode}; see {target.relative_to(ROOT)}')
            else: checks.append(f'{gid}: offline specification verifier PASS in isolated copy (not gameplay QA)')
        except Exception as exc: errors.append(f'{gid}: verifier {exc}')
    for game in projects:
        if game['id'] in P0: continue
        directory = ROOT/'games'/game['id']
        for name in DOCS:
            if not (directory/name).is_file(): errors.append(f'{game["id"]}/{name}: research structure missing')
        if not (directory/'research-gaps.json').is_file(): errors.append(f'{game["id"]}/research-gaps.json missing')
    evidence = ROOT/'research/benchmarks/benchmarks.json'
    if evidence.is_file():
        data = read(evidence)
        cards = data if isinstance(data,list) else data.get('benchmarks',data.get('cards',[]))
        if len({c.get('benchmark_id') for c in cards}) != len(cards): errors.append('duplicate/missing benchmark IDs')
        for pid in (f'P{i:02d}' for i in range(1,7)):
            count = sum(x.get('platform_id') == pid for x in cards)
            deep = sum(x.get('platform_id') == pid and isinstance(x.get('deep_analysis'),dict) for x in cards)
            if not 3 <= count <= 5: errors.append(f'{pid}: {count} benchmark cards; require 3–5')
            else: checks.append(f'{pid}: {count} benchmark cards')
            if deep < 2: errors.append(f'{pid}: only {deep} detailed benchmark analyses')
            else: checks.append(f'{pid}: {deep} detailed analyses (method labels retained)')
        for c in cards:
            if not all(c.get(k) for k in ['source_url','accessed_at','evidence_type','metric_definition']):
                errors.append(f'{c.get("benchmark_id")}: missing evidence metadata')
            for rel in c.get('direct_play',{}).get('evidence_paths',[]):
                if not (evidence.parent/rel).is_file(): errors.append(f'{c.get("benchmark_id")}: evidence file missing: {rel}')
        if not cards: errors.append('benchmark registry has no cards')
        try:
            manifest = read(evidence.parent/'delivery_manifest.json')
            manifest_paths = [item['path'] for item in manifest['files']]
            if len(manifest_paths) != len(set(manifest_paths)): raise ValueError('duplicate manifest path')
            for item in manifest['files']:
                path = (evidence.parent/item['path']).resolve()
                if not path.is_relative_to(evidence.parent.resolve()) or {'runtime','raw'}.intersection(path.relative_to(evidence.parent.resolve()).parts):
                    raise ValueError('manifest path outside benchmark delivery')
                if path.stat().st_size != item['bytes'] or hashlib.sha256(path.read_bytes()).hexdigest() != item['sha256']:
                    raise ValueError(f'stale benchmark manifest: {item["path"]}')
            for item in manifest.get('associated_read_only', []):
                if item.get('relative_to') != 'research/': raise ValueError('invalid association base')
                path = (ROOT/'research'/item['path']).resolve()
                if path != (ROOT/'research/observation-summary.md').resolve():
                    raise ValueError('unapproved benchmark association')
                if path.stat().st_size != item['bytes'] or hashlib.sha256(path.read_bytes()).hexdigest() != item['sha256']:
                    raise ValueError('stale associated observation summary hash')
            validation_receipt = read(evidence.parent/'validation.json')
            if validation_receipt.get('result') != 'PASS': raise ValueError('benchmark validation receipt not PASS')
            if validation_receipt.get('check_count') != manifest.get('validation_check_count'):
                raise ValueError('benchmark manifest and validation receipt disagree')
            checks.append(f"Current benchmark delivery manifest and associated observation hash match ({validation_receipt['check_count']} checks)")
        except Exception as exc: errors.append(f'benchmark manifest: {exc}')
    else: errors.append('benchmark registry missing')
    # Check the recorded research evidence itself, separately from game-spec witnesses.
    screenshot_hashes = 0
    evidence_logs = 0
    for log in (ROOT/'research/playthroughs').glob('*/operations.jsonl'):
        evidence_logs += 1
        try:
            for line in log.read_text(encoding='utf-8-sig').splitlines():
                if not line.strip(): continue
                event = json.loads(line)
                if event.get('event') == 'screenshot':
                    relative, expected_hash = event['file'], event['sha256']
                elif event.get('screenshot') and event.get('screenshot_sha256'):
                    relative, expected_hash = event['screenshot'], event['screenshot_sha256']
                else:
                    continue
                candidate = (log.parent/relative).resolve()
                if not candidate.is_relative_to(log.parent.resolve()):
                    raise ValueError('screenshot escapes evidence directory')
                if hashlib.sha256(candidate.read_bytes()).hexdigest() != expected_hash.lower():
                    raise ValueError(f'screenshot hash mismatch: {relative}')
                screenshot_hashes += 1
        except Exception as exc: errors.append(f'{log.relative_to(ROOT)}: {exc}')
    checks.append(f'{screenshot_hashes} logged screenshot hashes match across {evidence_logs} observation logs')
    for gid in P0:
        if not (ROOT/'reviews'/f'{gid}-audit.md').is_file(): errors.append(f'{gid}: independent audit missing')
    try:
        decisions = read(ROOT/'reviews/decisions.json')
        if isinstance(decisions,dict): decisions = decisions.get('decisions', [])
        if len(decisions) != 3 or {x['game_id'] for x in decisions} != set(P0):
            raise ValueError('decisions must contain exactly G01/G02/G04')
        for decision in decisions:
            gid = decision['game_id']
            audit = read(ROOT/'reviews'/f'{gid}-audit.json')
            if decision['verdict'] not in ('GO','REVISE','KILL') or audit['verdict'] != decision['verdict']:
                raise ValueError(f'{gid}: invalid or inconsistent audit verdict')
            if any(len(decision.get(k, [])) != len(audit.get(k, [])) for k in ('unresolved_blockers','unresolved_majors')):
                raise ValueError(f'{gid}: decision finding counts differ from audit')
            if decision['verdict']=='GO' and (decision.get('unresolved_blockers') or decision.get('unresolved_majors')):
                raise ValueError(f'{gid}: GO retains unresolved BLOCKER/MAJOR')
        checks.append('Three independent audit decisions present and consistent (verdict is not artifact PASS)')
    except Exception as exc: errors.append(f'independent audit decisions: {exc}')
    warnings += ['Schema/level witnesses do not prove player enjoyment, market fit, originality clearance, SDK builds or partner acceptance.',
                 'Indirect benchmark analyses are not recorded playthroughs. Unobserved timing and economics remain UNKNOWN.']
    report = dict(checked_at=datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(timespec='seconds'),
                  result='PASS' if not errors else 'FAIL', checks=checks, errors=errors, limitations=warnings,
                  environment=dict(python_executable=sys.executable,python_version=sys.version,
                                   verifiers_use_same_interpreter=True),
                  checks_scope='PREPARATION_ARTIFACTS_ONLY', game_build_executed=False)
    folder = ROOT/'validation'
    folder.mkdir(exist_ok=True)
    (folder/'preparation-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n', encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))
    return bool(errors)

if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
    raise SystemExit(main())
