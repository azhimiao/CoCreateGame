"""Export a Windows build, then package runnable and source archives."""
import argparse
import hashlib
import shutil
import subprocess
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGES = ROOT / 'packages'
WINDOWS = ROOT / 'runtime' / 'windows'
EXCLUDED = {'.git', '.godot', 'runtime', 'packages', '__pycache__'}


def source_files():
    for path in sorted(ROOT.rglob('*')):
        relative = path.relative_to(ROOT)
        if path.is_file() and not EXCLUDED.intersection(relative.parts) and path.suffix not in {'.pyc', '.tmp'}:
            yield path, relative.as_posix()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--godot', default=shutil.which('godot') or 'godot')
    args = parser.parse_args()
    PACKAGES.mkdir(exist_ok=True)
    WINDOWS.mkdir(parents=True, exist_ok=True)
    subprocess.run([args.godot, '--headless', '--path', str(ROOT), '--import'], check=True)
    executable = WINDOWS / 'Layer relay.exe'
    subprocess.run([args.godot, '--headless', '--path', str(ROOT), '--export-release',
                    'Windows Desktop', str(executable)], check=True)
    if not executable.exists():
        raise RuntimeError('Godot did not produce the Windows executable')
    player_notes = '''Layer Relay · 折光机关

解压整个压缩包，双击 Layer relay.exe 运行，无需安装 Godot。
完整 50 关；设置功能正在开发中。

方向键 / WASD：移动    X / 空格：升降    Z：撤销
R：重开    H：提示    Enter：暂停 / 恢复

存档自动保存在 %APPDATA%/Godot/app_userdata/Layer Relay/。
程序中的 Godot 引擎及第三方组件许可见 licenses/。
'''
    windows_zip = PACKAGES / 'Layer-relay-Windows-x64.zip'
    with zipfile.ZipFile(windows_zip, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for path in sorted(WINDOWS.iterdir()):
            if path.is_file() and path.suffix in {'.exe', '.pck', '.dll'} and not path.name.endswith('.console.exe'):
                archive.write(path, 'Layer relay/' + path.name)
        archive.writestr('Layer relay/开始游玩.txt', player_notes.encode('utf-8-sig'))
        for path in sorted((ROOT / 'licenses').glob('*.txt')):
            archive.write(path, 'Layer relay/licenses/' + path.name)
    source_zip = PACKAGES / 'Layer-relay-source.zip'
    with zipfile.ZipFile(source_zip, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for path, relative in source_files():
            archive.write(path, 'Layer relay/' + relative)
    checksums = []
    for path in [windows_zip, source_zip]:
        with zipfile.ZipFile(path) as archive:
            if archive.testzip() is not None:
                raise RuntimeError('Archive integrity check failed: ' + path.name)
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        checksums.append(f'{digest}  {path.name}')
        print(f'PACKAGED {path.name}: {path.stat().st_size:,} bytes; SHA256 {digest}')
    (PACKAGES / 'SHA256SUMS.txt').write_text('\n'.join(checksums) + '\n', encoding='utf-8', newline=chr(10))


if __name__ == '__main__':
    main()
