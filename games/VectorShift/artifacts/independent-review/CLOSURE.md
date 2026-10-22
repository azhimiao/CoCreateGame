# Targeted closure verification

All five previously outstanding findings are CLOSED in the rebuilt app served at http://127.0.0.1:4173/. Served JavaScript matched the source during this run (source SHA-256 34a25e3afccb9a838597fe059bdd23dfcb93f130f5c5a0cc2871c0ba7c34f6b6; served HTML SHA-256 16b436fd9830a04910f982f42d3cd7347b6807c2fb65e8c4bee606f41c50c814).

- Exit clipping: after legal prerequisite removals, real touch removed heart s01 and then s04. At animation time zero, all four formerly clipped tail cells retained alpha 255 and effectively identical RGB. Initial, intermediate, and final frames were inspected; original body remains intact initially and retracts along its path. No global-plane disappearance remains.
- Off-center pinch: native CDP touches around stationary midpoint (150,360) produced zoom 1.6667, pan (30,39.1667), and measured focal drift 0 CSS pixels. No arrow was removed. A subsequent pan and single Fit tap restored {zoom:1,x:0,y:0}, remaining stable after 400ms, with no delayed duplicate activation.
- Invalid statistics: overflow strings "1e309", huge/negative values, and fractional counters were tested. Invalid values normalize to zero; 2.9/3.7 counters normalize to 2/3. Completing the overflow-seeded board through native touches produced finite normal time and zero hints, with no NaN/Infinity.
- Mouse buttons: actual right-click on a clear head leaves moves=0.
- Accessible labels: actual DOM labels are "第1条小蛇，朝右" and "Snake 1, facing right".

Correction to the earlier reproduction shorthand: current heart s01 is blocked by s09/s11, while s04 is initially clear. This verification legally cleared s01 prerequisites while retaining s04, then removed s01 followed by s04. The old report's claim that s01 directly unblocks s04 was incorrect; the clipping observation itself was valid.

No project source edits. No pageerror events during this targeted pass. Landscape fixes are outside this closure rerun; no new five-stage sweep was performed. These results close the five specific review findings and do not assert broader release or real-device validation.

Evidence: closure-results.json, closure-check.cjs, closed-heart-before.png, closed-heart-first-frame.png, closed-heart-frame-0.18.png, closed-heart-frame-0.5.png, closed-normalized-stats-win.png.
