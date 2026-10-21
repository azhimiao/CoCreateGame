"""Offline audit probes: injected rule verdicts, integer toy state, static rectangles.

NOT a runnable game, persistence adapter, input handler, engine or SDK integration.
Protocol tables assert externally authored expected outcomes; real rules live only
in verify.py's independent board verifier. Rendering/performance remain NOT_RUN.
"""
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


class Probe:
    def __init__(self):
        self.run, self.epoch, self.high = "R1", "E1", 0
        self.cache, self.history = {}, []
        self.logical = self.count = self.revision = self.ordinal = 0
        self.events = self.saves = 0  # atomic publication/write requests, not SDK events
        self.status = "PLAY"
        self.replay = []
        self.checkpoint = self.snapshot()
        self.first = None

    def snapshot(self):
        return copy.deepcopy({"logical":self.logical,"count":self.count,"revision":self.revision,
                              "history":self.history,"ordinal":self.ordinal})

    @staticmethod
    def effect(s, op):
        s = copy.deepcopy(s)
        if op == "undo":
            old = s["history"].pop()
            s["logical"], s["count"] = old
        else:
            s["history"].append([s["logical"], s["count"]])
            s["history"] = s["history"][-128:]
            s["logical"] += 1
            s["count"] += 1
        s["revision"] += 1
        return s

    def dispatch(self, cmd, verdict):
        before = self.snapshot()
        def transport(reason):
            assert self.snapshot() == before
            return {"reason":reason, "cached":False}
        args = {"move":{"src","dst"},"seal":{"at"},"undo":set()}.get(cmd.get("op"),set())
        if (set(cmd) != {"run_id","command_epoch","command_seq","expected_revision","op"}|args
                or any(not isinstance(cmd[k],str) or not cmd[k] for k in {"run_id","command_epoch","op"}|args)
                or type(cmd["command_seq"]) is not int or not 1 <= cmd["command_seq"] <= 9007199254740991
                or type(cmd["expected_revision"]) is not int or not 0 <= cmd["expected_revision"] <= 9007199254740991
                or cmd["op"] not in ("move","seal","undo")):
            return transport("BAD_ENVELOPE")
        if cmd["run_id"] != self.run:
            return transport("STALE_RUN")
        if cmd["command_epoch"] != self.epoch:
            return transport("STALE_EPOCH")
        n, payload = cmd["command_seq"], canonical(cmd)
        if n in self.cache:
            old_payload, receipt = self.cache[n]
            if old_payload != payload:
                return transport("ID_CONFLICT")
            return {"reason":receipt["reason"], "cached":True,"receipt":copy.deepcopy(receipt)}
        if n <= self.high:
            return transport("STALE_COMMAND")
        if n != self.high + 1:
            return transport("SEQUENCE_GAP")
        self.high = n  # every first in-order decision consumes exactly one sequence
        if self.status == "ANIMATING":
            reason = "BUSY"
        elif self.status != "PLAY" and not (self.status == "DEADLOCK" and cmd["op"] == "undo"):
            reason = "NOT_PLAYING"
        elif cmd["expected_revision"] != self.revision:
            reason = "STALE_REVISION"
        elif cmd["op"] == "undo" and not self.history:
            reason = "EMPTY_HISTORY"
        else:
            reason = "OK" if verdict in ("ACCEPT","ACCEPT_WIN") else verdict
        accepted = reason == "OK"
        # Capture endpoint BEFORE first record beyond the 4096-record tail.
        if len(self.replay) == 4096:
            self.checkpoint = self.snapshot()
            self.replay = []
        if accepted:
            nxt = self.effect(self.snapshot(), cmd["op"])
            self.logical, self.count, self.revision, self.history = (nxt[k] for k in ("logical","count","revision","history"))
            self.saves += 1
            if verdict == "ACCEPT_WIN":
                self.status = "WIN"
        self.events += 1  # one injected fixture event batch on each first decision
        self.ordinal += 1
        receipt = {"accepted":accepted,"reason":reason,"revision_before":before["revision"],
            "revision_after":self.revision,"logical_action_count_after":self.count,
            "state_hash_after":hashlib.sha256(canonical([self.logical,self.count]).encode()).hexdigest(),
            "event_ids":[f"probe:{self.events}"]}
        self.cache[n] = payload, copy.deepcopy(receipt)
        self.cache = {k:v for k,v in self.cache.items() if k >= max(1,self.high-127)}
        self.replay.append({"ordinal":self.ordinal,"op":cmd["op"],"accepted":accepted,
                            "before_revision":before["revision"],"after_revision":self.revision})
        if self.first is None:
            self.first = copy.deepcopy(receipt)
        return {"reason":reason,"cached":False,"receipt":receipt}

    def restore(self, epoch):
        assert epoch and epoch != self.epoch
        # Simulate an actual JSON serialization/reparse before rebuilding probe state.
        payload = json.loads(canonical({"snapshot":self.snapshot(),"checkpoint":self.checkpoint,"replay":self.replay}))
        saved = payload["snapshot"]
        self.logical,self.count,self.revision,self.history,self.ordinal = (saved[k] for k in ("logical","count","revision","history","ordinal"))
        self.checkpoint, self.replay = payload["checkpoint"], payload["replay"]
        self.epoch, self.high, self.cache, self.status = epoch, 0, {}, "PLAY"

    def replay_matches(self):
        restored = copy.deepcopy(self.checkpoint)
        for record in self.replay:
            assert record["before_revision"] == restored["revision"]
            if record["accepted"]:
                restored = self.effect(restored,record["op"])
            restored["ordinal"] = record["ordinal"]
            assert record["after_revision"] == restored["revision"]
        return restored == self.snapshot()

    def observed(self):
        return {"high":self.high,"floor":max(1,self.high-127),"cache_size":len(self.cache),
            "revision":self.revision,"logical":self.logical,"history":len(self.history),
            "events":self.events,"saves":self.saves,"replay_size":len(self.replay),
            "checkpoint_ordinal":self.checkpoint["ordinal"]}


def protocol_checks():
    tables = json.loads((ROOT/"protocol-vectors.json").read_text(encoding="utf-8"))
    results = []
    for case in tables["cases"]:
        p, decisions, assertions = Probe(), 0, 0
        for index, step in enumerate(case["steps"]):
            action, outcome = step["action"], {}
            if action == "dispatch":
                stable_before = canonical([p.snapshot(),p.observed(),p.cache,p.replay,p.status])
                outcome = p.dispatch(step["command"],step["fixture_rule_verdict"])
                if outcome.get("cached") or "receipt" not in outcome:
                    assert stable_before == canonical([p.snapshot(),p.observed(),p.cache,p.replay,p.status]), (case["id"],index,"retry/transport side effect")
                decisions += 1
            elif action == "fill":
                for seq in range(step["start"],step["end"]+1):
                    reject = step["mode"] == "reject"
                    cmd = {"run_id":"R1","command_epoch":p.epoch,"command_seq":seq,
                        "expected_revision":p.revision,"op":"undo" if step["mode"]=="undo" else "move"}
                    if cmd["op"] == "move":
                        cmd.update(src="T0",dst="T2")
                    out = p.dispatch(cmd,"TOP_MISMATCH" if reject else "ACCEPT")
                    assert out["reason"] == ("TOP_MISMATCH" if reject else "OK"), case["id"]
                    decisions += 1
            elif action == "status":
                p.status = step["value"]
            elif action == "restore":
                before = p.snapshot()
                p.restore(step["new_epoch"])
                assert before == p.snapshot(), "restore must preserve full undo state and monotonic revision"
            elif action == "callback":
                before = p.snapshot(),p.events,p.saves,p.high
                outcome["ignored"] = step["epoch"] != p.epoch
                assert outcome["ignored"] and before == (p.snapshot(),p.events,p.saves,p.high)
            elif action == "replay_checkpoint":
                outcome["replay_matches"] = p.replay_matches()
            else:
                assert action == "assert"
            observed = {**p.observed(),**outcome}
            if "receipt" in outcome:
                observed["receipt_revision"] = outcome["receipt"]["revision_after"]
            for key, value in step.get("expect",{}).items():
                if key == "receipt_equals":
                    assert value == "first" and outcome["receipt"] == p.first, (case["id"],index,key)
                else:
                    assert observed.get(key) == value, (case["id"],index,key,value,observed)
                assertions += 1
            # Duplicate deliveries and transport rejects must change nothing but delivery metadata.
            assert p.revision >= 0 and len(p.cache) <= 128 and len(p.history) <= 128
        assert p.replay_matches(), case["id"]
        results.append({"case":case["id"],"dispatches":decisions,"expected_assertions":assertions,"status":"PASS"})
    return results


def intersects(a,b):
    return max(a[0],b[0]) < min(a[0]+a[2],b[0]+b[2]) and max(a[1],b[1]) < min(a[1]+a[3],b[1]+b[3])


def layout_checks(spec):
    c = spec["ui"]["layout_contract"]
    cases = json.loads((ROOT/c["fixtures"]).read_text(encoding="utf-8"))["cases"]
    results = []
    for case in cases:
        w,h = case["viewport"]
        l,t,r,b = case["insets"]
        w,h = w-l-r,h-t-b
        landscape = w >= h
        mode = "landscape" if landscape else "portrait"
        assert mode == case["expected_mode"]
        assert w >= c[mode+"_min_safe"][0] and h >= c[mode+"_min_safe"][1]
        cols = c[mode+"_columns"]
        cw = (w-8-(cols-1)*c["card_gap"])/cols
        buttons = [("pause",[0,0,44,44]),("sound",[w-44,0,44,44])]
        ty = c[mode+"_tools_y"]
        for i in range(3):
            buttons.append((f"tool{i}",[4+i*(w-8)/3,ty,(w-8)/3-4,44]))
        min_label_width = 7*12*0.62*case["font_scale"] # declared ASCII text budget 'T5 ABCD'
        assert cw-4 >= min_label_width and 12*case["font_scale"] <= c["label_line_height"]
        assert 14*12*case["font_scale"] <= w-8
        for tray in range(6):
            x,y = 4+(tray%cols)*(cw+c["card_gap"]), c["board_y"]+(tray//cols)*(c["card_height"]+c["card_gap"])
            # Worst-case each possible occupied top; mutually exclusive hitboxes checked per occupancy.
            seal = [x+4,y+114,cw-8,44]
            buttons.append((f"seal{tray}",seal))
            for centre in c["item_centres_y_bottom_to_top"]:
                top = [x+cw/2-22,y+centre-22,44,44]
                assert not intersects(top,seal)
                assert top[0]>=0 and top[1]>=0 and top[0]+44<=w and top[1]+44<=h
            buttons.append((f"top{tray}",[x+cw/2-22,y+42-22,44,44]))
        for name,rect in buttons:
            assert rect[2]>=44 and rect[3]>=44,(case["id"],name,rect)
            assert rect[0]>=0 and rect[1]>=0 and rect[0]+rect[2]<=w+1e-9 and rect[1]+rect[3]<=h+1e-9,(name,rect,w,h)
        for i,(name,a) in enumerate(buttons):
            for other,b in buttons[i+1:]:
                assert not intersects(a,b),(case["id"],name,other)
        results.append({"case":case["id"],"safe_size":[w,h],"mode":mode,"font_scale":case["font_scale"],
            "six_trays_visible":True,"min_hit_css_px":44,"body_scroll":False,"play_scroll":False,
            "scope":"STATIC_RECTANGLES_AND_TEXT_BUDGET_ONLY","status":"PASS"})
    return results


def release_gate_checks(tasks):
    by = {t["id"]:t for t in tasks["tasks"]}
    def ancestors(tid):
        return {tid} | set().union(*(ancestors(x) for x in by[tid]["depends_on"]))
    assert by["T15"]["platform_ids"] == ["P02","P04"]
    assert ancestors("T18") >= {"T13","T14"} and by["T18"]["platform_ids"] == ["P05"]
    assert ancestors("T19") >= {"T16","T17"} and by["T19"]["platform_ids"] == ["P06"]
    def reachable(tid,done,conditions):
        return set(by[tid]["depends_on"])<=done and set(by[tid]["required_conditions"])<=conditions
    web_done = ancestors("T15")-{"T15"}
    web_conditions = set(by["T15"]["required_conditions"])
    assert reachable("T15",web_done,web_conditions)
    assert not reachable("T18",web_done,web_conditions)
    assert not reachable("T19",web_done,web_conditions)
    p05_done = web_done | {"T13","T14"}
    p05_conditions = web_conditions | set(by["T18"]["required_conditions"])
    assert reachable("T18",p05_done,p05_conditions)
    assert not reachable("T19",p05_done,p05_conditions)
    assert all(not t["verified_conditions"] for t in tasks["tasks"])
    return {"web_gate_scope":["P02","P04"],"web_approval_does_not_unlock_mobile":True,
        "p05_confirmation_does_not_unlock_p06":True,"actual_verified_conditions":[],"status":"PASS"}
