# Vector Shift engineering notes

This project was imported as a separate game under `CoCreateGame/games/VectorShift/`. It is not G01 Signal Harbor and does not change any G01–G10 research or review decision. The current implementation state is in `README.md` and `delivery/PLAYTEST.md`; this file records the technical contracts and verification boundaries.

## Contracts

- `game-core.js` is the only authority for collision, clear paths, phase rotation, transitions, solving, and level validation. Rendering and hit tests must not decide whether a move is legal.
- Arrows retain `{id, color, d, cells}` with cells ordered tail to head. Blue bodies rotate clockwise around their heads with phase; gold bodies stay fixed.
- A ray leaving the playable mask is clear. Mask holes are void, not occupied cells.
- The source remains self-contained and offline-first. Coolmath has no remote SDK or telemetry. CrazyGames Basic may initialize its official SDK and send `GameplayStart`; no ad module is called.
- Keep competitor assets, names, levels, and proprietary code out of the playable build.

## Current test evidence

- Core suite: 52 levels, 50 phase-necessary levels, 14 levels requiring two toggles on a shortest solution, 360 solution actions replayed, 100 fuzz sequences, and shaped-level checks.
- Playwright smoke: path-specific taps, blocked feedback, zoom, exit guide, local run restoration, pinch and touch, daily result, responsive layouts at 1440×1000, 390×844, 320×568, and 844×390, plus both channel builds.
- Smoke tests use emulated Chromium viewports and input. They do not replace physical-device, blind-player, or platform testing.

## Build

`python src/build.py` regenerates the demo, Coolmath candidate, CrazyGames Basic candidate, root `index.html`, and the two matching submission HTML files. `python src/package_delivery.py` creates and verifies `delivery/Vector_Shift_playtest.zip`.
