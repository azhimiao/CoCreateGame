# G02 系统、数据与异常合同

版本1.1｜2026-10-21。全部运行时接口是未来实现合同（HYPOTHESIS）；当前仅有离线Python规格验证器，不声称TS模块已实现。

## 1. 静态实体与不变量

`LevelSpec={id,name,variant,demand,containers,win,solution,par_actions,target_seconds,tutorial,feature_coverage}`；实际20组值在 game-spec.json。`ContainerSpec={id,capacity,items,accepts,unlock_after,sealable}`；items底→顶。`Demand: Record<Colour,2|3>`；Colour=A/B/C/D。静态Schema拒绝额外字段；跨字段关系由verify.py检查。target_seconds是玩家设计目标，par_actions是当前模型BFS得出的最短前进动作数（含seal），不能当真人难度。

运行`LogicalState={stacks: Colour[][], sealed: (Colour|null)[]}`，数组索引与containers顺序一致。Python校验器内部以空字符串表示未封，序列化哈希见下文；TS运行时可用null，但跨实现哈希必须先规范化。锁状态只派生，不独立存储；无手工给出可与章矛盾的unlocked字段。`RunState={levelId,variant,logical,revision,logicalActionCount,history,replay,runId,commandEpoch,commandHighWater,receiptCache,status}`；选择、动画、焦点、系统时间均在Presentation层，不进规则状态。

守恒：`每类当前全盘数量 + 已封该类需求量 = 初始demand`。同类最多封一次。SEALED盘无物件。容量、接收集合、锁颜色引用始终有效。关卡加载遇错转ERROR，不启动半关。未知字段、重复盘ID、不匹配的需求、缺少合法解、非法variant配置均内容错误。V0/X2锁列表必须空，V0/X1接收全色。

## 2. 模块与接口

| 模块 / 输入 | 输出 | 错误与职责 |
|---|---|---|
| Content.load(levelId,contentHash) | 校验后的LevelSpec | INVALID_CONTENT/UNKNOWN_LEVEL；不补随机关 |
| Rules.legalActions(spec,state) | seal按盘ID，再move按源/目标ID升序 | 纯函数，无引擎/时间/SDK |
| Rules.apply(spec,state,action) | 新state或拒绝理由 | 不原地修改；仅MOVE/SEAL进入RuleCore |
| Run.dispatch(command) | `{receipt,delivery}`；当前盘面另行read | 严格按下述总序；缓存命中只重送不可变receipt |
| Run.dispatch(undo) / Navigation.restart | receipt / 新RunState | UNDO必须走同一dispatch，不能直接绕过幂等；重开确认后生成新runId |
| Hint.search(spec,state,budget) | FOUND(firstAction)/UNSOLVABLE/UNKNOWN | 只有全图穷尽才UNSOLVABLE；预算退出UNKNOWN |
| Save.write/read | 成功/内存降级/恢复提示 | 两槽协议，不把存档失败当输 |
| View.render(run,ui) | Cocos节点更新 | 动画不能决定规则结果 |
| Platform.init/ready/gameplayStart/Stop/save/load/track | capability与Promise结果 | 每构建一个adapter；拒绝不得抛至RuleCore |

### 2.1 命令身份与唯一总序（替代旧commandId合同）

命令共同字段为`{run_id,command_epoch,command_seq,expected_revision,op}`，MOVE额外且仅有`src,dst`，SEAL仅`at`，UNDO无参数；JSON不允许额外字段。run/epoch为非空不透明字符串，op为小写move/seal/undo；盘ID为T0…T5。command_seq必须是**数值整数**1…9007199254740991，expected_revision为同范围含0；不接受字符串、布尔、小数。比较只按整数，不按字典序。序号耗尽进入需重新载入恢复的错误态，不回绕。UI为每个新意图分配本epoch下一个序号；传输重试必须保持整个命令不变。

以下步骤严格依次执行；不能把状态/BUSY/版本提前：

1. 校验完整envelope类型/字段，不合返回BAD_ENVELOPE。随后run不等返回STALE_RUN，再epoch不等返回STALE_EPOCH。三者都是传输拒绝，无缓存、无序号消费、无事件、无保存；旧身份即使在旧缓存中也不可恢复执行。
2. 在当前身份`(run_id,command_epoch,command_seq)`缓存中查找。payload为整个合法命令的递归键排序JSON（数组顺序保留、无空白）。完全相同返回**原receipt逐字段不变**，不再检查当前status/revision；同身份异payload返回ID_CONFLICT且不替换原receipt。ID_CONFLICT无任何副作用。
3. 未命中且seq≤high_watermark返回STALE_COMMAND；seq>high_watermark+1返回SEQUENCE_GAP。两者不消费、无缓存/事件/保存。窗口外无法证明payload是否相同，统一STALE_COMMAND，不猜测、不执行。
4. 仅seq=high_watermark+1进入一次新决定，先消费序号，high_watermark更新。**无论接受或以下任一拒绝都缓存**。缓存保留数值区间`[max(1,high_watermark-127), high_watermark]`的128个已消费决定，拒绝也占位；不是最近128成功动作，也不按字符串排序。
5. 首次新决定按status：ANIMATING→BUSY；非PLAY→NOT_PLAYING，但DEADLOCK下UNDO例外允许；PAUSE/WIN/ERROR不允许新规则动作。再检查expected_revision，不等→STALE_REVISION。最后检查操作规则。
6. MOVE拒绝次序：缺盘/同盘BAD_ID/SAME_CONTAINER→SOURCE_SEALED→SOURCE_LOCKED→EMPTY_SOURCE→TARGET_SEALED→TARGET_LOCKED→TARGET_FULL→FILTER_MISMATCH→TOP_MISMATCH。SEAL：BAD_ID→SEALED→LOCKED→NOT_SEALABLE→EMPTY_SOURCE→NOT_HOMOGENEOUS→DEMAND_MISMATCH。UNDO无历史→EMPTY_HISTORY。只返回第一个理由。

成功MOVE/SEAL/UNDO revision始终+1；UNDO只回退logical和logical_action_count，revision不回退。所有拒绝保持规则盘面、revision、撤销历史和逻辑动作数不变，但第4步已消费的拒绝会推进**协议**序号及拒绝分析流水。RESTART/下一关属于导航事务而非上述command：确认后创建新run和新epoch、revision=0，旧run迟回被第1步拒绝。

`receipt={accepted,reason,revision_before,revision_after,logical_action_count_after,state_hash_after,event_ids}`；成功reason=OK。receipt不包含可变化的当前盘面。`delivery={from_cache,events_to_publish,save_requests}`；缓存命中from_cache=true、events_to_publish=[]、save_requests=0，不重复历史、计数、声音、动画、胜利确认或SDK动作。首次消费决定：成功只创建一次04§5所述事件批次/一次保存请求；拒绝只创建一次action_rejected、保存请求0。Probe中的events计的是一次发布批次，不是假定SEAL只发一个业务事件。传输拒绝没有receipt，只返回transport_reason。UI若需当前盘面调用readCurrent，不能把旧receipt的hash当当前状态覆盖显示。

| 原决定 / 当前状态 | 精确原样重试 | 新序号命令 |
|---|---|---|
| MOVE成功，已进入ANIMATING | 原OK、原revision_after；0事件/0保存 | BUSY并缓存 |
| MOVE成功，已回PLAY或PAUSE | 原OK；即使expected_revision已旧 | PLAY再检查版本；PAUSE为NOT_PLAYING |
| 最后SEAL成功，当前WIN | 原OK、同一level_end事件ID；不重结算 | NOT_PLAYING并缓存 |
| TOP_MISMATCH或BUSY已拒绝，后来条件改变 | 原失败理由；不重新尝试 | 按新条件决定；改payload必须新seq |
| 相同ID改dst/expected_revision | ID_CONFLICT；原结果保留 | 新seq再走规则 |
| 旧run/epoch迟回 | STALE_RUN/STALE_EPOCH | 当前epoch可从其下一个seq继续 |

表驱动输入与唯一预期在protocol-vectors.json；tools/check_contracts.py只用注入规则判决的整数探针校验协议，**不实现游戏调度器**。

## 3. 确定性输入路由

`selection=null|trayId` 不改变逻辑。无选中：只点OPEN非空盘顶部可选源；点盘非顶部区不选；点锁只解释。有选中：同源盘任一区取消；所有其他盘先MOVE，失败保留源，成功清空；盘外空白取消。不允许非法目标点击自动变新源。锁/已封盘作为其他目标时也保留源。换源=取消→新选；已选源顶部可启动拖动，其它盘不能以拖动绕过换源步骤。封箱按钮命中优先，不把按钮tap再当盘tap；成功封箱清选择、失败保留。

PLAY没有ScrollView/边缘自动滚动。pointerDown仅捕获一个pointer：封箱/工具按钮优先，其次顶部物件、其它盘、盘外空白。顶部为GAME owner，位移>8CSSpx仅进入物件拖动，pointerUp最多发一个command；相同手势不转为滚动。其它盘点击沿既定MOVE优先，拖动不得借道改源。拖出/OS cancel清选择但不动逻辑；动画期间不排队棋盘命令。屏幕旋转、失焦、暂停均取消拖动并清选择；已提交动画直接收尾，不回滚。键盘通过同一个选择路由，保证触摸/鼠标/键盘无规则差异。

其它允许滚动的屏幕仅HOME窄屏内容、LEVEL_SELECT、COLLECTION_COMPLETE、CREDITS和弹窗正文（按06）：down时记录唯一owner和tap候选；内容区累计位移>8CSSpx后由SCROLL永久持有到up/cancel、取消tap/选择，不发游戏命令。≤8且up仍在同一按钮才tap；固定头尾按钮由BUTTON持有，移出其热区或>8即取消，绝不转交SCROLL。滚动边界钳制，无冒泡到body/下层棋盘，无边缘滚动触发MOVE。弹窗出现、第二指、旋转均不转移第一指owner；第二指忽略，系统cancel结束第一指。PLAY选中态进入菜单即清选择，返回不恢复悬空源。键盘焦点仅在当前屏幕/浮层。

## 4. 状态机

BOOT→HOME或ERROR；HOME→LEVEL_SELECT/PLAY/PAUSE_SETTINGS/CREDITS。PLAY可带selection；逻辑提交后短暂ANIMATING再PLAY/WIN/DEADLOCK。PAUSE_SETTINGS保存原screen与returnStatus；其间游戏时钟停止。RESTART_CONFIRM取消返回原screen（死局仍死局），确认从初始新run。DEADLOCK可UNDO→重新派生PLAY/DEADLOCK或重开；不可普通前进。WIN只可下一关/再试/选关；L20下一步为COLLECTION_COMPLETE。ERROR_RECOVERY可以重试资源/恢复备份/回主页；重大内容错误禁继续该关。

后台触发`gameplayStop`一次并暂停音乐；回前台先显示暂停覆盖，玩家点“继续”才start，避免未看屏幕计时。所有弹窗有关闭/取消（44CSSpx）；死局弹窗关闭后显示禁前进棋盘但撤销/重开仍可用；错误弹窗关闭回HOME。胜利弹窗关闭回选关，完成状态保留。

## 5. 事件定义与发送边界

公共事件外壳：`{schema_version:1,event_id,session_id,run_id,seq,event_name,level_id,variant,active_ms,revision,command_epoch,command_seq,payload}`（非命令事件两命令字段为null）。seq单会话递增，event_id=`session_id:seq`，不含姓名、邮箱、广告ID、指纹或IP自采。active_ms为前台PLAY/ANIMATING有效时长，暂停/广告不计；分析raw操作次数不随undo回退。UNKNOWN指标不填0。

| event_name | payload 必填字段 | 发出时机 |
|---|---|---|
| session_start | build_id, platform_id, content_hash | 每次会话一次 |
| level_start | entry:new/replay/resume, attempt | 初始/恢复后一次 |
| action_accepted | op, src/dst或at, logical_action_count, state_hash | 原子提交后 |
| action_rejected | op, reason | 只有显式输入；BUSY单次手势最多一次 |
| selection_changed | previous, current, reason | 仅本地QA；测误触，不向外部自建统计发送 |
| seal_unlocked | sealed_colour, newly_open_trays | 一次seal结果；无新锁则空数组 |
| undo_used | restored_revision_source, remaining_history | undo成功后 |
| hint_result | result, explored_states, elapsed_ms | 搜索结束；UNKNOWN不说无解 |
| level_end | outcome:win/deadlock/restart/leave, active_ms, accepted_total, undo_total, rejected_total | win幂等一次；死局进出可多次但episode区分 |
| save_issue | code, recovery:backup/memory/reset_cancelled | 不包含存档内容或系统路径 |
| ad_result | request_id, result:shown/skipped/error/timeout, active_ms | 仅未来获准变现版本，广告失败仍前进 |

默认全部只入本地最多1000条环形QA日志，满则丢最旧、显示dropped_count。生产P04只允许Bridge支持的事件映射，未支持字段留本地或不采；不嵌GA4/自建统计终端，不把离线日志自动上传。P02 Basic无SDK时用平台自动统计+本地测试；Full只用批准SDK。P01若未来获准另版，编译禁开发者回传/广告/外链且不导出QA；当前不建此候选。P05/P06的统计严格以书面SDK和用户授权为准。

## 6. 存档结构与原子恢复

主槽key=`g02.save.v2`，备份key=`g02.save.v2.backup`。schema_version=2；示意包：

```json
{"schema_version":2,"content_hash":"sha256-of-current-game-spec-bytes","save_seq":7,
 "profile":{"completed":["L01"],"settings":{"music":true,"sfx":true,"reduced_motion":false,"locale":"zh-CN"}},
 "active_run":{"level_id":"L02","variant":"V0","run_id":"r7","revision":0,
  "logical":{"stacks":[["A","B"],["B","A"],[]],"sealed":[null,null,null]},
  "logical_action_count":0,"history":[],
  "source_command_context":{"epoch":"e-old","high_watermark":0},
  "replay_checkpoint":{"ordinal":0,"revision":0,"logical_action_count":0,"logical":{"stacks":[["A","B"],["B","A"],[]],"sealed":[null,null,null]},"history":[]},
  "replay_tail":[]},"checksum":"sha256-of-canonical-payload-excluding-checksum"}
```

上例是初始盘面/revision=0/空历史空尾段的结构示意，hash字符串是占位说明；实际写入需计算hash，checkpoint+tail必须重建当前逻辑/历史/revision，不能省略已发生记录。source_command_context只供诊断，**不可用作恢复后的身份分配器**。

采用**每次恢复新epoch**方案：从任一有效槽恢复原run_id、revision、盘面、逻辑动作数、最多128撤销快照和回放；在启用输入/SDK回调前，用OS加密随机UUID生成与source epoch不同的新command_epoch，初始化high_watermark=0/cache空/next_seq=1。epoch不参与关卡随机性。旧pending命令/选择/动画全部取消；原run不变但旧epoch所有命令与SDK迟回丢弃，绝不重试到新epoch。不能用revision、回放长度、存档save_seq推新命令序号。UUID失败保持恢复错误态，不复用旧epoch。前台同一页普通暂停继续不换epoch；页面重载/存档恢复/主动读云档均换。

每次成功move/seal/undo、暂停、设置改变、完成关后写；相同缓存应答不写，首次拒绝也不触发写。失败决定的内存缓存/未保存回放可能随崩溃丢失，但恢复epoch强隔离确保旧命令不重做。最多128历史快照，记录logical及logical_action_count；revision、事件序号不进入可回退快照。

回放与幂等窗口独立：每个**首次消费的决定**（接受或拒绝）记录`{ordinal,command,accepted,reason,before_hash,after_hash,revision_before,revision_after}`；transport拒绝/缓存回复不进入回放。ordinal跨epoch单局递增。尾段≤4096：第4097条加入前，先将前4096条的**终点**逻辑、revision、logical_action_count、完整最近128撤销快照与ordinal=4096写入checkpoint，清尾段，再加第4097条。即便尾段第一条是UNDO，也有checkpoint历史可恢复；拒绝为no-op。快照必须是终点而非当关初态。之后每4096条同法轮换；导出只证明checkpoint起的片段，不假称完整开局录像。当前epoch的128receipt缓存不因checkpoint清理而变；恢复时按新epoch清缓存，不从回放重建旧缓存。

历史完成ID排序去重，下一可选关由已完成连续前缀推导，不能信任外部传入unlocked_level。

写协议：产生新payload/checksum→旧有效主槽写backup→新包整体setItem主槽→读回验hash。中途失败保留旧有效包，内存继续并提示“本次进度暂未保存”。读取两槽各自校验schema、checksum、content_hash、状态守恒及seal需求；选择有效save_seq最高者。存储禁用/满转内存模式，不循环请求授权。两槽都坏提示“进度无法读取”，可取消回主页或明确确认后新开；不能静默清进度。校验失败包在本机隔离，不上传。

版本迁移：当前准备合同升级v2，尚无投产v1玩家档。旧设计v1若被输入，仅保留经校验completed/设置并提示确认从活动关初态重来，不迁移活动盘/历史或旧命令身份；v2有效同content_hash档才能精确恢复并换epoch。未知较新schema只读拒绝覆盖，显示需更新。content_hash变更时只保留合法completed与设置，活动盘面及history不能跨版本复用；经用户确认从该关初始重来。云存档冲突以平台协议为前提；未有合并语义时保留本地/云两份并让玩家选择，不逐盘拼接。P04云写失败降级本地，仍不得开发者私服回传。

## 7. 哈希、回放和时序

离线报告的state_hash输入严格为UTF-8 `json.dumps([stacks,sealed_normalized],separators=(',',':'))`，未封归一化为空字符串，盘ID次序固定，颜色ASCII。例如`[[["A"],["B"],[]],["","",""]]`。SHA-256仅用于一致性/损坏检测，不能当反作弊安全或加密存储。存档checksum对除checksum外的payload递归按键字典序、无空格、UTF-8编码；数组保持顺序。content_hash对发布时game-spec.json原始字节，禁止重排后沿用旧hash。

广告/音频/云存档回调携带run_id、command_epoch、request_id；先筛run/epoch再按request_id一次结算，旧epoch不写档、不发事件、不复活界面。回调不会改变RuleCore。可见性变化和超时按单一运行队列处理；广告request_id只结算一次、超时10秒回skipped，迟回不二次跳关。当前广告关闭，此为未来Full适配验收合同，未执行。

## 8. 已知异常清单

断网：已下载内容可玩，SDK失败禁变现并提示本地存档；首次资源失败可重试。WebGL丢失：暂停、保存逻辑、恢复渲染，禁止重复发动作。多标签页：启动检测同key更大save_seq，进入只读提示，避免旧标签覆盖；玩家选择刷新后读最新，不自动合并。系统时间回拨不影响规则、收益（无收益）或active_ms；用单调计时累加。连续快速点击、pointercancel、SDK不回调、保存配额满、损坏/新版本存档均需10中的测试，当前不是已通过结果。
