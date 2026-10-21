"""Preparation data authoring only. No game runtime, UI, engine or network."""
from pathlib import Path
import json
from contracts import CAMPAIGN_IDS, LEGAL_ORDER, COMMIT_ORDER, SESSION_CONTRACT, MAX_REVISION, TUTORIAL_IDS

ROOT = Path(__file__).resolve().parents[1]

def put(name, value):
    (ROOT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def arrow(name, direction, cells, toggles=()):
    return dict(id=name, direction=direction, cells=cells, toggles=list(toggles))

def gate(name, cells, opened=False):
    return dict(id=name, cells=cells, initial_open=opened)

def level(num, name, mode, size, arrows, solution, objective, gates=(), walls=(), manifest=()):
    return dict(id=f'L{num:02}', name=name, evidence_status='HYPOTHESIS', mode=mode,
                width=size[0], height=size[1], arrows=arrows, gates=list(gates), walls=list(walls),
                manifest=list(manifest), initial_state=dict(removed=[], manifest_cursor=0),
                win=dict(all_arrows_removed=True, manifest_consumed=True),
                solution=[dict(type='EXIT', arrow_id=x) for x in solution.split()],
                learning_objective=objective, seed=10100+num,
                target_seconds=[10+num*3, 25+num*6])

A=arrow; G=gate; L=level
levels=[
L(1,'开港','BASE',(4,4),[A('a','E',[[1,1],[2,1]]),A('b','N',[[1,3],[1,2]])],'a b','点击整条箭头，清空棋盘'),
L(2,'先疏后发','BASE',(5,4),[A('a','E',[[0,1],[1,1]]),A('b','N',[[3,2],[3,1]]),A('c','W',[[2,3],[1,3]])],'b a c','路径被另一箭条占用时先移除阻挡者'),
L(3,'弯条也要净空','BASE',(5,5),[A('a','E',[[0,1],[0,2],[1,2]]),A('b','N',[[3,2],[3,1]]),A('c','S',[[4,3],[4,4]]),A('d','W',[[2,4],[1,4]])],'b a c d','弯条整体平移，尾部的扫掠也算碰撞'),
L(4,'交叉码头','BASE',(6,6),[A('a','E',[[0,1],[1,1]]),A('b','N',[[3,2],[3,1]]),A('c','W',[[5,4],[4,4]]),A('d','S',[[2,3],[2,4]]),A('e','E',[[0,5],[1,5]])],'b a d c e','两组依赖、可自由交换的独立操作',walls=[[5,0]]),
L(5,'第一盏信号','RELAY',(5,5),[A('a','E',[[0,1],[1,1]]),A('b','E',[[2,3],[3,3]],['g'])],'b a','带 g 印记箭条离港后翻转 g 门',gates=[G('g',[[3,1]])]),
L(6,'开门之前','RELAY',(6,5),[A('a','E',[[0,1],[1,1]]),A('b','N',[[3,2],[3,1]]),A('c','E',[[0,4],[1,4]],['g'])],'c b a','几何遮挡和门遮挡同时检查',gates=[G('g',[[5,1]])]),
L(7,'双灯串联','RELAY',(6,6),[A('a','E',[[0,1],[1,1]]),A('b','N',[[3,5],[3,4]],['h']),A('c','E',[[0,2],[1,2]],['g'])],'c b a','g 放行 b，b 再打开 h 给 a',gates=[G('g',[[3,3]]),G('h',[[4,1]])]),
L(8,'不要连按开关','RELAY',(5,5),[A('a','E',[[0,1],[1,1]]),A('b','E',[[2,3],[3,3]],['g']),A('c','W',[[2,4],[1,4]],['g'])],'b a c','两次翻转关门；合法操作也可能造成残局死锁',gates=[G('g',[[3,1]])]),
L(9,'两门交替','RELAY',(6,6),[A('a','E',[[0,1],[1,1]],['h']),A('b','N',[[4,5],[4,4]]),A('c','E',[[0,3],[1,3]],['g']),A('d','W',[[2,5],[1,5]],['g'])],'c a b d','先用 g 通行，再交付 h；提前 d 会关 g',gates=[G('g',[[3,1]]),G('h',[[4,2]])]),
L(10,'弯桥继电','RELAY',(7,6),[A('a','E',[[0,1],[0,2],[1,2]],['h']),A('b','N',[[5,5],[5,4]]),A('c','E',[[0,0],[1,0]],['g']),A('d','W',[[2,5],[1,5]],['g']),A('e','S',[[6,4],[6,5]])],'c a b d e','弯条尾部、两组门和独立安全出口',gates=[G('g',[[4,1]]),G('h',[[5,3]])]),
L(11,'船期单','MANIFEST',(5,5),[A('a','E',[[0,1],[1,1]]),A('b','N',[[3,4],[3,3]]),A('c','W',[[2,4],[1,4]])],'a b c','必须按右、上、左出港',manifest=['E','N','W']),
L(12,'先清航线','MANIFEST',(5,5),[A('a','E',[[0,1],[1,1]]),A('b','N',[[3,2],[3,1]]),A('c','S',[[4,3],[4,4]])],'b a c','船期和几何依赖一致，错误方向不会消耗步数',manifest=['N','E','S']),
L(13,'同向二选一','MANIFEST',(5,5),[A('a','N',[[1,1]]),A('b','N',[[3,3],[3,2]]),A('c','E',[[0,2],[1,2]])],'b c a','第一步两条朝上，先 a 会让下一条朝右无法离港',manifest=['N','E','N']),
L(14,'两次交接','MANIFEST',(6,6),[A('a','N',[[1,1]]),A('b','N',[[4,3],[4,2]]),A('c','E',[[0,2],[1,2]]),A('d','S',[[2,4],[2,5]]),A('e','W',[[5,4],[4,4]])],'b c a d e','同向选择后再处理另一组阻挡',manifest=['N','E','N','S','W']),
L(15,'曲线船期','MANIFEST',(7,6),[A('a','E',[[0,1],[0,2],[1,2]]),A('b','N',[[4,2],[4,1]]),A('c','S',[[6,4],[6,5]]),A('d','W',[[3,4],[2,4]]),A('e','N',[[1,5]])],'b a c d e','弯条放行后按五项船期完成',manifest=['N','E','S','W','N']),
L(16,'灯号与船期','COMBINED',(5,5),[A('a','E',[[0,1],[1,1]]),A('b','N',[[4,4],[4,3]],['g']),A('c','W',[[2,4],[1,4]],['g'])],'b a c','识别船期与门依次放行；唯一合法路线用于组合教学，不作为二选一规划题',gates=[G('g',[[3,1]])],manifest=['N','E','W']),
L(17,'同向不同信号','COMBINED',(6,6),[A('a','N',[[1,1]]),A('b','N',[[4,5],[4,4]],['g']),A('c','E',[[0,2],[1,2]])],'b c a','两条朝上只有 b 能打开下一班的门',gates=[G('g',[[3,2]])],manifest=['N','E','N']),
L(18,'双灯船队','COMBINED',(6,6),[A('a','E',[[0,1],[1,1]],['h']),A('b','N',[[4,5],[4,4]]),A('c','E',[[0,3],[1,3]],['g']),A('d','W',[[2,5],[1,5]],['g'])],'c a b d','两条朝右对象中初态仅c合法，辨认g阻挡a；不是两个合法候选的选择题',gates=[G('g',[[3,1]]),G('h',[[4,2]])],manifest=['E','E','N','W']),
L(19,'双信号分流','COMBINED',(7,7),[A('a','E',[[0,1],[0,2],[1,2]],['h']),A('b','N',[[5,6],[5,5]]),A('c','E',[[0,4],[1,4]],['g']),A('d','W',[[3,6],[2,6]],['g','h']),A('e','S',[[6,5],[6,6]]),A('f','W',[[3,0],[2,0]])],'c a b d e f','辨认提交后多门翻转；船期保护排除无船期的16个losing状态，不宣称组合必增策略',gates=[G('g',[[4,1]]),G('h',[[5,3]])],manifest=['E','E','N','W','S','W']),
L(20,'最后一班','COMBINED',(7,7),[A('a','N',[[1,1]]),A('b','N',[[4,4],[4,3]],['g']),A('c','E',[[0,2],[1,2]],['h']),A('d','N',[[6,6],[6,5]]),A('e','W',[[3,6],[2,6]],['g']),A('f','S',[[1,4],[1,5]]),A('z','W',[[3,0],[2,0]],['h'])],'b c a d e f z','两次同向选择与门闭合时机；计划七次离港',gates=[G('g',[[3,2]]),G('h',[[6,3]])],manifest=['N','E','N','N','W','S','W'])
]

spec=dict(spec_version='1.0.0',game_id='G01',working_title='信号港 / Signal Harbor',
    status='REVISION_REQUIRED',ready_for_build=False,independent_review='RECHECK_PENDING',human_build_approval=False,
    preparation_date='2026-10-21',all_design_values='HYPOTHESIS',
    candidate_platform_ids=['P02','P04','P05'],audience='16+ logic-puzzle players; not child-directed',
    engine=dict(name='Cocos Creator',candidate_version='3.8.8',language='TypeScript',
        version_source='https://www.cocos.com/en/creator-download',checked_date='2026-10-21',
        installation='NOT_VERIFIED; executable not found on PATH',build_tested=False),
    rules=dict(coordinates='integer x right, y down; origin top-left; 0<=x<width,0<=y<height',
        arrow_shape='ordered distinct orthogonally adjacent cells, tail to head; last segment equals direction; singleton allowed',
        movement='rigid translation of ALL occupied cells by heading vector; no snake-following, rotation or partial movement',
        collision='union of in-bounds translated cells for k=1..max(width,height), against other remaining arrows, walls and CLOSED gates; own initial cells ignored',
        exit_edge='direction alone determines edge; any coordinate on that edge is valid',
        legal_order=list(LEGAL_ORDER),
        commit_order=list(COMMIT_ORDER),
        gate_semantics='initial_open XOR removed-arrow toggles; gates never rotate or move; open gates are passable and never occupy an initial arrow cell',
        manifest_semantics='empty disables; otherwise one direction per arrow; next direction must match; no skip and no wildcard',
        invalid_action='state unchanged; no hearts, time limit, currency or loss of attempt',
        deadlock='remaining>0 AND no legal EXIT; undo/reset enabled; no ad rescue',
        win='all arrows removed AND manifest cursor == manifest length',
        undo='pop last accepted EXIT; recompute gates and manifest from original data and remaining log; no redo',
        hint='lexicographically first arrow whose successor can reach win; no legal winning successor => show undo/reset',
        rng='none in play; level seed is provenance only',canonical_state_key='removed bitmask; gates and cursor derived'),
    variants=[dict(id='BASE',relay=False,manifest=False),dict(id='RELAY',relay=True,manifest=False),dict(id='MANIFEST',relay=False,manifest=True),dict(id='COMBINED',relay=True,manifest=True)],
    session_contract=SESSION_CONTRACT,
    progression=dict(order=list(CAMPAIGN_IDS),unlock='L01 open; L(n+1) after first completion Ln; all completed replayable',
        rewards='one first-clear stamp per level, replay gives none; stamp count derived from completed-level set',
        hint_cost=0,undo_cost=0,retry_cost=0,ads='disabled in initial product; Full/P04 adapter ad capability reserved but not activated',
        end='after L20 show all 20 stamps and replay/map buttons; no endless or daily mode'),
    ui=dict(screens=['BOOT','HOME','MAP','PLAY','PAUSE','HELP','DEADLOCK','WIN','COMPLETE','SETTINGS','CREDITS','RECOVERY','ERROR'],
        portrait_reference=[390,844],landscape_reference=[844,390],min_viewport=[320,360],
        touch_min_css_px=44,pointer_commit='pointerup on same arrow after <=10 CSS px movement, pointercancel cancels; no hold timer',
        keyboard='Tab focus by arrow ID then controls; Enter/Space activate; U undo; H hint; R opens reset confirmation; Escape pause/back',
        palette=dict(background='#101F2B',surface='#193546',arrow='#F4EBD0',signal_g='#F0B75E',signal_h='#62C9CB',error='#F27578'),
        reduced_motion=True,default_music=False,default_sound=True,languages=['en','zh-CN']),
    save=dict(version=1,key='G01.signalharbor.{profile}.v1',fields=['version','content_version','revision','completed','active_level','accepted_exits','tutorial_seen','settings'],
        authoritative='accepted_exits replay; never trust stored gates/cursor',
        commit='temp JSON -> validate -> backup old -> main; recover newest valid revision; local commit after every EXIT/UNDO/RESET/WIN/settings',
        migration='v0 absent starts new; v1 strict validation; unknown newer version read-only recovery, never overwrite automatically',
        cloud='same channel only; union completed and choose newest valid active revision; equal revision conflict prompts user; no device fingerprint',
        private_mode='memory-only with visible notice; no blocking gameplay',envelope_schema='save-envelope.schema.json'),
    channel_profiles=[
      dict(id='LOCAL_QA',sdk='none',analytics='local opt-in bounded replay, no upload',ads=False,total_mb_cap=15,file_cap=250),
      dict(id='P02_BASIC',sdk='none',analytics='platform-native outside bundle; no third-party SDK',ads=False,total_mb_cap=20,file_cap=250),
      dict(id='P02_FULL',sdk='CrazyGames required',analytics='CrazyGames SDK only',ads=False,total_mb_cap=250,file_cap=1500),
      dict(id='P04',sdk='Playgama Bridge required',analytics='Bridge only; no GA4 or equivalent',ads=False,total_mb_cap=300,file_cap=250),
      dict(id='P05',sdk='UNKNOWN pending written mobile compatibility',analytics='none until publisher-specific isolated contract approval',ads=False,total_mb_cap=100,file_cap=250),
      dict(id='P01_RESERVED',sdk='none',analytics='none; no developer callback',ads=False,total_mb_cap=15,file_cap=250)],
    performance_hypotheses=dict(total_web_mb=15,initial_web_mb=8,frame_p95_ms=20.0,input_feedback_p95_ms=100,
        local_solver_max_states=256,local_solver_budget_ms=50,measured=False),
    levels=levels)
if [l['id'] for l in levels]!=list(CAMPAIGN_IDS):
    raise ValueError('CAMPAIGN_SEQUENCE: generator requires exact unique L01..L20')
put('game-spec.json',spec)

def task(tid,title,deps,role,files,inputs,outputs,dod,verify,stage='AFTER_HUMAN_BUILD_APPROVAL',gate_name='BUILD_APPROVAL'):
    return dict(id=tid,title=title,depends_on=deps,role=role,write_scope='games/G01/',files=files,inputs=inputs,outputs=outputs,
                definition_of_done=dod,verification=verify,stage=stage,approval_gate=gate_name,status='NOT_STARTED')
tasks=[
task('T01','接收主控独立审计并关闭整改',[],'G01 author; independent audit owned by controller',['audit/review-remediation.md'],['00–12','game-spec.json','tasks.json','READ_ONLY external reviews/G01-audit.md'],['主控独立审计只读引用','逐项修订与复验闭环'],['独立审计由主控写reviews/G01-audit.md，作者不代写代签','冷读能复述规则和接口','阻断关闭有可核查证据，本地自检不代替独立审计'],['核对主控独立审计与整改复验'],stage='PREPARATION',gate_name='NONE'),
task('T02','人类批准档案与游戏 ID',['T01'],'human owner',['audit/approval-record.md'],['独立审计与修订版'],['明确 G01、版本、允许开发范围'],['全部阻断关闭','明确书面开发许可'],['人工核对批准记录'],stage='DECISION',gate_name='HUMAN'),
task('T03','安装锁版与引擎许可核验',['T02'],'toolchain engineer',['future/toolchain/'],['07','08'],['3.8.8 编辑器校验和','许可清单','TS编译器确切版本'],['Dashboard 来源可追溯','命令行构建最小空项目成功','不将MIT引擎等同编辑器许可'],['Creator --version','导出空 Web 测试'],gate_name='BUILD_APPROVAL'),
task('T04','确定性规则事实与测试向量',['T03'],'rules engineer',['future/rules/','future/tests/rules/'],['03','04','game-spec.json','validation/report.json','contracts/session-vectors.json'],['纯规则RuleFacts/UndoFacts类型与TS规则','Python/TS一致性报告'],['20关每一步状态一致','RuleFacts不得含eventId/firstClear/stampCount或发布总线','相同Attempt不同completed历史返回相同规则事实','全扫掠/门时序/死锁/非法操作一致'],['未来 npm run test:rules']),
task('T05','原创视觉音频生产',['T02'],'asset artist',['future/assets/','future/assets/licenses/'],['06','08'],['全部资产源文件与导出','逐文件权属'],['清单无缺项','文本可读','禁用对标截图/图形/音效'],['人工视觉听觉检查','逐文件SHA256']),
task('T06','Session状态机总线与UI装配',['T04','T05'],'application/UI engineer',['future/session/','future/app-state/','future/events/','future/ui/','future/scenes/','future/tests/session/'],['06','04','game-spec.json/session_contract','contracts/session-vectors.json'],['SessionCoordinator与SessionBus唯一publisher','应用状态机与RuleFacts富化','13屏/输入装配','SavePort接口'],['Session唯一分配eventId并发布含进度的事件','同局面不同历史与胜利撤销再完成向量通过','每接受revision仅一个SaveRequested，回执不触发新保存','44px触区、键盘等价、返回路径、门形状编码'],['未来 npm run test:session','未来 npm run test:ui']),
task('T07','存档与恢复传输',['T06'],'persistence engineer',['future/save/','future/tests/save/'],['04','save-envelope.schema.json','contracts/save-vectors.json','T06 SavePort'],['v1原子本地存档传输','恢复结果返回Session的接口'],['不自行发布事件/计算首通/修改revision','固定合法非法存档向量通过','断写/配额/版本异常覆盖','云冲突不静默丢失'],['未来 npm run test:save']),
task('T08','20关进度与Session存档集成',['T04','T06','T07'],'campaign integrator',['future/content/','future/tutorial/','future/progress/','future/integration/','future/tests/campaign/'],['05','04','game-spec.json','contracts/session-vectors.json','contracts/save-vectors.json'],['Progress首通集合策略供Session唯一调用','Session/SavePort/20关端到端装配','首通印章与结束页'],['关序锁与重玩正确','同规则事实不同历史载荷正确','胜利撤销再完成/动画中断不重复章或提交保存','20关映射哈希一致','无付费/广告墙'],['未来 npm run test:campaign','未来 npm run test:session']),
task('T09','本地浏览器真机性能',['T08'],'QA engineer',['future/qa/local/'],['07','10'],['原始测量日志','设备与浏览器版本'],['包体/文件数/首屏/帧率实际记录','未知不得填通过','WebGL丢失可恢复'],['未来 npm run test:web','真机矩阵']),
task('T10','盲测及两变体消融',['T09'],'research QA',['future/qa/players/'],['12'],['同意记录与匿名原始数据','BASE/RELAY/MANIFEST比较'],['达到预注册样本或标不足','区分误触与规则不懂','不虚报留存'],['人工按12章协议分析']),
task('T11','渠道合同与权利隔离',['T10'],'business reviewer',['future/business/'],['11','08'],['每渠道权利矩阵','停止/继续建议'],['列明IP保留/排他/回收/退出','缺正文不得提交'],['人工逐条合同审查']),
task('T12','P02 Basic 独立包',['T09','T11'],'P02 adapter engineer',['future/platforms/P02_BASIC/'],['07','11'],['无SDK无广告Basic包','网络白名单QA'],['<=20MB总包','无第三方回传','PEGI12且非儿童定位','<=1500文件'],['未来 npm run build:p02-basic','网络抓包']),
task('T13','P04 独立 Bridge 包',['T09','T11'],'P04 adapter engineer',['future/platforms/P04/'],['07','11'],['Bridge包','平台统计接口验证'],['无GA4等统计','无P02SDK','root index.html','<=300MB','拒绝外部登录依赖'],['未来 npm run build:p04','Bridge QA与抓包']),
task('T14','P05 SDK可行性与原生试包',['T09','T11'],'mobile engineer',['future/platforms/P05/'],['07','11'],['SDK书面支持记录','Android试包或停止报告'],['Cocos支持必须确认','不得把Web包当APK','ABI/16KB内存页实际检验'],['未来指定SDK样例编译','Android真机检查']),
task('T15','各渠道提交前资料与最终闸门',['T12','T13','T14'],'release manager',['future/release/'],['10','11'],['逐渠道截图视频版权表','提交建议'],['所有拟提交渠道分别QA','某渠道停止可用正式停止报告结项','人类批准后才可对外提交'],['人工逐包签核'],gate_name='SEPARATE_SUBMISSION_APPROVAL'),
task('T16','P02 Full SDK 升级（条件分支）',['T12'],'P02 adapter engineer',['future/platforms/P02_FULL/'],['正式Full邀请','最新SDK文档'],['Full专用包','生命周期事件验证'],['只有正式邀请后启动','Full SDK必须','初始<=50MB/移动<=20MB','总<=250MB/1500文件','产品仍默认无广告'],['未来 npm run build:p02-full','平台Full QA'],stage='AFTER_FULL_INVITATION',gate_name='FULL_INVITATION')]
put('tasks.json',dict(version='1.0.0',game_id='G01',scope='games/G01/',status='PLANNED_ONLY',tasks=tasks))

def obj(props,required=None):
    return dict(type='object',properties=props,required=list(props) if required is None else required,additionalProperties=False)
def arr(items,min_items=0,max_items=None):
    out=dict(type='array',items=items,minItems=min_items)
    if max_items is not None: out['maxItems']=max_items
    return out
S=dict(type='string',minLength=1); B=dict(type='boolean'); I=dict(type='integer',minimum=0)
D=dict(enum=['N','E','S','W']); ID=dict(type='string',pattern='^[a-z][a-z0-9_]*$')
cell=dict(type='array',prefixItems=[I,I],items=False,minItems=2,maxItems=2)
astr=arr(S); aunique=dict(type='array',items=ID,uniqueItems=True)
arrow_schema=obj(dict(id=ID,direction=D,cells=arr(cell,1,8),toggles=aunique))
gate_schema=obj(dict(id=ID,cells=arr(cell,1,8),initial_open=B))
lv=obj(dict(id=dict(type='string',pattern='^L(0[1-9]|1[0-9]|20)$'),name=S,evidence_status=dict(const='HYPOTHESIS'),
    mode=dict(enum=['BASE','RELAY','MANIFEST','COMBINED']),width=dict(type='integer',minimum=4,maximum=7),height=dict(type='integer',minimum=4,maximum=7),
    arrows=arr(arrow_schema,2,8),gates=arr(gate_schema,0,2),walls=arr(cell),manifest=arr(D,0,8),
    initial_state=obj(dict(removed=dict(const=[]),manifest_cursor=dict(const=0))),
    win=obj(dict(all_arrows_removed=dict(const=True),manifest_consumed=dict(const=True))),
    solution=arr(obj(dict(type=dict(const='EXIT'),arrow_id=ID)),2,8),learning_objective=S,seed=I,
    target_seconds=dict(type='array',items=dict(type='integer',minimum=1),minItems=2,maxItems=2)))
props={
 'spec_version':dict(const='1.0.0'),'game_id':dict(const='G01'),'working_title':S,'status':dict(const='REVISION_REQUIRED'),
 'ready_for_build':dict(const=False),'independent_review':dict(const='RECHECK_PENDING'),'human_build_approval':dict(const=False),
 'preparation_date':dict(const='2026-10-21'),'all_design_values':dict(const='HYPOTHESIS'),
 'candidate_platform_ids':dict(const=['P02','P04','P05']),'audience':S,
 'engine':obj(dict(name=dict(const='Cocos Creator'),candidate_version=dict(const='3.8.8'),language=dict(const='TypeScript'),version_source=S,checked_date=S,installation=S,build_tested=dict(const=False))),
 'rules':obj({k:(dict(type='array',const=list(LEGAL_ORDER if k=='legal_order' else COMMIT_ORDER)) if k in ['legal_order','commit_order'] else S) for k in spec['rules']}),
 'session_contract':obj({k:dict(const=v) for k,v in SESSION_CONTRACT.items()}),
 'variants':arr(obj(dict(id=dict(enum=['BASE','RELAY','MANIFEST','COMBINED']),relay=B,manifest=B)),4,4),
 'progression':obj(dict(order=dict(type='array',const=list(CAMPAIGN_IDS),uniqueItems=True,minItems=20,maxItems=20),unlock=S,rewards=S,hint_cost=dict(const=0),undo_cost=dict(const=0),retry_cost=dict(const=0),ads=S,end=S)),
 'ui':obj(dict(screens=arr(S,13,13),portrait_reference=cell,landscape_reference=cell,min_viewport=cell,touch_min_css_px=dict(const=44),pointer_commit=S,keyboard=S,palette=obj({k:S for k in spec['ui']['palette']}),reduced_motion=B,default_music=B,default_sound=B,languages=dict(const=['en','zh-CN']))),
 'save':obj({k:(I if isinstance(v,int) else astr if isinstance(v,list) else S) for k,v in spec['save'].items()}),
 'channel_profiles':arr(obj(dict(id=dict(enum=['LOCAL_QA','P02_BASIC','P02_FULL','P04','P05','P01_RESERVED']),sdk=S,analytics=S,ads=dict(const=False),total_mb_cap=dict(type='integer',minimum=1),file_cap=dict(type='integer',minimum=1))),6,6),
 'performance_hypotheses':obj({k:(dict(const=False) if k=='measured' else dict(type='number',minimum=0)) for k in spec['performance_hypotheses']}),
 'levels':dict(type='array',minItems=20,maxItems=20,items=False,prefixItems=[dict(allOf=[{'$ref':'#/$defs/level'},dict(properties=dict(id=dict(const=i)))]) for i in CAMPAIGN_IDS])}
put('game-spec.schema.json',dict({'$schema':'https://json-schema.org/draft/2020-12/schema','$id':'urn:foundry:G01:game-spec:1.0.0','$defs':dict(level=lv)},**obj(props)))
tprops=dict(id=dict(type='string',pattern='^T[0-9]{2}$'),title=S,depends_on=dict(type='array',items=dict(type='string',pattern='^T[0-9]{2}$'),uniqueItems=True),role=S,write_scope=dict(const='games/G01/'),files=arr(S,1),inputs=arr(S,1),outputs=arr(S,1),definition_of_done=arr(S,1),verification=arr(S,1),stage=dict(enum=['PREPARATION','DECISION','AFTER_HUMAN_BUILD_APPROVAL','AFTER_FULL_INVITATION']),approval_gate=dict(enum=['NONE','HUMAN','BUILD_APPROVAL','SEPARATE_SUBMISSION_APPROVAL','FULL_INVITATION']),status=dict(const='NOT_STARTED'))
put('tasks.schema.json',dict({'$schema':'https://json-schema.org/draft/2020-12/schema','$id':'urn:foundry:G01:tasks:1.0.0'},**obj(dict(version=dict(const='1.0.0'),game_id=dict(const='G01'),scope=dict(const='games/G01/'),status=dict(const='PLANNED_ONLY'),tasks=arr(obj(tprops),16,16)))))
save_schema=obj(dict(version=dict(type='integer',const=1),content_version=dict(type='string',const='1.0.0'),revision=dict(type='integer',minimum=0,maximum=MAX_REVISION),completed=dict(type='array',items=dict(enum=list(CAMPAIGN_IDS)),uniqueItems=True,maxItems=20),active_level=dict(enum=list(CAMPAIGN_IDS)),accepted_exits=dict(type='array',items=ID,uniqueItems=True,maxItems=8),tutorial_seen=dict(type='array',items=dict(enum=list(TUTORIAL_IDS)),uniqueItems=True,maxItems=4),settings=obj(dict(language=dict(enum=['en','zh-CN']),sound=B,music=B,reducedMotion=B))))
put('save-envelope.schema.json',dict({'$schema':'https://json-schema.org/draft/2020-12/schema','$id':'urn:foundry:G01:save-envelope:1.0.0'},**save_schema))
print('Authored 20 level records, complete spec, 16 planned tasks and three strict schemas including SaveEnvelope.')
