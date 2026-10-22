# Vector Shift — crazygames-basic candidate

Status: internal playable candidate; not submitted or platform-approved.

## Description

Untangle a colorful garden of winding snakes. Follow their gaze, clear the path ahead, and watch each body glide out along its own curves. Five original patterns include a dense courtyard, heart, leaf, larger garden and a small introduction. Hints, undo and zoom are always available.

The main collection has five stages and 128 snakes. A local menu link opens the preserved 52-stage phase challenge, where blue paths rotate together and gold paths remain fixed. The main collection has no phase switching: its six colors identify individual paths.

## Controls

Tap/click a head or body with a clear exit. Z: undo; H: hint. Arrow keys select on the Canvas; Enter/Space releases. Pinch to zoom and drag while enlarged. The collection opens in the top-left menu; phase settings link back to it.

## Files and verification

Ship **both** `index.html` (new collection, approximately 133 KB uncompressed) and `phase.html` (preserved challenge, approximately 139 KB). Main gameplay needs no assets or font downloads. English UI and accessible direction labels are included. Developer helpers are disabled in channel builds.

Six viewport checks and real pointer/touch-emulated interactions passed; all five dense stages were cleared through actual head/body taps. Phase regression also passed. See the project `artifacts/dense-browser-report.json`, `docs/10_密盘重做与验证.md`, and current captures in `../assets/`.

## Channel configuration

CrazyGames candidate loads the official v3 SDK, initializes it, and calls gameplayStart. No ad calls. The lifecycle was tested with a local mock; live platform integration remains unverified.

## Remaining review

Physical-device comfort/performance, real-player preference, name clearance and platform review remain open. No revenue or competitive superiority claim. Rights notes: `../RIGHTS.md`. A Chinese demo playthrough is available in the project artifacts; record the final English portal capture after the product is approved for submission.
