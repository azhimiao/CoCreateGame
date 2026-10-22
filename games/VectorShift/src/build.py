#!/usr/bin/env python3
"""Build single-file HTML for demo, coolmath, and crazygames-basic channels."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
template = (ROOT / 'src/index.template.html').read_text(encoding='utf8')
levels = json.dumps(
    json.loads((ROOT / 'data/levels.json').read_text(encoding='utf8')),
    ensure_ascii=False,
    separators=(',', ':'),
).replace('</', '<\\/')

CRAZY_SDK = (
    '<script src="https://sdk.crazygames.com/crazygames-sdk-v3.js"></script>\n'
    '<!-- CrazyGames Basic: GameplayStart only; no ads module calls. -->'
)

for channel in ('demo', 'coolmath', 'crazygames-basic'):
    html = template
    head = CRAZY_SDK if channel == 'crazygames-basic' else ''
    pieces = {
        '<!--INJECT_HEAD-->': head,
        '/*INJECT_STYLES*/': (ROOT / 'src/styles.css').read_text(encoding='utf8'),
        '/*INJECT_CHANNEL*/': f'window.VS_CHANNEL={json.dumps(channel)};',
        '/*INJECT_CORE*/': (ROOT / 'src/game-core.js').read_text(encoding='utf8'),
        '/*INJECT_LEVELS*/': levels,
        '/*INJECT_APP*/': (ROOT / 'src/app.js').read_text(encoding='utf8'),
    }
    for key, value in pieces.items():
        assert key in html, key
        html = html.replace(key, value)

    # Commercial builds: hard-disable ?qa= even if app.js is edited later.
    if channel != 'demo':
        html = html.replace(
            "if(CHANNEL==='demo')qa=new URLSearchParams(location.search).has('qa');",
            'qa=false;',
        )

    if channel == 'coolmath':
        # Hide export control in markup and scrub outbound-looking copy from the bundle.
        html = html.replace(
            '<button id="exportButton" class="quiet-button" type="button">Export playtest log ↓</button>',
            '',
        )
        html = html.replace(
            '<button id="exportButton" type="button">Export log</button>',
            '',
        )
        for phrase in (
            'Export playtest log ↓',
            '导出试玩记录 ↓',
            'Playtest events stay in this browser',
            '试玩事件只保留在当前浏览器中，可手动导出',
            'telemetry_exported',
            'vector-shift-playtest.json',
            'EXPERIMENTAL',
            'NOT A PUBLISHED GAME',
            'MECHANICAL PROTOTYPE',
        ):
            html = html.replace(phrase, '')

    html = '\n'.join(line.rstrip() for line in html.splitlines()) + '\n'
    # Preserve the original phase campaign as its own accessible mode.
    out = ROOT / 'dist' / channel / 'phase.html'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding='utf8')
    if channel == 'demo':
        (ROOT / 'phase.html').write_text(html, encoding='utf8')
    elif channel in ('coolmath', 'crazygames-basic'):
        submission = ROOT / 'submission' / channel / 'phase.html'
        submission.parent.mkdir(parents=True, exist_ok=True)
        submission.write_text(html, encoding='utf8')
    print(channel, 'phase', len(html.encode('utf8')), 'bytes')

    dense = (ROOT / 'src/dense.template.html').read_text(encoding='utf8')
    dense_levels = json.dumps(json.loads((ROOT / 'data/dense-levels.json').read_text(encoding='utf8')), ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
    for marker, content in {
        '<!--INJECT_HEAD-->': head,
        '/*INJECT_STYLES*/': (ROOT / 'src/dense.css').read_text(encoding='utf8'),
        '/*INJECT_CHANNEL*/': f'window.VS_CHANNEL={json.dumps(channel)};',
        '/*INJECT_CORE*/': (ROOT / 'src/dense-core.js').read_text(encoding='utf8'),
        '/*INJECT_LEVELS*/': dense_levels,
        '/*INJECT_APP*/': (ROOT / 'src/dense-app.js').read_text(encoding='utf8'),
    }.items():
        assert marker in dense
        dense = dense.replace(marker, content)
    if channel != 'demo':
        dense = dense.replace('<html lang="zh-CN">', '<html lang="en">')
        dense = dense.replace('<title>Vector Shift · 绮彩长蛇</title>', '<title>Vector Shift · Winding Paths</title>')
    dense = '\n'.join(line.rstrip() for line in dense.splitlines()) + '\n'
    (ROOT / 'dist' / channel / 'index.html').write_text(dense, encoding='utf8')
    if channel == 'demo':
        (ROOT / 'index.html').write_text(dense, encoding='utf8')
    else:
        (ROOT / 'submission' / channel / 'index.html').write_text(dense, encoding='utf8')
    print(channel, 'dense', len(dense.encode('utf8')), 'bytes')
