"""Generate offline contract schemas/fixtures in G04 only; no game implementation."""
from __future__ import annotations
import copy, hashlib, json
from pathlib import Path
ROOT = Path(__file__).resolve().parent
MAX = 9007199254740991
def obj(properties, required=None):
    return {"type": "object", "properties": properties,
            "required": list(properties) if required is None else required,
            "additionalProperties": False}
def integer(lo=0, hi=MAX):
    return {"type": "integer", "minimum": lo, "maximum": hi}
def array(items, lo=0, hi=128):
    return {"type": "array", "items": items, "minItems": lo, "maxItems": hi}
def enum(*values):
    return {"enum": list(values)}
def text(pattern=None):
    return {"type": "string", **({"pattern": pattern} if pattern else {"minLength": 1, "maxLength": 128})}
def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
def checksum(envelope):
    return hashlib.sha256(canonical({k:v for k,v in envelope.items() if k != "checksum"})).hexdigest()
def seal(value):
    value["checksum"] = checksum(value)
    return value
def write(name, value):
    (ROOT/name).write_text(json.dumps(value, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
def main():
    pos = {"type":"array", "prefixItems":[integer(0,1),integer(0,4),integer(0,4)],"items":False,"minItems":3,"maxItems":3}
    state = obj({"position":pos,"bits":integer(0,7),"pending":integer(0,7),"nextBeacon":integer(0,6),
        "used":integer(0,128),"status":enum("PLAYING","FAILED","WON"),
        "failure":enum(None,"FLOOR_CLOSED","BEACON_ORDER","MOVE_LIMIT")})
    state["allOf"] = [{"if":{"properties":{"status":{"const":"FAILED"}}},
        "then":{"properties":{"failure":enum("FLOOR_CLOSED","BEACON_ORDER","MOVE_LIMIT")}},
        "else":{"properties":{"failure":{"const":None}}}}]
    attempt = text(r"^a-[0-9a-f]{32}$")
    levelid = text(r"^G04-(L(?:0[1-9]|1[0-9]|20)|X[12]-A)$")
    active = obj({"levelId":levelid,"levelName":text(),"variant":enum("B0","X1","X2"),"attemptId":attempt,
        "assisted":{"type":"boolean"},"nextSeq":integer(1),"totalAccepted":integer(),"undoCount":integer(),
        "acceptedCommands":array(enum("U","R","D","L","X")),"ruleState":{"$ref":"#/$defs/RuleState"}})
    active["allOf"]=[{"properties":{"ruleState":{"properties":{"status":enum("PLAYING","FAILED")}}}}]
    record = obj({"levelId":text(r"^G04-L(?:0[1-9]|1[0-9]|20)$"),"completed":{"type":"boolean"},
        "bestStars":integer(0,3),"bestUsed":{"anyOf":[{"type":"null"},integer(1,128)]}})
    record["allOf"]=[{"if":{"properties":{"completed":{"const":True}}},
        "then":{"properties":{"bestStars":integer(1,3),"bestUsed":integer(1,128)}},
        "else":{"properties":{"bestStars":{"const":0},"bestUsed":{"const":None}}}}]
    settings=obj({"sfx":{"type":"boolean","default":True},"music":{"type":"boolean","default":False},
        "reducedMotion":{"type":"boolean","default":False},"locale":{"enum":["zh-CN","en"],"default":"zh-CN"},
        "contrast":{"enum":["standard","high"],"default":"standard"}})
    progress=obj({"records":array({"$ref":"#/$defs/ProgressRecord"},20,20),"highestUnlocked":integer(1,20),
        "lastCommittedAttemptId":{"anyOf":[{"type":"null"},attempt]}})
    schema=obj({"schemaVersion":{"const":1},"ruleVersion":{"const":"1.0.0"},
        "profile":enum("local-qa","P01","P02-basic-nosdk","P02-basic-sdk","P02-full"),
        "contentHash":text(r"^[0-9a-f]{64}$"),"revision":integer(1),
        "updatedAt":{"type":"string","format":"date-time","pattern":r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$"},
        "progress":{"$ref":"#/$defs/Progress"},"settings":{"$ref":"#/$defs/Settings"},
        "activeSession":{"anyOf":[{"type":"null"},{"$ref":"#/$defs/ActiveSession"}]},
        "checksum":text(r"^[0-9a-f]{64}$")})
    schema.update({"$schema":"https://json-schema.org/draft/2020-12/schema","$id":"urn:G04:save-envelope:1",
        "$defs":{"RuleState":state,"Settings":settings,"ProgressRecord":record,"Progress":progress,"ActiveSession":active}})
    write("save-envelope.schema.json",schema)
    def fact(kind,payload):
        return obj({"type":{"const":kind},"payload":payload})
    facts = [fact("CommandAccepted",obj({"command":enum("U","R","D","L","X"),"used":integer(1,128),"from":pos,"to":pos})),
        fact("PendingApplied",obj({"mask":integer(1,7),"bits":integer(0,7)})),
        fact("SwitchEntered",obj({"mask":integer(1,7),"mode":enum("IMMEDIATE","DELAYED"),"bits":integer(0,7),"pending":integer(0,7)})),
        fact("BeaconAdvanced",obj({"index":integer(0,5)})),
        fact("StateCommitted",obj({"state":{"$ref":"#/$defs/RuleState"}})),
        fact("RuleWon",obj({"used":integer(1,128),"par":integer(1,128)})),
        fact("RuleFailed",obj({"reason":enum("FLOOR_CLOSED","BEACON_ORDER","MOVE_LIMIT")})),
        fact("CommandRejected",obj({"reason":enum("BLOCKED","NO_LIFT","INVALID_ACTION_OR_TERMINAL")}))]
    richer=[]
    for f in copy.deepcopy(facts):
        kind=f["properties"]["type"]["const"]
        if kind=="RuleWon":
            f["properties"]["type"]["const"]="LevelWon"
            f["properties"]["payload"]=obj({"used":integer(1,128),"par":integer(1,128),"assisted":{"type":"boolean"},"stars":integer(1,3)})
        elif kind=="RuleFailed": f["properties"]["type"]["const"]="LevelFailed"
        richer.append(f)
    richer += [fact("UndoApplied",obj({"restored":{"$ref":"#/$defs/RuleState"}})),
        fact("AttemptRestarted",obj({"previousAttemptId":attempt,"newAttemptId":attempt})),
        fact("HintConfirmed",obj({"assisted":{"const":True}})),
        fact("SaveDegraded",obj({"reason":enum("QUOTA","SECURITY","TIMEOUT","IO")}))]
    event_variants=[]
    for f in richer:
        event_variants.append(obj({"v":{"const":1},"seq":integer(1),"attemptId":attempt,"levelId":levelid,
            "source":enum("keyboard","touch","mouse","system","qa"),**f["properties"]}))
    write("event-contract.schema.json",{"$schema":"https://json-schema.org/draft/2020-12/schema",
        "$id":"urn:G04:events:1","$defs":{"RuleState":state,"RuleFact":{"oneOf":facts},"SessionEvent":{"oneOf":event_variants}},
        "oneOf":[{"$ref":"#/$defs/RuleFact"},{"$ref":"#/$defs/SessionEvent"}]})
    spec=json.loads((ROOT/"game-spec.json").read_text(encoding="utf-8"))
    content_hash=hashlib.sha256((ROOT/"game-spec.json").read_bytes()).hexdigest()
    records=[{"levelId":f"G04-L{i:02d}","completed":i==1,"bestStars":3 if i==1 else 0,"bestUsed":2 if i==1 else None} for i in range(1,21)]
    l2=spec["levels"][1]
    import validate_spec as rules
    def state_obj(t,reason="OK"):
        return {"position":list(t[:3]),"bits":t[3],"pending":t[4],"nextBeacon":t[5],"used":t[6],"status":t[7],
            "failure":reason if t[7]=="FAILED" else None}
    t,_=rules.step(l2,rules.initial(l2),"R")
    legal=seal({"schemaVersion":1,"ruleVersion":"1.0.0","profile":"local-qa","contentHash":content_hash,
        "revision":7,"updatedAt":"2026-10-21T10:30:00.000Z",
        "progress":{"records":records,"highestUnlocked":2,"lastCommittedAttemptId":"a-"+"0"*31+"1"},
        "settings":{"sfx":True,"music":False,"reducedMotion":False,"locale":"zh-CN","contrast":"standard"},
        "activeSession":{"levelId":l2["id"],"levelName":l2["name"],"variant":"B0","attemptId":"a-"+"0"*31+"2",
            "assisted":True,"nextSeq":12,"totalAccepted":3,"undoCount":2,"acceptedCommands":["R"],"ruleState":state_obj(t)}})
    failed=copy.deepcopy(legal); level=spec["levels"][0]; st=rules.initial(level); before=None
    commands=list("RLRLRL")
    for op in commands:
        before=st;st,reason=rules.step(level,st,op)
    failed["revision"]=8
    failed["activeSession"].update(levelId=level["id"],levelName=level["name"],attemptId="a-"+"0"*31+"3",
        acceptedCommands=commands,totalAccepted=6,undoCount=0,ruleState=state_obj(st,reason),nextSeq=30)
    seal(failed)
    cases=[]
    def case(name,change,result,reseal=True):
        sample=copy.deepcopy(legal);change(sample)
        if reseal:seal(sample)
        cases.append({"id":name,"value":sample,"expected":result})
    case("bad_checksum",lambda s:s["settings"].update(music=True),"CHECKSUM_MISMATCH",False)
    case("duplicate_settings_authority",lambda s:s["progress"].update(settings=copy.deepcopy(s["settings"])),"SCHEMA_INVALID")
    case("forged_final_bits",lambda s:s["activeSession"]["ruleState"].update(bits=7),"REPLAY_MISMATCH")
    case("completed_without_best_used",lambda s:s["progress"]["records"][0].update(bestUsed=None),"SCHEMA_INVALID")
    case("unlocked_chain_forged",lambda s:s["progress"].update(highestUnlocked=20),"PROGRESS_INVALID")
    case("future_schema",lambda s:s.update(schemaVersion=2),"UNSUPPORTED_SCHEMA")
    case("unknown_rule",lambda s:s.update(ruleVersion="2.0.0"),"UNSUPPORTED_RULE")
    case("other_profile",lambda s:s.update(profile="P01"),"PROFILE_MISMATCH")
    case("content_update",lambda s:s.update(contentHash="f"*64),"CONTENT_CHANGED")
    case("saved_won_session",lambda s:s["activeSession"]["ruleState"].update(status="WON"),"SCHEMA_INVALID")
    case("wrong_level_name",lambda s:s["activeSession"].update(levelName="伪造关名"),"SESSION_INVALID")
    case("invalid_timestamp",lambda s:s.update(updatedAt="2026-13-21T10:30:00.000Z"),"SCHEMA_INVALID")
    simple={"z":"中文会话","a":{"b":[2,True,None,"上层\n校准"],"a":"折光机关"}}
    raw=canonical(simple)
    write("save-fixtures.json",{"fixture_revision":"r2","content_hash":content_hash,
        "canonical_vector":{"value":simple,"canonical_utf8":raw.decode("utf-8"),"canonical_hex":raw.hex(),"sha256":hashlib.sha256(raw).hexdigest()},
        "valid":[{"id":"chinese_active_playing","value":legal,"expected":"OK","expected_payload_sha256":legal["checksum"]},
                 {"id":"failed_can_undo","value":failed,"expected":"OK","expected_payload_sha256":failed["checksum"],"expected_undo_state":state_obj(before)}],
        "invalid_or_migration":cases})
    before_state={"position":[0,1,1],"bits":1,"pending":0,"nextBeacon":0,"used":1,"status":"PLAYING","failure":None}
    final_state={**before_state,"position":[0,2,1],"used":2,"status":"WON"}
    facts_expected=[{"type":"CommandAccepted","payload":{"command":"R","used":2,"from":[0,1,1],"to":[0,2,1]}},
        {"type":"StateCommitted","payload":{"state":final_state}},{"type":"RuleWon","payload":{"used":2,"par":2}}]
    pairs=[]
    for assisted,seq,num in [(False,20,4),(True,200,5)]:
        attempt_id="a-"+"0"*31+str(num)
        expected=[]
        for i,f in enumerate(facts_expected):
            event={"v":1,"seq":seq+i,"attemptId":attempt_id,"levelId":"G04-L01","source":"keyboard",**copy.deepcopy(f)}
            if event["type"]=="RuleWon":event.update(type="LevelWon",payload={"used":2,"par":2,"assisted":assisted,"stars":2 if assisted else 3})
            expected.append(event)
        pairs.append({"assisted":assisted,"attemptId":attempt_id,"nextSeq":seq,"expected_events":expected})
    write("session-contract-vectors.json",{"levelId":"G04-L01","before":before_state,"command":{"op":"R","source":"keyboard"},
        "expected_facts":facts_expected,"sessions":pairs,
        "terminal_repeat":{"repeated_callbacks":3,"expected_commit_win_calls":1,"expected_level_won_publications":1},
        "note":"Fixed specification expectations; no TS, scene, animation or SDK has been executed."})
    print("Generated 2 contract schemas and 2 fixture files inside G04 only")
if __name__=="__main__":main()
