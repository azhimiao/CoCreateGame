"""Validate research references and emit a runtime-excluding delivery allowlist."""
from collections import Counter
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from urllib.parse import unquote, urlsplit
import json
import re

ROOT = Path(__file__).resolve().parent
DATE = '2026-10-21'
checks = []
ASSOCIATED_READ_ONLY = {(ROOT.parent / 'observation-summary.md').resolve()}

def check(condition, label):
    if not condition:
        raise AssertionError(label)
    checks.append(label)

def read_json(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def reference_allowed(target):
    return (target in ASSOCIATED_READ_ONLY or
            (target.is_relative_to(ROOT) and not {'runtime', 'raw'}.intersection(target.relative_to(ROOT).parts)))

def local_reference(value, base=ROOT):
    target = (base / unquote(value.split('#', 1)[0])).resolve()
    check(reference_allowed(target), f'local reference within delivery or explicit read-only association: {value}')
    check(target.is_file(), f'local reference exists: {value}')

def main():
    for value in ['../../MASTER_HANDOFF.md', '../../../Windows/win.ini', 'evidence/runtime/profile/cache', 'raw/page.txt']:
        check(not reference_allowed((ROOT / value).resolve()), f'out-of-scope reference rejected: {value}')
    data = read_json(ROOT / 'benchmarks.json')
    cards = data['benchmarks']
    sources = {s['source_id']: s for s in data['sources']}
    pids = {f'P{i:02}' for i in range(1, 7)}
    gids = {f'G{i:02}' for i in range(1, 11)}
    check(len(cards) == 24, '24 platform-game cards')
    check(len({c['benchmark_id'] for c in cards}) == 24, 'unique benchmark record keys')
    check(Counter(c['platform_id'] for c in cards) == {p: 4 for p in pids}, 'four cards per platform')
    deep_cards = [c for c in cards if c['deep_analysis']]
    check(len(deep_cards) == 12, '12 deep analyses')
    check(Counter(c['platform_id'] for c in deep_cards) == {p: 2 for p in pids}, 'two deep analyses per platform')
    fields = {'platform_id', 'game_id', 'name', 'source_url', 'accessed_at', 'published_at',
              'evidence_type', 'metric_definition', 'deep_analysis_source', 'known', 'unknown'}
    sections = {'first_30_seconds', 'first_5_minutes', 'core_input', 'success', 'failure',
                'retry', 'mid_term_loop', 'ui', 'ads_economy', 'devices'}
    for c in cards:
        key = c['benchmark_id']
        check(fields <= c.keys(), f'{key}: required machine-readable fields')
        check(set(c['game_id']) <= gids, f'{key}: only G01-G10 mapping')
        check(bool(c['mapping']['explanation']), f'{key}: mapping reason present')
        check(c['accessed_at'] == DATE, f'{key}: access date')
        check(c['ready_for_build'] is False, f'{key}: no build-ready promotion')
        check(c['source_url'].startswith('https://'), f'{key}: exact official HTTPS URL')
        for ref in c['direct_play']['evidence_paths']:
            local_reference(ref)
        if 'session_log' in c['direct_play']:
            local_reference(c['direct_play']['session_log'])
        if c['deep_analysis']:
            d = c['deep_analysis']
            check(d['mode'] == 'SECONDARY_RECONSTRUCTION', f'{key}: reconstruction label')
            check(d['timing']['first_30_seconds'] == d['timing']['first_5_minutes'] == 'UNKNOWN', f'{key}: unknown timing')
            check(set(d['sections']) == sections, f'{key}: all requested workflow dimensions')
            check(all(v['unknown'] for v in d['sections'].values()), f'{key}: itemized unknowns')
            check(d['video_evidence']['watched'] is False, f'{key}: no invented video viewing')
            check(bool(c['deep_analysis_source']), f'{key}: official reconstruction sources')
    def walk(value):
        if isinstance(value, dict):
            if 'source_ids' in value:
                check(set(value['source_ids']) <= sources.keys(), 'all source IDs resolve')
            for k, v in value.items():
                if k == 'accessed_at':
                    check(v == DATE, 'all source/card access dates consistent')
                if k == 'source_url' and not urlsplit(v).scheme:
                    local_reference(v)
                walk(v)
        elif isinstance(value, list):
            for item in value:
                walk(item)
    walk(data)
    for filename in ['methodology.md'] + [f'P{i:02}.md' for i in range(1, 7)]:
        text = (ROOT / filename).read_text(encoding='utf-8')
        check('\ufffd' not in text, f'{filename}: valid UTF-8 without replacement characters')
        check('|\n\n|' not in text, f'{filename}: contiguous Markdown table rows')
        for link in re.findall(r'\[[^\]]*\]\(([^)]+)\)', text):
            if not urlsplit(link).scheme:
                local_reference(link)
    journal = read_json(ROOT / 'evidence/session.json')
    shots = {entry['screenshot'] for entry in journal if entry.get('screenshot')}
    for shot in shots:
        local_reference(shot, ROOT / 'evidence')
    check(len({entry['id'] for entry in journal if entry.get('id')}) == 3, 'three browser game IDs only')
    check(sum(c['direct_play']['confirmed_gameplay_input'] for c in cards) == 1, 'one confirmed partial gameplay input')
    check(data['summary']['complete_direct_playthroughs'] == 0, 'zero completed direct playthroughs')
    check(data['summary']['secondary_reconstruction_deep_analyses'] == 12, 'all 12 deep narratives indirect')
    check(not (ROOT / 'evidence/browser-session.json').exists(), 'obsolete session filename absent')
    cleanup = read_json(ROOT / 'evidence/cleanup.json')
    check(cleanup['runtime_removed'] is False, 'cleanup policy rejection explicitly retained')
    check('evidence/runtime/' in data['metadata']['delivery_exclude_paths'], 'runtime explicitly excluded in dataset')
    report = {
        'accessed_at': DATE,
        'validated_at_utc': datetime.now(timezone.utc).isoformat(),
        'result': 'PASS',
        'check_count': len(checks),
        'cards': len(cards), 'deep_analyses': len(deep_cards),
        'per_platform': data['summary']['per_platform'],
        'official_or_publisher_source_records': len(sources) - 1,
        'browser_journal_events': len(journal), 'referenced_screenshots': len(shots),
        'missing_references': [],
        'limitations': ['No new web or browser activity during validation.',
                        'Semantic claims retain the source/observation limits in methodology.md.',
                        'Local runtime directory remains after policy rejection and MUST be excluded from packaging.'],
    }
    (ROOT / 'validation.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    roots = [ROOT / n for n in ['benchmarks.json', 'methodology.md', 'build_benchmarks.py', 'validate_delivery.py', 'validation.json']]
    roots += [ROOT / f'P{i:02}.md' for i in range(1, 7)]
    roots += [ROOT / 'evidence' / n for n in ['browser-probe.cjs', 'session.json', 'cleanup.json']]
    roots += sorted((ROOT / 'evidence/screenshots').glob('*.png'))
    allowlist = []
    for p in roots:
        rel = p.relative_to(ROOT).as_posix()
        check(not rel.startswith('evidence/runtime/'), 'allowlist contains no runtime path')
        allowlist.append({'path': rel, 'bytes': p.stat().st_size, 'sha256': sha256(p.read_bytes()).hexdigest()})
    manifest = {
        'accessed_at': DATE,
        'root': str(ROOT),
        'packaging_rule': 'Include ONLY files below plus delivery_manifest.json itself; never recursively pack the whole directory.',
        'excluded_paths': ['evidence/runtime/', 'evidence/runtime/**'],
        'associated_read_only': [{'path': str(p.relative_to(ROOT.parent)),
                                 'relative_to': 'research/', 'bytes': p.stat().st_size,
                                 'sha256': sha256(p.read_bytes()).hexdigest(),
                                 'included_in_this_subpackage': False} for p in sorted(ASSOCIATED_READ_ONLY)],
        'manifest_self_hash': 'OMITTED_TO_AVOID_RECURSIVE_HASH',
        'files': allowlist,
    }
    (ROOT / 'delivery_manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, ensure_ascii=True, indent=2))

if __name__ == '__main__':
    main()
