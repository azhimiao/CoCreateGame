"""Lightweight Playwright smoke for the dense commercial UI.
Requires: pip install playwright && playwright install chromium
Skips cleanly if Playwright/Chromium are unavailable.
"""
from pathlib import Path
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from functools import partial
from threading import Thread
import sys
import json

r = Path(__file__).resolve().parents[1]

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print('SKIP smoke — playwright not installed')
    sys.exit(0)

server = ThreadingHTTPServer(('127.0.0.1', 0), partial(SimpleHTTPRequestHandler, directory=str(r)))
Thread(target=server.serve_forever, daemon=True).start()
HTML = (r / 'index.html').read_text().replace(
    "qa=new URLSearchParams(location.search).has('qa')", "qa=true"
)

chromium = '/usr/bin/chromium'
if not Path(chromium).exists():
    chromium = '/usr/bin/google-chrome'
if not Path(chromium).exists():
    chromium = None

with sync_playwright() as p:
    try:
        browser = p.chromium.launch(
            headless=True,
            executable_path=chromium,
            args=['--no-sandbox', '--disable-web-security'],
        )
    except Exception as e:
        print('SKIP smoke — chromium launch failed:', e)
        server.shutdown()
        sys.exit(0)
    try:
        page = browser.new_page(viewport={'width': 1390, 'height': 930}, device_scale_factor=1)
        errors = []
        page.on('pageerror', lambda err: errors.append(str(err)))
        page.set_content(HTML, wait_until='load')
        page.locator('[data-testid="piece-0"]').wait_for()
        # L1 is 5×5
        assert page.locator('.grid-cell').count() == 25
        assert page.locator('.snake-hit').count() == 2
        page.screenshot(path=str(r / 'artifacts/desktop.png'), full_page=True)
        page.evaluate('window.VectorShiftDebug.solveAndPlay()')
        page.locator('#continueWin, #viewLevelsWin, #dailyBackWin').first.wait_for(timeout=5000)
        assert 1 in page.evaluate('window.VectorShiftDebug.getProgress().completed')
        page.locator('#continueWin').click()
        assert '2 /' in page.locator('#levelChip').inner_text()
        page.locator('#hintButton').click()
        assert page.locator('#feedback').inner_text()
        page.locator('#phaseButton').click()
        assert page.evaluate('window.VectorShiftDebug.getState().phase') == 1
        page.locator('#undoButton').click()
        assert page.evaluate('window.VectorShiftDebug.getState().phase') == 0
        page.locator('#levelMenuButton').click()
        page.locator('#modalTitle').wait_for()
        page.locator('#modalClose').click()
        page.evaluate('window.VectorShiftDebug.setLevel(52)')
        assert '52 /' in page.locator('#levelChip').inner_text()
        page.evaluate('window.VectorShiftDebug.solveAndPlay()')
        page.locator('#viewLevelsWin, #replayWin').first.wait_for(timeout=5000)
        assert 52 in page.evaluate('window.VectorShiftDebug.getProgress().completed')
        assert page.evaluate('window.VectorShiftDebug.getState().remaining.length') == 0
        assert not errors, errors

        # Shape / density screenshots (indices from data/levels.json)
        page.evaluate('window.VectorShiftDebug.setLevel(1)')
        page.locator('.snake-hit').first.wait_for()
        page.screenshot(path=str(r / 'artifacts/level1.png'), full_page=True)
        heart_idx = 11
        page.evaluate(f'window.VectorShiftDebug.setLevel({heart_idx})')
        page.locator('.snake-hit').first.wait_for()
        page.screenshot(path=str(r / 'artifacts/shape_heart.png'), full_page=True)
        void_count = page.evaluate("() => document.querySelectorAll('.grid-cell.void').length")
        assert void_count > 0, 'heart should show void cells'
        dense_idx = 29  # plus high-fill long snakes
        page.evaluate(f'window.VectorShiftDebug.setLevel({dense_idx})')
        page.locator('.snake-hit').first.wait_for()
        page.screenshot(path=str(r / 'artifacts/shape_dense.png'), full_page=True)
        page.evaluate('window.VectorShiftDebug.setLevel(20)')
        page.locator('.snake-hit').first.wait_for()
        page.screenshot(path=str(r / 'artifacts/level20.png'), full_page=True)
        levels_json = json.loads((r / 'data/levels.json').read_text())
        sq_idx = 20
        for i in range(len(levels_json) - 1, 13, -1):
            if levels_json[i].get('shape', 'square') == 'square':
                sq_idx = i + 1
                break
        page.evaluate(f'window.VectorShiftDebug.setLevel({sq_idx})')
        page.locator('.snake-hit').first.wait_for()
        page.screenshot(path=str(r / 'artifacts/square_dense_long.png'), full_page=True)
        print('SHAPE SHOTS — heart', heart_idx, 'dense', dense_idx, 'square_long', sq_idx, 'voids', void_count)

        print('DESKTOP PASS — levels 1 and 52, hint, undo, phase toggle, modal')

        mob = browser.new_page(
            viewport={'width': 390, 'height': 844},
            device_scale_factor=1,
            has_touch=True,
            is_mobile=True,
        )
        errors2 = []
        mob.on('pageerror', lambda err: errors2.append(str(err)))
        mob.set_content(HTML, wait_until='load')
        mob.evaluate('window.VectorShiftDebug.setLevel(20)')
        mob.locator('.snake-hit').first.wait_for()
        mob.screenshot(path=str(r / 'artifacts/mobile.png'), full_page=True)
        bbox = mob.locator('.board').bounding_box()
        assert bbox['x'] >= 0 and bbox['x'] + bbox['width'] <= 390, bbox
        target = mob.locator('.snake-hit').first.bounding_box()
        assert target['width'] >= 40, target
        mob.locator('#phaseButton').tap()
        assert mob.evaluate('window.VectorShiftDebug.getState().phase') == 1
        assert not errors2, errors2
        print('MOBILE PASS — touch and board in viewport, touch target', round(target['width'], 1))

        cool = r / 'dist/coolmath/index.html'
        if cool.exists():
            rc = cool.read_text()
            release = browser.new_page(viewport={'width': 375, 'height': 812})
            release.set_content(rc, wait_until='load')
            assert release.evaluate('typeof window.VectorShiftDebug') == 'undefined'
            # export lives in sr-only / settings; must not be visibly interactive in play chrome
            assert release.locator('.play-top #exportButton').count() == 0
            assert release.locator('.snake-hit').count() >= 2
            assert not release.evaluate('document.documentElement.scrollWidth > window.innerWidth + 1')
            print('COOLMATH PRE-BUILD PASS — QA hooks hidden, layout ok')
    finally:
        browser.close()
        server.shutdown()
