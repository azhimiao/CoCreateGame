"""Independent specification audit; all inputs/outputs stay under reviews/.

This is a bounded data model checker, not game source or a product runtime.
Run from repository root: python -X utf8 -B reviews/audit_g04.py
"""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import platform
import sys
from collections import Counter, deque
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from pathlib import Path

from jsonschema import Draft202012Validator

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "G04-baseline"
OUTPUT = ROOT / "G04-checks"
ACTIONS = "URDLX"
VECTORS = {"U": (0, -1), "R": (1, 0), "D": (0, 1), "L": (-1, 0)}


def read(name):
    return json.loads((INPUT / name).read_text(encoding="utf-8-sig"))


@dataclass(frozen=True)
class Node:
    pos: tuple[int, int, int]
    bits: int
    pending: int = 0
    beacon: int = 0
    used: int = 0
    status: str = "PLAYING"
    failure: str | None = None

    def trace(self):
        return [*self.pos, self.bits, self.pending, self.beacon, self.used, self.status]

    def key(self):
        return self.pos, self.bits, self.pending, self.beacon


class Model:
    def __init__(self, level):
        self.level = level
        self.terrain = {
            (layer, x, y)
            for layer, rows in enumerate(level["floors"])
            for y, row in enumerate(rows)
            for x, char in enumerate(row)
            if char == "."
        }
        self.gates = {tuple(g["at"]): (g["bit"], g["value"]) for g in level["gates"]}
        self.switches = {tuple(s["at"]): s["mask"] for s in level["switches"]}
        self.lifts = set(map(tuple, level["lifts"]))
        self.beacons = {tuple(pos): index for index, pos in enumerate(level["beacons"])}

    def initial(self):
        return Node(tuple(self.level["initial"]["position"]), self.level["initial"]["bits"])

    def support(self, pos, bits):
        if pos not in self.terrain:
            return False
        if pos not in self.gates:
            return True
        bit, value = self.gates[pos]
        return bool(bits & (1 << bit)) == bool(value)

    def transition(self, before, command):
        if before.status != "PLAYING" or command not in ACTIONS or len(command) != 1:
            return False, before, "INVALID_ACTION_OR_TERMINAL"
        layer, x, y = before.pos
        if command == "X":
            if (x, y) not in self.lifts:
                return False, before, "NO_LIFT"
            destination = (1 - layer, x, y)
        else:
            dx, dy = VECTORS[command]
            destination = (layer, x + dx, y + dy)
        if not self.support(destination, before.bits):
            return False, before, "BLOCKED"
        after = replace(before, pos=destination, used=before.used + 1,
                        bits=before.bits ^ before.pending, pending=0)
        if not self.support(after.pos, after.bits):
            return True, replace(after, status="FAILED", failure="FLOOR_CLOSED"), "FLOOR_CLOSED"
        mask = self.switches.get(after.pos, 0)
        after = (replace(after, pending=mask) if self.level["variant"] == "X2"
                 else replace(after, bits=after.bits ^ mask))
        if not self.support(after.pos, after.bits):
            return True, replace(after, status="FAILED", failure="FLOOR_CLOSED"), "FLOOR_CLOSED"
        if self.level["variant"] == "X1" and after.pos in self.beacons:
            index = self.beacons[after.pos]
            if index > after.beacon:
                return True, replace(after, status="FAILED", failure="BEACON_ORDER"), "BEACON_ORDER"
            if index == after.beacon:
                after = replace(after, beacon=after.beacon + 1)
        target = self.level["victory"]
        if (after.pos == tuple(target["position"]) and after.bits == target["bits"]
                and after.pending == 0 and after.beacon == len(self.beacons)):
            return True, replace(after, status="WON"), "GOAL"
        if after.used == self.level["move_limit"]:
            return True, replace(after, status="FAILED", failure="MOVE_LIMIT"), "MOVE_LIMIT"
        return True, after, "OK"

    def route(self, commands):
        state, states, reasons = self.initial(), [self.initial().trace()], []
        for command in commands:
            accepted, state, reason = self.transition(state, command)
            assert accepted and state.status != "FAILED", (self.level["id"], command, reason)
            states.append(state.trace())
            reasons.append(reason)
        return state, states, reasons

    def search(self):
        # Includes used in the visited state: an independent bounded graph,
        # rather than assuming the author's reduced BFS key is sound.
        initial = self.initial()
        todo = deque([(initial, "")])
        seen = {initial}
        shortest, goals, failures, transitions, undoable = None, [], Counter(), 0, 0
        while todo:
            state, path = todo.popleft()
            for action in ACTIONS:
                accepted, nxt, reason = self.transition(state, action)
                transitions += 1
                if not accepted:
                    assert nxt == state
                    continue
                assert nxt.used == state.used + 1
                if nxt.status != "WON":
                    undoable += 1  # restoring the pre-action snapshot is an exact inverse
                if nxt.status == "FAILED":
                    failures[reason] += 1
                if nxt.status == "WON":
                    if shortest is None:
                        shortest = path + action
                    goals.append(nxt.used)
                if nxt not in seen:
                    seen.add(nxt)
                    todo.append((nxt, path + action))
        return {"shortest": shortest, "reachable_full_states": len(seen),
                "transition_count": transitions, "goal_lengths": sorted(set(goals)),
                "failure_edges": dict(failures), "undoable_edges": undoable}, seen


def golden(vector):
    model = Model(vector["level"])
    state, stack, reasons = model.initial(), [], []
    for command in vector["actions"]:
        if command == "UNDO":
            if state.status == "WON":
                reasons.append("UNDO_LOCKED")
            else:
                state = stack.pop() if stack else state
                reasons.append("UNDO")
        elif command == "RESTART":
            state, stack = model.initial(), []
            reasons.append("RESTART")
        else:
            accepted, nxt, reason = model.transition(state, command)
            if accepted:
                stack.append(state)
            state = nxt
            reasons.append(reason)
    assert state.trace() == vector["expected_state"], (vector["id"], state.trace())
    assert reasons == vector["expected_reasons"], (vector["id"], reasons)
    return {"id": vector["id"], "passed": True}


def topological(tasks):
    incoming = {t["id"]: set(t["depends_on"]) for t in tasks}
    assert len(incoming) == len(tasks)
    assert all(d <= incoming.keys() for d in incoming.values())
    order = []
    while incoming:
        ready = sorted(k for k, deps in incoming.items() if not deps)
        assert ready, "cycle"
        for k in ready:
            order.append(k)
            del incoming[k]
        for deps in incoming.values():
            deps.difference_update(ready)
    return order


def main():
    OUTPUT.mkdir(exist_ok=True)
    spec, tasks, original = read("game-spec.json"), read("tasks.json"), read("validation-report.json")
    report = {"project_id": "G04", "scope": "INDEPENDENT_OFFLINE_SPEC_AUDIT",
              "generated_at_utc": datetime.now(timezone.utc).isoformat(),
              "python": platform.python_version(), "engine_build_executed": False,
              "player_test_executed": False}
    report["author_input_hash_matches"] = {
        name: hashlib.sha256((INPUT / name).read_bytes()).hexdigest() == digest
        for name, digest in original["input_sha256"].items()}
    assert all(report["author_input_hash_matches"].values())
    schemas = {}
    for stem, document in (("game-spec", spec), ("tasks", tasks)):
        schemas[stem] = Draft202012Validator(read(stem + ".schema.json"))
        Draft202012Validator.check_schema(schemas[stem].schema)
        schemas[stem].validate(document)
    report["schemas"] = "PASS"
    loader = importlib.util.spec_from_file_location("author_g04_frozen", INPUT / "validate_spec.py")
    author = importlib.util.module_from_spec(loader)
    loader.loader.exec_module(author)
    levels = spec["levels"] + spec["experiment_levels"]
    assert len(spec["levels"]) == 20 and len(levels) == len({l["id"] for l in levels}) == 22
    assert spec["progression"]["campaign_order"] == [l["id"] for l in spec["levels"]]
    report["levels"] = []
    differential_count = 0
    author_reports = {r["id"]: r for r in original["levels"]}
    for level in levels:
        model = Model(level)
        assert model.support(model.initial().pos, model.initial().bits)
        final, trace, reasons = model.route(level["solution"])
        assert final.status == "WON"
        result, reachable = model.search()
        assert len(result["shortest"]) == level["par"] == len(level["solution"])
        assert trace == author_reports[level["id"]]["trace"]
        assert level["par"] <= level["move_limit"] <= 128
        for state in reachable:
            for command in (*ACTIONS, "WAIT"):
                accepted, nxt, reason = model.transition(state, command)
                their_next, their_reason = author.step(level, tuple(state.trace()), command)
                assert reason == their_reason
                assert (their_next is not None) == accepted
                assert list(their_next) == nxt.trace() if accepted else nxt == state
                differential_count += 1
        report["levels"].append({"id": level["id"], "par": level["par"],
                                 "move_limit": level["move_limit"],
                                 "witness": "".join(level["solution"]), "trace": trace,
                                 "trace_matches_author_report": True, **result})
    report["differential_transitions"] = differential_count
    report["golden_vectors"] = [golden(v) for v in read("qa-vectors.json")]
    report["experiment_controls"] = []
    for level in spec["experiment_levels"]:
        control = copy.deepcopy(level)
        control["variant"], control["beacons"] = "B0", []
        result, _ = Model(control).search()
        assert len(result["shortest"]) == {"X1": 5, "X2": 7}[level["variant"]]
        report["experiment_controls"].append({"id": level["id"], **result})
    report["task_order"] = topological(tasks["tasks"])
    ancestors = {}
    lookup = {t["id"]: t for t in tasks["tasks"]}
    for tid in report["task_order"]:
        ancestors[tid] = set(lookup[tid]["depends_on"])
        for dependency in lookup[tid]["depends_on"]:
            ancestors[tid].update(ancestors[dependency])
    assert all("G04-T01" in ancestors[t] for t in lookup if t not in {"G04-T00", "G04-T01"})
    report["all_build_tasks_after_human_gate"] = True
    # Fault injection against the real author validation path. In-memory inputs
    # and a separate output directory ensure no author documents are mutated.
    cases = {
        "campaign_unknown_id": lambda d: d["progression"]["campaign_order"].__setitem__(0, "G04-L99"),
        "campaign_duplicate_id": lambda d: d["progression"]["campaign_order"].__setitem__(1, "G04-L01"),
        "campaign_wrong_order": lambda d: d["progression"]["campaign_order"].reverse(),
        "nonliteral_rule_order": lambda d: d["rules"]["arrival_order"].reverse(),
        "level_id_outside_campaign": lambda d: d["levels"][0].update(id="G04-L99"),
        "campaign_contains_experiment_variant": lambda d: d["levels"][0].update(variant="X2"),
        "switch_mask_out_of_bit_range": lambda d: d["levels"][0]["switches"][0].update(mask=3),
        "duplicate_switch_position": lambda d: d["levels"][0]["switches"].append(copy.deepcopy(d["levels"][0]["switches"][0])),
    }
    report["mutation_probes"] = []
    for name, mutate in cases.items():
        changed = copy.deepcopy(spec)
        mutate(changed)
        test_output = OUTPUT / name
        test_output.mkdir(exist_ok=True)
        (test_output / "game-spec.json").write_text(json.dumps(changed, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        documents = {"game-spec.json": changed}
        author.ROOT = test_output
        author.load = lambda n, documents=documents: copy.deepcopy(documents[n]) if n in documents else read(n)
        try:
            author.main()
        except Exception as exc:
            outcome = {"author_checker": "REJECTED", "error": type(exc).__name__, "detail": str(exc)}
        else:
            outcome = {"author_checker": "PASS", "accepted_invalid_document": True}
        report["mutation_probes"].append({"id": name,
            "schema_accepts": schemas["game-spec"].is_valid(changed), **outcome})
    # Independent diagnostics for repeated puzzles / teaching bypass, not edits.
    report["ablation"] = []
    for level in spec["levels"]:
        without = copy.deepcopy(level)
        without["gates"] = []
        result, _ = Model(without).search()
        report["ablation"].append({"id": level["id"], "original_par": level["par"],
                                   "no_gates_shortest": result["shortest"]})
    report["result"] = "LOGIC_PASS_WITH_REVIEW_FINDINGS"
    (OUTPUT / "independent-results.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"result": report["result"], "levels": len(levels),
                      "golden_vectors": len(report["golden_vectors"]),
                      "differential_transitions": differential_count,
                      "tasks": len(report["task_order"]),
                      "mutation_probes": [{k: v for k, v in probe.items() if k != "detail"}
                                          for probe in report["mutation_probes"]]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
