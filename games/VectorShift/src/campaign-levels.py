"""Generate/audit the offline 120-level journey. No runtime procedural levels."""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import statistics

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("dense_generator", ROOT / "src/dense-levels.py")
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)
OUT = ROOT / "data/campaign-levels.json"
REPORT = ROOT / "artifacts/campaign-generation-report.json"
CHAPTERS = [
    ("初见", "First Steps", 6, 6, 4, 10),
    ("回环", "Little Loops", 10, 12, 10, 14),
    ("花径", "Garden Paths", 12, 14, 14, 18),
    ("心弦", "Heartstrings", 14, 16, 18, 22),
    ("织彩", "Woven Colors", 16, 18, 22, 26),
    ("叶语", "Leaf Stories", 18, 22, 26, 30),
    ("交错", "Interwoven", 20, 24, 30, 36),
    ("深庭", "Hidden Courtyards", 22, 26, 36, 42),
    ("流光", "Flowing Light", 24, 28, 42, 48),
    ("万花", "In Full Bloom", 26, 30, 48, 56),
]
SHAPES = ["rounded", "ellipse", "heart", "rounded", "leaf", "ellipse"]


def mask_for(shape, w, h):
    if shape == "ellipse":
        return [(x, y) for y in range(h) for x in range(w)
                if ((x+.5-w/2)/(w/2))**2 + ((y+.5-h/2)/(h/2))**2 <= 1]
    return g.silhouette(shape, w, h)


def canonical(level):
    """Ignore IDs, skins, head orientation, rotation and reflection for uniqueness."""
    forms = []
    for flip in (False, True):
        for rotate in range(4):
            paths = []
            for a in level["arrows"]:
                p = []
                for x, y in a["cells"]:
                    if flip:
                        x = -x
                    for _ in range(rotate):
                        x, y = -y, x
                    p.append((x, y))
                paths.append(p)
            min_x = min(x for p in paths for x, y in p)
            min_y = min(y for p in paths for x, y in p)
            normalized = []
            for p in paths:
                p = tuple((x-min_x, y-min_y) for x, y in p)
                normalized.append(min(p, p[::-1]))
            forms.append(tuple(sorted(normalized)))
    return hashlib.sha256(repr(min(forms)).encode()).hexdigest()


def difficulty(m):
    # Observation/tracing workload proxy, not a player-calibrated difficulty score.
    return round(m["snakeCount"] * 2 + m["dependencyDepth"] * 2.5
                 + m["dependencyEdges"] * .45 + m["turnsTotal"] * .15, 2)


def build_one(ch, slot, attempt):
    zh, en, w, h, lo, hi = CHAPTERS[ch]
    if ch == 0:
        count = [4, 4, 5, 5, 6, 5, 7, 7, 8, 8, 7, 10][slot]
        w = h = 6 + slot // 3
        shape = "rounded"
    else:
        count = round(lo + (hi-lo) * slot / 11)
        if slot in (5, 10):
            count = max(lo, count-2)
        shape = SHAPES[(slot + ch) % len(SHAPES)]
    seed = 410000 + ch * 10000 + slot * 200 + attempt
    mask = mask_for(shape, w, h)
    paths, info = g.search(mask, count, seed, 18000 if ch == 0 else 36000 + ch*2500)
    paths, solution = g.choose_orientation(paths, set(mask), seed)
    paths = g.trim_tails(paths, set(mask), seed, occupancy=.94)
    skins = g.assign_skins(paths, seed)
    number = ch*12 + slot+1
    ids = [f"s{i+1:02d}" for i in range(count)]
    level = {"id": f"journey-{number:03d}", "title": f"{zh} · {slot+1:02d}",
             "titleEn": f"{en} · {slot+1:02d}", "width": w, "height": h, "size": max(w,h),
             "mask": [list(c) for c in mask], "shape": shape, "ruleVersion": 2,
             "mode": "classic", "phaseEnabled": False, "cutBudget": int(number >= 6),
             "chapter": ch+1, "chapterTitle": zh, "chapterTitleEn": en, "number": number,
             "breather": slot in (5,10),
             "arrows": [{"id": ids[i], "cells": [list(c) for c in p], "d": g.direction(p[-2],p[-1]),
                         "skin": skins[i], "color": "gold"} for i,p in enumerate(paths)],
             "solution": [ids[i] for i in solution], "generation": {"version": 1, **info}}
    level["metrics"] = g.audit(level)
    m = level["metrics"]
    g.fail(not m["sameSkinTouchingPairs"], "Adjacent identity colors collide")
    g.fail(m["fillRate"] >= .85, "Sparse mask")
    g.fail(m["dependencyDepth"] >= (2 if ch < 2 else 4), "Missing dependency layers")
    g.fail(m["straightSnakes"] <= (1 if ch == 0 else 0), "Too many straight paths")
    if ch:
        g.fail(m["snakesWith3PlusTurns"] >= count*.65, "Insufficient winding variety")
        g.fail(len([v for v in m["headDirections"].values() if v]) == 4, "Missing head direction")
    level["workloadScore"] = difficulty(m)
    level["canonicalGeometry"] = canonical(level)
    return level


def report(levels):
    chapters = []
    for ch in range(1,11):
        group = [l for l in levels if l["chapter"] == ch]
        chapters.append({"chapter": ch, "levels": len(group),
                         "snakes": [min(len(l["arrows"]) for l in group), max(len(l["arrows"]) for l in group)],
                         "meanWorkload": round(statistics.mean(l["workloadScore"] for l in group),2),
                         "depthRange": [min(l["metrics"]["dependencyDepth"] for l in group),
                                        max(l["metrics"]["dependencyDepth"] for l in group)]})
    g.fail(all(b["meanWorkload"] > a["meanWorkload"] for a,b in zip(chapters,chapters[1:])),
           "Chapter workloads must increase")
    return {"date": "2026-10-22", "levels": len(levels), "uniqueGeometries": len({canonical(l) for l in levels}),
            "snakeTotal": sum(len(l["arrows"]) for l in levels), "chapters": chapters,
            "withoutSkillsSolvable": True, "status": "verified-content; player difficulty calibration pending",
            "limits": "Workload is a geometry/dependency proxy, not player evidence. Breather levels intentionally relax the curve."}


def sequence_chapters(levels):
    # Settle the authored workload rhythm after geometry search. Positions 6/11
    # must actually be easier than their predecessor, not merely carry a flag.
    rhythm = [0, 1, 2, 4, 6, 3, 5, 8, 9, 10, 7, 11]
    result = []
    for ch in range(10):
        group = levels[ch*12:(ch+1)*12]
        if ch:
            group = sorted(group, key=lambda l: (l["workloadScore"],l["generation"]["seed"]))
            group = [group[i] for i in rhythm]
        for slot,l in enumerate(group):
            n = ch*12+slot+1
            l.update(id=f"journey-{n:03d}",number=n,breather=slot in (5,10),
                     title=f"{CHAPTERS[ch][0]} · {slot+1:02d}",
                     titleEn=f"{CHAPTERS[ch][1]} · {slot+1:02d}")
            result.append(l)
    return result


def verify(levels):
    """Release gate: recompute evidence instead of trusting stored summaries."""
    g.fail(len(levels) == 120, "Expected 120 levels")
    for i,l in enumerate(levels):
        g.fail(l["id"] == f"journey-{i+1:03d}" and l["number"] == i+1
               and l["chapter"] == i//12+1, "Sequence mismatch")
        g.fail(l["cutBudget"] == int(i >= 5), "Skill introduction mismatch")
        g.fail(l["breather"] == (i % 12 in (5,10)), "Breather schedule mismatch")
        g.fail(g.audit(l) == l["metrics"], "Stored audit mismatch")
        g.fail(l["workloadScore"] == difficulty(l["metrics"]), "Stored workload mismatch")
        g.fail(canonical(l) == l["canonicalGeometry"], "Canonical geometry mismatch")
        if l["breather"]:
            g.fail(l["workloadScore"] < levels[i-1]["workloadScore"], "Breather must reduce workload")
    summary = report(levels)
    g.fail(summary["uniqueGeometries"] == 120, "Repeated geometry")
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    if args.verify:
        levels = json.loads(OUT.read_text(encoding="utf8"))
    else:
        levels, seen = [], set()
        cache = ROOT / "runtime/campaign-generation-v1"
        cache.mkdir(parents=True, exist_ok=True)
        for ch in range(10):
            for slot in range(12):
                checkpoint = cache / f"{ch*12+slot+1:03d}.json"
                if checkpoint.exists():
                    level = json.loads(checkpoint.read_text(encoding="utf8"))
                else:
                    for attempt in range(40):
                        try:
                            level = build_one(ch, slot, attempt)
                            g.fail(level["canonicalGeometry"] not in seen, "Duplicate geometry")
                            break
                        except ValueError:
                            if attempt == 39:
                                raise
                    checkpoint.write_text(json.dumps(level,ensure_ascii=False),encoding="utf8")
                seen.add(level["canonicalGeometry"])
                levels.append(level)
            print(f"Chapter {ch+1}: 12 original verified boards", flush=True)
        levels = sequence_chapters(levels)
        verify(levels)
        OUT.write_text(json.dumps(levels,ensure_ascii=False,indent=2)+"\n",encoding="utf8",newline="\n")
    summary = verify(levels)
    REPORT.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf8",newline="\n")
    print(json.dumps(summary,ensure_ascii=False),flush=True)


if __name__ == "__main__":
    main()
