"""Offline specification verifier. No renderer, engine, network, or game build.

State is (bottom-to-top stacks, sealed colour per tray). Locks are derived.
Run from any directory: python tools/verify.py --all
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.metadata
import inspect
import json
import platform
import sys
import traceback
from collections import Counter, deque
from pathlib import Path
from check_contracts import protocol_checks, layout_checks, release_gate_checks

ROOT = Path(__file__).resolve().parents[1]


def read(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def initial(level):
    return (tuple(tuple(t["items"]) for t in level["containers"]),
            tuple("" for _ in level["containers"]))


def unlocked(level, state, index):
    return set(level["containers"][index]["unlock_after"]) <= set(state[1])


def actions(level, state):
    stacks, sealed = state
    trays = level["containers"]
    # Explicit seal first, then source/destination ascending. No auto-clear.
    for i, stack in enumerate(stacks):
        if sealed[i] or not unlocked(level, state, i) or not stack:
            continue
        if (trays[i]["sealable"] and len(set(stack)) == 1
                and len(stack) == level["demand"][stack[0]]):
            yield {"op": "seal", "at": trays[i]["id"]}
    for i, stack in enumerate(stacks):
        if sealed[i] or not unlocked(level, state, i) or not stack:
            continue
        colour = stack[-1]
        for j, target in enumerate(stacks):
            if (i == j or sealed[j] or not unlocked(level, state, j)
                    or len(target) >= trays[j]["capacity"]
                    or colour not in trays[j]["accepts"]
                    or (target and target[-1] != colour)):
                continue
            yield {"op": "move", "src": trays[i]["id"], "dst": trays[j]["id"]}


def step(level, state, action):
    if action not in list(actions(level, state)):
        raise ValueError(f"illegal action: {action}; state={state}")
    stacks, sealed = [list(s) for s in state[0]], list(state[1])
    ids = [t["id"] for t in level["containers"]]
    if action["op"] == "seal":
        i = ids.index(action["at"])
        sealed[i] = stacks[i][0]
        stacks[i] = []
    else:
        i, j = ids.index(action["src"]), ids.index(action["dst"])
        stacks[j].append(stacks[i].pop())
    return tuple(tuple(s) for s in stacks), tuple(sealed)


def won(level, state):
    return not any(state[0]) and Counter(c for c in state[1] if c) == Counter(level["win"]["sealed_colours"])


def invariant(level, state):
    stacks, sealed = state
    actual = Counter(c for s in stacks for c in s)
    for i, c in enumerate(sealed):
        assert len(stacks[i]) <= level["containers"][i]["capacity"]
        assert set(stacks[i]) <= set(level["containers"][i]["accepts"])
        if c:
            assert not stacks[i]
            actual[c] += level["demand"][c]
    assert actual == Counter(level["demand"]), (actual, level["demand"])


def solve(level, limit=300000):
    start = initial(level)
    queue, previous = deque([start]), {start: None}
    while queue:
        state = queue.popleft()
        if won(level, state):
            result = []
            while previous[state] is not None:
                state, action = previous[state]
                result.append(action)
            return list(reversed(result)), len(previous)
        for action in actions(level, state):
            nxt = step(level, state, action)
            if nxt not in previous:
                previous[nxt] = (state, action)
                queue.append(nxt)
                if len(previous) > limit:
                    raise RuntimeError("SEARCH_LIMIT_UNKNOWN: no unsolvability claim")
    return None, len(previous)


def structural(level):
    trays = level["containers"]
    assert len({t["id"] for t in trays}) == len(trays)
    assert set(level["demand"]) == set(level["win"]["sealed_colours"])
    assert level["win"]["all_items_removed"] is True
    assert set(level["demand"]) <= set("ABCD")
    for t in trays:
        assert len(t["items"]) <= t["capacity"]
        assert set(t["items"]) <= set(t["accepts"])
        assert set(t["accepts"]) <= set(level["demand"])
        assert set(t["unlock_after"]) <= set(level["demand"])
    if level["variant"] in ("V0", "X2"):
        assert all(not t["unlock_after"] for t in trays)
    if level["variant"] in ("V0", "X1"):
        assert all(set(t["accepts"]) == set(level["demand"]) for t in trays)
    invariant(level, initial(level))


def validate_schemas(spec, tasks):
    from jsonschema import Draft202012Validator, FormatChecker
    for name, data in [("game-spec", spec), ("tasks", tasks)]:
        schema = read(f"{name}.schema.json")
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema, format_checker=FormatChecker()).validate(data)
    return 2


def task_order(tasks):
    entries = tasks["tasks"]
    by_id = {t["id"]: t for t in entries}
    assert len(by_id) == len(entries)
    for t in entries:
        assert set(t["depends_on"]) <= by_id.keys()
        assert t["id"] not in t["depends_on"]
        for p in t["outputs"]:
            assert p.startswith("games/G02/") and ".." not in p
    pending, done = set(by_id), []
    while pending:
        ready = sorted(k for k in pending if set(by_id[k]["depends_on"]) <= set(done))
        assert ready, "DAG cycle"
        done.extend(ready)
        pending.difference_update(ready)
    paths = [p for t in entries for p in t["outputs"]]
    assert len(paths) == len(set(paths)), "tasks must own distinct outputs"
    assert all(t["status"] != "DONE" for t in entries if t["phase"] == "build")
    return done


def rule_vectors():
    def level(stacks, capacity=2, locks=None, accepts=None, sealable=None):
        colours = sorted(set("".join(stacks)))
        return {"demand": dict(Counter("".join(stacks))),
                "win": {"sealed_colours": colours, "all_items_removed": True},
                "containers": [{"id": f"T{i}", "capacity": capacity,
                    "items": list(s), "accepts": (accepts or {}).get(i, colours),
                    "unlock_after": (locks or {}).get(i, []),
                    "sealable": (sealable or {}).get(i, True)} for i, s in enumerate(stacks)]}
    def move(i, j):
        return {"op": "move", "src": f"T{i}", "dst": f"T{j}"}
    def first_failed_move_predicate(board, state, src, dst):
        # Preparation-only diagnostics in the documented error priority order.
        ids = [t["id"] for t in board["containers"]]
        if src not in ids or dst not in ids:
            return "BAD_ID"
        i,j = ids.index(src),ids.index(dst)
        stacks,sealed = state
        tests = [("SAME_CONTAINER",i!=j),("SOURCE_SEALED",not sealed[i]),
            ("SOURCE_LOCKED",unlocked(board,state,i)),("EMPTY_SOURCE",bool(stacks[i])),
            ("TARGET_SEALED",not sealed[j]),("TARGET_LOCKED",unlocked(board,state,j)),
            ("TARGET_FULL",len(stacks[j])<board["containers"][j]["capacity"])]
        for reason,passed in tests:
            if not passed:
                return reason
        colour = stacks[i][-1]
        if colour not in board["containers"][j]["accepts"]:
            return "FILTER_MISMATCH"
        if stacks[j] and stacks[j][-1] != colour:
            return "TOP_MISMATCH"
        return "OK"
    checks = []
    def check(name, value):
        assert value, name
        checks.append(name)
    l = level(["AB", "BA", ""])
    s = initial(l)
    # Source top B, destination A with ONE FREE SLOT, accepts B, both open.
    # Unlike AB/BA this rejects solely because of the same-top guard.
    isolated = level(["B", "A", "AB"])
    si = initial(isolated)
    invariant(isolated, si)
    original = copy.deepcopy(si)
    check("same_top_spare_capacity_rejected", move(0, 1) not in list(actions(isolated, si)))
    check("same_top_single_cause_reason", first_failed_move_predicate(isolated,si,"T0","T1")=="TOP_MISMATCH")
    try:
        step(isolated, si, move(0, 1))
    except ValueError:
        pass
    else:
        raise AssertionError("same_top_spare_capacity_must_reject")
    check("same_top_rejection_preserves_all_state", si == original)
    # A full matching A target isolates capacity; no top/filter/lock ambiguity.
    full = level(["A", "AA", ""])
    check("full_matching_target_rejected", move(0, 1) not in list(actions(full, initial(full))))
    check("full_matching_single_cause_reason",first_failed_move_predicate(full,initial(full),"T0","T1")=="TARGET_FULL")
    check("full_before_top_error_priority",first_failed_move_predicate(l,s,"T0","T1")=="TARGET_FULL")
    check("same_container_rejected", move(0, 0) not in list(actions(l, s)))
    check("empty_source_rejected", move(2, 0) not in list(actions(l, s)))
    s1 = step(l, s, move(0, 2))
    check("single_top_only", s1[0] == (("A",), ("B", "A"), ("B",)))
    check("full_target_rejected", move(2, 1) not in list(actions(l, s1)))
    check("input_does_not_mutate", s == initial(l))
    l2 = level(["AA", "BB", ""], locks={1: ["A"]})
    a2 = list(actions(l2, initial(l2)))
    check("locked_seal_and_source_rejected", all(a.get("at") != "T1" and a.get("src") != "T1" for a in a2))
    after = step(l2, initial(l2), {"op": "seal", "at": "T0"})
    check("seal_removes_items", after[0][0] == () and after[1][0] == "A")
    check("seal_unlocks_atomically", unlocked(l2, after, 1))
    check("sealed_tray_unusable", all(a.get("src") != "T0" and a.get("dst") != "T0" for a in actions(l2, after)))
    end = step(l2, after, {"op": "seal", "at": "T1"})
    check("win_only_after_seal", won(l2, end) and not won(l2, initial(l2)))
    # Actually commit seal, serialize a snapshot, then undo into a NEW state.
    before_snapshot = {"logical":initial(l2),"logical_action_count":7}
    committed = {"logical":after,"logical_action_count":8,"revision":22,
                 "history":[before_snapshot]}
    restored_store = json.loads(json.dumps(committed))
    snapshot = restored_store["history"].pop()
    restored = (tuple(tuple(x) for x in snapshot["logical"][0]),tuple(snapshot["logical"][1]))
    restored_store.update(logical=restored,logical_action_count=snapshot["logical_action_count"],revision=restored_store["revision"]+1)
    check("snapshot_undo_exact_after_serialization", restored_store["logical"] == initial(l2)
          and restored_store["logical_action_count"] == 7 and restored_store["revision"] == 23
          and not restored_store["history"])
    check("undo_seal_restores_items_and_seals", restored[0][0] == ("A","A") and restored[1][0] == "")
    check("undo_seal_relocks_after_actual_restore", unlocked(l2, after, 1) and not unlocked(l2, restored, 1))
    invariant(l2, restored)
    lf = level(["AB", "BA", ""], accepts={2: ["A"]})
    check("filter_rejects_empty_wrong_colour", move(0, 2) not in list(actions(lf, initial(lf))))
    lb = level(["AA", ""], sealable={0: False})
    check("buffer_cannot_seal", {"op": "seal", "at": "T0"} not in list(actions(lb, initial(lb))))
    dead = level(["AB", "BA"])
    check("zero_actions_deadlock", not list(actions(dead, initial(dead))))
    check("deadlock_exhaustive_unsolvable", solve(dead)[0] is None)
    perm = copy.deepcopy(l)
    perm["containers"][0]["items"] = ["B", "A"]
    check("top_order_changes_state", initial(perm) != s)
    check("json_round_trip", json.loads(json.dumps({"stacks": s1[0], "sealed": s1[1]}))["stacks"] == [list(x) for x in s1[0]])
    # Abstract selection protocol only: no engine input or UI has been built.
    def tap(selected, target, legal):
        if selected == target or target is None:
            return None, "cancel"
        if selected is not None:
            return (None, "move") if legal else (selected, "reject")
        return target, "select"
    check("selected_other_illegal_preserves_source", tap("T0", "T1", False) == ("T0", "reject"))
    check("selected_other_legal_moves_clears", tap("T0", "T2", True) == (None, "move"))
    check("selected_locked_preserves_source", tap("T0", "T3", False) == ("T0", "reject"))
    check("same_source_cancels_before_reselection", tap("T0", "T0", False) == (None, "cancel"))
    check("outside_cancels", tap("T0", None, False) == (None, "cancel"))
    # Execute the actual actions function with only its same-top clause deleted.
    # The dedicated fixture must then fail; no full-board/BFS confounder.
    source = inspect.getsource(actions).replace("def actions(", "def mutated_actions(")
    needle = "or (target and target[-1] != colour)"
    assert needle in source
    source = source.replace(needle, "or False")
    namespace = {}
    exec(compile(source,"<offline-same-top-mutation>","exec"),globals(),namespace)
    check("same_top_single_guard_mutation_detected", move(0,1) in list(namespace["mutated_actions"](isolated, si)))
    return checks


def revision_metadata_checks(spec):
    index = read("revision-index.json")
    assert index["project_state"] == spec["state"] == "REVISION_REQUIRED"
    assert index["independent_review"] == spec["independent_review"] == "PENDING_RE_REVIEW"
    assert index["ready_for_build"] is spec["ready_for_build"] is False
    assert [f["id"] for f in index["findings"]] == ["B-G02-01","M-G02-01","M-G02-02","N-G02-01","N-G02-02","N-G02-03"]
    for finding in index["findings"]:
        assert finding["independent_closed"] is False
        assert finding["author_resolution"] == "FIXED_PENDING_INDEPENDENT_CONFIRMATION"
        assert all((ROOT/name).is_file() for name in finding["files"])
    for name in ("README.md","STATUS.md","HANDOFF_STATE.md","00_Project_Charter.md"):
        assert "REVISION_REQUIRED" in (ROOT/name).read_text(encoding="utf-8")[:600], name
    evidence = read(spec["research_observation"]["team_supplement"])
    assert evidence["overall_status"] == "BLOCKED_CORE_BEHAVIOR"
    assert evidence["confirmed_effective_core_inputs"] == 0 and evidence["site_ui_inputs"] == 3
    assert len(evidence["screenshots"]) == 13
    assert evidence["continuous_first_30_seconds"] == evidence["continuous_first_5_minutes"] == "UNKNOWN_NOT_RECORDED"
    assert all(g["confirmed_effective_core_inputs"] == 0 for g in evidence["game_results"])
    return {"six_author_fixes_indexed":True,"independent_closure":"PENDING_RE_REVIEW",
        "entry_states_consistent":True,"team_browser_core_evidence":"BLOCKED_CORE_BEHAVIOR",
        "screenshot_hashes":"13 checked at incorporation; shared originals not required by portable ZIP verifier"}


def verify():
    spec, tasks = read("game-spec.json"), read("tasks.json")
    schema_count = validate_schemas(spec, tasks)
    assert spec["project_id"] == tasks["project_id"] == "G02"
    assert spec["ready_for_build"] is False
    assert spec["candidate_platform_ids"] == ["P02", "P04", "P05", "P06"]
    levels = spec["levels"]
    assert [l["id"] for l in levels] == [f"L{i:02d}" for i in range(1, 21)]
    assert len({json.dumps(l["containers"], sort_keys=True) for l in levels}) == 20
    level_results = []
    for l in levels:
        structural(l)
        state, hashes = initial(l), []
        for action in l["solution"]:
            state = step(l, state, action)
            invariant(l, state)
            hashes.append(hashlib.sha256(json.dumps(state, separators=(",", ":")).encode()).hexdigest())
        assert won(l, state), l["id"]
        shortest, visited = solve(l)
        assert shortest is not None and len(shortest) == len(l["solution"]), l["id"]
        assert l["par_actions"] == len(shortest)
        optional = l["feature_coverage"]["optional_container_ids"]
        if optional:
            assert l["id"] in ("L09","L13")
            removed = copy.deepcopy(l)
            removed["containers"] = [t for t in removed["containers"] if t["id"] not in optional]
            reduced = initial(removed)
            for action in l["solution"]:
                assert not (set(action.values()) & set(optional))
                reduced = step(removed,reduced,action)
                invariant(removed,reduced)
            assert won(removed,reduced)
        level_results.append({"level_id": l["id"], "variant": l["variant"],
            "solution_actions": len(l["solution"]), "bfs_shortest_actions": len(shortest),
            "bfs_discovered_states": visited, "replay_state_sha256": hashes,
            "win": True, "conservation": True,"optional_containers":optional,
            "optional_removal_preserves_published_solution":bool(optional)})
    # Ablation checks on the same states; enabling/removing features changes legal options.
    ablations = []
    for variant in ("X1", "X2"):
        candidates = [l for l in levels if l["variant"] == variant]
        changed = 0
        for l in candidates:
            baseline = copy.deepcopy(l)
            for t in baseline["containers"]:
                t["unlock_after"] = []
                t["accepts"] = list(l["demand"])
            if list(actions(l, initial(l))) != list(actions(baseline, initial(baseline))):
                changed += 1
            assert solve(baseline)[0] is not None
        assert changed > 0
        ablations.append({"variant": variant, "independent_toggle": True,
                          "boards_with_changed_initial_legal_actions": changed,
                          "baseline_solvable": True})
    return {"overall_status": "PASS", "scope": "OFFLINE_SPEC_ONLY_NOT_ENGINE_OR_PLAYER_VALIDATION", "date": "2026-10-21",
        "input_sha256": {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in
                         ["game-spec.json", "tasks.json", "game-spec.schema.json", "tasks.schema.json", "tools/verify.py",
                          "tools/check_contracts.py","protocol-vectors.json","layout-cases.json",
                          "revision-index.json","evidence/team-browser-observation-index.json",
                          "STATUS.md","REVISIONS.md"]},
        "python": platform.python_version(), "jsonschema": importlib.metadata.version("jsonschema"),
        "schemas_validated": schema_count, "dag_topological_order": task_order(tasks),
        "rule_vectors_passed": rule_vectors(), "levels": level_results, "ablations": ablations,
        "protocol_vectors":protocol_checks(),"static_layout_cases":layout_checks(spec),
        "release_branch_checks":release_gate_checks(tasks),
        "revision_metadata_checks":revision_metadata_checks(spec),
        "engine_build": "NOT_RUN", "device_performance": "UNKNOWN", "independent_audit": "PENDING_RE_REVIEW"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--all", action="store_true", help="validate schemas, rules, levels, DAG")
    parser.add_argument("--report", default="verification/verification-report.json")
    args = parser.parse_args()
    dest = (ROOT / args.report).resolve()
    assert dest.is_relative_to(ROOT), "all output must stay in G02"
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        result = verify()
    except Exception as error:
        result = {"overall_status": "FAIL", "scope": "OFFLINE_SPEC_ONLY", "error_type": type(error).__name__,
                  "message": str(error), "python_executable": sys.executable, "traceback": traceback.format_exc()}
        dest.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"FAIL: {type(error).__name__}: {error}", flush=True)
        print(f"Report: {dest}", flush=True)
        print(result["traceback"], flush=True)
        sys.exit(1)
    dest.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"PASS: {len(result['levels'])}/20 solutions + BFS; 2 schemas; "
          f"{len(result['rule_vectors_passed'])} rule vectors; DAG {len(result['dag_topological_order'])} nodes; "
          f"{len(result['protocol_vectors'])} protocol tables; {len(result['static_layout_cases'])} static layout cases")
    print(f"Report: {dest}")
