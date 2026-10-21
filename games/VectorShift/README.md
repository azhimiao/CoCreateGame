# Vector Shift / 相位箭头

Vector Shift is a complete, offline-first HTML5 puzzle game in its own `CoCreateGame/games/VectorShift/` project directory. The current build contains 52 solver-verified stages, shaped boards, multi-cell arrows, phase rotation, local daily challenges, accessible controls, and separate demo and portal builds.

## Play

Open [`index.html`](index.html) directly in a modern browser. It is a single-file game and needs no local server or network connection. The normal build starts at the campaign board; local progress and an interrupted run are saved on the device.

For the browser-served build with refresh support, run `python src/serve.py` and open the URL printed in the terminal. The packaged, single-file tester build is [`delivery/Vector_Shift_playtest.zip`](delivery/Vector_Shift_playtest.zip).

## Game

- Tap an arrow whose path is clear to the board edge or the outside of a shaped board; its full body slides away.
- Shift Phase rotates all blue arrows and their bodies 90 degrees. Gold arrows remain fixed.
- Levels combine square, heart, ring, plus, diamond, letter, and other masks. Empty silhouette cells are not obstacles.
- Undo, retry, hints, path preview, an all-exits guide, zoom, drag-to-pan, and touch pinch-zoom are available without ads, timers that force play, or paid items.
- Daily puzzles are deterministic per local calendar date. Completion, time, misses, hints, and streak are stored locally. Sharing only occurs when a player presses Share.
- The interface supports Chinese in the demo and English in both channel builds. Reduced-motion preferences are respected.

## Project map

| Path | Contents |
| --- | --- |
| `src/game-core.js` | Collision, phase rules, solver, and validation |
| `src/app.js`, `src/styles.css`, `src/index.template.html` | Game UI and renderer |
| `src/generate_levels.py` | Deterministic level generation |
| `src/build.py` | Rebuild demo and portal-specific single-file HTML |
| `src/package_delivery.py` | Rebuild and verify the small tester ZIP |
| `data/levels.json`, `data/level_audit.csv` | 52 stages and level audit |
| `tests/` | Core suite and Playwright browser / touch smoke |
| `dist/` | Generated builds (ignored by Git) |
| `submission/` | Current Coolmath and CrazyGames Basic candidate pages and materials |
| `artifacts/` | Current responsive QA screenshots and supplied competitor references |
| `docs/` | Original handoff plus the implementation record |

## Build and verification

```powershell
node tests/core.test.cjs
python src/build.py
python src/package_delivery.py
```

The browser smoke needs Node Playwright and a Chromium executable. Set `PLAYWRIGHT_MODULE` to the Playwright module and optionally `CHROMIUM_PATH` to a local Chromium executable, then run:

```powershell
node tests/smoke.cjs
```

The smoke exercises path hit testing, blocked moves, phase and undo, zoom, all-exits view, local resume, touch pinch and tap, daily results, four screen sizes, and both release builds. It writes screenshots under `artifacts/`.

## Release status

The demo and two channel builds are technically ready for human review. The game has not completed blind player testing, physical-device testing, name clearance, or official platform review. Coolmath contains no external SDK or analytics. CrazyGames Basic references the official SDK for initialization and `GameplayStart` only; it has no ad calls. No platform approval, player preference, or revenue result is claimed.

The source handoff and competitor screenshots are retained as project references. Competitor assets, code, and levels are not included in the playable build.
