# Coolmath Games — Vector Shift submission pack

**Status:** technical candidate only. Not platform-approved. No live player testing claimed.

## Pitch (one-liner)
Vector Shift is a 52-level logic puzzle: clear winding arrows from a board; blue arrows rotate together when you Shift Phase, while gold arrows stay fixed. Shaped boards, path planning, and reversible moves make order matter.

## Controls
- **Tap / click** an arrow with a clear path to the edge to remove it
- **Shift Phase** (button or Space): rotate all blue arrows 90°
- **Undo** (Z), **Retry** (R), **Hint** for the next solver step
- Controls have 44px or larger hit areas on phone layouts; arrow hit testing follows each drawn path

## Family-safe statement
HTML5 thinking / puzzle game. No violence, no foul language, no name entry, no chat, no user-generated content, no ads, no external links in the Coolmath build, no outbound stats reporting.

## Credits
Independent Puzzle Studio (name only — no URL, email, or social links in-build).

## Rights
Original authored code and generated puzzles. No third-party game assets, levels, or trademarks embedded. See `../RIGHTS.md`.

## What was disabled / configured for Coolmath
- Local playtest event logging is a no-op (`CHANNEL==='coolmath'`)
- Export playtest control removed from markup; outbound-looking copy scrubbed
- `?qa=1` developer skip disabled
- No third-party ads/analytics SDK
- No invented Coolmath SDK (willing to add theirs later if they ask)
- English UI throughout

## Build
- File: `index.html` (single-file, about 138 KB uncompressed)
- Rebuild source: `python3 src/build.py` → `dist/coolmath/index.html`

## Honest gaps before send
- No blind-player test yet
- No 30–60s capture video in this pack (screenshots only under `../assets/`)
- Trademark clearance for the name “Vector Shift” is still open
