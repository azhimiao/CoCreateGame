## 1.0.0-phase-shift (2026-10-21)
- Reworked board sizing and desktop/mobile game chrome; fixed collapsed desktop header.
- Replaced overlapping rectangular arrow hit boxes with path-following SVG hit targets.
- Added zoom, pan, pinch, all-exits view, local active-run restore, and separate campaign/daily saves.
- Added miss/time/hint tracking, daily streak and result summary, opt-in share, keyboard-accessible dialogs, and vibration preference.
- Rebuilt demo, Coolmath, and CrazyGames Basic HTML; added viewport, touch, pinch, resume, and daily-result Playwright smoke.
- The 52 level data and game-core rules are unchanged. Physical-device, blind-player, name-clearance, and portal checks remain open.

## 0.8.1-dense-mid (2026-10-21 21:50 Asia/Shanghai)
- Mid levels L15–30 dense pack: L20 fill 87.8%, avgLen 5.38; coverage + empty-blob gates (generator v7).
- Screenshots refreshed; tests PASS; playtest zip rebuilt.

## 0.8.0-long-tube (2026-10-21 21:42 Asia/Shanghai)
- Commercial long-arrow look: generator v6 prefers 4–12+ cell winding snakes (teaching stays short).
- Glossy tube render (~0.88 cell): dark outline, underside shade, bright specular, chevron + cartoon eyes.
- L20 avgLen 5.33; L38 avgLen 4.75; L13+ avg 6.19 (max 12).
- Masks / phase / void-exit / Chinese UI kept. Tests PASS. Screenshots refreshed.


## 0.7.0-shape (2026-10-21)
- Irregular board masks (heart/plus/diamond/ring/letter/blob); void exit = clear.
- Density bands relative to mask; 32/52 shaped levels; L10+ ~72% non-square.
- Design doc: docs/竞争力-形状密度难度复用.md
## 0.6.0-dense (2026-10-21 Asia/Shanghai)
- Commercial-density visual pass: chunky outlined snakes, candy palette, packed boards (≥65% mid/late fill)
- Mobile puzzle chrome (no SaaS topbar/legend/demo footer); exit path as thick green/red cells
- Stronger slide-off + ghost trail; generator v4; 52 levels; tests PASS

## 0.5.0-visual (2026-10-21 Asia/Shanghai)
- Polyline multi-cell arrows (tail→head); both phases occupancy-validated
- SVG capsule bodies + exit rays + slide-out / blocked flash
- Casual pastel UI; de-AI chrome; 52 levels; tests PASS
