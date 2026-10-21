"""Author preparation-only protocol tables and static layout cases. No game code."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = {
    "version": 2, "identity": ["run_id", "command_epoch", "command_seq"],
    "sequence_type": "integer_1_to_9007199254740991",
    "order": ["envelope_and_scope", "cached_payload_identity", "sequence_window",
              "consume_next_sequence", "status", "expected_revision", "rule_verdict"],
    "receipt_window": 128, "cache_rejections": True, "cache_hit_events": 0,
    "cache_hit_saves": 0, "conflict": "ID_CONFLICT_no_replace",
    "recovery": "fresh_epoch_preserve_run_revision_logical_and_undo_reset_sequence_to_1",
    "old_epoch": "STALE_EPOCH_no_side_effect", "replay_limit": 4096,
    "checkpoint": "endpoint_with_logical_revision_action_count_and_undo_history",
    "fixtures": "protocol-vectors.json", "probe": "tools/check_contracts.py"
}
LAYOUT = {
    "units": "CSS_px_after_safe_insets_no_uniform_downscale", "play_scroll": False,
    "portrait_min_safe": [304, 480], "landscape_min_safe": [480, 296],
    "portrait_columns": 3, "landscape_columns": 6,
    "card_height": 158, "card_gap": 4, "board_y": 84,
    "header": [0, 0, "W", 44], "orders": [4, 48, "W-8", 32],
    "portrait_message": [4, 408, "W-8", 20], "portrait_tools_y": 436,
    "landscape_tools_y": 252, "touch_min": 44,
    "card_label": [2, 0, "cardW-4", 20],
    "item_centres_y_bottom_to_top": [90, 66, 42],
    "item_visual_size": 24, "top_hit_size": 44,
    "seal_rect": [4, 114, "cardW-8", 44],
    "font_scale_max": 1.3, "label_base_font": 12, "label_line_height": 20,
    "message_base_font": 12, "message_max_zh_characters": 14,
    "other_screen_scroll_owner": "scroll_region_after_8px_cancel_tap_no_game_commands",
    "fixtures": "layout-cases.json"
}


def dispatch(seq, op="move", revision=0, expect=None, **extra):
    command = {"run_id":"R1","command_epoch":"E1","command_seq":seq,"expected_revision":revision,"op":op}
    command.update({"src":"T0","dst":"T2"} if op=="move" else {"at":"T0"} if op=="seal" else {})
    return {"action": "dispatch", "command": command,
        "fixture_rule_verdict": extra.pop("verdict", "ACCEPT"),
        "expect": expect or {}, **extra}


def write_contract_fixtures():
    steps = [dispatch(1, expect={"reason":"OK", "revision":1,"saves":1,"events":1})]
    for status in ["ANIMATING", "PAUSE", "WIN", "PLAY"]:
        steps += [{"action":"status", "value":status}, dispatch(1, expect={
            "reason":"OK","cached":True,"receipt_equals":"first","revision":1,"saves":1,"events":1})]
    conflict = dispatch(1, expect={"reason":"ID_CONFLICT","revision":1,"saves":1,"events":1})
    conflict["command"]["dst"] = "T1"
    steps += [conflict, dispatch(1,expect={"reason":"OK","cached":True,"receipt_equals":"first","revision":1,"events":1,"saves":1}),
        dispatch(2, revision=0, expect={"reason":"STALE_REVISION","revision":1}),
        dispatch(3, revision=1, verdict="TOP_MISMATCH", expect={"reason":"TOP_MISMATCH","revision":1}),
        {"action":"status","value":"ANIMATING"},
        dispatch(3, revision=1, verdict="TOP_MISMATCH", expect={"reason":"TOP_MISMATCH","cached":True}),
        dispatch(4, revision=1, expect={"reason":"BUSY"}), {"action":"status","value":"PLAY"},
        dispatch(4, revision=1, expect={"reason":"BUSY","cached":True}),
        dispatch(5, revision=1, expect={"reason":"OK","revision":2,"saves":2,"events":5})]
    bad_run = dispatch(1, expect={"reason":"STALE_RUN","saves":2,"events":5})
    bad_run["command"]["run_id"] = "R0"
    steps.append(bad_run)
    cases = [{"id":"retry_identity_before_busy_stale_pause_win", "steps":steps},
        {"id":"final_seal_retry_in_win", "steps":[dispatch(1, "seal", verdict="ACCEPT_WIN", expect={"reason":"OK","revision":1}),
            dispatch(1, "seal", verdict="ACCEPT_WIN", expect={"reason":"OK","cached":True,"saves":1,"events":1}),
            dispatch(2, revision=1, expect={"reason":"NOT_PLAYING","revision":1})]},
        {"id":"numeric_9_10", "steps":[{"action":"fill","start":1,"end":10,"mode":"reject"},
            {"action":"assert","expect":{"high":10,"floor":1,"cache_size":10,"revision":0}},
            dispatch(9, verdict="TOP_MISMATCH", expect={"reason":"TOP_MISMATCH","cached":True}),
            dispatch(10, verdict="TOP_MISMATCH", expect={"reason":"TOP_MISMATCH","cached":True})]},
        {"id":"numeric_window_127_128_129", "steps":[{"action":"fill","start":1,"end":127,"mode":"reject"},
            {"action":"assert","expect":{"high":127,"floor":1,"cache_size":127}},
            dispatch(128, verdict="TOP_MISMATCH", expect={"reason":"TOP_MISMATCH","floor":1,"cache_size":128}),
            dispatch(129, verdict="TOP_MISMATCH", expect={"reason":"TOP_MISMATCH","floor":2,"cache_size":128}),
            dispatch(1, verdict="TOP_MISMATCH", expect={"reason":"STALE_COMMAND"}),
            dispatch(2, verdict="TOP_MISMATCH", expect={"reason":"TOP_MISMATCH","cached":True}),
            dispatch(128, verdict="TOP_MISMATCH", expect={"reason":"TOP_MISMATCH","cached":True}),
            dispatch(129, verdict="TOP_MISMATCH", expect={"reason":"TOP_MISMATCH","cached":True}),
            dispatch(131, expect={"reason":"SEQUENCE_GAP","high":129}),
            dispatch(130, expect={"reason":"OK","high":130,"revision":1})]},
        {"id":"mixed_accept_reject_undo", "steps":[
            dispatch(1, expect={"reason":"OK","logical":1,"revision":1,"history":1}),
            dispatch(2, revision=1, verdict="TOP_MISMATCH", expect={"reason":"TOP_MISMATCH","history":1}),
            dispatch(3, revision=1, expect={"reason":"OK","logical":2,"revision":2}),
            dispatch(4,"undo",2, {"reason":"OK","logical":1,"revision":3,"history":1}),
            dispatch(5,"undo",3, {"reason":"OK","logical":0,"revision":4,"history":0}),
            dispatch(6,"undo",4, {"reason":"EMPTY_HISTORY","revision":4}),
            dispatch(7,revision=0,expect={"reason":"STALE_REVISION","revision":4}),
            dispatch(3,revision=1,expect={"reason":"OK","cached":True,"receipt_revision":2,"revision":4,"saves":4,"events":7})]},
        {"id":"restore_new_epoch_old_late_callback", "steps":[dispatch(1),
            dispatch(2,revision=1,verdict="TOP_MISMATCH"), dispatch(3,revision=1),
            {"action":"restore","new_epoch":"E2","expect":{"revision":2,"logical":2,"history":2,"high":0,"cache_size":0}},
            dispatch(3,revision=1,expect={"reason":"STALE_EPOCH","revision":2,"saves":2,"events":3}),
            {"action":"callback","epoch":"E1","expect":{"ignored":True,"revision":2,"saves":2,"events":3}},
            {**dispatch(1,"undo",2,{"reason":"OK","revision":3,"logical":1,"history":1}),
             "command":{"run_id":"R1","command_epoch":"E2","command_seq":1,"expected_revision":2,"op":"undo"}}]},
        {"id":"checkpoint_4096_independent_of_cache", "steps":[{"action":"fill","start":1,"end":4096,"mode":"forward"},
            {"action":"assert","expect":{"revision":4096,"logical":4096,"history":128,"replay_size":4096,"checkpoint_ordinal":0,"cache_size":128,"floor":3969}},
            dispatch(4097,"undo",4096,{"reason":"OK","revision":4097,"logical":4095,"history":127,"checkpoint_ordinal":4096,"replay_size":1,"floor":3970}),
            dispatch(4096,"move",4095,{"reason":"OK","cached":True,"receipt_revision":4096,"revision":4097}),
            {"action":"replay_checkpoint","expect":{"replay_matches":True,"revision":4097,"logical":4095,"history":127}},
            {"action":"restore","new_epoch":"E2","expect":{"revision":4097,"logical":4095,"history":127,"high":0}},
            {"action":"callback","epoch":"E1","expect":{"ignored":True,"revision":4097}},
            {**dispatch(1,"undo",4097,{"reason":"OK","revision":4098,"logical":4094,"history":126}),
             "command":{"run_id":"R1","command_epoch":"E2","command_seq":1,"expected_revision":4097,"op":"undo"}}]},
        {"id":"undo_history_127_128_129", "steps":[{"action":"fill","start":1,"end":127,"mode":"forward"},
            {"action":"assert","expect":{"history":127,"revision":127}},
            dispatch(128,revision=127,expect={"reason":"OK","history":128,"revision":128}),
            dispatch(129,revision=128,expect={"reason":"OK","history":128,"revision":129}),
            dispatch(130,"undo",129,{"reason":"OK","history":127,"logical":128,"revision":130}),
            {"action":"fill","start":131,"end":257,"mode":"undo"},
            {"action":"assert","expect":{"history":0,"logical":1,"revision":257}},
            dispatch(258,"undo",257,{"reason":"EMPTY_HISTORY","logical":1,"revision":257})]}]
    # Identity errors must not allocate a sequence or publish a rejection event.
    malformed = dispatch("10", expect={"reason":"BAD_ENVELOPE","high":0,"events":0,"saves":0})
    cases.append({"id":"typed_identity_no_string_sort", "steps":[malformed,
        dispatch(2, expect={"reason":"SEQUENCE_GAP","high":0,"events":0}),
        dispatch(1,expect={"reason":"OK","high":1,"revision":1})]})
    dump("protocol-vectors.json", {"scope":"OFFLINE_ABSTRACT_PROTOCOL_TABLES_NOT_GAME_RUNTIME",
        "fixture_rule_verdict":"Injected test decisions; game rules are tested separately in verify.py",
        "cases":cases})
    dump("layout-cases.json", {"scope":"STATIC_GEOMETRY_AND_TEXT_BUDGET_NOT_RENDERED_UI",
        "cases":[{"id":name,"viewport":[w,h],"insets":[l,t,r,b],"font_scale":f,"expected_mode":mode}
            for name,w,h,l,t,r,b,f,mode in [
                ("small_portrait_safe_font13",320,568,8,44,8,34,1.3,"portrait"),
                ("small_portrait_no_notch",320,568,0,0,0,0,1.0,"portrait"),
                ("small_landscape_safe_font13",568,320,44,8,34,8,1.3,"landscape"),
                ("desktop",960,600,0,0,0,0,1.3,"landscape"),
                ("standard_portrait",390,844,0,44,0,34,1.3,"portrait")]]})


def dump(name, value):
    (ROOT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")


if __name__ == "__main__":
    write_contract_fixtures()
