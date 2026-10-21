"""Package a small, offline-playable build with current QA screenshots."""
from hashlib import sha256
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / 'delivery' / 'Vector_Shift_playtest.zip'
FILES = (
    ('dist/demo/index.html', 'index.html'),
    ('README.md', 'README.md'),
    ('delivery/PLAYTEST.md', 'PLAYTEST.md'),
    ('artifacts/level20-desktop.png', 'artifacts/level20-desktop.png'),
    ('artifacts/level20-mobile.png', 'artifacts/level20-mobile.png'),
    ('artifacts/daily-result-mobile.png', 'artifacts/daily-result-mobile.png'),
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
