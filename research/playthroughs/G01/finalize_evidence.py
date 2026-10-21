"""Local-only integrity check; never starts a browser or changes other directories."""
from pathlib import Path
from hashlib import sha256
from datetime import datetime, timezone
from urllib.parse import urlsplit, unquote
import json
import re

ROOT = Path(__file__).resolve().parent

def save(name, value):
    (ROOT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

def main():
    rows = [json.loads(x) for x in (ROOT / 'operations.jsonl').read_text(encoding='utf-8').splitlines()]
    hashes = []
    for line_number, row in enumerate(rows, 1):
        if not row.get('screenshot'):
            continue
        p = (ROOT / row['screenshot']).resolve()
        assert p.is_relative_to(ROOT / 'screenshots') and p.is_file()
        digest = sha256(p.read_bytes()).hexdigest()
        assert digest == row['screenshot_sha256'], p
        hashes.append(dict(path=p.relative_to(ROOT).as_posix(), sha256=digest,
                           bytes=p.stat().st_size, operations_jsonl_line=line_number,
                           captured_at_utc=row['ended_at_utc']))
    assert len(hashes) == 21
    assert len(list((ROOT/'screenshots').glob('*.png'))) == 21
    environments = [r for r in rows if r['event'] == 'environment']
    closes = [r for r in rows if r['event'] == 'context_closed']
    assert len(environments) == len(closes) == 2
    assert all(r['normal_close'] for r in closes)
    start = datetime.fromisoformat(environments[0]['at_utc'].replace('Z','+00:00'))
    end = datetime.fromisoformat(closes[-1]['at_utc'].replace('Z','+00:00'))
    span = (end-start).total_seconds()
    assert span < 480
    observation = (ROOT/'observation.md').read_text(encoding='utf-8')
    assert '\ufffd' not in observation
    for ref in re.findall(r'\[[^\]]*\]\(([^)]+)\)', observation):
        if not urlsplit(ref).scheme:
            p=(ROOT/unquote(ref)).resolve()
            assert p.is_relative_to(ROOT)
            if p.name not in {'validation.json','screenshot_hashes.json','delivery_manifest.json'}:
                assert p.is_file(), ref
    save('screenshot_hashes.json', dict(accessed_at='2026-10-21',algorithm='SHA-256',files=hashes))
    summary = dict(accessed_at='2026-10-21',
        status='PARTIAL_TUTORIAL_VISIBLE_INPUT_UNCONFIRMED',
        legal_core_move_confirmed=False, illegal_core_move_confirmed=False,
        victory_confirmed=False, failure_confirmed=False, in_game_retry_confirmed=False,
        complete_first_30_seconds=False, complete_first_5_minutes=False,
        complete_direct_playthroughs=0,official_videos_watched=0,
        attempted_game_urls=2, games_with_tutorial_ui_observed=1,
        browser_contexts=2,normal_context_closes=2,
        first_environment_at_utc=environments[0]['at_utc'],
        final_close_at_utc=closes[-1]['at_utc'],
        attempt_span_seconds=span,
        timing_definition='First environment record to final normal context close, including review/tool overhead and one restart; not gameplay duration.',
        successful_operation_records=sum(r['event']=='operation' for r in rows),
        operation_errors=sum(r['event']=='operation_error' for r in rows),
        screenshots=len(hashes),
        delivery_exclusions=['runtime/','runtime/**'],
        remaining_gap='Core legal/illegal arrow transitions and win/loss/retry remain UNKNOWN; no build-ready promotion.')
    save('summary.json', summary)
    save('validation.json', dict(result='PASS',validated_at_utc=datetime.now(timezone.utc).isoformat(),
        jsonl_lines=len(rows),screenshot_hashes_verified=len(hashes),missing_references=[],
        attempt_span_below_480_seconds=True,normal_context_closes_verified=2,
        asserted_observation_limits=summary['status'],runtime_excluded=True))
    names=['observation.md','operations.jsonl','browser-observe.cjs','sources.json','cleanup.json',
           'finalize_evidence.py','screenshot_hashes.json','summary.json','validation.json']
    files=[ROOT/n for n in names]+sorted((ROOT/'screenshots').glob('*.png'))
    entries=[]
    for p in files:
        rel=p.relative_to(ROOT).as_posix()
        assert not rel.startswith('runtime/')
        entries.append(dict(path=rel,bytes=p.stat().st_size,sha256=sha256(p.read_bytes()).hexdigest()))
    save('delivery_manifest.json', dict(accessed_at='2026-10-21',root=str(ROOT),
        packaging_rule='Include only listed files plus delivery_manifest.json itself; do not recursively package G01.',
        excluded_paths=['runtime/','runtime/**'],files=entries))
    print(json.dumps(summary,ensure_ascii=True,indent=2))

if __name__ == '__main__':
    main()
