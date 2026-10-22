"""Package a small, offline-playable build with current QA screenshots."""
from hashlib import sha256
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / 'delivery' / 'Vector_Shift_playtest.zip'
FILES = (
    ('dist/demo/index.html', 'index.html'),
    ('dist/demo/phase.html', 'phase.html'),
    ('delivery/PLAYTEST.md', 'README.md'),
    ('artifacts/dense-pattern-1.png', 'artifacts/dense-pattern-1.png'),
    ('artifacts/dense-pattern-2.png', 'artifacts/dense-pattern-2.png'),
    ('artifacts/dense-pattern-3.png', 'artifacts/dense-pattern-3.png'),
    ('artifacts/dense-same-width-comparison.png', 'artifacts/dense-same-width-comparison.png'),
    ('artifacts/dense-playthrough.webm', 'artifacts/dense-playthrough.webm'),
    ('artifacts/campaign/board-001.png', 'artifacts/journey-first.png'),
    ('artifacts/campaign/board-120.png', 'artifacts/journey-finale.png'),
    ('artifacts/campaign/chapter-01.png', 'artifacts/journey-chapters.png'),
    ('artifacts/campaign/journey-playthrough.webm', 'artifacts/journey-playthrough.webm'),
    ('artifacts/mobile/game-320x568.png', 'artifacts/mobile-small-screen.png'),
    ('artifacts/mobile/chapters-320x568.png', 'artifacts/mobile-chapter-sheet.png'),
    ('artifacts/mobile/report.json', 'artifacts/mobile-report.json'),
)

members = [(source, target, (ROOT / source).read_bytes()) for source, target in FILES]
ARCHIVE.parent.mkdir(parents=True, exist_ok=True)
with ZipFile(ARCHIVE, 'w', ZIP_DEFLATED, compresslevel=8) as archive:
    for _, target, payload in members:
        archive.writestr(target, payload)

with ZipFile(ARCHIVE) as archive:
    assert archive.testzip() is None
    assert set(archive.namelist()) == {target for _, target, _ in members}
    for _, target, payload in members:
        packaged = archive.read(target)
        assert len(packaged) == len(payload)
        assert sha256(packaged).digest() == sha256(payload).digest()

print(f'PASS {ARCHIVE.name}: {len(members)} files, {ARCHIVE.stat().st_size} bytes')

archives = [ARCHIVE]
for channel in ('coolmath', 'crazygames-basic'):
    candidates = [('index.html', ROOT / 'dist' / channel / 'index.html'),
                  ('phase.html', ROOT / 'dist' / channel / 'phase.html'),
                  ('README.md', ROOT / 'submission' / channel / 'SUBMISSION.md'),
                  ('RIGHTS.md', ROOT / 'submission/RIGHTS.md')]
    archive_path = ROOT / 'delivery' / f'Vector_Shift_{channel}_candidate.zip'
    with ZipFile(archive_path, 'w', ZIP_DEFLATED, compresslevel=8) as archive:
        for target, source in candidates:
            archive.writestr(target, source.read_bytes())
    with ZipFile(archive_path) as archive:
        assert archive.testzip() is None
        assert set(archive.namelist()) == {target for target, _ in candidates}
        for target, source in candidates:
            assert sha256(archive.read(target)).digest() == sha256(source.read_bytes()).digest()
    print(f'PASS {archive_path.name}: {len(candidates)} files, {archive_path.stat().st_size} bytes')
    archives.append(archive_path)

# Keep the review evidence and shipped HTML tied to the same exact bytes.
audit = json.loads((ROOT / 'artifacts/campaign/release-audit.json').read_text(encoding='utf8'))
for build in audit['builds']:
    html = (ROOT / 'dist' / build['channel'] / 'index.html').read_bytes()
    assert sha256(html).hexdigest() == build['sha256'], 'Re-run release-audit.cjs for the current build'
manifest = {'release': '2026-10-22-campaign-120', 'levels': 120, 'chapters': 10,
            'status': 'offline release candidate; not submitted',
            'builds': [{key: b[key] for key in ('channel', 'bytes', 'sha256')} for b in audit['builds']],
            'archives': []}
for archive_path in archives:
    with ZipFile(archive_path) as archive:
        manifest['archives'].append({'file': archive_path.name, 'bytes': archive_path.stat().st_size,
                                    'sha256': sha256(archive_path.read_bytes()).hexdigest(),
                                    'members': archive.namelist()})
(ARCHIVE.parent / 'RELEASE_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf8',newline='\n')
print('PASS release manifest: audited HTML hashes match every current build')
