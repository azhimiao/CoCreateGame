# Vector Shift — crazygames-basic candidate

Status: internal playable release candidate; not submitted or platform-approved.

## Description

Untangle a colorful garden of winding snakes. The offline journey contains 120 original stages in 10 ordered chapters, from four short paths to late boards with up to 56. Five full-pattern gallery boards remain freely selectable. Hints and undo are always available; a scissors skill unlocks at level 6, can release one blocked path per level, and can itself be undone.

The journey's 3,268 authored paths have independent solvability audits and are playable without the skill. The gallery contains the five previously reviewed boards, including the onboarding board. A local menu link opens the preserved 52-stage phase challenge, where blue paths rotate together and gold paths remain fixed. The new journey has no phase switching: its six colors identify individual paths.

## Controls

Tap/click a head or body with a clear exit. Z: undo; H: hint. Open the menu to switch journey/gallery and select a chapter page. The scissors enters select-and-confirm mode. Arrow keys select on the Canvas; Enter/Space releases. Pinch to zoom and drag while enlarged. The phase challenge remains a separate local mode.

## Files and verification

Ship **both** `index.html` (journey plus gallery, approximately 1.58 MB uncompressed) and `phase.html` (preserved challenge, approximately 139 KB). The campaign level data is embedded for reliable offline play. Gameplay needs no external assets or font downloads. English UI and accessible direction labels are included. Developer helpers are disabled in channel builds.

All 120 levels and all 3,268 paths have offline geometric and solvability checks. Browser replay covers all stages, scissors undo/save, six viewports, gallery and English builds; motion replay includes early and final boards. See `artifacts/campaign/release-audit.json` and `browser-report.json`, plus `docs/12_量产关卡与技能施工.md`.

## Channel configuration

CrazyGames candidate loads the official v3 SDK, initializes it, and calls gameplayStart. No ad calls. The lifecycle was tested with a local mock; live platform integration remains unverified.

Technical preflight source checked 2026-10-22: https://docs.crazygames.com/requirements/technical/. The current uncompressed startup HTML is approximately 1.58 MB. Relative internal links and mouse/keyboard/touch support are included; Chrome/Edge/Safari and physical-device coverage still need final portal/device QA.

## Remaining review

Physical-device performance, human difficulty calibration, name clearance, final platform preflight, submission and platform review remain open. Workload scores are authored geometry proxies, not player evidence. No revenue or competitive superiority claim. Rights notes: `../RIGHTS.md`.
