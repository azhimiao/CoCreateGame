#!/usr/bin/env python3
"""Original deterministic classic arrow-snake boards (no phase mechanics).

Only writes ../data/dense-levels.json. Python 3.10+, standard library only.
Run: python -B src/dense-levels.py
Audit saved data: python -B src/dense-levels.py --verify

Geometry is generated from analytic silhouettes and seeded path-cover search;
no reference-game coordinates, assets, or puzzles are inputs. Cells are ordered
tail -> head; d is the last edge (0 up, 1 right, 2 down, 3 left). A ray ends at
the outer board boundary, crossing all mask gaps. Removing a legal snake is monotonic. Rendering should move
the body along its ordered path behind the head, never translate the whole body.

Search starts with a row cover, then repeatedly exchanges connected segments
between neighbours and reroutes endpoints. Both endpoint orientations are tested
with a bitset closure after every accepted geometry change. Annealing optimizes
turn variety, lengths and interleaving, not the row cover. Tail trimming leaves
small breathing spaces without changing any head or invalidating the witness.
An independent coordinate-scanning replay and dependency-graph topological sort
audit the serialized result. Visual/interaction quality still needs renderer QA.
"""
from __future__ import annotations

import argparse
from collections import Counter, deque
import hashlib
import itertools
import json
import math
from pathlib import Path
import random
import statistics
import sys

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "dense-levels.json"
VERSION = 2
DIRS = ((0, -1), (1, 0), (0, 1), (-1, 0))


def direction(a, b):
    return DIRS.index((b[0] - a[0], b[1] - a[1]))


def silhouette(shape, w, h):
    cells = []
    for y in range(h):
        for x in range(w):
            if shape == "rounded":
                r = 2.6
                dx = max(r - x - .5, x + .5 - (w - r), 0)
                dy = max(r - y - .5, y + .5 - (h - r), 0)
                inside = dx * dx + dy * dy <= r * r
            elif shape == "heart":
                # Implicit heart, independently sampled at cell centres.
                u = (x + .5 - w / 2) / (w * .43)
                v = (h * .55 - y - .5) / (h * .40)
                inside = (u * u + v * v - 1) ** 3 - u * u * v ** 3 <= 0
            elif shape == "leaf":
                # Lens whose pointed axis runs southwest -> northeast.
                u = (x + .5 - w / 2) / (w * .49)
                v = (y + .5 - h / 2) / (h * .49)
                major = (u - v) / math.sqrt(2)
                minor = (u + v) / math.sqrt(2)
                inside = abs(major) <= 1.24 and abs(minor) <= .70 * (1 - (major / 1.24) ** 2)
            else:
                raise ValueError(shape)
            if inside:
                cells.append((x, y))
    return cells


def initial_cover(mask, count, rng):
    rows = {}
    for x, y in mask:
        rows.setdefault(y, []).append(x)
    paths = []
    for y, xs in sorted(rows.items()):
        run = []
        for x in sorted(xs):
            if run and x != run[-1][0] + 1:
                if len(run) >= 2:
                    paths.append(run)
                run = []
            run.append((x, y))
        if len(run) >= 2:
            paths.append(run)
    while len(paths) < count:
        choices = [i for i, p in enumerate(paths) if len(p) >= 8]
        if not choices:
            raise ValueError("Cannot seed this silhouette with requested count")
        i = max(rng.sample(choices, min(3, len(choices))), key=lambda j: len(paths[j]))
        p = paths[i]
        cut = rng.randint(3, len(p) - 3)
        paths[i] = p[:cut]
        paths.append(p[cut:])
    if len(paths) != count:
        raise ValueError("Too many silhouette row runs")
    return paths


def endpoint_blockers(paths, mask, owner):
    width = max(x for x, y in mask) + 1
    height = max(y for x, y in mask) + 1
    result = []
    for i, p in enumerate(paths):
        options = []
        for head, neck in ((p[0], p[1]), (p[-1], p[-2])):
            dx, dy = head[0] - neck[0], head[1] - neck[1]
            x, y = head[0] + dx, head[1] + dy
            blocked = 0
            while 0 <= x < width and 0 <= y < height:
                j = owner.get((x, y))
                if j is not None:
                    # Reject a head pointing back through its own body too:
                    # stronger than the rule, avoids self-crossing animation.
                    blocked |= 1 << j
                x, y = x + dx, y + dy
            options.append(blocked)
        result.append(options)
    return result


def orientable(paths, mask, owner):
    blockers = endpoint_blockers(paths, mask, owner)
    remaining = (1 << len(paths)) - 1
    order = []
    while remaining:
        progress = False
        for i, (a, b) in enumerate(blockers):
            if not (remaining >> i & 1):
                continue
            if not (a & remaining) or not (b & remaining):
                side = 0 if not (a & remaining) else 1
                order.append((i, side))
                remaining ^= 1 << i
                progress = True
        if not progress:
            return None
    return order


def path_stats(p):
    ds = [direction(a, b) for a, b in zip(p, p[1:])]
    turns = sum(a != b for a, b in zip(ds, ds[1:]))
    runs = []
    for d in ds:
        if runs and runs[-1][0] == d:
            runs[-1][1] += 1
        else:
            runs.append([d, 1])
    # Isolated U hairpins are useful; repeated alternating one-cell corners
    # make a staircase rather than a long rounded snake.
    stairs = sum(runs[k][1] == 1 and runs[k-1][0] == runs[k+1][0]
                 for k in range(1, len(runs) - 1))
    return turns, [r[1] for r in runs], stairs


def path_score(p, target=None):
    n = len(p)
    turns, runs, stairs = path_stats(p)
    score = min(turns, 6) * 3.0 + (5 if turns >= 3 else 0) + (5 if turns >= 5 else 0)
    score -= max(0, 6 - n) ** 2 * 3.5
    score -= max(0, n - 27) ** 2 * .16
    score -= stairs * 2.4
    score -= max(0, turns - n * .53) * 3
    score -= max(0, max(runs) - 8) * .8
    if turns == 0:
        score -= 10
    # A mixture of sweeping runs and tight returns, with readable room in
    # the body; do not reward filling everything with tiny accordion bends.
    score += min(3, sum(r >= 3 for r in runs)) * 1.3
    if target is not None:
        score -= (n - target) ** 2 * .65
        # Long bodies should sweep across several neighbourhoods, not pack
        # all their turns into a little square. Short paths can be compact.
        span = max(x for x, y in p) - min(x for x, y in p)
        span += max(y for x, y in p) - min(y for x, y in p)
        score += min(span, n * .62) * (1.0 if target >= 18 else .15)
    return score


def propose(paths, owner, rng):
    """Two connected cover-preserving moves; no cells created or overlapped."""
    n = len(paths)
    i = rng.randrange(n)
    p = paths[i]
    if rng.random() < .64:
        # Grow one endpoint into a neighbour and give that neighbour's prefix
        # or suffix to this snake. This continuously dissolves row boundaries.
        reverse = rng.randrange(2)
        a = p[::-1] if reverse else p
        x, y = a[-1]
        dx, dy = rng.choice(DIRS)
        cell = x + dx, y + dy
        j = owner.get(cell)
        if j is None or j == i:
            return None
        b = paths[j]
        k = b.index(cell)
        if rng.randrange(2):
            new_a, new_b = a + b[k::-1], b[k+1:]
        else:
            new_a, new_b = a + b[k:], b[:k]
        if len(new_b) < 3 or len(new_a) > 38:
            return None
        return i, new_a, j, new_b
    # Swap the two sides of a unit square occupied by parallel path edges.
    # Reconnect prefixes/suffixes. Keeps count and coverage, adds interlocking
    # U/S shapes spanning the previous snakes' territories.
    k = rng.randrange(len(p) - 1)
    a, b = p[k], p[k+1]
    dx, dy = b[0] - a[0], b[1] - a[1]
    sign = rng.choice((-1, 1))
    ox, oy = -dy * sign, dx * sign
    c, d = (a[0] + ox, a[1] + oy), (b[0] + ox, b[1] + oy)
    j = owner.get(c)
    if j is None or j == i or owner.get(d) != j:
        return None
    q = paths[j]
    l = q.index(c)
    if l + 1 < len(q) and q[l+1] == d:
        new_a = p[:k+1] + q[l::-1]
        new_b = p[:k:-1] + q[l+1:]
    elif l > 0 and q[l-1] == d:
        new_a = p[:k+1] + q[l:]
        new_b = p[:k:-1] + q[:l][::-1]
    else:
        return None
    if min(len(new_a), len(new_b)) < 3 or max(len(new_a), len(new_b)) > 38:
        return None
    return i, new_a, j, new_b


def search(mask_list, count, seed, iterations):
    rng = random.Random(seed)
    mask = set(mask_list)
    paths = initial_cover(mask_list, count, rng)
    owner = {c: i for i, p in enumerate(paths) for c in p}
    roles = [2.35, .65, 1.15, .80, .62, 1.05, 1.20, .68]
    weights = [roles[i % len(roles)] for i in range(count)]
    targets = [max(5.5, t * len(owner) / sum(weights)) for t in weights]
    scores = [path_score(p, targets[i]) for i, p in enumerate(paths)]
    score = sum(scores)
    best, best_score = [p[:] for p in paths], score
    accepted = 0
    for step in range(iterations):
        move = propose(paths, owner, rng)
        if move is None:
            continue
        i, a, j, b = move
        sa, sb = path_score(a, targets[i]), path_score(b, targets[j])
        delta = sa + sb - scores[i] - scores[j]
        temp = 2.8 * (1 - step / iterations) ** 1.4 + .12
        if delta < 0 and rng.random() >= math.exp(delta / temp):
            continue
        old_a, old_b = paths[i], paths[j]
        paths[i], paths[j] = a, b
        for c in a:
            owner[c] = i
        for c in b:
            owner[c] = j
        if orientable(paths, mask, owner) is None:
            paths[i], paths[j] = old_a, old_b
            for c in old_a:
                owner[c] = i
            for c in old_b:
                owner[c] = j
            continue
        scores[i], scores[j] = sa, sb
        score += delta
        accepted += 1
        if score > best_score:
            best, best_score = [p[:] for p in paths], score
    return best, {"seed": seed, "iterations": iterations, "acceptedMutations": accepted,
                  "geometryScore": round(best_score, 3)}


def choose_orientation(paths, mask, seed):
    """Choose a legal orientation/witness with diverse heads and a layered DAG."""
    owner = {c: i for i, p in enumerate(paths) for c in p}
    blockers = endpoint_blockers(paths, mask, owner)
    rng = random.Random(seed ^ 0x5F371)
    best, best_value = None, -float("inf")
    for attempt in range(160):
        remaining = (1 << len(paths)) - 1
        chosen, counts = [], [0] * 4
        while remaining:
            options = []
            for i, options_i in enumerate(blockers):
                if not (remaining >> i & 1):
                    continue
                for side, b in enumerate(options_i):
                    if b & remaining:
                        continue
                    p = paths[i]
                    d = direction(p[1], p[0]) if side == 0 else direction(p[-2], p[-1])
                    # Blockers that have already left become useful dependencies
                    # once the initial board is reconstructed.
                    merit = b.bit_count() * .6 - counts[d] * .65 + rng.random() * 3
                    options.append((merit, i, side, d))
            if not options:
                raise ValueError("Search produced an unorientable cover")
            _, i, side, d = max(options)
            chosen.append((i, side))
            counts[d] += 1
            remaining ^= 1 << i
        oriented = [p[:] for p in paths]
        depth = {}
        initial_open = 0
        edges = 0
        for i, side in chosen:
            if side == 0:
                oriented[i].reverse()
            bits = blockers[i][side]
            ds = [depth[j] for j in depth if bits >> j & 1]
            depth[i] = max(ds, default=0) + 1
            initial_open += not bits
            edges += bits.bit_count()
        value = -sum((c - len(paths) / 4) ** 2 for c in counts) * 1.3
        value += min(12, max(depth.values())) * 2 + min(edges, len(paths) * 2) * .3
        value -= abs(initial_open - max(3, len(paths) // 6)) * 2
        if value > best_value:
            best, best_value = (oriented, [i for i, side in chosen]), value
    return best


def trim_tails(paths, mask, seed, occupancy=.945):
    """Small tail gaps, preserve silhouette boundary and every head/neck."""
    rng = random.Random(seed ^ 0xF17)
    target = round(len(mask) * occupancy)
    paths = [p[:] for p in paths]
    occupied = {c for p in paths for c in p}
    trimmed = set()
    while sum(map(len, paths)) > target:
        choices = []
        for i, p in enumerate(paths):
            if len(p) <= 6 or i in trimmed:
                continue
            x, y = p[0]
            if sum((x+dx, y+dy) in mask for dx, dy in DIRS) < 4:
                continue
            if any((x+dx, y+dy) not in occupied for dx, dy in DIRS):
                continue
            loss = path_score(p) - path_score(p[1:])
            choices.append((loss + rng.random() * 2, i))
        if not choices:
            break
        _, i = min(choices)
        occupied.remove(paths[i][0])
        paths[i] = paths[i][1:]
        trimmed.add(i)
    return paths


def assign_skins(paths, seed):
    """Six identity colours; neighbouring paths prefer different colours."""
    owner = {c: i for i, p in enumerate(paths) for c in p}
    contacts = [Counter() for p in paths]
    for c, i in owner.items():
        for dx, dy in DIRS:
            j = owner.get((c[0] + dx, c[1] + dy))
            if j is not None and j != i:
                contacts[i][j] += 1
    rng = random.Random(seed ^ 0xC010)
    skins, counts = {}, Counter()
    # Contracting each connected, disjoint grid path gives a planar contact
    # graph. Smallest-degree elimination is <=5, so reverse order has a legal
    # colour among six. Adjacency is a hard constraint, balance breaks ties.
    remaining, elimination = set(range(len(paths))), []
    while remaining:
        i = min(remaining, key=lambda j: (len(remaining.intersection(contacts[j])), j))
        elimination.append(i)
        remaining.remove(i)
    for i in reversed(elimination):
        forbidden = {skins[j] for j in contacts[i] if j in skins}
        available = [c for c in range(6) if c not in forbidden]
        fail(available, "Six-colour contact assignment failed")
        skins[i] = min(available, key=lambda c: counts[c] + rng.random() * .5)
        counts[skins[i]] += 1
    return skins


def fail(condition, message):
    if not condition:
        raise ValueError(message)


def audit(level):
    """Independent verifier: coordinates -> DAG -> Kahn, then moving-body replay.

    Does not use search orientation/bitsets, and does not trust stored metrics or
    the supplied solution. Edges point from a blocker to the blocked snake.
    Acyclicity proves ANY sequence of legal removals can finish (no additions,
    rotations or new blockers). All legal choices commute; no exponential BFS.
    """
    w, h = level["width"], level["height"]
    mask = set(map(tuple, level["mask"]))
    arrows = level["arrows"]
    fail(len(mask) == len(level["mask"]), "Duplicate mask cell")
    fail(level["size"] == max(w, h), "size mismatch")
    fail(all(0 <= x < w and 0 <= y < h for x, y in mask), "Mask out of bounds")
    fail(mask, "Empty mask")
    seen, pending = {min(mask)}, [min(mask)]
    while pending:
        x, y = pending.pop()
        for dx, dy in DIRS:
            c = x+dx, y+dy
            if c in mask and c not in seen:
                seen.add(c)
                pending.append(c)
    fail(seen == mask, "Disconnected mask")
    owner, by_id, per_snake = {}, {}, []
    for a in arrows:
        sid = a["id"]
        fail(sid not in by_id, "Duplicate snake ID")
        by_id[sid] = a
        p = list(map(tuple, a["cells"]))
        fail(len(p) >= 2 and len(set(p)) == len(p), "Short/self-overlapping snake")
        fail(a["color"] == "gold" and 0 <= a["skin"] <= 5, "Invalid classic skin/colour")
        for c in p:
            fail(c in mask and c not in owner, "Outside mask/overlapping paths")
            owner[c] = sid
        for a0, b0 in zip(p, p[1:]):
            fail(abs(a0[0]-b0[0]) + abs(a0[1]-b0[1]) == 1, "Non-adjacent body cells")
        fail(a["d"] in range(4) and direction(p[-2], p[-1]) == a["d"], "Head tangent mismatch")
        turns, runs, stairs = path_stats(p)
        per_snake.append({"id": sid, "length": len(p), "turns": turns,
                          "straightRuns": runs, "staircaseCorners": stairs})
    blockers, rays = {}, {}
    for a in arrows:
        sid = a["id"]
        dx, dy = DIRS[a["d"]]
        x, y = a["cells"][-1]
        ray, blocked = [], set()
        while True:
            x, y = x + dx, y + dy
            if not (0 <= x < w and 0 <= y < h):
                break
            ray.append((x, y))
            other = owner.get((x, y))
            fail(other != sid, "Head ray crosses own body")
            if other is not None:
                blocked.add(other)
        blockers[sid], rays[sid] = blocked, ray
    dependents = {sid: [] for sid in by_id}
    for sid, bs in blockers.items():
        for b in sorted(bs):
            dependents[b].append(sid)
    indegree = {sid: len(bs) for sid, bs in blockers.items()}
    ready = deque(sorted(sid for sid, n in indegree.items() if n == 0))
    topological, depth = [], {}
    while ready:
        sid = ready.popleft()
        topological.append(sid)
        depth[sid] = max((depth[b] for b in blockers[sid]), default=0) + 1
        for d in sorted(dependents[sid]):
            indegree[d] -= 1
            if indegree[d] == 0:
                ready.append(d)
    fail(len(topological) == len(arrows), "Cyclic dependency graph / unsolvable")

    solution = level["solution"]
    fail(len(solution) == len(by_id) and set(solution) == set(by_id), "Incomplete witness")
    live, live_owner = set(by_id), dict(owner)
    choice_counts, stages = [], []
    milestones = {0, round(len(arrows)*.25), round(len(arrows)*.5), round(len(arrows)*.75), len(arrows)}
    animation_steps = 0
    for step in range(len(solution) + 1):
        legal = sorted(sid for sid in live
                       if all(live_owner.get(c) in (None, sid) for c in rays[sid]))
        if step in milestones:
            stages.append({"removed": step, "remaining": len(live), "legalIds": legal,
                           "occupiedCells": len(live_owner),
                           "remainingIds": sorted(live)})
        if step == len(solution):
            break
        sid = solution[step]
        fail(sid in legal, f"Illegal witness move {sid} at {step}")
        choice_counts.append(len(legal))
        # Actual body-follow replay: pop tail, add next head cell. Once the
        # head reaches the full rectangular boundary, its continuation is outside.
        # Silhouette gaps are empty space, never teleport exits.
        p = deque(map(tuple, by_id[sid]["cells"]))
        dx, dy = DIRS[by_id[sid]["d"]]
        hx, hy = p[-1]
        exited = False
        for tick in range(len(rays[sid]) + len(p) + 1):
            new_head = hx+dx, hy+dy
            hx, hy = new_head
            if not (0 <= new_head[0] < w and 0 <= new_head[1] < h):
                exited = True
            p.popleft()
            if not exited:
                fail(live_owner.get(new_head) in (None, sid), "Moving head hits another body")
                fail(new_head not in p, "Moving head hits its own body")
            p.append(None if exited else new_head)
            animation_steps += 1
        fail(all(c is None for c in p), "Body did not follow head fully out of mask")
        for c in by_id[sid]["cells"]:
            del live_owner[tuple(c)]
        live.remove(sid)
    fail(not live and not live_owner, "Replay did not empty board")

    # Fixed-seed independent legal-order stress: witness is not a forced order.
    for trial in range(48):
        rng = random.Random(20261022 + trial)
        live = set(by_id)
        while live:
            legal = sorted(s for s in live if not blockers[s].intersection(live))
            fail(legal, "A legal alternative removal order got stuck")
            live.remove(rng.choice(legal))
    lengths = [s["length"] for s in per_snake]
    bends = [s["turns"] for s in per_snake]
    contacts = set()
    for (x, y), sid in owner.items():
        for dx, dy in ((1, 0), (0, 1)):
            other = owner.get((x+dx, y+dy))
            if other is not None and other != sid:
                contacts.add(tuple(sorted((sid, other))))
    same_skin_contacts = [list(pair) for pair in sorted(contacts)
                          if by_id[pair[0]]["skin"] == by_id[pair[1]]["skin"]]
    regions = {}
    crossing = []
    for a in arrows:
        rs = {min(2, y * 3 // h) for x, y in a["cells"]}
        regions[a["id"]] = rs
        if len(rs) > 1:
            crossing.append(a["id"])
    cross_edges = [[b, sid] for sid, bs in blockers.items() for b in sorted(bs)
                   if regions[b] != regions[sid]]
    geometry = {k: level[k] for k in ("width", "height", "mask", "arrows")}
    fingerprint = hashlib.sha256(json.dumps(geometry, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return {
        "maskCells": len(mask), "bodyCells": len(owner), "snakeCount": len(arrows),
        "fillRate": round(len(owner) / len(mask), 6),
        "lengthMin": min(lengths), "lengthMedian": statistics.median(lengths),
        "lengthMean": round(statistics.mean(lengths), 3), "lengthMax": max(lengths),
        "lengthBands": {"short2to8": sum(n <= 8 for n in lengths),
                        "medium9to17": sum(9 <= n <= 17 for n in lengths),
                        "long18plus": sum(n >= 18 for n in lengths)},
        "turnsTotal": sum(bends), "turnsMedian": statistics.median(bends),
        "snakesWith3PlusTurns": sum(t >= 3 for t in bends),
        "snakesWith5PlusTurns": sum(t >= 5 for t in bends),
        "straightSnakes": sum(t == 0 for t in bends),
        "headDirections": {str(d): sum(a["d"] == d for a in arrows) for d in range(4)},
        "skinCounts": {str(s): sum(a["skin"] == s for a in arrows) for s in range(6)},
        "initialChoices": sum(not bs for bs in blockers.values()),
        "dependencyEdges": sum(map(len, blockers.values())), "dependencyDepth": max(depth.values()),
        "dependencyLayers": [[sid for sid in sorted(depth) if depth[sid] == d]
                             for d in range(1, max(depth.values()) + 1)],
        "blockersById": {sid: sorted(bs) for sid, bs in blockers.items()},
        "independentTopologicalSolution": topological,
        "allLegalOrdersSolvable": True, "randomLegalReplays": 48,
        "witnessChoiceCounts": choice_counts, "bodyFollowReplaySteps": animation_steps,
        "releaseStages": stages, "touchingSnakePairs": len(contacts),
        "sameSkinTouchingPairs": same_skin_contacts,
        "thirdBandCrossingIds": crossing, "crossBandDependencyEdges": cross_edges,
        "perSnake": per_snake, "geometrySha256": fingerprint,
    }


CONFIGS = [
    ("dense-01", "织光长庭", "Woven Courtyard", "rounded", 16, 22, 28, 18037),
    ("dense-02", "心间回环", "Heartstrings", "heart", 22, 22, 32, 26189),
    ("dense-03", "叶脉之舞", "Leaf Waltz", "leaf", 22, 22, 28, 41761),
    ("dense-04", "流彩花园", "Ribbon Garden", "rounded", 18, 24, 32, 62743),
    ("dense-05", "初遇回环", "First Loops", "rounded", 8, 8, 8, 10639),
]


def generate(config, iterations):
    lid, title, title_en, shape, w, h, count, seed = config
    mask = silhouette(shape, w, h)
    paths, search_info = search(mask, count, seed, iterations)
    paths, solution = choose_orientation(paths, set(mask), seed)
    paths = trim_tails(paths, set(mask), seed)
    skins = assign_skins(paths, seed)
    ids = [f"s{i+1:02d}" for i in range(count)]
    level = {"id": lid, "title": title, "titleEn": title_en, "ruleVersion": 2,
             "width": w, "height": h, "size": max(w, h),
             "mode": "classic", "phaseEnabled": False, "shape": shape,
             "difficulty": "onboarding" if count <= 8 else "dense",
             "mask": [list(c) for c in mask],
             "arrows": [{"id": ids[i], "color": "gold", "d": direction(p[-2], p[-1]),
                         "cells": [list(c) for c in p], "skin": skins[i]}
                        for i, p in enumerate(paths)],
             "solution": [ids[i] for i in solution]}
    level["metrics"] = audit(level)
    quality_gate(level)
    level["generation"] = {"version": VERSION, "algorithm": "annealed-connected-path-cover",
                           **search_info, "source": "original analytic mask + seeded search",
                           "metricDefinitions": {
                               "fillRate": "occupied cells / playable mask cells; not pixel area",
                               "length": "number of ordered grid cells, including tail and head",
                               "turns": "90-degree direction changes between consecutive grid edges",
                               "dependencyDepth": "number of simultaneous topological removal waves",
                               "thirdBandCrossingIds": "paths spanning horizontal thirds; geometric proxy only",
                               "sameSkinTouchingPairs": "distinct snakes sharing a grid edge and skin",
                           },
                           "qualityStatus": "geometry-verified; renderer-and-player-review-pending"}
    return level


def quality_gate(level):
    """Fail loudly instead of exporting a solved but sparse/striped candidate."""
    m = level["metrics"]
    fail(not m["sameSkinTouchingPairs"], "Adjacent paths must have distinct skins")
    fail(m["straightSnakes"] == 0, "Repeated sticks are not a dense candidate")
    if level["difficulty"] == "onboarding":
        fail(5 <= m["snakeCount"] <= 8, "Onboarding must have 5-8 snakes")
        return
    fail(.85 <= m["fillRate"] <= .96, "Dense occupancy outside 85-96%")
    lo, hi = {"rounded": (26, 34), "heart": (30, 45), "leaf": (26, 40)}[level["shape"]]
    fail(lo <= m["snakeCount"] <= hi, "Snake count outside silhouette target")
    fail(m["lengthMin"] >= 5 and m["lengthMax"] >= 18, "Missing short/long variety")
    fail(m["snakesWith3PlusTurns"] >= 8 and m["snakesWith5PlusTurns"] >= 4,
         "Insufficient winding paths")
    fail(min(m["headDirections"].values()) >= 3, "Insufficient head-direction diversity")
    fail(max(m["headDirections"].values()) <= math.ceil(m["snakeCount"] * .45),
         "Dominant head direction")
    fail(m["dependencyDepth"] >= 4 and m["crossBandDependencyEdges"], "Insufficient layered release")


def summary(level):
    m = level["metrics"]
    return {"id": level["id"], "size": [level["width"], level["height"]],
            "snakes": m["snakeCount"], "occupancy": m["fillRate"],
            "lengths": [m["lengthMin"], m["lengthMedian"], m["lengthMax"]],
            "turns3plus": m["snakesWith3PlusTurns"], "turns5plus": m["snakesWith5PlusTurns"],
            "straight": m["straightSnakes"], "directions": m["headDirections"],
            "initialChoices": m["initialChoices"], "depth": m["dependencyDepth"],
            "edges": m["dependencyEdges"], "score": level["generation"]["geometryScore"]}


def repair_exits(level):
    """Migrate existing authored geometry with the fewest head/tail reversals.

    This preserves the published silhouettes and colours. It also supplies a
    deterministic migration for the v1 first-void rule, separate from new search.
    """
    paths = [list(map(tuple, a["cells"])) for a in level["arrows"]]
    options = endpoint_blockers(paths, set(map(tuple, level["mask"])),
                                {c: i for i, path in enumerate(paths) for c in path})
    def peel(flips):
        alive, witness = (1 << len(paths)) - 1, []
        while alive:
            ready = [i for i in range(len(paths)) if alive >> i & 1
                     and not options[i][0 if i in flips else 1] & alive]
            if not ready:
                return None
            for i in ready:
                alive ^= 1 << i
                witness.append(level["arrows"][i]["id"])
        return witness
    for count in range(5):
        for flips in itertools.combinations(range(len(paths)), count):
            witness = peel(flips)
            if witness is not None:
                for i in flips:
                    a = level["arrows"][i]
                    a["cells"].reverse()
                    a["d"] = direction(a["cells"][-2], a["cells"][-1])
                # Retain legal existing witnesses; only the changed heart needs one.
                if flips:
                    level["solution"] = witness
                    level.setdefault("generation", {})["exitRepair"] = {
                        "ruleVersion": 2, "reversedIds": [level["arrows"][i]["id"] for i in flips],
                        "method": "minimum reversals in ID order; geometry/skin unchanged"}
                level["ruleVersion"] = 2
                level["metrics"] = audit(level)
                quality_gate(level)
                return
    raise ValueError("Existing board needs more than four reversals; author a repair explicitly")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", action="store_true", help="Independently audit saved JSON and stored metrics")
    parser.add_argument("--repair-exits", action="store_true", help="Migrate existing geometry to full-board exit rules")
    parser.add_argument("--iterations", type=int, default=180000)
    parser.add_argument("--only", choices=[c[0] for c in CONFIGS], help="Generate one board to stdout, without writing data")
    args = parser.parse_args()
    if args.repair_exits:
        levels = json.loads(OUTPUT.read_text(encoding="utf-8"))
        for level in levels:
            repair_exits(level)
        OUTPUT.write_text(json.dumps(levels, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        print("Verified and migrated five existing layouts to full-board exits")
        return
    if args.verify:
        levels = json.loads(OUTPUT.read_text(encoding="utf-8"))
        for level in levels:
            measured = audit(level)
            fail(measured == level["metrics"], "Stored metrics differ from independent remeasurement")
            quality_gate(level)
            print(json.dumps(summary(level), ensure_ascii=True), flush=True)
        print(f"Verified {len(levels)} boards, complete witnesses, topology and body-follow replay.")
        return
    if args.iterations <= 0:
        parser.error("--iterations must be positive")
    levels = []
    for config in CONFIGS:
        if args.only and args.only != config[0]:
            continue
        level = generate(config, args.iterations)
        levels.append(level)
        print(json.dumps(summary(level), ensure_ascii=True), file=sys.stderr, flush=True)
    content = json.dumps(levels, ensure_ascii=False, indent=2) + "\n"
    if args.only:
        sys.stdout.reconfigure(encoding="utf-8")
        print(content, end="")
    else:
        OUTPUT.write_text(content, encoding="utf-8", newline="\n")
        print(f"Wrote {len(levels)} original classic boards to {OUTPUT}")


if __name__ == "__main__":
    main()
