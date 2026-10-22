# Static benchmark alignment evidence

Observed 2026-10-22 using existing supplied screenshots. These images document a gap, not an accepted replacement product.

- `same-width-comparison.png`: visible puzzle bodies normalized to 360px width with original aspect ratios.
- `*-crop.png`: source-resolution crops; no stretching or repainting.
- `*-annotated.png`: manual head coordinates and straight-body sample cuts from `docs/benchmark-measurements.json`. The 8Great reference has 26 annotated paired-eye heads; the current L20 has 8.
- `measurements.json`: source SHA-256 fingerprints, crop dimensions, sample widths, and normalization results.

Reproduce with `python src/build_benchmark_alignment.py` from the game directory. Requires Pillow and a CJK font. Source screenshots remain unchanged in `artifacts/competitors/`; their rights belong to their respective owners. They are references only and are not included in the playable game.

Measurements include visible body edges and exclude detached cast shadows, heads, and bends. Anti-aliased edge selection has about +/-2 source pixels of uncertainty. This is manually sampled static evidence, not inferred logical fill rate, clickable area, true difficulty, animation, audio, haptics, or live-build verification. The differently proportioned boards are not controlled-area difficulty experiments.
