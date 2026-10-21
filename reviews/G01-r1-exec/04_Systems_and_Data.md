# G01 系统、事件与数据合同

全部接口为待施工设计 **HYPOTHESIS**，不是游戏源码。本包只有离线数据/合同验证工具。规则见03，具体坐标与解见game-spec；不一致即阻断，不许实现者择一。

## 实体与规则权威

| 实体 | 字段 | 不变量 |
|---|---|---|
| Level | id、width/height、arrows、gates、walls、manifest、seed | 正式集合及数组次序精确L01..L20，各出现一次；尺寸4—7；箭条2—8；门0—2；seed不参与运行随机 |
| Arrow | id、direction:N/E/S/W、cells:[x,y][]、toggles:gateId[] | 1—8格、正交连续、无重复；末段=方向；关内ID唯一；引用门存在、不重复 |
| Gate | id、cells、initial_open:boolean | 与初始箭条/墙/其他门格不重叠；仅关闭时阻挡；不移动 |
| Attempt | levelId、acceptedExits:arrowId[]、revision | 日志逐步合法；每箭至多一次；撤销删尾、reset清空 |
| DerivedState | removedMask:uint8、gateOpen、manifestCursor、legalMoves、solvable、terminal | 从Level+日志导出，不落盘为权威；mask为0..2^n−1 |
| Progress | completed、activeLevel、tutorialSeen | completed为L01起连续前缀；stampCount=集合大小；已完成可重玩 |
| Settings | language:en/zh-CN、sound、music、reducedMotion | 三开关为boolean；首次未知locale回英文；sound默认on、music默认off、弱动效遵循系统 |

拒绝未知键、NaN、负/浮点/越界坐标、断裂折线、重复ID、重复占用/toggle、坏引用、非空manifest长度不等箭条数。schema负责形状，独立语义检查负责引用、几何、可解性；schema通过不等于内容合法。game-spec.schema对levels各位置ID和progression.order作const约束；tools/contracts.py及语义检查另验唯一集合与固定次序。

固定规则合同的拒绝优先级：UNKNOWN_OR_REMOVED → MANIFEST_MISMATCH → ARROW_COLLISION → WALL_COLLISION → CLOSED_GATE。提交阶段精确依次为：①提交前完整扫掠校验；②移除；③各列出门XOR一次；④非空船期游标推进；⑤先胜利再死锁；⑥持久逻辑快照入串行队列；⑦动画。03、game-spec.rules、schema const及离线语义检查同步绑定；不能靠先翻门救自己。

## 纯规则返回与Session交接

未来接口声明（本轮不实现）：

```text
validateLevel(Level) -> ValidationIssue[]
derive(Level, acceptedExits[]) -> State | InvalidReplay(index, reason)
evaluateExit(Level, State, arrowId) -> Legal | Reject(reason, blockerCell?, blockerId?)
commitExit(Level, Attempt, arrowId, expectedRevision) -> Accepted(nextAttempt, RuleFacts) | Reject
undo(Level, Attempt, expectedRevision) -> Accepted(nextAttempt, UndoFacts) | Reject
solve(Level, State) -> {solvable, firstWinningArrow?, solution[], visitedCount}
SavePort.persist(snapshot, requestKey) -> Promise<{snapshotRevision,persisted,errorCode?}>
```

RuleFacts精确字段：`kind="ExitAccepted",level_id,arrow_id,from_mask,to_mask,gate_changes:[{id,was_open,is_open}],manifest_cursor,won,deadlocked`；gate_changes按门ID排序。UndoFacts为 `kind="UndoAccepted",level_id,from_mask,to_mask,won,deadlocked`。这些是Level+Attempt推得的事实，**不是总线事件**；不得含eventId/sessionId/firstClear/stampCount/completed，不读Progress，不调用保存/SDK/总线。相同规则输入在任意完成历史中结果相同。Reject也只返回原因。

规则检查expectedRevision，旧值返回STALE_REVISION；nextAttempt只返回本次rev+1建议值，不拥有全局计数器。**SessionCoordinator是Attempt、Progress、revision、应用状态机和事件序号的唯一写入者**。它同步验命令、调用规则、赋值nextAttempt、合并Progress、发布富化事件、排保存，然后才允许动画。T08的Progress策略只能由Session调用；T07只传输快照并返回结果。UI/规则/Adapter不得另行发章或保存。

接受的EXIT/UNDO/RESET、关卡切换、实际改变的设置/教程标记各升一次统一revision；已胜未记章的恢复修复也只升一次。胜利是该EXIT的结果，不另升rev/另存一次。拒绝/无变化命令/回执不升rev。revision范围0..9007199254740991；达到上限后新的持久变更返回REVISION_EXHAUSTED并进只读恢复说明，不溢出/绕回。有效最大rev档仍可读。

状态键为removedMask；门由初态XOR已移除箭toggles推导，非空船期cursor=popcount(mask)，空船期恒0。相同mask后续规则相同，可合并搜索；日志仍须逐步合法。求解器选ID字典序的可通关后继。每成功解均n次移除，最短步不代表难度。

## 应用状态机与中断

```text
BOOT -> HOME | RECOVERY | ERROR
HOME -> PLAY(新档L01/继续) | MAP | SETTINGS | CREDITS
MAP -> PLAY(已解锁关) | HOME
PLAY.INPUT -> PLAY.COMMIT -> PLAY.ANIMATING -> PLAY.INPUT | DEADLOCK | WIN
PLAY -> PAUSE -> PLAY | HOME | SETTINGS | HELP | 重来确认
DEADLOCK -> PLAY(撤销/关闭) | PLAY(确认重来)
WIN -> PLAY(下一关/重玩/撤销) | MAP | COMPLETE(L20下一步)
COMPLETE -> MAP | PLAY(L20重玩) | HOME
ERROR -> BOOT(重试) | HOME(若已有可用内容)
RECOVERY -> BOOT(恢复备份/确认新档) | 只读说明
```

Session独占转换和输入锁，BoardView仅发送命令/消费事件。先逻辑提交、排保存再动画，胜利快照必须含completed；写盘失败保持内存已提交结果并提示，不能宣称保存成功。页面隐藏停止音频并flush已有队列，同revision不再创建保存请求。隐藏/旋转/WebGL丢失取消动画；回归重绘已提交状态，不重新执行EXIT。暂停只冻结呈现。死锁是非空且无合法EXIT；面板可关闭但事实不变。仍可走但未来无解是LOSING，允许继续，提示建议撤销/重来。

## 事件、序号与唯一publisher

**SessionBus.publish只允许SessionCoordinator调用（T06）**。输入/Content/生命周期/Adapter/SaveCoordinator只向它提交命令或结果；纯规则不发布。ExitRequested是输入命令 `{arrowId,expectedRevision,inputType}`，不是规则事件。

全部事件含 `eventId="<sessionId>:<seq>",revision`及可选levelId。sessionId每启动生成内存命名空间，不落盘、不作身份或回传；seq从1起逐事件严格递增，拒绝及回执也占序号，不能拿revision当序号。固定样例从41起表示已有40事件。消费方按eventId去重；重启换命名空间。调试可含monotonicMs，无姓名/文本输入/指纹。

| 事件 | 必需payload | Session发布条件/消费者 |
|---|---|---|
| ContentLoaded / ContentRejected | contentVersion / issueCode | 内容校验结果→BOOT |
| AttemptStarted | levelId,resumed,variant | 进入关卡→教程/本地QA |
| ExitRejected | arrowId,reason,blockerCell? | 拒绝→UI，不改日志/进度/保存 |
| ExitCommitted | arrowId,fromMask,toMask,gatesChanged[],cursor | 富化RuleFacts→动画；UI不负责保存 |
| UndoCommitted / ResetCommitted | fromMask,toMask | 撤销/重来→重绘；历史completed保留 |
| HintShown | arrowId?,solvable | 求解后→UI，不改局面 |
| DeadlockDetected | mask,legalCount=0 | 提交/恢复后非空无合法走法→面板 |
| LevelCompleted | levelId,firstClear,stampCount | firstClear=操作前completed未含本关；stampCount=合并后集合大小 |
| SaveRequested | snapshotRevision | 每接受revision只发一次；内部队列同时交付完整不可变SaveEnvelope |
| SaveSucceeded / SaveFailed | snapshotRevision / snapshotRevision,errorCode | SavePort回执→Session发布；不升rev、不触发新保存 |
| VisibilityChanged / AudioInterrupted | hidden / reason | 生命周期→音频/重绘 |
| AdapterReady / AdapterUnavailable | profile,capabilitySet / reason | 平台初始化→能力处理，不假装强制SDK已合规 |

赢局顺序固定ExitCommitted → LevelCompleted → SaveRequested，同一接受后revision；非赢局ExitCommitted → SaveRequested，若死锁再发DeadlockDetected。UNDO/RESET各自一提交一保存。requestKey=`profile/sessionId/snapshotRevision`，串行保存；重试/flush复用key，不形成新逻辑请求。相同key+结果重复回执无事件；失败后显式重试成功允许一次成功通知。旧rev回执payload标原snapshotRevision，事件revision取当前Session值，不能覆盖内存/诱发递归保存。

P02仅映射准许的loading/gameplay生命周期至官方API；P04只用Bridge；本地事件不能默认后台采集。P01_RESERVED完全不回传，CREDITS不放URL。发布包去掉调试导出。

### 同局面不同历史及胜利撤销再完成表向量

`contracts/session-vectors.json`精确列出3局11步的规则事实、上下文、事件ID/载荷及保存快照，离线合同检查实际运行；这不是Session运行实现。共同输入：L01、log=[a]、revision=7、EXIT b、expectedRevision=7。共同规则输出：mask1→3、门空、cursor0、won=true、deadlocked=false、nextAttempt.log=[a,b]/rev8。

| 历史 | LevelCompleted | 保存 | 关系 |
|---|---|---|---|
| A completed=[]、next_seq=41 | A:42，firstClear=true，stampCount=1 | rev8、[L01]、[a,b] | RuleFacts与B/C完全相同 |
| B completed=[L01]、next_seq=1 | B:2，firstClear=false，stampCount=1 | rev8、[L01]、[a,b] | 历史首通不重发章 |
| C completed=[L01,L02]、next_seq=1 | C:2，firstClear=false，stampCount=2 | rev8、[L01,L02]、[a,b] | 章数是历史集合大小 |

A：首胜rev8 → 成功回执 → 动画中断（0新提交/0新保存）→ 撤销b，rev9、completed仍[L01]、log=[a] → 再EXIT b，rev10、firstClear=false/stampCount=1 → 成功回执 → 重复回执（0事件）→ 旧rev9命令（拒绝不保存）。保存仅rev8/9/10各一份。撤销和再完成都改变状态，因此各须保存；禁止的是同一次提交/回执重复保存。无REDO命令，undo-redo在本档指重新提交b。

## SaveEnvelope字段与判定边界

key=`G01.signalharbor.{profile}.v1`，各渠道隔离，字节上限65536（HYPOTHESIS）。本目录`save-envelope.schema.json`为交换格式；`contracts/save-vectors.json`含27个固定合法/非法样例。

| 字段 | 精确边界 |
|---|---|
| version / content_version | 当前1 / "1.0.0"；整数version>1只读保留原字节；未知内容版本RECOVERY，不套旧日志 |
| revision | 整数0..9007199254740991，不能bool/小数/负数；数值超界拒绝 |
| completed | L01..L20无重复，且按L01起连续前缀排序，长度0..20 |
| active_level | L01..L20，0起索引≤completed.length；可重玩已完成关或最高解锁未完成关 |
| accepted_exits | 0..8、不重复、pattern ^[a-z][a-z0-9_]*$、ID属活动关；必须逐步合法重放 |
| tutorial_seen | 0..4、不重复、仅base/relay/manifest/combined；允许子集，不据此推断完成 |
| settings | 恰好language(en/zh-CN)、sound(bool)、music(bool)、reducedMotion(bool)，无额外键 |

所有字段必需、对象拒绝额外键。解析前UTF-8字节数≤65536；严格JSON，任意深度重复键/NaN/Infinity拒绝，不可依赖JSON.parse最后键覆盖。JSON Schema不能检测重复键或原始数字词法，读取器还须拒绝revision的小数/指数词法，离线整数类型检查拒绝1.0与1e0，未来实现须等价。

示例合法部分局：
```json
{"version":1,"content_version":"1.0.0","revision":7,"completed":["L01"],"active_level":"L02","accepted_exits":["b"],"tutorial_seen":["base"],"settings":{"language":"en","sound":true,"music":false,"reducedMotion":false}}
```

判定次序：字节/严格JSON → version较新只读 → content不匹配恢复 → schema/整数 → completed前缀 → active解锁 → 逐步重放 → 全清补记章。新版本只读不尝试v1 schema改写。无档才是v0新档；损坏档不能当无档静默覆盖。

| 固定样例 | 判定 |
|---|---|
| 新档L01空log；L01 log=[a]；completed=[L01]的L01重玩；active=L02空log | ACCEPT |
| L01 log=[a,b]、completed=[]、rev7 | ACCEPT_REPAIR_COMPLETION，输出completed=[L01]、rev8；第二遍ACCEPT且无再次保存 |
| version=2 / content_version不同 | READ_ONLY_NEWER_VERSION / RECOVERY_CONTENT_VERSION |
| 负/小数/bool/超安全整数rev | REJECT_SCHEMA；最大rev档无需修复可读 |
| 额外root/settings键、未知/重复tutorial、重复log | REJECT_SCHEMA |
| L01 log=[b] / [z] | REJECT_REPLAY：先b被挡 / ID不存在 |
| completed=[]却active=L03；completed=[L02]或[L02,L01] | REJECT_LOCKED_ACTIVE / REJECT_COMPLETED_PREFIX |
| 重复JSON根键/设置键；超64KiB | REJECT_JSON / REJECT_OVERSIZE |

全清未记章由Session单次补当前关、revision+1，排一份规范化快照；不重执行EXIT、不重播奖励事件。再次载入规范档不再修复。若最大rev且需修复则RECOVERY_REVISION_EXHAUSTED，保留文件供更新/明确新档。章数永远推导，不存独立权威数字。进入另一关先排保存，新关清log；仅一个活动局。

## 写入、恢复、云与故障

写tmp → 读回验证 → 合法旧main拷贝bak → 替换main → 验main → 清tmp。Web Storage无跨key事务，启动检查main/tmp/bak，选合法最大revision；同rev不同规范内容转RECOVERY手选，不静默合并局面。序列化按schema字段规范序、集合规范序，同内容比较不依赖原JSON空白。当前任一候选为未知更高version时先只读RECOVERY，不能自动拿低版本覆盖；无效/tmp/bak原字节保留，用户明确新建才替换。

所有写入串行；失败保持已提交内存态并显示“此设备无法保存，当前游戏仍可继续”。SaveCoordinator不加章/改revision/发总线，只返回结果。断写/配额/权限/私密模式未来T07实测；当前仅检查固定数据判定，**未实跑Web Storage故障注入**。

云仅同渠道能力明确后启用；两边先同样验证，completed并集后规范为前缀，活动局取较高rev，同rev冲突列关卡/离港数供选择。合并是Session持久变更，写max(localRev,cloudRev)+1，超界转RECOVERY；不得直接拼不同关日志。云失败回本地；P04不得发自有服务器，P01无开发者云，无SDK Basic仅本地；无跨站同步/账号依赖。

## 边界与竞态

双击首个接受后锁棋盘到动画结束，第二次丢弃不排队；焦点丢失/pointercancel/第二指取消按下，回归重新按下；pointerup落别箭不转选，键盘repeat忽略。弹窗独占输入；重来取消保持状态，不同时退出与重来。未获音频手势则无声继续。SDK回调场景销毁后按token丢弃；Save回执由应用Session接收，不依赖棋盘场景存活。未来广告如另获批准，暂停音画/输入且回调去重，不授未确认奖励，不在本版自动启用。
