"""Offline specification checker, not a Cocos game or runtime implementation.

Run: python -B validate_spec.py
Requires jsonschema; only writes validation-report.json beside this file.
"""
from __future__ import annotations
import copy
import hashlib
import importlib.metadata
import json
import platform
from collections import deque
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ACTIONS = ("U", "R", "D", "L", "X")
DELTA = {"U": (0, -1), "R": (1, 0), "D": (0, 1), "L": (-1, 0)}


def load(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def initial(level):
    # l,x,y,bits,pending,next_beacon,used,status
    return (*level["initial"]["position"], level["initial"]["bits"], 0, 0, 0, "PLAYING")


def supported(level, pos, bits):
    l, x, y = pos
    if not (0 <= x < level["width"] and 0 <= y < level["height"]):
        return False
    if level["floors"][l][y][x] != ".":
        return False
    return all(((bits >> g["bit"]) & 1) == g["value"]
               for g in level["gates"] if tuple(g["at"]) == pos)


def step(level, state, action):
    if action not in ACTIONS or state[-1] != "PLAYING":
        return None, "INVALID_ACTION_OR_TERMINAL"
    l, x, y, bits, pending, progress, used, _ = state
    if action == "X":
        if [x, y] not in level["lifts"]:
            return None, "NO_LIFT"
        pos = (1 - l, x, y)
    else:
        dx, dy = DELTA[action]
        pos = (l, x + dx, y + dy)
    if not supported(level, pos, bits):
        return None, "BLOCKED"
    used += 1
    bits ^= pending
    pending = 0
    status, reason = "PLAYING", "OK"
    if not supported(level, pos, bits):
        status, reason = "FAILED", "FLOOR_CLOSED"
    else:
        mask = next((s["mask"] for s in level["switches"] if tuple(s["at"]) == pos), 0)
        if level["variant"] == "X2":
            pending = mask
        else:
            bits ^= mask
        if not supported(level, pos, bits):
            status, reason = "FAILED", "FLOOR_CLOSED"
        else:
            for i, beacon in enumerate(level["beacons"]):
                if tuple(beacon) == pos:
                    if i == progress:
                        progress += 1
                    elif i > progress:
                        status, reason = "FAILED", "BEACON_ORDER"
            target = level["victory"]
            if status == "PLAYING" and (list(pos) == target["position"]
                    and bits == target["bits"] and pending == 0
                    and progress == len(level["beacons"])):
                status, reason = "WON", "GOAL"
    if status == "PLAYING" and used >= level["move_limit"]:
        status, reason = "FAILED", "MOVE_LIMIT"
    return (*pos, bits, pending, progress, used, status), reason


def shortest(level):
    start = initial(level)
    queue = deque([(start, [])])
    seen = {start[:6]}
    while queue:
        state, path = queue.popleft()
        for action in ACTIONS:
            nxt, _ = step(level, state, action)
            if nxt is None or nxt[-1] == "FAILED":
                continue
            route = path + [action]
            if nxt[-1] == "WON":
                return route, len(seen)
            key = nxt[:6]
            if key not in seen:
                seen.add(key)
                queue.append((nxt, route))
    return None, len(seen)


def semantic(level):
    assert level["variant"] == "X1" or not level["beacons"], "beacons require X1"
    n = level["bit_count"]
    limit = 1 << n
    assert level["initial"]["bits"] < limit and level["victory"]["bits"] < limit
    assert len(level["floors"]) == 2
    for layer in level["floors"]:
        assert len(layer) == level["height"]
        assert all(len(row) == level["width"] for row in layer)
    def floor(pos):
        l, x, y = pos
        assert 0 <= l < 2 and 0 <= x < level["width"] and 0 <= y < level["height"]
        assert level["floors"][l][y][x] == "."
    for collection in (level["gates"], level["switches"]):
        positions = [tuple(item["at"]) for item in collection]
        assert len(positions) == len(set(positions)), "duplicate cell entity"
        for item in collection:
            floor(item["at"])
    for gate in level["gates"]:
        assert gate["bit"] < n
    for switch in level["switches"]:
        assert 0 < switch["mask"] < limit
    assert len(level["lifts"]) == len({tuple(p) for p in level["lifts"]})
    for x, y in level["lifts"]:
        floor([0, x, y]); floor([1, x, y])
    assert len(level["beacons"]) == len({tuple(p) for p in level["beacons"]})
    for beacon in level["beacons"]:
        floor(beacon)
    floor(level["initial"]["position"]); floor(level["victory"]["position"])
    assert supported(level, tuple(level["initial"]["position"]), level["initial"]["bits"])
    assert supported(level, tuple(level["victory"]["position"]), level["victory"]["bits"])
    assert all(tuple(s["at"]) != tuple(level["initial"]["position"]) for s in level["switches"])
    assert level["initial"]["position"] not in level["beacons"]
    assert not (level["initial"]["position"] == level["victory"]["position"]
                and level["initial"]["bits"] == level["victory"]["bits"] and not level["beacons"])


def golden_vectors(vectors):
    results = []
    for vector in vectors:
        level = vector["level"]
        semantic(level)
        state = initial(level)
        history = []
        reasons = []
        for action in vector["actions"]:
            if action == "UNDO":
                if state[-1] == "WON":
                    reason = "UNDO_LOCKED"
                else:
                    state = history.pop() if history else state
                    reason = "UNDO"
            elif action == "RESTART":
                state = initial(level); history = []; reason = "RESTART"
            else:
                nxt, reason = step(level, state, action)
                if nxt is not None:
                    history.append(state); state = nxt
            reasons.append(reason)
        assert list(state) == vector["expected_state"], (vector["id"], state)
        assert reasons == vector["expected_reasons"], (vector["id"], reasons)
        # JSON round-trip guards tuple/list serialization drift; runtime save I/O is future work.
        assert json.loads(json.dumps(list(state))) == vector["expected_state"]
        results.append({"id": vector["id"], "passed": True})
    return results


def dag(tasks):
    ids = {t["id"] for t in tasks}
    assert len(ids) == len(tasks)
    order = []
    remaining = {t["id"]: set(t["depends_on"]) for t in tasks}
    assert all(deps <= ids for deps in remaining.values()), "unknown dependency"
    while remaining:
        ready = sorted(key for key, deps in remaining.items() if not deps)
        assert ready, "cyclic task graph"
        for key in ready:
            order.append(key); remaining.pop(key)
        for deps in remaining.values():
            deps.difference_update(ready)
    return order


def campaign_semantic(spec):
    """The frozen campaign must resolve one-to-one to the B0 level records."""
    expected = [f"G04-L{i:02d}" for i in range(1, 21)]
    assert spec["progression"]["campaign_order"] == expected, "campaign order changed"
    assert [level["id"] for level in spec["levels"]] == expected, "campaign IDs/order mismatch"
    assert all(level["variant"] == "B0" for level in spec["levels"]), "experiment in main campaign"
    assert all(not level["beacons"] for level in spec["levels"]), "B0 campaign has experimental beacons"
    assert all(level["variant"] in {"X1", "X2"} for level in spec["experiment_levels"]), "nonexperiment fixture"
    assert not set(expected).intersection(level["id"] for level in spec["experiment_levels"])


def main():
    from jsonschema import Draft202012Validator
    report = {"project_id": "G04", "scope": "OFFLINE_SPEC_DATA_ONLY",
              "generated_at_utc": datetime.now(timezone.utc).isoformat(),
              "environment": {"python": platform.python_version(),
                              "jsonschema": importlib.metadata.version("jsonschema")},
              "engine_build_executed": False, "player_test_executed": False}
    for stem in ("game-spec", "tasks"):
        schema = load(stem + ".schema.json")
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(load(stem + ".json"))
    report["schema_validation"] = {"game-spec": "PASS", "tasks": "PASS"}
    spec = load("game-spec.json")
    campaign_semantic(spec)
    assert len(spec["levels"]) == 20
    all_levels = spec["levels"] + spec["experiment_levels"]
    assert len({l["id"] for l in all_levels}) == len(all_levels)
    report["levels"] = []
    for level in all_levels:
        semantic(level)
        state = initial(level)
        trace = [list(state)]
        for action in level["solution"]:
            nxt, reason = step(level, state, action)
            assert nxt is not None and nxt[-1] != "FAILED", (level["id"], action, reason)
            state = nxt; trace.append(list(state))
        assert state[-1] == "WON", level["id"]
        route, explored = shortest(level)
        assert route is not None and len(route) == level["par"], level["id"]
        assert len(level["solution"]) == level["par"], "documented route not shortest"
        report["levels"].append({"id": level["id"], "variant": level["variant"],
            "solution": level["solution"], "shortest_length": len(route),
            "explored_states": explored, "trace": trace, "passed": True})
    report["golden_vectors"] = golden_vectors(load("qa-vectors.json"))
    report["experiment_controls"] = []
    for experiment in spec["experiment_levels"]:
        control = copy.deepcopy(experiment)
        control["variant"] = "B0"
        control["beacons"] = []
        route, explored = shortest(control)
        expected = {"X1": 5, "X2": 7}[experiment["variant"]]
        assert route is not None and len(route) == expected
        report["experiment_controls"].append({
            "paired_with": experiment["id"], "variant": "B0",
            "only_changes": ["variant", "beacons"], "solution": route,
            "shortest_length": len(route), "explored_states": explored,
            "passed": True})
    report["task_topological_order"] = dag(load("tasks.json")["tasks"])
    from validate_contracts import validate as validate_contracts
    report["contracts"] = validate_contracts(spec, load("tasks.json"))
    # Test that schemas actually reject malformed critical data.
    negative_results = []
    for stem, mutate in [
        ("game-spec", lambda d: d["levels"][0]["solution"].append("TELEPORT")),
        ("game-spec", lambda d: d["levels"][0]["gates"].append({"at": [0, 0, 0], "bit": 0, "value": 2})),
        ("tasks", lambda d: d["tasks"][0].pop("depends_on")),
        ("tasks", lambda d: d["tasks"][0].update({"status": "DONE_WITHOUT_APPROVAL"})),
    ]:
        sample = copy.deepcopy(load(stem + ".json")); mutate(sample)
        assert not Draft202012Validator(load(stem + ".schema.json")).is_valid(sample)
        negative_results.append("REJECTED_AS_EXPECTED")
    report["schema_negative_cases"] = negative_results
    report["campaign_semantic_negative_cases"] = []
    for case, mutate in [
        ("level_id_outside_campaign", lambda d: d["levels"][0].update(id="G04-L99")),
        ("duplicate_campaign_id", lambda d: d["levels"][1].update(id="G04-L01")),
        ("campaign_record_order", lambda d: d["levels"].reverse()),
        ("experiment_variant_in_campaign", lambda d: d["levels"][0].update(variant="X2")),
    ]:
        sample = copy.deepcopy(spec)
        mutate(sample)
        try:
            campaign_semantic(sample)
        except AssertionError:
            report["campaign_semantic_negative_cases"].append({"case": case, "result": "REJECTED_AS_EXPECTED"})
        else:
            raise AssertionError(f"invalid campaign accepted: {case}")
    # Pin all specification sources, not only level data. Generated receipts are excluded.
    generated = {"validation-report.json", "DELIVERY_MANIFEST.json", "archive-verification.json"}
    report["input_sha256"] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                              for p in ROOT.iterdir() if p.is_file() and p.suffix in {".md", ".json", ".py", ".txt"}
                              and p.name not in generated}
    report["result"] = "PASS"
    (ROOT / "validation-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"result": "PASS", "campaign_levels": 20,
                      "experiment_levels": len(spec["experiment_levels"]),
                      "golden_vectors": len(report["golden_vectors"]),
                      "tasks": len(report["task_topological_order"]),
                      "engine_build_executed": False}, ensure_ascii=False))


if __name__ == "__main__":
    main()
