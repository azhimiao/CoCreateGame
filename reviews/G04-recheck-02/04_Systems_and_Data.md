# 系统、接口、数据与异常合同

所有接口为施工规格，尚未有TS运行实现。规则函数的离线Python核对器不是产品运行时。规格版本 `1.0.0`，关卡数据与两份Schema均在本目录，不依赖根目录数据更新。

## 权威实体与状态

Level：id/name/variant/width/height/bit_count/floors/initial/victory/lifts/switches/gates/beacons/move_limit/par/solution/design_intent。坐标、枚举、掩码与尺寸边界受 `game-spec.schema.json` 校验；尺寸一致、引用落在地面、实体同类不重复、mask不越位、有解等关系约束由 `validate_spec.py` 检查。公开solution是研究交付数据；正式玩家包不得通过普通UI暴露完整路径，运行提示从当前态求路。

RuleState：`{position:[l,x,y],bits:0..7,pending:0..7,nextBeacon:0..6,used:0..limit,status:PLAYING|WON|FAILED,failure:null|FLOOR_CLOSED|BEACON_ORDER|MOVE_LIMIT}`。位数取Level，整数不随帧漂移。Python报告 trace 按 `[l,x,y,bits,pending,nextBeacon,used,status]` 写出，原因见向量 expected_reasons；failure由事件原因及终态重建。

Session：levelId/contentHash/ruleVersion/RuleState/history/acceptedCommands/assisted/attemptId。history存全部RuleState动作前快照，最多128条；acceptedCommands只记当前撤销后保留路线，撤销同步pop。另有UI的 viewLayer/selectedCell/pauseReasons/inputLocked，不进入规则，也不影响求解键。assisted与总尝试/undo计数属于会话元数据，撤销不回滚assisted。

Progress：20关完成集合、每关bestStars/bestUsed、highestUnlocked、settings。已完成集合推导解锁链，不信任用户任意写入的highestUnlocked。尝试完成用attemptId去重；重复WON回调不会重复结算。无货币和服务器经济。

## 模块接口

| 接口 | 输入 → 输出 | 不变量/异常 |
|---|---|---|
| validateContent | unknown JSON → ValidatedSpec或ContentError[] | Schema先行再语义验证；不可静默修正 |
| createSession | validated Level, attemptId → Session | 不触发初始开关；起点必须受支撑 |
| reduceCommand | Level, RuleState, U/R/D/L/X → {accepted,state,events} | 纯函数、不改入参；无效时state逐字段不变 |
| undo | Session → Session+events | 仅PLAYING/FAILED；恢复全快照，WON拒绝 |
| restart | Level, Progress → 新Session | 清历史/assisted，保留best记录 |
| solve | Level,currentState,maxRemaining → Solution或NO_PATH/BUDGET_EXCEEDED | BFS键=位置,bits,pending,nextBeacon；不包含渲染时间；先到同键为最省步 |
| computeStars | used,par,assisted →1/2/3 | 见03，纯函数 |
| commitWin | progress,session → progress | 仅WON，幂等；解锁恰好下一关 |
| serializeSave | progress,session → UTF-8 JSON | 不存音频对象、引擎引用或URL |
| restoreSave | text,contentHash → restored或RecoverableError | Schema/哈希/重放比对后才能继续 |
| platform.init | profile → Promise<capabilities> | 10秒超时；离线QA可降级，P02 Full SDK缺失阻止发行 |
| platform.gameplay | running:boolean → void | 仅状态翻转时调用，防重复 |
| platform.analytics | allowedEvent → void | P01编译为no-op；只准官方SDK白名单/本地QA |
| platform.storage | read/write UTF-8 → Promise<Result> | 单次3秒超时；不抹掉有效本地存档 |

求解上限：最大50基础格×8bits×8pending×7信标进度=22400个键，单线程分片每200节点归还主循环，内部目标2秒，超时只提示暂不可用，不变更棋盘。预算和实际耗时未测。解序列遍历命令次序 U,R,D,L,X，多个最短解取首次；不得宣称解唯一。

## 事件次序与载荷

事件信封 `{v:1,seq:uint,attemptId,levelId,type,payload}`；seq是会话内递增安全整数。RuleState权威先提交，事件用于显示，动画完成不决定规则结果。

有效动作事件次序：`CommandAccepted{command,used,from,to}` → 可选 `PendingApplied{mask,bits}` → 若未失败可选 `SwitchEntered{mask,mode,bits,pending}` → 可选 `BeaconAdvanced{index}` → `StateCommitted{state}` → 可选 `LevelWon{used,par,assisted}` 或 `LevelFailed{reason}`。地面关闭即跳过后面的机关事件。无效输入仅 `CommandRejected{reason}`，reason为BLOCKED/NO_LIFT/INVALID_ACTION_OR_TERMINAL；不入规则回放。

UNDO发 `UndoApplied{restored}`，RESTART发 `AttemptRestarted{newAttemptId}`。VIEW_LAYER/InspectCell只由UI发。持久化错误发 `SaveDegraded{reason}`，不转LevelFailed。正式遥测只允许level_start/level_complete/level_fail/pause/resume的非个人字段映射；原始命令、attemptId、存档、设备标识不向开发者发送。P01完全禁统计，离线QA才可由测试员手工导出无身份回放。

## 应用状态机

BOOT → LOADING → HOME。无存档HOME开始直接L01，有存档可继续/地图。MAP → PLAYING；PLAYING → FAILED/WON由规则触发，PLAYING/FAILED → PAUSED由用户或后台触发，PAUSED恢复原状态。WON页可下一关/重玩/地图，不能undo。SETTINGS/HELP/HINT/RESTART_CONFIRM是可退出覆盖层，添加暂停原因，不新建关局。

pauseReasons是集合 USER/HIDDEN/MODAL/SDK；只在集合从空到非空时gameplay(false)，最后原因移除且可操作时才gameplay(true)。切后台清空输入缓冲、冻结音画；回前台加USER恢复页，等待明确继续手势恢复音频。失败页和胜利页不算可操作Gameplay，SDK报告停止。

## 存档格式与事务

命名空间 `g04:save:v1:<profile>`，P01/P02/local分别隔离。信封：`{schemaVersion:1,ruleVersion:'1.0.0',contentHash,revision,updatedAt,progress,settings,activeSession|null,checksum}`。checksum为排除checksum字段后键排序紧凑JSON的SHA-256（UTF-8；无浮点）；仅检测损坏，不当作防作弊。contentHash为原始 `game-spec.json` 文件字节SHA-256。系统时间不可靠，按revision选择，不按时钟奖励。

每个有效动作结算后、undo/restart/win/settings/visibility hidden写入；可合并250ms内待写，但离开前立即尝试。双槽A/B：写入较旧槽 → 回读校验 → 更新active指针；读取时忽略错误指针，选最高有效revision。单槽崩溃保留另一槽。保存历史通过acceptedCommands从初态逐条重放重建，比较终态；不得直接信任缓存history。FAILED终态可恢复并撤销，WON已结算后activeSession置null。

每槽上限256KiB，128步内超限属格式错误。浏览器拒绝/配额满时转内存保存并常驻“本次进度暂不能保存”，不扣步不阻止玩；页面关闭可能丢失会话，此限制明示。损坏槽仅隔离不上传；另槽有效就恢复。两槽无效则保留设置中可验证部分并询问本地新开，不能提示“云端已恢复”。未知schemaVersion保留原字节、不写回覆盖，允许从地图新开独立临时会话。contentHash不一致保留已完成的有效levelId和best记录，中间局丢弃并说明“关卡已更新，当前关重新开始”；版本迁移另审不猜测。

云存档V1关闭。未来P02 SDK存储若另获批准，必须加revision冲突策略：完成集合取并集、星取max、bestUsed取min，活动会话不拼接，由玩家在本地/远端有效版本中选择；未经此审查不能开云同步。

## 并发与输入异常

同一时刻只有一个SessionReducer写状态。每次动画锁最长180ms，锁内移动事件丢弃而非排队，UNDO/暂停可中断动画并立即重绘权威态；每次新命令有递增token，旧动画回调不得改状态。双指只认首pointerId，CANCEL不移动；失焦取消按下态。SDK超时、音频拒绝、资源缺失分别由恢复页处理，不能借异常隐式发X或重跑开关。JSON非法/关卡无解是内容阻断，禁止进入该关并回地图，不伪造通关。
