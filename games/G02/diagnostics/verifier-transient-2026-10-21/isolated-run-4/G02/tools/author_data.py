"""Deterministic authoring of original research data and local JSON Schemas.
Preparation utility only; no game runtime or Cocos project is generated.
"""
import json
from pathlib import Path
from verify import solve
from author_contracts import PROTOCOL, LAYOUT, write_contract_fixtures

ROOT = Path(__file__).resolve().parents[1]


def write(name, data):
    (ROOT / name).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def obj(properties, required=None):
    return {"type": "object", "additionalProperties": False, "properties": properties,
            "required": list(properties) if required is None else required}


S = {"type": "string", "minLength": 1}
I = {"type": "integer", "minimum": 0}
B = {"type": "boolean"}
COLOUR = {"enum": list("ABCD")}
COLOURS = {"type": "array", "items": COLOUR, "uniqueItems": True}
STRINGS = {"type": "array", "items": S}
ACTION = {"oneOf": [obj({"op": {"const": "move"}, "src": S, "dst": S}),
                      obj({"op": {"const": "seal"}, "at": S})]}
TRAY = obj({"id": {"type": "string", "pattern": "^T[0-5]$"},
    "capacity": {"type": "integer", "minimum": 1, "maximum": 3},
    "items": {"type": "array", "items": COLOUR, "maxItems": 3},
    "accepts": {**COLOURS, "minItems": 1}, "unlock_after": COLOURS, "sealable": B})
LEVEL = obj({"id": {"type": "string", "pattern": "^L(0[1-9]|1[0-9]|20)$"}, "name": S,
    "variant": {"enum": ["V0", "X1", "X2", "X12"]}, "status": {"const": "HYPOTHESIS"},
    "intent": S, "demand": {"type": "object", "minProperties": 1, "maxProperties": 4,
        "propertyNames": {"pattern": "^[ABCD]$"}, "additionalProperties": {"enum": [2, 3]}},
    "containers": {"type": "array", "items": TRAY, "minItems": 2, "maxItems": 6},
    "win": obj({"all_items_removed": {"const": True}, "sealed_colours": {**COLOURS, "minItems": 1}}),
    "solution": {"type": "array", "items": ACTION, "minItems": 1},
    "par_actions": {"type": "integer", "minimum": 1}, "target_seconds": {"type": "integer", "minimum": 10},
    "tutorial": S, "feature_coverage": obj({"optional_container_ids": STRINGS,
        "mandatory_mastery_claim": {"const": False}, "evidence": S})})

# All states below are original authored arrangements, not transcriptions of references.
# Strings list each stack from bottom to top. Empty string is a completely empty tray.
boards = [
 ("双件入箱", "V0", ["A", "A", ""], 2, {}, {}, "一次移动后手动封箱；理解没有自动消除", "将顶部圆片移到另一圆片，再点封箱"),
 ("交叉归位", "V0", ["AB", "BA", ""], 2, {}, {}, "一个空托盘用于交换顶层", "空托盘先借位，异类顶层不能叠放"),
 ("三角借位", "V0", ["AB", "CA", "BC", ""], 2, {}, {}, "三类闭环需要选择第一种归箱色", "先找顶部同类，保留借位空间"),
 ("三件邮包", "V0", ["AAB", "BBA", ""], 3, {}, {}, "容量变三；同类连续两件仍须逐件移动", "每次只移动一件，三件同类可封箱"),
 ("斜纹整理", "V0", ["ABC", "BCA", "CAB", "", ""], 3, {}, {}, "两处空位与三层深度", "观察全部层，规划两处借位"),
 ("圆章开锁", "X1", ["AB", "BA", "", "CC"], 2, {3:["A"]}, {}, "A封箱解锁现成C箱；按条件而非倒计时解锁", "封好圆片A后，星片托盘解锁"),
 ("隔柜取星", "X1", ["AB", "BA", "C", "C", ""], 2, {3:["B"]}, {}, "锁内物品可见但不可取放；先封B", "菱片B封箱后才能取锁内星片"),
 ("两翼解锁", "X1", ["AB", "BA", "", "CD", "DC", ""], 2, {3:["A"],4:["A"]}, {}, "一个章解锁两个混合柜；先后两组排序", "圆片A解锁右侧两柜"),
 ("留空等章", "X1", ["AB", "CA", "BC", "", ""], 2, {4:["A"]}, {}, "可选锁空盘展示解锁后增容；当前最短解不用它，不验证开锁掌握", "观察T4缺A章；可不使用T4完成，另问何时可用"),
 ("三层钥印", "X1", ["AAB", "BBA", "", "CCC"], 3, {3:["B"]}, {}, "三件需求与B解锁", "三件菱片B封好才可封星片"),
 ("单签借位", "X2", ["AB", "BA", ""], 2, {}, {2:"A"}, "唯一空盘只接A；改变第一步合法动作", "标签圆片A的空盘不接菱片"),
 ("分流双签", "X2", ["AB", "CA", "BC", "", ""], 2, {}, {3:"A",4:"BC"}, "两个定向缓冲；不依赖锁系统", "看标签再移动，同色顶层仍须匹配"),
 ("窄盘暂存", "X2", ["AAB", "BBA", "", ""], 3, {}, {2:"B",3:"A"}, "B专色缓冲参与解；A窄盘T3为可选演示，不验证其使用或不可封规则掌握", "T3只接A且不可封；可不使用，另问能否在T3封箱"),
 ("三层双路", "X2", ["ABC", "BCA", "CAB", "", ""], 3, {}, {3:"AC",4:"B"}, "多层排序与A/C双签", "双标签表示可接两类，不能混顶"),
 ("四色邮路", "X2", ["AB", "BC", "CD", "DA", "", ""], 2, {}, {4:"BD",5:"AC"}, "四色循环与两条借位路线", "按BD和AC标签分流顶部物件"),
 ("签章联动", "X12", ["AB", "BA", "", "CC"], 2, {3:["A"]}, {2:"A",3:"C"}, "先用A专色位，再封A开C", "标签与锁分别检查，二者都满足才可移动"),
 ("先菱后星", "X12", ["AB", "BA", "C", "C", "", ""], 2, {3:["B"]}, {4:"AB",5:"C"}, "已露C不可提前全部归箱；两种缓冲职责", "先拿菱章B，星片分流盘可先留空"),
 ("三层分签", "X12", ["AAB", "BBA", "", "CCC", ""], 3, {3:["A"]}, {2:"A",3:"C",4:"BC"}, "先A定向借位，再开C，不能靠所有盘通用", "A签盘只接圆片，BC签盘可临时收菱片"),
 ("双章门", "X12", ["AB", "BA", "", "CD", "DC", ""], 2, {3:["A","B"],4:["A","B"]}, {2:"A",5:"CD"}, "AND锁必须A和B都封；两阶段分签排序", "锁上的两个章都要点亮"),
 ("邮路终试", "X12", ["ABC", "BCA", "CAB", "", "", "DDD"], 3, {5:["A","C"]}, {3:"AC",4:"B",5:"D"}, "三层三类借位加双章末箱；四类总复习", "先整理ABC，圆章和星章共同解锁叶片D")
]

levels = []
for n, (name, variant, stacks, cap, locks, filters, intent, tutorial) in enumerate(boards, 1):
    colours = sorted(set("".join(stacks)))
    counts = {c: "".join(stacks).count(c) for c in colours}
    level = {"id": f"L{n:02d}", "name": name, "variant": variant, "status": "HYPOTHESIS", "intent": intent,
        "demand": counts, "containers": [{"id": f"T{i}", "capacity": (1 if n == 13 and i == 3 else cap),
            "items": list(s), "accepts": list(filters.get(i, "".join(colours))),
            "unlock_after": locks.get(i, []), "sealable": not (n == 13 and i == 3)} for i, s in enumerate(stacks)],
        "win": {"all_items_removed": True, "sealed_colours": colours},
        "target_seconds": (25 if n == 1 else 45 + n * 5), "tutorial": tutorial}
    solution, visited = solve(level)
    if solution is None:
        raise RuntimeError(f"Unsolvable authored level {n}")
    level.update(solution=solution, par_actions=len(solution))
    level["feature_coverage"] = {"optional_container_ids": ["T4"] if n == 9 else ["T3"] if n == 13 else [],
        "mandatory_mastery_claim": False,
        "evidence": "Published solution never references optional tray; removing it preserves that legal winning sequence" if n in (9, 13)
        else "No per-level teaching-mastery conclusion; legal solution is not a player comprehension measurement"}
    levels.append(level)
    print(level["id"], variant, "shortest", len(solution), "states", visited)

rules = {"stack_order": "bottom_to_top", "move_units": 1, "match": "empty_or_same_top",
    "selected_input_policy": "other_tray_always_attempt_move_reject_preserves_source_cancel_before_reselect",
    "capacity_unit": "one_item", "seal": "manual_exact_demand_homogeneous_then_remove_items_and_retire_tray",
    "unlock": "all_required_colours_sealed", "filter": "destination_accepts_colour",
    "undo": "unlimited_full_snapshot_including_seals_and_locks", "redo": False,
    "failure": "zero_legal_forward_actions_and_not_win", "no_solution_inference": "never_from_search_timeout",
    "win_priority": "win_before_deadlock", "invalid_action_cost": 0, "time_limit_seconds": None,
    "move_limit": None, "randomness": "none_in_20_authored_levels", "timer_affects_rules": False}
variants = [{"id":"V0","locks":False,"filters":False,"hypothesis":"基础借位与手动封箱可理解性"},
    {"id":"X1","locks":True,"filters":False,"hypothesis":"封箱解锁创造可读的先后决策"},
    {"id":"X2","locks":False,"filters":True,"hypothesis":"接收标签改变路线规划而非只改外观"},
    {"id":"X12","locks":True,"filters":True,"hypothesis":"组合收益需单独验证，不能外推两个单因子成功"}]
spec = {"schema_version":"1.1.0", "project_id":"G02", "working_title":"签章收纳台 / Seal & Sort Desk",
    "date":"2026-10-21", "state":"REVISION_REQUIRED", "ready_for_build":False,
    "independent_review":"PENDING_RE_REVIEW", "development_authorized":False,
    "candidate_platform_ids":["P02","P04","P05","P06"], "audience":"13+ adolescents and adults; not child-targeted",
    "assumption_label":"HYPOTHESIS: all original mechanics, levels, timings, budgets and player thresholds",
    "rules":rules, "variants":variants, "levels":levels,
    "economy":{"currency":"none", "lives":"none", "hint_cost":0, "undo_cost":0,
               "progression":"complete Lnn to unlock Lnn+1; completed replay unrestricted; L20 opens collection-complete screen",
               "iap":False, "rewarded_ads":False, "basic_monetization":False,
               "future_interstitial":"Full/approved publisher only; after results and explicit next, >=180 active seconds and >=3 completions since previous; never necessary"},
    "command_protocol": PROTOCOL,
    "research_observation": {"initial_author_scope":"OFFICIAL_WEB_DESCRIPTION_ONLY_NO_CORE_PLAY",
        "team_supplement":"evidence/team-browser-observation-index.json", "status":"BLOCKED_CORE_BEHAVIOR",
        "confirmed_core_inputs":0, "continuous_30s":"UNKNOWN", "continuous_5min":"UNKNOWN"},
    "data":{"save_version":2, "key":"g02.save.v2", "maximum_history":128,
        "overflow":"drop_oldest_undo_snapshot_only", "maximum_local_events":1000,
        "consent_default":"no_developer_network_telemetry", "replay":"4096 consumed-command records; checkpoint includes logical state, revision, action count and undo history; independent from receipt cache"},
    "ui":{"design_width":390,"design_height":844,"coordinate_origin":"safe_content_top_left",
          "min_touch_css_px":44,"move_ms":160,"seal_ms":240,"unlock_ms":180,"reduced_motion_ms":0,
          "screens":["boot","home","level_select","play","pause_settings","restart_confirm","deadlock","win","collection_complete","error_recovery","credits"],
          "layout_contract": LAYOUT},
    "technology":{"engine_candidate":"Cocos Creator 3.8.8", "typescript_checker_candidate":"5.6.3",
        "language_subset":"Cocos official 3.8 language page documents TypeScript 4.1.0 subset",
        "compatibility":"UNVERIFIED; pin installed editor build/hash and run T03 before adopting", "engine_build":"NOT_RUN",
        "mobile":"P05/P06 SDK and engine support pending publisher confirmation; separate native project or port"},
    "platform_constraints":[
        {"id":"P02","max_total_mb":250,"max_files":1500,"no_sdk_max_total_mb":50,"mobile_homepage_initial_mb":20,
         "full_sdk_required":True,"basic_monetization":False,"external_analytics":False,"age_policy":"PEGI-12 compatible; reject child-targeted content","source":"E04;E05"},
        {"id":"P04","sdk":"Playgama Bridge","external_analytics":False,"analytics":"Bridge only or local offline QA; never GA4","source":"E06;E07"},
        {"id":"P01","active_candidate":False,"ads":False,"external_links":False,"developer_telemetry":False,"source":"E10"}],
    "performance_targets":{"status":"HYPOTHESIS_NOT_MEASURED","initial_mb":12,"total_mb":20,"files":200,
        "fps_mobile":60,"fps_fallback":30,"memory_mb":160,"first_playable_seconds_10mbps":5},
    "blocking_unknowns":["Independent audit REVISE; six author fixes pending same-reviewer re-review", "Reference hands-on trajectories UNKNOWN",
        "Cocos/TypeScript combination not compiled", "Player comprehension and enjoyment not measured",
        "P05/P06 SDK/build requirements and commercial terms UNKNOWN", "Final asset provenance and contract rights pending"]}
write("game-spec.json", spec)

# Explicit schemas: reject unknown keys and constrain every gameplay field.
RULE_SCHEMA = obj({k: {"const":v} for k,v in rules.items()})
VARIANT_SCHEMA = obj({"id":{"enum":["V0","X1","X2","X12"]},"locks":B,"filters":B,"hypothesis":S})
schema = obj({
    "schema_version":{"const":"1.1.0"},"project_id":{"const":"G02"},"working_title":S,
    "date":{"type":"string","format":"date"},"state":{"const":"REVISION_REQUIRED"},"ready_for_build":{"const":False},
    "independent_review":{"const":"PENDING_RE_REVIEW"},"development_authorized":{"const":False},
    "candidate_platform_ids":{"const":["P02","P04","P05","P06"]},"audience":S,"assumption_label":S,
    "rules":RULE_SCHEMA,"variants":{"type":"array","items":VARIANT_SCHEMA,"minItems":4,"maxItems":4},
    "levels":{"type":"array","items":LEVEL,"minItems":20,"maxItems":20},
    "economy":obj({"currency":{"const":"none"},"lives":{"const":"none"},"hint_cost":{"const":0},
        "undo_cost":{"const":0},"progression":S,"iap":{"const":False},"rewarded_ads":{"const":False},
        "basic_monetization":{"const":False},"future_interstitial":S}),
    "command_protocol": {"const": PROTOCOL},
    "research_observation": {"const":spec["research_observation"]},
    "data":obj({"save_version":{"const":2},"key":{"const":"g02.save.v2"},"maximum_history":{"const":128},
        "overflow":S,"maximum_local_events":{"const":1000},"consent_default":S,"replay":S}),
    "ui":obj({"design_width":{"const":390},"design_height":{"const":844},"coordinate_origin":S,
        "min_touch_css_px":{"const":44},"move_ms":I,"seal_ms":I,"unlock_ms":I,"reduced_motion_ms":I,"screens":STRINGS,
        "layout_contract":{"const":LAYOUT}}),
    "technology":obj({k:S for k in spec["technology"]}),
    "platform_constraints":{"type":"array","minItems":3,"maxItems":3,"items":{"oneOf":[
        obj({"id":{"const":"P02"},"max_total_mb":{"const":250},"max_files":{"const":1500},
            "no_sdk_max_total_mb":{"const":50},"mobile_homepage_initial_mb":{"const":20},"full_sdk_required":{"const":True},
            "basic_monetization":{"const":False},"external_analytics":{"const":False},"age_policy":S,"source":S}),
        obj({"id":{"const":"P04"},"sdk":S,"external_analytics":{"const":False},"analytics":S,"source":S}),
        obj({"id":{"const":"P01"},"active_candidate":{"const":False},"ads":{"const":False},"external_links":{"const":False},"developer_telemetry":{"const":False},"source":S})]}},
    "performance_targets":obj({"status":{"const":"HYPOTHESIS_NOT_MEASURED"},"initial_mb":I,"total_mb":I,"files":I,
        "fps_mobile":I,"fps_fallback":I,"memory_mb":I,"first_playable_seconds_10mbps":I}),
    "blocking_unknowns":{**STRINGS,"minItems":1}})
schema.update({"$schema":"https://json-schema.org/draft/2020-12/schema","title":"G02 preparation specification v1"})
write("game-spec.schema.json",schema)

task_rows = [
 ("T01","review",[],"同一独立审查者修订复核","research-reviewer","REVISIONS、00—12、两JSON及两Schema、向量/验证报告；reviews/G02-audit.md/.json只读原件","audit/independent-review-receipt.md","首审REVISE；作者只登记原件hash/六项修订与证据，关闭由同一独立审查者决定", "python -B tools/verify.py --all"),
 ("T02","review",["T01"],"人类批准G02与施工档案","owner","独立审计与修正差异","audit/human-build-approval.md","明确批准ID/档案hash/预算/渠道；未批准保持门禁", "人工核对签批记录与所有BLOCKER关闭"),
 ("T03","build",["T02"],"工具链可行性切片","engineer","07版本候选与官方链接","implementation/toolchain/toolchain-lock.json","固定编辑器安装hash；TS类型检查和空项目Web构建；只报告实际日志", "Creator CLI --project <path> --build <exported-config>; exit=36; typecheck"),
 ("T04","build",["T03"],"无引擎规则核","core-engineer","03规则、04接口、20关合法解","implementation/core/RuleCore.ts","接受/拒绝、单因顶色/容量隔离、真实快照恢复重锁、状态不变性与Python向量一致", "npm run test:rules"),
 ("T05","build",["T04"],"存档回放与提示","data-engineer","04总序/v2存档、protocol-vectors.json","implementation/data/Persistence.ts","身份/去重先于BUSY/STALE，失败缓存，缓存0事件保存；恢复新epoch，128窗口/撤销，4096终点checkpoint首条UNDO，UNKNOWN", "npm run test:persistence; npm run test:replay"),
 ("T06","build",["T03"],"原创音画与许可证入库","artist","06逐项资产预算、08许可","implementation/art/asset-ledger.json","每项作者/源文件/hash/授权；音画尺寸与字体子集正确；无参考游戏专有表达", "人工逐项核对asset-ledger；npm run check:assets"),
 ("T07","build",["T04","T06"],"全部屏幕与输入","ui-engineer","06坐标/03玩家路径、layout-cases.json","implementation/ui/GameShell.ts","11屏、320×568含safe/font1.3/小横屏，PLAY6盘无滚动，44CSS热区、菜单单owner、真实字体测量及触控、减少动效", "npm run test:ui"),
 ("T08","build",["T04","T05","T07"],"20关与单因子实验","game-designer","05关表、12实验计划","implementation/content/experiment-config.json","默认顺序、V0/X1/X2互斥试验组、采集无第三方统计", "npm run test:levels; python tools/verify.py --all"),
 ("T09","build",["T03"],"P02独立适配","platform-engineer-p02","07、11、E04/E05","implementation/platforms/p02/Adapter.ts","Basic无变现；Full强制SDK；生命周期与音频；250MB/1500文件/无SDK50MB/移动20MB", "npm run test:platform -- P02; npm run check:bundle -- P02"),
 ("T10","build",["T03"],"P04独立适配","platform-engineer-p04","07、11、E06/E07","implementation/platforms/p04/Adapter.ts","Bridge存档/生命周期；零GA4/外部统计；横竖屏和所有弹窗关闭", "npm run test:platform -- P04; npm run test:network -- P04"),
 ("T11","build",["T05","T07","T08","T09","T10"],"Web集成和浏览器真机矩阵","qa-engineer","10测试矩阵","implementation/qa/web-results.json","全部自动检查与实际设备记录；实测下载/性能；无凭空通过", "npm run test:integration; npm run test:browser; npm run check:bundle"),
 ("T12","build",["T11"],"盲测与可证伪决策","ux-researcher","12抽样阈值与本地事件","implementation/qa/player-study.md","记录分母、设备、退出和变体；按阈值REVISION/KILL；真实结果保留", "人工执行12盲测协议并核对本地导出记录"),
 ("T13","review",["T02"],"P05 SDK书面条件核实","publisher-liaison-p05","11问题单、另行受权后P05答复","audit/p05-sdk-confirmation.md","仅P05明确引擎/SDK/版本/数据权/签名/包形；不代表P06；本轮不联系外部", "核对P05书面条件；无答复维持BLOCKED"),
 ("T14","build",["T03","T04","T05","T06","T13"],"P05原生分支与实际安装研究","mobile-engineer-p05","P05书面条件、规则和原创资产","implementation/mobile/p05/native-feasibility.md","仅P05：选择可接SDK的Cocos原生或独立移植；完整移动UI/签名安装/崩溃前后台/SDK/隐私/性能及移动盲测证据", "P05指定构建安装命令待T13确认，未确认不得执行"),
 ("T15","release",["T11","T12"],"P02/P04网页发行审批","release-reviewer-web","11合同字段、许可证和网页真实QA","audit/web-release-gate.md","仅P02/P04，分别用户批准渠道提交；权利无冲突；不代表P05/P06；不自动提交", "分别核对P02/P04当前条款、真实QA及书面批准"),
 ("T16","review",["T02"],"P06 SDK书面条件核实","publisher-liaison-p06","11问题单、另行受权后P06答复","audit/p06-sdk-confirmation.md","仅P06确认引擎/SDK/版本/权利/签名/包形；不继承P05确认；本轮不联系外部", "核对P06书面条件；无答复维持BLOCKED"),
 ("T17","build",["T03","T04","T05","T06","T16"],"P06原生分支与实际安装研究","mobile-engineer-p06","P06专属书面条件、规则和原创资产","implementation/mobile/p06/native-feasibility.md","仅P06：引擎SDK可行性、完整移动UI/原生签名安装/生命周期/隐私/性能/移动盲测；Web构建不作APK证据", "P06指定构建安装命令待T16确认，未确认不得执行"),
 ("T18","release",["T13","T14"],"P05移动发行单独审批","release-reviewer-p05","P05 SDK确认/原生QA/移动盲测/权利合同","audit/p05-release-gate.md","P05书面条件、T14真实结果、渠道权利和人类提交批准全部满足；独立于Web和P06", "人工核对P05专属条件，UNKNOWN不能通过"),
 ("T19","release",["T16","T17"],"P06移动发行单独审批","release-reviewer-p06","P06 SDK确认/原生QA/移动盲测/权利合同","audit/p06-release-gate.md","P06书面条件、T17真实结果、渠道权利和人类提交批准全部满足；不得复用P05批准", "人工核对P06专属条件，UNKNOWN不能通过")
]
tasks=[]
for tid,phase,deps,title,owner,inputs,output,dod,test in task_rows:
    tasks.append({"id":tid,"phase":phase,"title":title,"owner_role":owner,"depends_on":deps,
        "status":"PENDING_RE_REVIEW" if tid=="T01" else "BLOCKED_BY_GATE",
        "inputs":[inputs],"outputs":["games/G02/"+output],"definition_of_done":[dod],
        "verification_commands":[test],"execution_status":"NOT_EXECUTED",
        "estimated_hours_hypothesis": 2 if phase=="review" else 6,
        "gate":"external_contact_requires_separate_user_authorization" if tid in ("T13","T16") else "build_requires_T02" if phase=="build" else "no_automatic_publication",
        "platform_ids": ["P05"] if tid in ("T13","T14","T18") else ["P06"] if tid in ("T16","T17","T19") else ["P02","P04"] if tid in ("T09","T10","T11","T12","T15") else ["P02","P04","P05","P06"],
        "required_conditions": (["p05_sdk_written","p05_native_qa","p05_mobile_study","p05_rights_clear","p05_human_submit_approval"] if tid=="T18" else
            ["p06_sdk_written","p06_native_qa","p06_mobile_study","p06_rights_clear","p06_human_submit_approval"] if tid=="T19" else
            ["p02_p04_rights_clear","web_device_qa","per_channel_human_submit_approval"] if tid=="T15" else
            ["p05_sdk_written"] if tid=="T14" else ["p06_sdk_written"] if tid=="T17" else []),
        "verified_conditions": []})
tasks[8]["platform_ids"] = ["P02"]
tasks[9]["platform_ids"] = ["P04"]
taskdata={"schema_version":"1.1.0","project_id":"G02","date":"2026-10-21",
    "planning_only":True,"tasks":tasks,"command_policy":"Preparation Python verifiers and packaging only; npm/Creator/mobile commands are future contracts, NOT_EXECUTED"}
write("tasks.json",taskdata)
task_schema=obj({"schema_version":{"const":"1.1.0"},"project_id":{"const":"G02"},"date":{"type":"string","format":"date"},
    "planning_only":{"const":True},"command_policy":S,"tasks":{"type":"array","minItems":19,"maxItems":19,
        "items":obj({"id":{"type":"string","pattern":"^T(0[1-9]|1[0-9])$"},"phase":{"enum":["review","build","release"]},
        "title":S,"owner_role":S,"depends_on":{**STRINGS,"uniqueItems":True},
        "status":{"enum":["PENDING_RE_REVIEW","BLOCKED_BY_GATE"]},"inputs":{**STRINGS,"minItems":1},
        "outputs":{"type":"array","minItems":1,"items":{"type":"string","pattern":"^games/G02/[^.].*"}},
        "definition_of_done":{**STRINGS,"minItems":1},"verification_commands":{**STRINGS,"minItems":1},
        "execution_status":{"const":"NOT_EXECUTED"},"estimated_hours_hypothesis":I,"gate":S,
        "platform_ids":{"type":"array","minItems":1,"uniqueItems":True,"items":{"enum":["P02","P04","P05","P06"]}},
        "required_conditions":{**STRINGS,"uniqueItems":True},"verified_conditions":{"const":[]}})}})
task_schema.update({"$schema":"https://json-schema.org/draft/2020-12/schema","title":"G02 task DAG v1"})
write("tasks.schema.json",task_schema)
write_contract_fixtures()
