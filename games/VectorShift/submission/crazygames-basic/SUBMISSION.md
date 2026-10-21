# CrazyGames Basic Launch — Vector Shift submission pack

**Status:** technical candidate for Basic Launch. Not platform-approved. No live player testing claimed. Monetization intentionally disabled (no ad calls).

## Short description (EN)
Clear every arrow from the board. Blue arrows rotate together when you Shift Phase; gold arrows stay put. Fifty-two logic stages reward planning over speed.

## Long description (EN)
Vector Shift is an original HTML5 logic puzzle. Each stage places winding arrows on a square or shaped board. Tap an arrow only when its path to the edge is empty. Shift Phase rotates every blue arrow 90° while gold arrows keep facing, so the same board can unlock a new exit order. Fifty-two solver-verified stages introduce the rule, then ask for path planning and occasional multi-shift solutions. Undo, retry, and hints keep friction low. Family-safe English UI, lands directly on the board.

## Controls
1. Click / tap an arrow with a clear path to remove it
2. Shift Phase — blue arrows rotate 90° together (Space)
3. Undo (Z) / Retry (R) / Hint
4. Level select after unlock

## PEGI / age note
Designed as PEGI 12 / family-safe puzzle content: abstract arrows only, no violence, no hate speech, no gambling, no social features, no ads in Basic.

## SDK note
Basic Launch SDK is optional. This pack **does** load the official CrazyGames HTML5 v3 script (`crazygames-sdk-v3.js`) and calls `SDK.init()` then `game.gameplayStart()` when the board becomes interactive. **No ad module calls.** Ads remain disabled for Basic even if present in the SDK.

## File size
- `index.html` ≈ 138 KB uncompressed (well under 50 MB initial download)
- Single file; relative paths only for local assets (none required)

## Metadata checklist for portal
- Language: English
- Genre: Puzzle / Logic
- Levels: 52
- Covers: use `../assets/desktop.png` and `../assets/mobile.png` (regenerate 30–60s gameplay capture before portal upload)

## Rights
See `../RIGHTS.md`.
