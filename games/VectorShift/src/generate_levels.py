#!/usr/bin/env python3
"""Generate solvable phase-arrow puzzles with optional irregular masks.
V7: dense mask pack (≥75% mid) + spatial spread; long tubes + commercial visuals.
Exit rule: stepping off the mask into void = clear (Arrow Out style).
"""
from __future__ import annotations

from collections import deque
import csv
import json
import pathlib
import random

ROOT = pathlib.Path(__file__).resolve().parents[1]
D = [(0, -1), (1, 0), (0, 1), (-1, 0)]
TARGET = 52
GENERATOR_VERSION = 7


def rot_cw(dx: int, dy: int) -> tuple[int, int]:
    return (-dy, dx)


def cells_at_phase(a: dict, phase: int) -> list[list[int]]:
    cells = [[c[0], c[1]] for c in a["cells"]]
    turns = (phase if a["color"] == "blue" else 0) % 4
    if not turns:
        return cells
    hx, hy = cells[-1]
    for _ in range(turns):
        for i in range(len(cells) - 1):
            dx, dy = cells[i][0] - hx, cells[i][1] - hy
            rdx, rdy = rot_cw(dx, dy)
            cells[i] = [hx + rdx, hy + rdy]
    return cells


def mask_set(mask: list[list[int]] | None, size: int) -> set[tuple[int, int]]:
    if mask:
        return {(x, y) for x, y in mask}
    return {(x, y) for y in range(size) for x in range(size)}


def occupancy_ok(arrows: list[dict], size: int, phase: int, playable: set[tuple[int, int]]) -> bool:
    seen: set[tuple[int, int]] = set()
    for a in arrows:
        for x, y in cells_at_phase(a, phase):
            if (x, y) not in playable:
                return False
            key = (x, y)
            if key in seen:
                return False
            seen.add(key)
    return True


def both_phases_ok(arrows: list[dict], size: int, playable: set[tuple[int, int]]) -> bool:
    return occupancy_ok(arrows, size, 0, playable) and occupancy_ok(arrows, size, 1, playable)


def rays(arrows: list[dict], size: int, playable: set[tuple[int, int]]) -> list[list[int]]:
    out = [[0, 0] for _ in arrows]
    for phase in (0, 1):
        owner: dict[tuple[int, int], int] = {}
        for j, a in enumerate(arrows):
            for x, y in cells_at_phase(a, phase):
                owner[(x, y)] = j
        for i, a in enumerate(arrows):
            d = (a["d"] + (phase if a["color"] == "blue" else 0)) % 4
            cells = cells_at_phase(a, phase)
            hx, hy = cells[-1]
            x, y = hx + D[d][0], hy + D[d][1]
            while (x, y) in playable:
                j = owner.get((x, y))
                if j is not None and j != i:
                    out[i][phase] |= 1 << j
                x += D[d][0]
                y += D[d][1]
    return out


def solve(arrows: list[dict], size: int, playable: set[tuple[int, int]], phase_enabled: bool = True):
    n = len(arrows)
    masks = rays(arrows, size, playable)
    initial = ((1 << n) - 1, 0)
    q = deque([initial])
    back = {initial: None}
    actions: dict = {}
    while q:
        mask, phase = q.popleft()
        if mask == 0:
            state = (mask, phase)
            out = []
            while back[state] is not None:
                out.append(actions[state])
                state = back[state]
            return list(reversed(out)), len(back)
        for i in range(n):
            if mask >> i & 1 and not (masks[i][phase] & mask):
                dest = (mask ^ (1 << i), phase)
                if dest not in back:
                    back[dest] = (mask, phase)
                    actions[dest] = i
                    q.append(dest)
        dest = (mask, 1 - phase)
        if phase_enabled and dest not in back:
            back[dest] = (mask, phase)
            actions[dest] = "toggle"
            q.append(dest)
    return None, len(back)


def stats(arrows: list[dict], size: int, playable: set[tuple[int, int]]):
    if not both_phases_ok(arrows, size, playable):
        return None
    path, states = solve(arrows, size, playable)
    if path is None:
        return None
    no, _ = solve(arrows, size, playable, False)
    num_toggle = sum(a == "toggle" for a in path)
    masks = rays(arrows, size, playable)
    mask = (1 << len(arrows)) - 1
    initial_open = sum(not (masks[i][0] & mask) for i in range(len(arrows)))
    blockers = sum(1 for i in range(len(arrows)) if masks[i][0] or masks[i][1])
    body_cells = sum(len(a["cells"]) for a in arrows)
    mcount = len(playable)
    avg_len = body_cells / len(arrows) if arrows else 0
    return {
        "solution": path,
        "minSteps": len(path),
        "minToggles": num_toggle,
        "phaseRequired": no is None,
        "initialChoices": initial_open,
        "exploredStates": states,
        "blockingArrows": blockers,
        "bodyCells": body_cells,
        "maskCells": mcount,
        "fillRate": body_cells / mcount if mcount else 0,
        "avgLen": round(avg_len, 2),
    }


# ---------- shape templates ----------

def square_mask(size: int) -> list[list[int]]:
    return [[x, y] for y in range(size) for x in range(size)]


def plus_mask(size: int) -> list[list[int]]:
    arm = max(1, size // 3)
    mid0 = size // 2 - (arm - 1) // 2
    mid1 = mid0 + arm
    out = []
    for y in range(size):
        for x in range(size):
            if mid0 <= x < mid1 or mid0 <= y < mid1:
                out.append([x, y])
    return out


def diamond_mask(size: int) -> list[list[int]]:
    c = (size - 1) / 2
    r = size // 2
    out = []
    for y in range(size):
        for x in range(size):
            if abs(x - c) + abs(y - c) <= r + 0.01:
                out.append([x, y])
    return out


def heart_mask(size: int) -> list[list[int]]:
    """Discrete heart scaled into size×size bbox."""
    # Unit heart sample then scale
    pts = []
    for y in range(size):
        for x in range(size):
            # Normalize to [-1.2,1.2] x [-1.4,1.0]
            nx = (x + 0.5) / size * 2.4 - 1.2
            ny = -((y + 0.5) / size * 2.4 - 1.2)  # y-down → flip for formula
            # Classic implicit heart: (x^2+y^2-1)^3 - x^2 y^3 <= 0
            a = nx * nx + ny * ny - 1
            if a * a * a - nx * nx * ny * ny * ny <= 0.02:
                pts.append([x, y])
    if len(pts) < size * 2:
        # fallback blob
        return diamond_mask(size)
    return pts


def ring_mask(size: int) -> list[list[int]]:
    c = (size - 1) / 2
    outer = size / 2 - 0.2
    inner = max(0.8, size / 2 - 2.2)
    out = []
    for y in range(size):
        for x in range(size):
            d = ((x - c) ** 2 + (y - c) ** 2) ** 0.5
            if inner < d <= outer + 0.35:
                out.append([x, y])
    return out if len(out) >= size * 2 else plus_mask(size)


def letter_t_mask(size: int) -> list[list[int]]:
    bar = max(2, (size + 1) // 3)
    stem = max(2, size // 3)
    sx = (size - stem) // 2
    out = []
    for y in range(size):
        for x in range(size):
            if y < bar or sx <= x < sx + stem:
                out.append([x, y])
    return out


def letter_c_mask(size: int) -> list[list[int]]:
    """C-like thick arc (ring with right opening)."""
    ring = {(x, y) for x, y in ring_mask(size)}
    c = (size - 1) / 2
    out = []
    for x, y in ring:
        # remove right-side wedge
        if x > c + size * 0.12 and abs(y - c) < size * 0.28:
            continue
        out.append([x, y])
    return out if len(out) >= size * 2 else letter_t_mask(size)


def blob_mask(size: int) -> list[list[int]]:
    """Soft asymmetric blob (letter-like)."""
    c = (size - 1) / 2
    out = []
    for y in range(size):
        for x in range(size):
            # ellipse + dent
            nx = (x - c) / (size * 0.42)
            ny = (y - c) / (size * 0.48)
            if nx * nx + ny * ny <= 1.05 and not (nx > 0.35 and ny < -0.15 and nx * nx + (ny + 0.4) ** 2 < 0.22):
                out.append([x, y])
    return out if len(out) >= size * 2 else diamond_mask(size)


SHAPES = {
    "square": square_mask,
    "plus": plus_mask,
    "diamond": diamond_mask,
    "heart": heart_mask,
    "ring": ring_mask,
    "letter_t": letter_t_mask,
    "letter_c": letter_c_mask,
    "blob": blob_mask,
}


def build_mask(shape: str, size: int) -> list[list[int]]:
    fn = SHAPES.get(shape, square_mask)
    return fn(size)


def region_pressure(cell: tuple[int, int], occupied: set[tuple[int, int]], playable: set[tuple[int, int]]) -> float:
    """Lower = sparser neighborhood — prefer starting snakes here for board-wide spread."""
    x, y = cell
    nearby = 0
    total = 0
    for dy in range(-2, 3):
        for dx in range(-2, 3):
            n = (x + dx, y + dy)
            if n in playable:
                total += 1
                if n in occupied:
                    nearby += 1
    return nearby / total if total else 1.0


def grow_snake(
    playable: set[tuple[int, int]],
    occupied: set[tuple[int, int]],
    rng: random.Random,
    min_len: int,
    max_len: int,
):
    """Grow a winding orthogonal snake; bias toward longer L/U/S paths and sparse regions."""
    free = [p for p in playable if p not in occupied]
    if not free:
        return None
    # Prefer free cells in under-filled neighborhoods so snakes spread across the mask
    free.sort(key=lambda c: (region_pressure(c, occupied, playable), rng.random()))
    # Mix: mostly sparse-first, some random for variety
    head = free[: max(40, len(free) // 2)]
    tail = free[max(40, len(free) // 2) :]
    rng.shuffle(tail)
    ordered = head + tail
    best = None
    for start in ordered[: min(160, len(ordered))]:
        # Bias length upward (commercial boards prefer long tubes)
        span = max(0, max_len - min_len)
        length = min_len + int(rng.random() ** 0.45 * (span + 1))
        length = max(min_len, min(max_len, length))
        cells = [start]
        used = {start}
        prev_dir = None
        ok = True
        for _ in range(length - 1):
            x, y = cells[-1]
            opts = []
            for di, (dx, dy) in enumerate(D):
                nxt = (x + dx, y + dy)
                if nxt in playable and nxt not in occupied and nxt not in used:
                    opts.append((di, nxt))
            if not opts:
                ok = False
                break
            # Prefer turns (~55%) so we get L/U/S instead of straight rods
            turn = [o for o in opts if prev_dir is None or o[0] != prev_dir]
            straight = [o for o in opts if prev_dir is not None and o[0] == prev_dir]
            pool = turn if turn and rng.random() < 0.55 else (straight or turn or opts)
            di, nxt = rng.choice(pool)
            cells.append(nxt)
            used.add(nxt)
            prev_dir = di
        if len(cells) < min_len:
            continue
        if not ok and len(cells) < min_len:
            continue
        # Accept partial if we reached min_len even if short of target
        hx, hy = cells[-1]
        if len(cells) >= 2:
            px, py = cells[-2]
            preferred = None
            for di, (dx, dy) in enumerate(D):
                if (hx - px, hy - py) == (dx, dy):
                    preferred = di
                    break
            d = preferred if preferred is not None and rng.random() < 0.7 else rng.randrange(4)
        else:
            d = rng.randrange(4)
        cand = (cells, d)
        if best is None or len(cells) > len(best[0]):
            best = cand
        # Take first sufficiently long winding snake quickly
        if len(cells) >= min(max_len, min_len + 2) or (len(cells) >= min_len and rng.random() < 0.35):
            return cand
    return best


def largest_empty_blob(playable: set[tuple[int, int]], occupied: set[tuple[int, int]]) -> int:
    free = playable - occupied
    seen: set[tuple[int, int]] = set()
    best = 0
    for start in free:
        if start in seen:
            continue
        stack = [start]
        seen.add(start)
        n = 0
        while stack:
            x, y = stack.pop()
            n += 1
            for dx, dy in D:
                nxt = (x + dx, y + dy)
                if nxt in free and nxt not in seen:
                    seen.add(nxt)
                    stack.append(nxt)
        best = max(best, n)
    return best

def try_pack(playable, min_n, max_n, min_len, max_len, min_fill, blue_bias, rng, size):
    """Pack long snakes first with spatial spread, then fill leftover cells densely."""
    occupied: set[tuple[int, int]] = set()
    arrows = []
    # Aim slightly above min_fill so accept() has headroom
    target_cells = int(len(playable) * min(0.95, min_fill + 0.06))
    hard_max = min(max(max_n, min_n + 4), 20)

    def place_one(lo, hi):
        nonlocal occupied
        grown = grow_snake(playable, occupied, rng, lo, hi)
        if not grown:
            return False
        cells, d = grown
        color = "blue" if rng.random() < blue_bias else "gold"
        candidate = {
            "id": len(arrows),
            "d": d,
            "color": color,
            "cells": [[x, y] for x, y in cells],
        }
        trial = arrows + [candidate]
        if not both_phases_ok(trial, size, playable):
            return False
        for c in cells:
            occupied.add(c)
        arrows.append(candidate)
        return True

    # Phase A: prefer long tubes
    stall = 0
    while len(arrows) < hard_max and (
        sum(len(a["cells"]) for a in arrows) < target_cells or len(arrows) < min_n
    ):
        if place_one(min_len, max_len):
            stall = 0
            continue
        stall += 1
        soft_lo = max(2, min_len - 1 - stall // 4)
        if place_one(soft_lo, max(soft_lo, max_len - 1)):
            stall = 0
            continue
        if stall > 40:
            break

    # Phase B: aggressive gap fill — commercial boards leave almost no voids
    soft_min = max(2, min_len - 2)
    fill_stall = 0
    while len(arrows) < hard_max and sum(len(a["cells"]) for a in arrows) < target_cells:
        if place_one(soft_min, max(soft_min + 1, min_len)):
            fill_stall = 0
            continue
        fill_stall += 1
        if place_one(2, max(3, soft_min)):
            fill_stall = 0
            continue
        if fill_stall > 35:
            break
        break

    # Phase C: keep plugging the largest empty blob until small or can't place
    for _ in range(40):
        if len(arrows) >= hard_max:
            break
        blob = largest_empty_blob(playable, occupied)
        if blob <= max(3, int(len(playable) * 0.10)):
            break
        if place_one(2, max(4, min_len)):
            continue
        if not place_one(2, 3):
            break
    return arrows


def pack_level(
    level_id: int,
    size: int,
    arrows: list[dict],
    playable: set[tuple[int, int]],
    shape: str,
    mask: list[list[int]],
    teaching_zh: str,
    teaching_en: str,
    tag: str,
    source: str,
):
    info = stats(arrows, size, playable)
    assert info is not None, (level_id, shape, "unsolvable")
    out = {
        "id": f"phase-{level_id:02d}",
        "size": size,
        "shape": shape,
        "arrows": arrows,
        "seed": -level_id if source == "editorial" else 20261021,
        "teaching": teaching_zh,
        "teachingEn": teaching_en,
        "tag": tag,
        "source": source,
        "generatorVersion": GENERATOR_VERSION,
        "metrics": {k: v for k, v in info.items() if k != "solution"},
        "solution": info["solution"],
    }
    if shape != "square":
        out["mask"] = mask
    return out


# ---------- teaching 1–8 (square, keep simple / phase intro) ----------
_TEACHING = json.loads(
    '[{"id": "phase-01", "size": 5, "arrows": [{"id": 0, "d": 1, "color": "gold", "cells": [[0, 2], [1, 2]]}, {"id": 1, "d": 1, "color": "gold", "cells": [[2, 2], [3, 2]]}], "teaching": "点击前方畅通的金色箭头，整条箭头会滑出棋盘。", "teachingEn": "Tap a gold arrow with a clear path — the whole snake slides off.", "tag": "clear_path"}, {"id": "phase-02", "size": 5, "arrows": [{"id": 0, "d": 1, "color": "gold", "cells": [[0, 1], [1, 1]]}, {"id": 1, "d": 2, "color": "gold", "cells": [[3, 0], [3, 1]]}, {"id": 2, "d": 2, "color": "gold", "cells": [[3, 2], [3, 3]]}, {"id": 3, "d": 1, "color": "gold", "cells": [[0, 4], [1, 4]]}, {"id": 4, "d": 1, "color": "gold", "cells": [[2, 4], [3, 4]]}], "teaching": "前方有阻挡时，先清走挡住去路的箭头。", "teachingEn": "When something blocks you, clear it first.", "tag": "blocker_order"}, {"id": "phase-03", "size": 5, "arrows": [{"id": 0, "d": 1, "color": "blue", "cells": [[0, 2], [1, 2]]}, {"id": 1, "d": 3, "color": "gold", "cells": [[4, 2], [3, 2]]}, {"id": 2, "d": 2, "color": "blue", "cells": [[1, 3], [0, 3]]}, {"id": 3, "d": 1, "color": "blue", "cells": [[2, 1], [2, 0]]}, {"id": 4, "d": 1, "color": "blue", "cells": [[0, 4], [1, 4]]}], "teaching": "两条箭头互相挡住了！试试切换相位。", "teachingEn": "These two block each other — try Shift Phase.", "tag": "phase_intro"}, {"id": "phase-04", "size": 5, "arrows": [{"id": 0, "d": 1, "color": "blue", "cells": [[0, 1], [1, 1]]}, {"id": 1, "d": 3, "color": "gold", "cells": [[4, 1], [3, 1]]}, {"id": 2, "d": 1, "color": "blue", "cells": [[0, 3], [1, 3]]}, {"id": 3, "d": 1, "color": "gold", "cells": [[4, 3]]}, {"id": 4, "d": 2, "color": "blue", "cells": [[2, 4], [3, 4]]}, {"id": 5, "d": 3, "color": "gold", "cells": [[4, 0], [3, 0]]}, {"id": 6, "d": 1, "color": "blue", "cells": [[1, 0], [0, 0]]}], "teaching": "观察蓝色箭头的身体会怎样跟着相位旋转。", "teachingEn": "Watch how blue arrow bodies rotate with phase.", "tag": "phase_read"}, {"id": "phase-05", "size": 5, "arrows": [{"id": 0, "d": 1, "color": "blue", "cells": [[0, 2], [1, 2]]}, {"id": 1, "d": 2, "color": "gold", "cells": [[3, 0], [3, 1]]}, {"id": 2, "d": 1, "color": "gold", "cells": [[2, 3], [3, 3]]}, {"id": 3, "d": 3, "color": "gold", "cells": [[4, 2]]}, {"id": 4, "d": 0, "color": "gold", "cells": [[4, 1], [4, 0]]}, {"id": 5, "d": 2, "color": "gold", "cells": [[1, 3], [0, 3], [0, 4]]}], "teaching": "先清能走的，再决定何时切换相位。", "teachingEn": "Clear what can leave, then decide when to shift.", "tag": "order_phase"}, {"id": "phase-06", "size": 6, "arrows": [{"id": 0, "d": 3, "color": "blue", "cells": [[0, 2], [1, 2], [1, 1]]}, {"id": 1, "d": 3, "color": "gold", "cells": [[4, 2], [4, 1]]}, {"id": 2, "d": 2, "color": "blue", "cells": [[3, 1], [3, 2], [3, 3]]}, {"id": 3, "d": 1, "color": "blue", "cells": [[1, 4], [2, 4]]}, {"id": 4, "d": 3, "color": "blue", "cells": [[5, 4], [4, 4]]}, {"id": 5, "d": 3, "color": "gold", "cells": [[3, 5], [2, 5], [1, 5]]}, {"id": 6, "d": 0, "color": "blue", "cells": [[5, 1], [5, 0]]}, {"id": 7, "d": 0, "color": "gold", "cells": [[0, 5], [0, 4], [0, 3]]}], "teaching": "金色固定；蓝色跟随相位——一起看身体与方向。", "teachingEn": "Gold stays fixed; blue follows phase — read body and facing.", "tag": "mixed_read"}, {"id": "phase-07", "size": 6, "arrows": [{"id": 0, "d": 3, "color": "blue", "cells": [[2, 0], [2, 1]]}, {"id": 1, "d": 3, "color": "blue", "cells": [[1, 5], [1, 4]]}, {"id": 2, "d": 3, "color": "gold", "cells": [[5, 5], [4, 5]]}, {"id": 3, "d": 1, "color": "blue", "cells": [[1, 2], [1, 1]]}, {"id": 4, "d": 2, "color": "gold", "cells": [[5, 3], [4, 3], [4, 2]]}, {"id": 5, "d": 2, "color": "blue", "cells": [[3, 3], [2, 3], [2, 4]]}, {"id": 6, "d": 2, "color": "blue", "cells": [[3, 1], [3, 2], [2, 2]]}, {"id": 7, "d": 2, "color": "gold", "cells": [[5, 4], [4, 4]]}, {"id": 8, "d": 3, "color": "gold", "cells": [[3, 0], [4, 0]]}], "teaching": "一次相位可能同时打开两条出路。", "teachingEn": "One phase shift can open more than one path.", "tag": "phase_chain"}, {"id": "phase-08", "size": 6, "arrows": [{"id": 0, "d": 2, "color": "gold", "cells": [[0, 2], [1, 2], [1, 3]]}, {"id": 1, "d": 2, "color": "blue", "cells": [[0, 1], [1, 1]]}, {"id": 2, "d": 3, "color": "gold", "cells": [[3, 2], [3, 1], [2, 1]]}, {"id": 3, "d": 0, "color": "blue", "cells": [[4, 1], [4, 0]]}, {"id": 4, "d": 0, "color": "blue", "cells": [[3, 3], [3, 4], [2, 4]]}, {"id": 5, "d": 0, "color": "blue", "cells": [[1, 5], [1, 4]]}, {"id": 6, "d": 3, "color": "blue", "cells": [[5, 3], [4, 3]]}, {"id": 7, "d": 1, "color": "blue", "cells": [[4, 2], [5, 2]]}, {"id": 8, "d": 3, "color": "blue", "cells": [[4, 5], [5, 5]]}], "teaching": "顺序比方向更重要：先想谁挡住了谁。", "teachingEn": "Order beats facing: ask who blocks whom.", "tag": "dependency"}]'
)

levels: list[dict] = []
for _t in _TEACHING:
    size = _t["size"]
    playable = mask_set(None, size)
    info = stats(_t["arrows"], size, playable)
    assert info is not None, _t["id"]
    levels.append(
        {
            "id": _t["id"],
            "size": size,
            "shape": "square",
            "arrows": _t["arrows"],
            "seed": -int(_t["id"].split("-")[1]),
            "teaching": _t["teaching"],
            "teachingEn": _t["teachingEn"],
            "tag": _t["tag"],
            "source": "editorial",
            "generatorVersion": GENERATOR_VERSION,
            "metrics": {k: v for k, v in info.items() if k != "solution"},
            "solution": info["solution"],
        }
    )


# ---------- hand-authored shaped showcases (L9–12) ----------
def make_editorial_shaped(number, size, shape, min_n, max_n, min_fill, zh, en, tag, seed, require_phase=True):
    mask = build_mask(shape, size)
    playable = mask_set(mask, size)
    local = random.Random(seed)
    for attempt in range(50_000):
        arrows = try_pack(playable, min_n, max_n, 4, 8, min_fill, 0.55, local, size)
        if len(arrows) < min_n:
            continue
        colors = {a["color"] for a in arrows}
        if "blue" not in colors or "gold" not in colors:
            continue
        s = stats(arrows, size, playable)
        if not s:
            continue
        if require_phase and not s["phaseRequired"]:
            continue
        if s["initialChoices"] < 1:
            continue
        if s["fillRate"] < min_fill * 0.85:
            continue
        return pack_level(number, size, arrows, playable, shape, mask, zh, en, tag, "editorial")
    raise RuntimeError(f"editorial shaped {number} {shape} failed")

hand_specs = [
    (9, 7, "plus", 3, 5, 0.55, "棋盘变成十字了——滑出剪影边缘也算出界。", "The board is a plus — sliding off the silhouette counts as clear.", "shape_plus", 9001, True),
    (10, 7, "diamond", 3, 5, 0.58, "菱形轮廓：先找朝向缺口的出口。", "Diamond silhouette — look for exits toward the void.", "shape_diamond", 10002, True),
    (11, 7, "heart", 4, 7, 0.68, "心形关：相位仍可用，滑出爱心边缘即可。", "Heart stage — phase still works; exit through the heart edge.", "shape_heart", 11003, True),
    (12, 7, "ring", 4, 7, 0.60, "甜甜圈：滑进中间空洞也算出界。", "Donut board — sliding into the hole also clears.", "shape_ring", 12004, True),
]
hand_levels = [make_editorial_shaped(*spec) for spec in hand_specs]
for hv in hand_levels:
    print("editorial", hv["id"], hv["shape"], f"fill={hv['metrics']['fillRate']*100:.0f}%", "phase", hv["metrics"]["phaseRequired"], "n", len(hv["arrows"]))

# Keep L1–8, append L9–12
levels = levels[:8] + hand_levels
assert [lv["id"] for lv in levels] == [f"phase-{i:02d}" for i in range(1, 13)]

rng = random.Random(20261021)
seen: set[tuple] = set()


def signature(arrows: list[dict]) -> tuple:
    return tuple(
        sorted((a["color"], a["d"], tuple((x, y) for x, y in a["cells"])) for a in arrows)
    )


for lev in levels:
    seen.add(signature(lev["arrows"]))


def shape_for(number: int) -> str:
    """From L10+ bias to non-square; L13+ rotate pool."""
    pool_early = ["plus", "diamond", "heart", "blob"]
    pool_mid = ["heart", "ring", "letter_t", "letter_c", "diamond", "plus"]
    pool_late = ["heart", "ring", "letter_t", "blob", "square", "diamond"]
    if number <= 14:
        return pool_early[(number - 10) % len(pool_early)]
    if number <= 30:
        # ~70% shaped
        if number % 5 == 0:
            return "square"
        return pool_mid[number % len(pool_mid)]
    if number % 4 == 0:
        return "square"
    return pool_late[number % len(pool_late)]




def coverage_ok(arrows: list[dict], playable: set[tuple[int, int]], number: int) -> bool:
    """Reject packs that leave large empty regions (empty top or hollow center)."""
    if number < 15:
        return True
    occupied = {(c[0], c[1]) for a in arrows for c in a["cells"]}
    if not occupied:
        return False
    ys_p = sorted({y for _, y in playable})
    xs_p = sorted({x for x, _ in playable})
    ys_o = [y for _, y in occupied]
    xs_o = [x for x, _ in occupied]
    if max(ys_o) - min(ys_o) < max(1, int((max(ys_p) - min(ys_p)) * 0.85)):
        return False
    if max(xs_o) - min(xs_o) < max(1, int((max(xs_p) - min(xs_p)) * 0.85)):
        return False
    n_rows = len(ys_p)
    top = set(ys_p[: max(1, n_rows // 3)])
    mid = set(ys_p[n_rows // 3 : (2 * n_rows) // 3 + 1])
    bot = set(ys_p[-(max(1, n_rows // 3)) :])
    if not any(y in top for _, y in occupied):
        return False
    if not any(y in mid for _, y in occupied):
        return False
    if not any(y in bot for _, y in occupied):
        return False
    touched_rows = {y for _, y in occupied}
    if len(touched_rows) < max(4, int(n_rows * 0.75)):
        return False
    touched_cols = {x for x, _ in occupied}
    if len(touched_cols) < max(4, int(len(xs_p) * 0.75)):
        return False
    # No large contiguous voids (hollow center looks uncommercial)
    blob = largest_empty_blob(playable, occupied)
    limit = max(3, int(len(playable) * (0.10 if number <= 30 else 0.14)))
    if blob > limit:
        return False
    return True


def band_for(number: int):
    # size, min_n, max_n, min_t, max_t, min_st, max_st, max_init_ratio, min_len, max_len, min_fill
    # Mid boards: dense commercial fill (≥75%) + long tubes spread across mask.
    if number <= 14:
        return 6, 3, 6, 1, 1, 4, 10, 0.85, 3, 6, 0.55
    if number <= 22:
        return 7, 6, 12, 1, 1, 7, 15, 0.85, 4, 9, 0.82
    if number <= 30:
        return 7, 6, 12, 1, 2, 7, 16, 0.8, 4, 10, 0.84
    if number <= 38:
        return 7, 5, 10, 1, 2, 6, 16, 0.7, 4, 10, 0.78
    if number <= 46:
        return 8, 5, 11, 2, 2, 7, 18, 0.65, 5, 12, 0.75
    return 8, 5, 11, 2, 3, 8, 22, 0.6, 5, 12, 0.78


def accept(number, s, n, min_fill, arrows=None, playable=None):
    if not s["phaseRequired"]:
        return False
    size_b, min_n, max_n, min_t, max_t, min_st, max_st, max_init_ratio, min_len, max_len, _mf = band_for(
        number
    )
    if s["minToggles"] < min_t or s["minToggles"] > max_t:
        return False
    if not (min_st <= s["minSteps"] <= max_st):
        return False
    if s["initialChoices"] < 1:
        return False
    if s["initialChoices"] > max(1, int(n * max_init_ratio)):
        return False
    if number >= 14 and s["blockingArrows"] < max(2, n // 4):
        return False
    if number >= 24 and s["exploredStates"] < n * 2:
        return False
    if number >= 40 and s["exploredStates"] < n * 3:
        return False
    if number >= 34 and s["minSteps"] < n:
        return False
    if s["fillRate"] < min_fill:
        return False
    # Mid commercial boards: hard floor — packed like 8Great
    if 15 <= number <= 30 and s["fillRate"] < 0.78:
        return False
    if arrows is not None and playable is not None and not coverage_ok(arrows, playable, number):
        return False
    return True


TAG_BY_BAND = {
    range(13, 15): "shape_intro",
    range(15, 23): "skill_build",
    range(23, 31): "mid_density",
    range(31, 39): "phase_skill",
    range(39, 47): "multi_toggle",
    range(47, 53): "finale",
}


def tag_for(number: int) -> str:
    for r, name in TAG_BY_BAND.items():
        if number in r:
            return name
    return "generated"


teach_zh = {
    "shape_intro": "异形棋盘：出口在剪影边缘。",
    "skill_build": "先规划离开顺序，再动手。",
    "mid_density": "更密了——先找唯一能滑出的箭头。",
    "phase_skill": "可能需要再切一次相位。",
    "multi_toggle": "两次相位切换：想清楚时机。",
    "finale": "终章：异形密盘，优雅多切相位。",
}
teach_en = {
    "shape_intro": "Irregular board — exits are silhouette edges.",
    "skill_build": "Plan the leaving order before you tap.",
    "mid_density": "Denser — find the one free exit first.",
    "phase_skill": "You may need another phase shift.",
    "multi_toggle": "Two phase shifts: time them carefully.",
    "finale": "Finale: dense silhouette, elegant multi-toggle.",
}

for number in range(13, TARGET + 1):
    size_b, min_n, max_n, min_t, max_t, min_st, max_st, max_init_ratio, min_len, max_len, min_fill = band_for(
        number
    )
    size = size_b
    shape = shape_for(number)
    mask = build_mask(shape, size)
    playable = mask_set(mask, size)
    # Tiny masks are unusable
    if len(playable) < 12:
        shape = "diamond"
        mask = build_mask(shape, size)
        playable = mask_set(mask, size)
    attempts = 0
    chosen = None
    blue_bias = 0.55 if number <= 30 else 0.68
    fill_floor = min_fill
    max_attempts = 250_000 if shape != "square" else 400_000
    while attempts < max_attempts:
        attempts += 1
        if attempts == 80_000:
            # Mid dense band: barely soften; late can soften more
            if 15 <= number <= 30:
                fill_floor = max(0.75, min_fill - 0.03)
            else:
                fill_floor = max(0.55, min_fill - 0.06)
        if attempts == 150_000:
            if 15 <= number <= 30:
                fill_floor = max(0.75, min_fill - 0.05)
            else:
                fill_floor = max(0.50, min_fill - 0.10)
        arrows = try_pack(playable, min_n, max_n, min_len, max_len, fill_floor, blue_bias, rng, size)
        if len(arrows) < min_n or len(arrows) > 20:
            continue
        colors = {a["color"] for a in arrows}
        if "blue" not in colors or "gold" not in colors:
            continue
        if not both_phases_ok(arrows, size, playable):
            continue
        sig = signature(arrows)
        if sig in seen:
            continue
        s = stats(arrows, size, playable)
        if not s:
            continue
        ok = accept(number, s, len(arrows), fill_floor, arrows, playable)
        if not ok:
            continue
        chosen = (arrows, s, attempts, sig, shape, mask, playable)
        break
    if not chosen:
        # Last-resort: square with soft fill
        shape = "square"
        mask = build_mask(shape, size)
        playable = mask_set(mask, size)
        fill_floor = max(0.40, min_fill - 0.15)
        while attempts < max_attempts + 200_000:
            attempts += 1
            arrows = try_pack(playable, min_n, max_n, min_len, max_len, fill_floor, blue_bias, rng, size)
            if len(arrows) < min_n:
                continue
            colors = {a["color"] for a in arrows}
            if "blue" not in colors or "gold" not in colors:
                continue
            sig = signature(arrows)
            if sig in seen:
                continue
            s = stats(arrows, size, playable)
            if not s or not accept(number, s, len(arrows), fill_floor, arrows, playable):
                continue
            chosen = (arrows, s, attempts, sig, shape, mask, playable)
            break
    if not chosen:
        raise RuntimeError(f"failed generating level {number}")
    a, s, tries, sig, shape, mask, playable = chosen
    seen.add(sig)
    tag = tag_for(number)
    levels.append(
        pack_level(
            number,
            size,
            a,
            playable,
            shape,
            mask,
            teach_zh.get(tag, ""),
            teach_en.get(tag, ""),
            tag,
            "generated+solver_verified",
        )
    )
    levels[-1]["generationAttempt"] = tries
    levels[-1]["seed"] = 20261021
    print(
        number,
        shape,
        "n",
        len(a),
        "mask",
        s["maskCells"],
        f"fill={s['fillRate']*100:.0f}%",
        "steps",
        s["minSteps"],
        "toggles",
        s["minToggles"],
        "attempts",
        tries,
        flush=True,
    )

# Verify solutions
for lev in levels:
    playable = mask_set(lev.get("mask"), lev["size"])
    n = len(lev["arrows"])
    mask_bits = (1 << n) - 1
    phase = 0
    r = rays(lev["arrows"], lev["size"], playable)
    for act in lev["solution"]:
        if act == "toggle":
            phase = 1 - phase
            continue
        assert mask_bits >> act & 1 and not (r[act][phase] & mask_bits), lev["id"]
        mask_bits ^= 1 << act
    assert mask_bits == 0, lev["id"]
    assert solve(lev["arrows"], lev["size"], playable)[0] == lev["solution"], lev["id"]
    assert both_phases_ok(lev["arrows"], lev["size"], playable), lev["id"]

assert len(levels) == TARGET
phase_early = [lv for i, lv in enumerate(levels) if i >= 2 and i < 8]
assert all(lv["metrics"]["phaseRequired"] for lv in phase_early)
late = levels[38:]
assert all(lv["metrics"]["minToggles"] >= 2 for lv in late)
steps = [lv["metrics"]["minSteps"] for lv in levels]
first = sorted(steps[:17])[8]
last = sorted(steps[-17:])[8]
assert last >= first, (first, last)

shaped = [lv for lv in levels if lv.get("shape", "square") != "square"]
from_10 = levels[9:]  # L10+
shaped_from_10 = [lv for lv in from_10 if lv.get("shape", "square") != "square"]
ratio = len(shaped_from_10) / len(from_10)
print(f"shaped total {len(shaped)} / {len(levels)}; L10+ shaped {len(shaped_from_10)}/{len(from_10)} = {ratio*100:.0f}%")
assert ratio >= 0.40, ratio

(ROOT / "data/levels.json").write_text(json.dumps(levels, ensure_ascii=False, indent=2), encoding="utf-8")

audit_path = ROOT / "data/level_audit.csv"
with audit_path.open("w", encoding="utf-8", newline="") as f:
    w = csv.writer(f)
    w.writerow(
        [
            "level",
            "size",
            "shape",
            "arrows",
            "body_cells",
            "mask_cells",
            "fill_pct",
            "minimum_actions",
            "minimum_phase_toggles",
            "phase_required",
            "initial_legal_choices",
            "bfs_explored_states",
            "blocking_arrows",
            "tag",
            "source",
        ]
    )
    for lv in levels:
        m = lv["metrics"]
        w.writerow(
            [
                lv["id"],
                lv["size"],
                lv.get("shape", "square"),
                len(lv["arrows"]),
                m.get("bodyCells", ""),
                m.get("maskCells", ""),
                round(m.get("fillRate", 0) * 100, 1),
                m["minSteps"],
                m["minToggles"],
                m["phaseRequired"],
                m["initialChoices"],
                m["exploredStates"],
                m.get("blockingArrows", ""),
                lv.get("tag", ""),
                lv["source"],
            ]
        )

print("Saved", len(levels), "levels; step curve first/last median", first, last)
fills = [lv["metrics"]["fillRate"] for lv in levels]
print(
    "fill L1/L20/L52:",
    f"{levels[0]['metrics']['fillRate']*100:.0f}%",
    f"{levels[19]['metrics']['fillRate']*100:.0f}%",
    f"{levels[51]['metrics']['fillRate']*100:.0f}%",
)
print("shapes:", sorted({lv.get("shape", "square") for lv in levels}))
for idx in (19, 37):
    lv = levels[idx]
    lens = [len(a["cells"]) for a in lv["arrows"]]
    print(f"avgLen L{idx+1}: {sum(lens)/len(lens):.2f} lens={sorted(lens)}")
mid = []
for lv in levels[12:]:
    mid.extend(len(a["cells"]) for a in lv["arrows"])
print(f"avgLen L13+: {sum(mid)/len(mid):.2f} max={max(mid)}")
