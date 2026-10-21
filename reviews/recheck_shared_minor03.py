"""Independent read-only-source recheck. All outputs are beneath reviews/."""
from pathlib import Path
from hashlib import sha256
from urllib.parse import unquote
from datetime import datetime, timezone
import importlib.util
import json
import shutil
import subprocess
import sys

BASE = Path(__file__).resolve().parent.parent
OUT = BASE / 'reviews/shared-recheck-03'
SOURCE = BASE / 'research/benchmarks'

def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def digest(path):
    return sha256(path.read_bytes()).hexdigest()

def main():
    OUT.mkdir(exist_ok=False)
    snapshot = OUT / 'research/benchmarks'
    shutil.copytree(SOURCE, snapshot, ignore=shutil.ignore_patterns('runtime', 'raw', '__pycache__'))
    shutil.copy2(BASE / 'research/observation-summary.md', OUT / 'research/observation-summary.md')
    manifest = load(snapshot / 'delivery_manifest.json')
    (OUT / 'input-delivery_manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    source_digests = {p: digest(SOURCE / p) for p in ['validate_delivery.py', 'validation.json', 'delivery_manifest.json']}
    source_digests['../observation-summary.md'] = digest(SOURCE.parent / 'observation-summary.md')
    payload = []
    for row in manifest['files']:
        p = snapshot / row['path']
        payload.append({'path': row['path'], 'size_matches': p.stat().st_size == row['bytes'], 'sha256_matches': digest(p) == row['sha256'], 'inside_package': p.resolve().is_relative_to(snapshot.resolve()), 'runtime_or_raw': bool({'runtime', 'raw'}.intersection(p.relative_to(snapshot).parts))})
    associated = []
    for row in manifest['associated_read_only']:
        p = OUT / 'research' / row['path']
        associated.append({'path': row['path'], 'relative_to': row['relative_to'], 'size_matches': p.stat().st_size == row['bytes'], 'sha256_matches': digest(p) == row['sha256'], 'excluded_from_payload': row['included_in_this_subpackage'] is False and row['path'] not in {r['path'] for r in manifest['files']}})
    spec = importlib.util.spec_from_file_location('independent_benchmark_validator', snapshot / 'validate_delivery.py')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    cases = [
        ('../observation-summary.md', True),
        ('.././observation-summary.md#evidence', True),
        ('..%2fobservation-summary.md', True),
        ('methodology.md', True),
        ('evidence/session.json', True),
        ('../../MASTER_HANDOFF.md', False),
        ('../../../Windows/win.ini', False),
        ('evidence/runtime/profile/cache', False),
        ('raw/page.txt', False),
        ('../methodology.md', False),
        ('../contracts-and-rights.md', False),
        ('../observation-summary.md.bak', False),
        ('..%2f..%2fMASTER_HANDOFF.md', False),
        ('evidence/../runtime/profile/cache', False),
        ('evidence/runtime/../../../../MASTER_HANDOFF.md', False),
    ]
    probes = []
    for value, expected in cases:
        target = (mod.ROOT / unquote(value.split('#', 1)[0])).resolve()
        actual = mod.reference_allowed(target)
        probes.append({'reference': value, 'expected_allowed': expected, 'actual_allowed': actual, 'matches': actual == expected})
    # Exercise the actual reference entry point, not only the policy predicate.
    for value in ['../observation-summary.md', '..%2fobservation-summary.md']:
        mod.local_reference(value)
    for value in ['../../MASTER_HANDOFF.md', '..%2f..%2fMASTER_HANDOFF.md', '../methodology.md', 'evidence/runtime/profile/cache', 'raw/page.txt', 'evidence/Runtime/profile/cache', 'RAW/page.txt']:
        try:
            mod.local_reference(value)
        except AssertionError:
            probes.append({'entrypoint_reject': value, 'matches': True})
        else:
            probes.append({'entrypoint_reject': value, 'matches': False})
    # Windows resolve canonicalizes existing paths. A nonexistent differently-cased
    # segment is not by itself a successful local_reference (is_file rejects it).
    for spelling in ['evidence/runtime', 'evidence/Runtime', 'evidence/RUNTIME']:
        actual_target = (SOURCE / spelling).resolve()
        probes.append({'existing_source_runtime_case': spelling, 'exists': actual_target.exists(), 'matches': actual_target.exists() and not mod.reference_allowed((snapshot / actual_target.relative_to(SOURCE)).resolve())})
    process = subprocess.run([sys.executable, '-X', 'utf8', '-B', str(snapshot / 'validate_delivery.py')], cwd=snapshot, capture_output=True, text=True, encoding='utf-8')
    (OUT / 'validator-rerun.stdout.txt').write_text(process.stdout, encoding='utf-8')
    (OUT / 'validator-rerun.stderr.txt').write_text(process.stderr, encoding='utf-8')
    unchanged = {p: digest(SOURCE / p) == before for p, before in source_digests.items()}
    report = {'checked_at_utc': datetime.now(timezone.utc).isoformat(), 'scope': 'SRA-m03 only; source directories read only; validator executes frozen reviews copy', 'probe_correction': 'shared-recheck-02 overasserted the policy predicate on nonexistent differently-cased paths. Full local_reference rejects these nonexistent paths, and existing Windows runtime paths normalize to the excluded lowercase directory. No source defect established by those preliminary assertions.', 'input_validator_sha256': source_digests['validate_delivery.py'], 'original_manifest_payload': payload, 'original_manifest_associated_read_only': associated, 'reference_probes': probes, 'validator_returncode': process.returncode, 'rerun_report': load(snapshot / 'validation.json'), 'source_unchanged': unchanged}
    report['result'] = 'PASS' if (process.returncode == 0 and all(unchanged.values()) and all(p['matches'] for p in probes) and all(p['size_matches'] and p['sha256_matches'] and p['inside_package'] and not p['runtime_or_raw'] for p in payload) and len(associated) == 1 and all(p['size_matches'] and p['sha256_matches'] and p['excluded_from_payload'] for p in associated)) else 'FAIL'
    (OUT / 'results.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'result': report['result'], 'payload_files': len(payload), 'associated_files': len(associated), 'reference_probes': len(probes), 'failed_probes': [p for p in probes if not p['matches']], 'check_count': report['rerun_report']['check_count'], 'source_unchanged': unchanged}, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
