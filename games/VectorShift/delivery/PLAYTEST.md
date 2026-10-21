# Vector Shift playtest build

Build: `1.0.0-phase-shift` · 2026-10-21

## Open

Unzip `Vector_Shift_playtest.zip` and open `index.html` in a current desktop or mobile browser. The gameplay is self-contained; no network connection is needed.

## Play

- Clear an arrow by tapping it when the line ahead is empty.
- Blue arrows and their bodies turn together when you Shift Phase. Gold arrows stay in place.
- If an arrow is blocked, inspect its red exit ray, choose another move, or use Undo, Retry, or Hint.
- Zoom with the controls or pinch. Drag the board when zoomed in. Show all exits for a board-wide path preview.
- Finish the board to see moves, time, misses, hints, and the shortest known solution status. Daily completion also records a local streak.

## Suggested review boards

- Level 1 teaches the exit rule.
- Level 11 introduces a heart silhouette.
- Level 20 shows the dense winding-arrow presentation.
- Level 52 is the final campaign board.

## Evidence and remaining checks

The deterministic core suite validates all 52 level solutions. An automated Playwright run checked desktop and emulated mobile layouts, touch taps, pinch zoom, progress recovery, daily results, and channel builds. See `artifacts/level20-desktop.png`, `artifacts/level20-mobile.png`, and `artifacts/daily-result-mobile.png` in the project.

No physical-device or blind-player study has been completed. No platform has approved this game. Trademark clearance and submission review remain open.
