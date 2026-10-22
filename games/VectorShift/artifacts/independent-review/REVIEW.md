# Dense app independent review

Reviewed 2026-10-22, using http://127.0.0.1:4173/ and the requested Chromium headless executable through F:/beautiful/node_modules/playwright. Project sources were read only. All reviewer writes are inside this directory. Sources/builds changed concurrently during this review; the exact served/source hashes and mismatch checks are in final-check.json.

## Outstanding findings

### P1: Irregular-exit clipping removes unmoved body segments on the first frame

Location: games/VectorShift/src/dense-app.js:63 (animation clip rectangle).

Reproduction: select pattern 2, the heart; remove s01 to unblock s04, then tap s04's head with motion enabled. s04 faces up at [21,5], exiting at y=4.5. Its tail runs through [20,3], [19,3], [19,4], [20,4]. The up-exit clipping rectangle clips the entire moving body below a horizontal plane at edge.y - 0.45 cells. Thus the top four tail cells disappear immediately, although they have not reached the exit along the snake path. A purple tail section above the head vanishes abruptly rather than following the path.

Evidence: heart-s04-before.png and heart-s04-first-frame.png. RAF was held to capture the initial paint after a real touchscreen tap; the first-frame image is not the completed animation. motion-results.json includes exact cells and screen positions. Similar crossing geometry exists in rectangle s15/s26 and leaf s11/s16. Clip only the extension after it reaches the exit; the original body can be on either side of the exit plane.

### P2: Restore accepts nonfinite counters and time, producing broken result text

Location: games/VectorShift/src/dense-app.js:69 (restore), :17 (time formatting).

Reproduction: preserve a valid runs['dense-01'].state in localStorage key vector-shift-dense-v1, set the same run's elapsed/hints/mistakes to the JSON string "1e309", and open a new page at the same origin. Number("1e309") is Infinity; Math.max(0, Number(value) || 0) does not reject it. Complete the board. The results show time "Infinity:NaN" and hints "Infinity". JSON numeric 1e309 is another accepted input. Fractional hints/mistakes are also retained.

Evidence: nonfinite-win.png, results.json entries nonfinite-stats and nonfinite-win. Require finite nonnegative elapsed and finite nonnegative integer counters separately from the core state validator.

### P2: Right pointer button commits gameplay actions

Location: games/VectorShift/src/dense-app.js:85 (pointerdown), :87 (endPointer).

Reproduction: on a fresh first board, right-click the clear s01 head. Remaining changes 28 -> 27 and moves changes 0 -> 1. Right-clicking a blocked snake likewise adds a mistake. pointerdown/pointerup accepts every mouse button; no e.button filter exists. Tested through Playwright mouse input, not debug.tap.

Evidence: final-check.json rightClick and results.json right-click. Restrict mouse/pen activation to the primary button without disabling multitouch pinch pointers.

### P2: Pinching away from board center loses the point under the fingers

Location: games/VectorShift/src/dense-app.js:86.

Reproduction: at 390x844, begin native two-finger touch at (120,330)/(180,390), move outward to (100,310)/(200,410). The midpoint remains (150,360). Zoom becomes 1.6667, view.x/view.y remain zero, so the board point originally under that midpoint moves to (120,317.83): a roughly 52 CSS px jump under stationary fingers. The code compensates only for midpoint translation; it does not compensate for scaling around an off-center focal point. This interferes with using pinch to inspect a particular dense junction.

Evidence: final-check.json pinch. Events were sent through CDP Input.dispatchTouchEvent. Ordinary panning after zoom works.

### P3: String snake IDs are concatenated into broken accessible labels

Location: games/VectorShift/src/dense-app.js:67.

Reproduction: inspect or Tab into keyboardLayer buttons on pattern 1. Data IDs are s01/s02; id+1 produces labels "第s011条小蛇" / "第s021条小蛇" (English: "Snake s011"). Adding directions in the parallel update does not fix the identifier conversion. Use the array index plus one or present the ID explicitly.

Evidence: motion-results.json keyboard-names. The served page also loses focus to BODY after keyboard activation; latest source now contains a focus-restoration fix, so that older-build observation is not an additional outstanding source finding.

## Earlier landscape observation; recheck after the parallel 44px control changes

### P3: Landscape hint button breaks a short Chinese label and exceeds its grid row

Location: games/VectorShift/src/dense.css:83, in combination with .hint-button padding.

Reproduction: use a 568x320, 667x375 or 844x390 viewport. The fixed 250px controls column leaves the hint button 148px wide, including icons, spark, gaps and 44px horizontal padding. "给点提示" wraps as "给点提" + "示" and the button becomes 66px tall inside a 60px grid row. At 568x320, shell min-height 340 additionally requires vertical scrolling. There is no horizontal overflow at tested widths.

Evidence: layout-568-320.png and results.json layout entries. Prioritize icon/text reflow or compact landscape padding instead of splitting a four-character command.

## Checks that passed and limits

- All five current levels (28/32/28/32/8 pieces, 128 total) cleared with real touchscreen taps, alternating exact body and head targets. Reduced motion was enabled for this full sweep. All counters reached zero and progress reached 100%; each win dialog appeared. Data witness tests had already passed independently.
- Normal pointer/touch release and blocked feedback work; a moved drag does not commit a tap; native pinch changes zoom without removing an arrow; zoomed drag pans.
- Valid partial state, undo history, hints and mistakes survive reload. Undo after reload restores the last piece. A forged core clear with incoherent moves/history is rejected and starts fresh.
- Portrait 320x568, 360x800, 390x844 and 412x915 had no document overflow or inaccessible game controls. Landscape 568x320, 667x375 and 844x390 had no horizontal overflow.
- No pageerror events during the initial interaction sweep. Dialog open/close and completion worked in tested flows.
- Parallel changes added focus restoration, array-container guards for runs/completed, localized ARIA names, and paused timing. A final repeat of final-check.cjs confirmed servedLatestCode=true and keyboard focus moves to s02 after releasing s01. Earlier array-container progress loss is fixed in the latest source and is omitted from outstanding findings.
- Headless Page.setWebLifecycleState did not generate visibilitychange here. Real background/foreground timing and real-device touch/haptics are not verified. Help-dialog dwell is counted by the current timer; no spec was supplied that establishes whether it should pause.

## Pinch -> pan -> fit regression investigated and fixed in parallel

fit-review.cjs reproduces the exact smoke sequence at 390x844 / DPR 2. Before the fix it failed 20/20 times, even after a one-second wait. fit-results.json records pointerdown/up and touchstart/end on zoomButton with no native click; zoom stays 2.2857142857 and pan stays (55,35). Thus this was a lost compatibility click, not an immediate-read race. The parent added delegated touch activation with click deduplication and reports all 13 smoke checks passing, including pinch/pan/fit. Latest source contains this handler. This fixed issue is not in the outstanding findings above; its fix does not address the separate off-center pinch anchoring issue.

Final independent review handoff: outstanding findings are the five items above the earlier-layout section. No additional timing defect is asserted beyond malformed nonfinite persisted statistics; visibility pausing is present in current code but could not be verified through real lifecycle visibility changes in this headless environment. String-ID accessible label concatenation remains present in current code.

## Reproduction artifacts

- review.cjs: viewport sweep, actual taps, persistence, counters, gestures, malformed stats.
- motion-review.cjs: all-five-board touch sweep, first-paint clipping capture, accessible labels, forged save fallback.
- final-check.cjs: served/source revision comparison and final native right-click/pinch observations.
- results.json, motion-results.json, final-check.json: structured observations, including full state where useful.
