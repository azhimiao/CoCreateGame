# Vector Shift / 相位箭头

Vector Shift is a playable HTML5 puzzle baseline in its own `CoCreateGame/games/VectorShift/` project directory. **Product status: REVISION_REQUIRED.** Its 52 solver-verified stages and working interface do not yet meet the required visual, interaction, or puzzle-depth standard.

## Design standard — start here

The user's quality review takes priority over the previous implementation-complete description. Read the [产品设计与验收规范 V1](docs/08_产品设计与验收规范.md), open the [interactive design specimen](docs/design-standard.html), and use the [level design worksheet](docs/level-design.template.json). The specimen illustrates proposed silhouettes, material semantics, and motion; it is not an implemented replacement game.

The [reproducible design audit](data/design-baseline.json) finds that all 52 stages can be solved with the minimum number of phase switches by removing everything currently clear and switching only when stuck. Across 5,065 reachable legal removal transitions, none loses solvability under the existing unlimited-toggle rules. Density and long bodies must therefore be evaluated separately from consequential decision depth.

Next: three refined real boards, a continuous input/motion sample, and four small relay-exit hypothesis stages; pass the visual, interaction, logic, and benchmark gates before producing the full content set. Relay exits are a design hypothesis and are not present in the current game.

## Play

Open [`index.html`](index.html) directly in a modern browser. It is a single-file game and needs no local server or network connection. The normal build starts at the campaign board; local progress and an interrupted run are saved on the device.

For the browser-served build with refresh support, run `python src/serve.py` and open the URL printed in the terminal. The packaged, single-file tester build is [`delivery/Vector_Shift_playtest.zip`](delivery/Vector_Shift_playtest.zip).

An earlier 20-level prelaunch candidate is retained at [`delivery/Vector_Shift_v02_prelaunch_candidate.zip`](delivery/Vector_Shift_v02_prelaunch_candidate.zip) for traceability. The 52-level project in this directory remains the current source of truth.

## Game

- Tap an arrow whose path is clear to the board edge or the outside of a shaped board; its full body slides away.
- Shift Phase switches blue arrows between their original pose and a 90-degree clockwise pose (0↔1). Gold arrows remain fixed; current renderer colors still require correction to match these semantic categories.
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
| `src/audit_design_baseline.cjs`, `data/design-baseline.json` | Reproducible design diagnosis: greedy policy, reachable states, topology, rotation fingerprints |
| `docs/08_产品设计与验收规范.md`, `docs/design-standard.html` | Current normative design standard and non-playable interactive specimen |
| `docs/level-design.template.json` | Authoring worksheet separating targets, measured evidence, and untested fields |
| `tests/` | Core suite and Playwright browser / touch smoke |
| `dist/` | Generated builds (ignored by Git) |
| `submission/` | Current Coolmath and CrazyGames Basic candidate pages and materials |
| `artifacts/` | Current responsive QA screenshots and supplied competitor references |
| `docs/` | Original handoff plus the implementation record |

## Build and verification

```powershell
node tests/core.test.cjs
node src/audit_design_baseline.cjs --check
python src/build.py
python src/package_delivery.py
```

The browser smoke needs Node Playwright and a Chromium executable. Set `PLAYWRIGHT_MODULE` to the Playwright module and optionally `CHROMIUM_PATH` to a local Chromium executable, then run:

```powershell
node tests/smoke.cjs
```

The smoke exercises path hit testing, blocked moves, phase and undo, zoom, all-exits view, local resume, touch pinch and tap, daily results, four screen sizes, and both release builds. It writes screenshots under `artifacts/`.

## Release status

The demo and two channel builds are functional baselines pending design rework. Prior core/browser smoke results remain technical evidence; the new design quality gates have not passed. The game has not completed blind player testing, physical-device testing, name clearance, or official platform review. Coolmath contains no external SDK or analytics. CrazyGames Basic references the official SDK for initialization and `GameplayStart` only; it has no ad calls. No competitor parity, platform approval, player preference, or revenue result is claimed.

The source handoff and competitor screenshots are retained as project references. Competitor assets, code, and levels are not included in the playable build.
