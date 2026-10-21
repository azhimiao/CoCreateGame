# G01 系统、事件与数据合同

全部接口为待施工设计 HYPOTHESIS；声明不是游戏源码。本包只有离线验证器。规则权威见03，坐标与解见game-spec；不一致应报阻断。

## 实体与不变量

| 实体 | 类型/字段 | 不变量 |
|---|---|---|
| Level | id、width/height、arrows、gates、walls、manifest、seed | 20关唯一ID；尺寸4—7；箭条2—8；门0—2；seed不参与运行随机 |
| Arrow | id:string；direction:N/E/S/W；cells:[x,y][]；toggles:gateId[] | 1—8格、连续、无重复；末段=方向；ID关内唯一；引用门存在且不重复 |
| Gate | id、cells、initial_open:boolean | 初态与箭条/墙/其他门都不重叠；关闭门才阻挡；不移动 |
| Attempt | levelId、acceptedExits:arrowId[]、revision | 每次EXIT只能记录一次；日志重放必须始终合法；撤销删尾、reset清空 |
| DerivedState | removedMask:uint8、gateOpen:map、manifestCursor、legalMoves、solvable、terminal | 不保存为真相；从Level+日志导出；mask范围0..2^n−1 |
| Progress | completed:set<levelId>、activeLevel、tutorialSeen:set | stamp=completed.size；下一关须前一关完成；不支持跨内容版本误用 |
| Settings | language:en/zh-CN；sound:boolean；music:boolean；reducedMotion:boolean | 首次按locale选语言（未知locale回英文）；声音on、音乐off、弱动效遵循系统 |

所有坐标整数、边界内；拒绝NaN、负数、浮点坐标、断裂折线、重复ID、未知键、重复toggle、manifest长度不等箭条数。schema负责形状，validator负责交叉引用/几何/可解性；schema通过不等于关卡合法。

## 规则模块的输入输出

未来实现接口（类型签名说明，不在本轮实现）：

```text
validateLevel(Level) -> ValidationIssue[]
derive(Level, acceptedExits[]) -> State | InvalidReplay(index, reason)
evaluateExit(Level, State, arrowId) -> Legal | Reject(reason, blockerCell?, blockerId?)
commitExit(Level, Attempt, arrowId, expectedRevision) -> Accepted(nextAttempt, events[]) | Reject
undo(Level, Attempt, expectedRevision) -> Attempt | NO_HISTORY
solve(Level, State) -> {solvable, firstWinningArrow?, solution[], visitedCount}
save(SaveEnvelope) -> Promise<{persisted:boolean, reason?}>
```

`expectedRevision` 与当前不符返回 STALE_REVISION，无变化。每次EXIT/UNDO/RESET/关卡切换+1；设置变更另由统一存档协调器升rev。无合法EXIT但非空才是DEADLOCK；求解器认为无解但仍有合法EXIT则是可继续的LOSING分支，不自动弹败。

状态键仅removedMask；门状态由初态XOR被移除箭条的toggles导出，船期游标为popcount(mask)或0。不同顺序到同一mask时后续规则相同，因此求解可合并；接受日志仍须逐步重放，不允许用mask跳过历史非法操作。求解选择ID字典序，成功解一律长n，不能用最短步数伪称难度。

## 屏幕与局内状态机

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

先逻辑提交，再渲染动画。页面隐藏立即落盘、停止音频；动画中隐藏/旋转/WebGL丢失时取消动画，恢复后按提交后状态重绘，避免重复提交。暂停只冻结呈现，不能反转已提交操作。胜利转场前必须持久化completed集合；失败写盘允许内存继续并明确提示。死锁面板关闭后棋盘可查看但仍没有合法走法，撤销/重来始终可用。

## 事件表（本地内部总线，不等于统计回传）

每个事件含 `eventId=session-local-seq`、`levelId?`、`revision`；调试包可含monotonicMs，不采集真实身份、文本输入、设备指纹。相同eventId由消费方去重。

| 事件 | 必需载荷 | 发出时机/消费者 |
|---|---|---|
| ContentLoaded / ContentRejected | contentVersion / issueCode | schema+语义验证后；BOOT |
| AttemptStarted | levelId, resumed, variant | 进入关卡；教程/本地QA |
| ExitRequested | arrowId, expectedRevision, inputType | 输入抬起或键盘激活；仅规则模块 |
| ExitRejected | arrowId, reason, blockerCell? | 校验失败；UI提示；不改日志/游标/进度 |
| ExitCommitted | arrowId, fromMask, toMask, gatesChanged[], cursor | 逻辑原子提交一次；存档/动画 |
| UndoCommitted / ResetCommitted | fromMask,toMask | 撤销/重来；存档/重绘；撤销不撤历史completed |
| HintShown | arrowId?、solvable | 求解后；UI；无解文案需匹配 |
| DeadlockDetected | mask, legalCount=0 | 提交/恢复后非空无合法移动；面板 |
| LevelCompleted | levelId, firstClear, stampCount | mask全满且船期耗尽；进度幂等合并 |
| SaveSucceeded / SaveFailed | revision / errorCode | 存档协调器；失败显示一次非阻断条 |
| VisibilityChanged / AudioInterrupted | hidden / reason | 生命周期；静音和重绘 |
| AdapterReady / AdapterUnavailable | profile, capabilitySet / reason | 平台初始化；不阻断已可离线玩的局面 |

P02仅将获准的生命周期映射至官方gameplay/loading API；P04只使用Bridge能力；本地调试事件不能默认变成后台采集。P01_RESERVED彻底不回传，CREDITS也不放URL。所有发布包移除调试导出入口。

## 存档格式与恢复算法

key=`G01.signalharbor.{profile}.v1`，每渠道独立，内容上限64KiB（HYPOTHESIS）。示例结构：

```json
{"version":1,"content_version":"1.0.0","revision":7,"completed":["L01"],"active_level":"L02","accepted_exits":["b"],"tutorial_seen":["base"],"settings":{"language":"en","sound":true,"music":false,"reducedMotion":false}}
```

schema/ID/设置类型通过后逐步重放accepted_exits，拒绝任何非法日志。完成集合必须是L01起连续前缀；完整日志恢复时若全清但completed未含当前关，执行一次幂等首通合并；不能信任存盘印章数字。进入另一关前先落盘，新关清日志；只保留一个活动局，完成集合保留所有首通。

写入流程：编码新envelope到`.tmp` → 读回验证 → 旧main拷贝`.bak` → main替换为新内容 → 校验main → 清tmp。Web Storage没有跨key事务，启动检查main/tmp/bak三份，选择**合法且最大revision**者；同revision不同内容进入RECOVERY供用户选择，不静默合并当前局。所有更新串行，失败回退内存态并显示“此设备无法保存，当前游戏仍可继续”。备份不是联网备份。

版本：无档=v0新档；v1按上述严格验证；未知更高版本不覆盖，只显示“此进度来自更新版本，请更新游戏或明确选择新建”；旧contentVersion没有显式ID映射则不套用旧日志，保留备份，用户确认才新档。损坏档不可把随机数据当过关。

云存档仅在同一渠道的能力确认后启用，先验证两边；completed集合取并集并检查连续前缀，active日志取更高rev；同rev冲突展示关卡与已出港数，用户选择。云失败回本地，不能上传P04数据至自有服务器。无SDK Basic只有本地；P01无开发者云；无跨站同步或账号注册要求。

## 边界与竞态

双击：第一点击提交后锁棋盘到动画结束，第二次丢弃；不能把旧EXIT排到下一状态。音频尚未获手势权限则无声继续。焦点丢失取消按下对象，恢复后必须重新按下。pointerup落在别的箭条不转选。键盘重复keydown忽略。重来确认“取消”保留原状态；不同时触发重来与退出。SDK回调在场景销毁后按token丢弃。未来若启用广告，必须暂停音画和输入、回调去重、不授予任何未确认奖励，且另审本产品规则。
