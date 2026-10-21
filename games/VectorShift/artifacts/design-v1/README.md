# Design standard V1 evidence

Date: 2026-10-21. These captures show `docs/design-standard.html`, an explanatory design specimen. They do not show a rebuilt game, playable authored levels, physical-device testing, or accepted competitor parity.

- `standard-desktop.png`: full specimen at 1440×1000 viewport.
- `standard-mobile.png`: full specimen at 390×844 emulated viewport.
- `shape-grammar.png`: six original continuous silhouette candidates; not validated masks.
- `material-semantics.png`: proposed tube appearance and persistent blue/gold category markers.
- `exit-midpoint.png`: path-window exit at 30% progress; explanatory animation only.
- `verification.json`: five viewport overflow checks, specimen interactions, final source fingerprint, and independent baseline replay counts.

Browser: local Chromium through Playwright. Checked silhouette/grid display, non-color marker view, path-window removal, directional blocked feedback, forward/backward phase interpolation, reduced motion, and no page script errors. Response-time targets in the standard have not been measured on physical devices.

Design audit reproduction: run `node src/audit_design_baseline.cjs --check` from the game directory. The stored report enumerates 2,700 reachable states and 5,065 legal removals. A separate read-only traversal using the public `game-core.js` transition API reproduced both totals and checked same-phase removability after every legal removal. No playable level or core rule changed in this revision.

The current game remains `REVISION_REQUIRED`. Q1–Q5 are pending; this folder supplies Q0 specification evidence only.
