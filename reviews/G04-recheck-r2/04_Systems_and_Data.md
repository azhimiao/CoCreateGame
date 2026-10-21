# 系统、接口、数据与异常合同

所有接口为施工规格，尚未有TS运行实现。规则函数的离线Python核对器不是产品运行时。规格版本 `1.0.0`，关卡数据、原两份及新增Save/Event Schema均在本目录，不依赖根目录数据更新。

## 权威实体与状态

Level：id/name/variant/width/height/bit_count/floors/initial/victory/lifts/switches/gates/beacons/move_limit/par/solution/design_intent。坐标、枚举、掩码与尺寸边界受 `game-spec.schema.json` 校验；尺寸一致、引用落在地面、实体同类不重复、mask不越位、有解等关系约束由 `validate_spec.py` 检查。公开solution是研究交付数据；正式玩家包不得通过普通UI暴露完整路径，运行提示从当前态求路。

RuleState：`{position:[l,x,y],bits:0..7,pending:0..7,nextBeacon:0..6,used:0..limit,status:PLAYING|WON|FAILED,failure:null|FLOOR_CLOSED|BEACON_ORDER|MOVE_LIMIT}`。位数取Level，整数不随帧漂移。Python报告 trace 按 `[l,x,y,bits,pending,nextBeacon,used,status]` 写出，原因见向量 expected_reasons；failure由事件原因及终态重建。

Session：levelId/RuleState/history/acceptedCommands/assisted/attemptId/nextSeq/totalAccepted/undoCount/winCommitted；contentHash/ruleVersion来自应用加载的只读内容上下文。history存全部RuleState动作前快照，最多128条；acceptedCommands只记当前撤销后保留路线，撤销同步pop。nextSeq从1开始、永不因撤销回退；assisted和原始计数只属Session。UI的viewLayer/selectedCell/pauseReasons/inputLocked不入规则。规则事实不能读取Session字段，富化来源及唯一发布见EVENT_CONTRACT.md。

Progress：恰20条campaign顺序records，每条levelId/completed/bestStars/bestUsed，加highestUnlocked/lastCommittedAttemptId。完成集合由records派生；highestUnlocked必须等于最长已完成连续前缀后的关号（全通为20），不信任输入。**Settings唯一权威位置是SaveEnvelope.settings，Progress严禁settings字段**。默认值、空记录、整数/时间边界、有效活动局与摘要算法全部按SAVE_CONTRACT.md及save-envelope.schema.json；不允许另一份“便利设置”持久化。

## 模块接口

| 接口 | 输入 → 输出 | 不变量/异常 |
|---|---|---|
| validateContent | unknown JSON → ValidatedSpec或ContentError[] | Schema先行再语义验证；不可静默修正 |
| createSession | validated Level, attemptId → Session | 不触发初始开关；起点必须受支撑 |
| reduceCommand | Level, RuleState, U/R/D/L/X → {accepted,state,facts:RuleFact[]} | 纯函数，facts无seq/attemptId/assisted/输入来源；同输入逐字相等 |
| reduceSession | content,Session,command{op,source},Progress → {session,progress,eventDrafts,effects} | 纯Session归约；元数据只从Session/command取，事务中幂等commitWin |
| SessionController.dispatch | command+activeAttemptToken → committed snapshot | 唯一应用状态写者及SessionEvent发布者；同次提交推进nextSeq，提交后广播一次，旧token拒绝 |
| undo | Session → Session+events | 仅PLAYING/FAILED；恢复全快照，WON拒绝 |
| restart | Level, Progress, freshAttemptId → 新Session | 清历史/assisted，保留best记录，新局首事件seq=1 |
| solve | Level,currentState,maxRemaining → Solution或NO_PATH/BUDGET_EXCEEDED | BFS键=位置,bits,pending,nextBeacon；不包含渲染时间；先到同键为最省步 |
| computeStars | used,par,assisted →1/2/3 | 见03，纯函数 |
| commitWin | progress,session → progress | 仅WON，幂等；解锁恰好下一关 |
| serializeSave | {profile,revision,updatedAt,progress,settings,activeSession},content → canonical UTF-8 JSON | 只一个settings，调用方注入时间/revision；SHA输入按CJ1，不读系统时间决定规则 |
| restoreSave | bytes,expectedProfile,currentContent → restored或具名恢复分支 | 先严格JSON/版本/Schema/checksum，再profile/内容与逐命令重放；详见SAVE_CONTRACT |
| platform.init | profile → Promise<capabilities> | 10秒超时；离线QA可降级，P02 Full SDK缺失阻止发行 |
| platform.gameplay | running:boolean → void | 仅状态翻转时调用，防重复 |
| platform.analytics | allowedEvent → void | P01编译为no-op；只准官方SDK白名单/本地QA |
| platform.storage | read/write UTF-8 → Promise<Result> | 单次3秒超时；不抹掉有效本地存档 |

求解上限：最大50基础格×8bits×8pending×7信标进度=22400个键，单线程分片每200节点归还主循环，内部目标2秒，超时只提示暂不可用，不变更棋盘。预算和实际耗时未测。解序列遍历命令次序 U,R,D,L,X，多个最短解取首次；不得宣称解唯一。

## 事件次序与载荷

**r2权威合同见EVENT_CONTRACT.md、event-contract.schema.json和session-contract-vectors.json。** 纯规则只返回`{type,payload}`的RuleFact，不带Session信封。SessionController唯一发布`{v:1,seq,attemptId,levelId,source,type,payload}`；seq从本Session.nextSeq取后递增。source来自command的keyboard/touch/mouse/system/qa，不能由规则猜测；assisted来自当前Session。规则状态先提交，事件用于显示，动画完成不决定结果。

有效RuleFact次序：`CommandAccepted{command,used,from,to}`→可选PendingApplied→若未失败可选SwitchEntered→可选BeaconAdvanced→StateCommitted→可选`RuleWon{used,par}`或RuleFailed。RuleWon由Session层变为LevelWon{used,par,assisted,stars}，其它事实载荷与事件Schema逐项一致。地面关闭跳过后续机关。无效规则输入仅CommandRejected，不改变RuleState；元数据及本地事件seq可以增长，不能误称规则扣步。

UNDO/RESTART/提示确认等Session命令的事件来源、seq以及新旧attempt边界见EVENT_CONTRACT。VIEW_LAYER/InspectCell是Presentation本地通知，不能进入SessionEvent总线冒充规则事件。存储adapter只返回结果，由SessionController发布SaveDegraded，不直接发布或调用commitWin。正式遥测仍只允许level_start/level_complete/level_fail/pause/resume的非个人字段映射；原始命令、attemptId、存档、设备标识不向开发者发送。P01完全禁统计。

## 应用状态机

BOOT → LOADING → HOME。无存档HOME开始直接L01，有存档可继续/地图。MAP → PLAYING；PLAYING → FAILED/WON由规则触发，PLAYING/FAILED → PAUSED由用户或后台触发，PAUSED恢复原状态。WON页可下一关/重玩/地图，不能undo。SETTINGS/HELP/HINT/RESTART_CONFIRM是可退出覆盖层，添加暂停原因，不新建关局。

pauseReasons是集合 USER/HIDDEN/MODAL/SDK；只在集合从空到非空时gameplay(false)，最后原因移除且可操作时才gameplay(true)。切后台清空输入缓冲、冻结音画；回前台加USER恢复页，等待明确继续手势恢复音频。失败页和胜利页不算可操作Gameplay，SDK报告停止。

## 存档格式与事务

命名空间`g04:save:v1:<profile>`，五个精确profile枚举与完整信封/Progress/Settings/ActiveSession均在SAVE_CONTRACT.md及save-envelope.schema.json。信封含profile，跨profile明确拒绝。checksum使用排除checksum字段后的CJ1规范化UTF-8字节SHA-256；递归键排序、原始中文、不做Unicode归一化、整数边界及固定预期摘要详见save-fixtures.json。contentHash仍为game-spec.json原始字节SHA-256。revision用于双槽选择，updatedAt仅显示，不影响规则/奖励。

每个有效动作结算后、undo/restart/win/settings/visibility hidden写入；可合并250ms内待写，但离开前立即尝试。双槽A/B：写入较旧槽 → 回读校验 → 更新active指针；读取时忽略错误指针，选最高有效revision。单槽崩溃保留另一槽。保存历史通过acceptedCommands从初态逐条重放重建，比较终态；不得直接信任缓存history。FAILED终态可恢复并撤销，WON已结算后activeSession置null。

每槽上限256KiB。浏览器拒绝/配额满时转内存保存并常驻提示；损坏槽隔离，不上传；另槽有效就恢复。双坏**不从未验证内容捞设置**：保留原字节，询问是否开临时新档，明确确认前不覆盖；确认后使用规范默认设置。未知schema/rule版本保留原字节，不写回；contentHash变化仅在checksum/Schema已有效后保留合法历史records和settings，activeSession清空，明确确认后从关卡初态开新attempt。各错误优先级、同revision槽冲突、FAILED重放及字段比较详见SAVE_CONTRACT，不能自行补迁移。

云存档V1关闭。未来P02 SDK存储若另获批准，必须加revision冲突策略：完成集合取并集、星取max、bestUsed取min，活动会话不拼接，由玩家在本地/远端有效版本中选择；未经此审查不能开云同步。

## 并发与输入异常

SessionReducer只计算纯事务；SessionController是唯一实际状态写者。每次动画锁最长180ms，锁内移动事件丢弃而非排队，UNDO/暂停可中断动画并立即重绘权威态；每次新命令有递增token，旧动画回调不得改状态。双指只认首pointerId，CANCEL不移动；失焦取消按下态。SDK超时、音频拒绝、资源缺失分别由恢复页处理，不能借异常隐式发X或重跑开关。JSON非法/关卡无解是内容阻断，禁止进入该关并回地图，不伪造通关。
