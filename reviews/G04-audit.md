# G04 独立审计｜REVISE（r2复核）

## r2独立复核结论｜2026-10-21 19:05 +08:00

冻结输入：`reviews/G04-recheck-r2/AUDIT_SNAPSHOT.json`；machine spec SHA-256 `dc0c5248a5e037fa96bf61ecf4eb5ffb4bb2533910f4010442f8e1959baac8da`。包内37项payload、ZIP 38成员及收据均与18:59:29版本相符，ZIP SHA-256 `0b1bce595af0643fe9404b04ee038d2e465702f3474369f540e915b89478ceac`。作者源文件在只读复核期间与冻结hash一致。

**当前裁决：0 BLOCKER、1未关闭MAJOR、0 MINOR；REVISE。** r2的M02、M03及m01/m02/m03已独立复核关闭。M01保持开放：Paint Master已有局部有效输入、过关、耗尽失败、菜单重开及再操作；完整连续首30秒/5分钟仍未取得，Bloxorz/Liquid2核心输入仍受阻。不能把市场证据限制扩大成“全部只有网页说明”，也不能据局部观察签无条件GO。

G04作者STATUS/REVISIONS和ZIP内状态是提交时的交接快照；本报告记录审计员在其hash下的当前复核结论。作者的`PENDING_RE_REVIEW`历史措辞不要求为更新状态而改写/重打包。本结果不等同Ready、开发或投稿批准。

独立r2脚本与160项结果：[复核代码](F:/CoCreateGame/reviews/recheck_g04_r2.py)、[结果](F:/CoCreateGame/reviews/G04-checks/r2/results.json)。没有重做未变关卡的79,998次状态转换搜索。

审计者不是 G04 作者。审阅 00—12、game-spec/tasks 与两份 schema、全部关卡见证、21 条 QA 向量、验证器、原始报告及交付清单。首轮快照为 2026-10-21 18:13:39 +08:00；18:24、18:26 两次复核主控补丁。原始快照及每次复核均保留在 reviews 下，不覆盖历史证据。

**首轮：0 个未解决 BLOCKER，3 个 MAJOR，3 个 MINOR；2 个旧 MAJOR 此前已关闭。r2复核后：0 BLOCKER、1个MAJOR、0 MINOR；另5项关闭。结论仍为 REVISE，不签无条件 GO。** 当前关卡并无已发现的无解或最短步错误；唯一剩余MAJOR为对标观察不足。未获未来开发/投稿授权、未运行 Cocos 或尚无报价，均不作为当前规则缺失的 Finding。

## 只凭施工档案的独立复述

首次进入 BOOT/LOADING，校验内容、初始化本渠道 profile、读取有效存档，然后 HOME。新访点“开始”直入 L01；合法活动会话显示继续。L01 是下层三格横道，初始位置 [0,0,1]、bits=0；向右进入开关使 bits=1，再向右到 [0,2,1]，用 2/6 步胜利。WON 页锁棋盘和撤销，提交完成记录与三星，可下一关、重玩或回地图。这个事件链可描述首 30 秒的预期内容；加载 3—10 秒只是设计目标，不能断言实际 30 秒内一定完成首关。

继续按 L02、L03、L04……顺序解锁；L02 的见证 RRDD，L03 RRXLL 首次用升降，L05 进入互补门教学。前五分钟能经过多少关取决于真实阅读、思考与输入，档案没有测量结果，不能据见证长度折算分钟。遇到无效移动只提示，不耗步；有效操作导致脚下关闭或步数耗尽才出现失败页，优先“撤销一步”，也可重开。没有体力、币、IAP 或广告门槛。提示免费、从当前状态求解，只给下一命令；确认后本局 assisted 保持 true，撤销不能洗掉，重开可清本局辅助标记。

两层使用相同尺寸网格，一枚无朝向光标；门由共享位 A/B/C 的指定值决定支撑，进入开关 XOR 翻位。U/R/D/L 正交走一格；X 只在升降台去另一层同坐标，均耗一有效步。观察另一层只是预览，不能移动棋子。旧 bits 先检目的格 → 保存前态并落位/加步 → 应用旧 pending、清空并查脚下 → 触发新开关并查脚下 → X1 信标顺序 → 目标 → 步数上限。目标须坐标、精确 bits、pending=0、全部信标共同满足；最后一步达标胜于耗步，脚下关闭/错序先于胜利。没有 WAIT，无效动作、预览、暂停不推进延迟。

B0 是全部正式 20 关。X1 只加顺序信标，提前踩未来信标失败、已完成可复踩；X2 只延迟开关至下一合法移动落位后生效，预检仍用旧 bits；二者不组合。PLAYING/FAILED 可恢复完整前态撤销，WON 不可撤销。三星是未提示且 used≤par，二星 used≤par+2，其他预算内一星；最终保留路线计步，不统计全部试错。首通开下一关，重复胜利只取最高星/最低 bestUsed。

规则接口为 validateContent、createSession、reduceCommand、undo、restart、solve、computeStars、commitWin、serializeSave、restoreSave。纯规则不依赖引擎/SDK；Session另持历史、辅助标记和attemptId。r2中reduceCommand仅出RuleFacts，reduceSession结合SessionContext补assisted/attempt/事件序号；SessionController唯一发布，预留事件批次并原子推进seq，胜利进度只提交一次。事件依次描述命令、pending、开关、信标、状态和终局；动画不能改规则，最长180ms输入锁丢弃移动，撤销/暂停可中断，旧回调按token作废。T03 Session/EventBus、T07 Boot装配及依赖明确，M02已关闭。

存档按profile隔离，双槽写旧槽、回读后更新指针；读最高有效revision，按acceptedCommands重放恢复历史与终态。r2的SaveEnvelope以唯一Settings权威、Progress和Session组成；CJ1按ASCII键递归排序、UTF-8保留中文、无Unicode归一化、受限整数，校验和不含自身。完整schema、坏档/迁移分支及固定样例在SAVE_CONTRACT中闭合，M03已关闭。有效动作/撤销/重开/胜利/设置/后台触发保存，可合并250ms；配额或安全异常转内存并常驻提示。单槽坏回另一槽；双坏询问新开；未知版本保留字节；内容hash更新保留有效完成记录、放弃中间局。云同步V1关闭。真实持久化故障I/O留未来验收。

## 实际独立验证

验证脚本 [audit_g04.py](F:/CoCreateGame/reviews/audit_g04.py) 自行建模，没有调用作者 step 来产生期望值；以包含 used/终态的有限状态图搜索，随后才与作者逐转换比对。它是审计工具，不是游戏源码。完整证据见 [independent-results.json](F:/CoCreateGame/reviews/G04-checks/independent-results.json)。

- 20 正式关、2 实验关的见证逐步合法、终态 WON、最短步均等于 par；所有 trace 与交付报告一致。正式 05 的 20 段局面 JSON 和两实验投影字段也逐项一致，名称/意图另列标题和摘要，不误判为冲突。
- 21 条固定向量全部符合独立语义，包括 WON 锁撤销、FAILED 撤销、旧 pending 关闭目的格后跳过新开关、目标 pending 未空不能胜、预算最后步先判胜。
- 对 22 关可达状态做 **79,998 次**动作/终态/非法 WAIT 转换比对，未发现分歧；这不覆盖浏览器、产品存储、动画或 SDK 实现。
- 两组同几何消融：X1 9 步/B0 5 步，X2 9 步/B0 7 步，规则差异确实改变可行路径；不能由此推出更好玩。第二套平衡盲测地图尚待获批后交付，12 已如实披露。
- 两份 schema 有效，16 任务依赖存在、无环，所有施工任务均位于 T01 人类决策之后；见下文任务覆盖问题。原报告输入 hash 与冻结文件一致。作者验证器在 reviews 副本重跑 PASS。
- 原环境一次子进程误用未装 jsonschema 的另一个解释器，已保留失败日志；改用已核版本的同一 sys.executable 后 PASS，不将前一次环境失败归罪作者。
- 初轮 ZIP 的 CRC、成员清单和内置 manifest 相符；准备 ZIP 不是游戏包体或可玩构建证据。

| 关卡 | 独立最短步 / 预算 | 见证 | 结果 |
|---|---:|---|---|
| L01 | 2 / 6 | RR | PASS |
| L02 | 4 / 8 | RRDD | PASS |
| L03 | 5 / 9 | RRXLL | PASS |
| L04 | 5 / 9 | DRRXD | PASS |
| L05 | 9 / 14 | LURRXUDLL | PASS |
| L06 | 8 / 12 | UUXRRXDD | PASS |
| L07 | 7 / 11 | RRDDXLL | PASS |
| L08 | 11 / 17 | RRRDDLRXLLL | PASS |
| L09 | 11 / 17 | RRRDDLRXLLL | PASS |
| L10 | 9 / 14 | RRRDDXLLL | PASS |
| L11 | 17 / 26 | RRRRDDXLLRRDDLLLL | PASS |
| L12 | 15 / 23 | RRRRDDXDDLLLRLL | PASS |
| L13 | 26 / 39 | RRRRXLLRRDDLLLLDDRRRRXLLLL | PASS |
| L14 | 17 / 26 | RRRRDDXLLRRDDLLLL | PASS |
| L15 | 19 / 29 | RRRRDDLRXLLRRDDLLLL | PASS |
| L16 | 19 / 29 | RRRRDDLRXLLRRDDLLLL | PASS |
| L17 | 22 / 33 | RRRRXLLRRDDLLRRDDXLLLL | PASS |
| L18 | 15 / 23 | UURRLLXUURLRRRR | PASS |
| L19 | 26 / 39 | RRRRXLLRRDDLLLLDDRRRRXLLLL | PASS |
| L20 | 18 / 27 | RRRRDDLLLLXRRLLXDD | PASS |

## BLOCKER

未发现当前内容无解、未知的胜负条件或无法消解的核心结算顺序。下列 MAJOR 修订前仍不能升无条件 READY；不能把“本次没找到 BLOCKER”改写为 GO。

## MAJOR（含修复历史；当前仅M01开放）

### G04-M01｜对标观察已有局部实证，完整时间窗与两种关键范式仍不充分

**位置：** [02_Benchmark_Playthrough.md](F:/CoCreateGame/games/G04/02_Benchmark_Playthrough.md)“时间窗证据空白”；[observation.md](F:/CoCreateGame/research/playthroughs/G04/observation.md)“范围与时间审计 / 给 P0 的证据增量”。

**证据与影响：** 不能再说本项目全部只有网页说明。后补 Paint Master 已有 14 次核心输入、一次单关完成、故意耗尽步数失败、菜单重开及重开后响应；本审计读取日志并目视核对 027/028 的 Move 10→9 和左列变化、033 LEVEL 2、053 GAME OVER。Bloxorz/Liquid2 仍受阻。离散截图跨度 283.708 秒不是连续五分钟，三款均无完整连续首 30 秒/5 分钟；桥/压力状态与液体控制的真实交互、后期/回归仍未确证。作者 UNKNOWN 披露诚实，局部成功不能补全其余流程或支持原创双层机制的体验判断。

**修法：** 把后补索引及已观察/未观察节点并入 G04 的证据覆盖表；对影响教学与规则取舍的节点补可核查操作、官方教学或合规公开视频，注明来源/定位/覆盖局限。PROMPT_01 允许无法操作时作间接分析，**不要求十二份真人录像，也不因 SECONDARY_RECONSTRUCTION 自动判伪造**。若仍不足，应保留“档案交付完成，但对标证据不足以无条件 Ready”的明确结论。

**验法：** 第三人从证据逐节点区分输入、画面响应、成功/失败、重试/回归和未知；不得拿驻留时间、宏观宣传或设计脚本补成实玩。完整时间窗未证明就继续标缺，观察充分的其他节点可以单独关闭。

### G04-M02｜纯规则事件缺少输入来源，Session/Boot 任务归属未闭合（CLOSED r2）

**位置：** [04_Systems_and_Data.md:21](F:/CoCreateGame/games/G04/04_Systems_and_Data.md:21) reduceCommand 与“事件次序与载荷”；[07_Tech_Architecture.md:11](F:/CoCreateGame/games/G04/07_Tech_Architecture.md:11)；[tasks.json](F:/CoCreateGame/games/G04/tasks.json) T02/T03/T07/T10。

**证据与影响：** reduceCommand 输入只有 Level、RuleState、命令，却规定返回 LevelWon{used,par,assisted} 和含 attemptId/seq 的事件；assisted、attemptId、seq 明确不在 RuleState。两局相同 RuleState、不同 assisted，纯函数输入相同而要求输出不同。可以由 Session 层补事件，但档案未明确这一边界。与此同时明确要求唯一 SessionReducer 和 Boot 单入口场景，16 项 write_scope 没有覆盖场景文件，Session/应用总线的产物/owner 也不明确；仅有 DAG 无环不足以证明集成有人负责。

**修法：** 由作者确定规则事实事件和 Session 富化事件各自接口、参数与唯一发布者；给 Boot 场景、SessionReducer、应用状态机/总线的产物写域和集成验收分配明确责任。无需改变玩法，也无需本轮写实现。

**验法：** 冷读者给两份仅 assisted/attemptId 不同的 Session，能唯一说明 reduceCommand 的输出和最后一次 LevelWon 的产生位置；T03→整合任务有明确依赖/写域，任一必需场景/脚本有且仅有负责者；动画和重复 SDK 回调不能重复 commitWin。

**关闭证据：** r2把`reduceCommand(Level,RuleState,op)`固定为纯RuleFact，Session字段不进入规则输入；`reduceSession`负责元数据富化，Controller在同次提交预留并推进seq、以唯一发布者广播，Progress结算单入口幂等。两个相同规则状态、不同assisted/attemptId/nextSeq的固定向量给出相同事实、不同LevelWon信封；Schema负向区分事实/发布事件。T03独占RuleCore/SessionReducer/Controller/EventBus，T07独占Boot.scene/meta及CompositionRoot/AppStateMachine并依赖T03/T08/T09；T02只持BuildProbe。10个required artifact逐项恰有一个owner，缺Boot/重复Session owner负例被拒。独立冷读合同、事件Schema/样例及任务写域；验证器重跑PASS，作者源hash与18:59快照一致。该关闭针对规格交接完整性；未来真实TS提交/SDK重入仍留明确施工验收，不称已运行。

### G04-M03｜存档校验要求明确，但缺少可互认的完整数据合同（CLOSED r2）

**位置：** [04_Systems_and_Data.md:13](F:/CoCreateGame/games/G04/04_Systems_and_Data.md:13) Progress；同文件“存档格式与事务”；现有两份 schema 只管施工规格和任务。

**证据与影响：** restoreSave 要求 Schema/哈希/重放校验，但没有 SaveEnvelope/Progress/Settings 的完整 schema 或等价类型表/固定样本。Progress 内有 settings，信封又有 settings，二者冲突时谁权威未定；updatedAt、revision 边界、空 bestUsed 的表示、完整重放比较字段也未封闭。“键排序紧凑 JSON 的 SHA-256”未给递归排序/Unicode 转义及测试向量，合法中文内容在不同序列化选择下可产生不同摘要。独立存档与 UI 工程师仍需自行定互认协议。

**修法：** 作者补齐一个权威设置位置、完整字段类型/默认值/边界/恢复判定及规范化摘要合同；交至少一个含中文与活动会话的合法样本和预期 checksum、一个损坏/冲突样本。可作为数据规格完成，不要求现在实现浏览器存储。

**验法：** 两个独立实现按文档产生完全相同字节/摘要，能对同一槽作一致接受/拒绝，并明确 settings 冲突、FAILED 恢复撤销、未知版本和内容更新的确定分支；真实双槽故障注入留在获批后的 T08，不冒充本轮通过。

**关闭证据：** SAVE_CONTRACT、严格SaveEnvelope Schema及固定夹具现为同一r2权威；Settings唯一位于信封，进度/活动会话不得私藏副本。字段、默认值、大小/安全整数/时间/状态边界、20条记录、acceptedCommands回放、progress派生、profile、双槽同revision冲突、失败槽/双坏/未知版/内容更新均有确定分支。CJ1规定递归键序、紧凑JSON、中文原样UTF-8、控制字符转义、整数格式和排除checksum字段；含中文活动/FAILED局、固定UTF8/hex/SHA、12负例/迁移样本。审计员使用独立编码器核摘要，并以Node20.11 JSON/crypto重现字节；独立规则模型重放合法活动局及FAILED撤销前态，8个额外边界变异均得预期拒绝/恢复。作者合同验证器在reviews冻结副本重跑，完整结果与交付报告一致，160项检查通过。真实浏览器双槽I/O与TS存档实现仍未运行，文档没有宣称运行。

## MINOR（r2复核关闭）

### G04-m01｜竖屏几何约束与断点优先级冲突（CLOSED r2）

**位置：** [06_UI_Art_Audio.md:9](F:/CoCreateGame/games/G04/06_UI_Art_Audio.md:9)“响应式坐标与触控”。**证据：** 高 64 的目标条放至少 72×72 缩略图；600×400 同时满足 width<700 的竖屏条件和宽高比≥1.3 的横屏条件。**修法：** 明确溢出/行高或调整几何，并给唯一断点优先级。**验法：** 列出 320×568、600×400、844×390 的确定布局算式；获批后按 10 的截图/触控标准实测。

### G04-m02｜20关有可量化的重复与机制贡献风险（CLOSED r2：披露/测试规格充分）

**位置：** [05_Levels_Economy.md](F:/CoCreateGame/games/G04/05_Levels_Economy.md) L08/09、L11/14、L13/19、L15/16 和 L20。**证据：** 四对见证相同；独立删除全部门的诊断中 15/20 关最短步不变，L20 原18步/去门14步，L19原26步。该诊断不等于门完全无用，也不证明题目不好玩；作者已承认不单调。**修法：** 每对说明要检验的新认知与反例，不以换 mask/步长自称新策略；将重复感和绕过教学列入内容验收。**验法：** 逐对比较最优/错误分支及机制消融，再用12的盲测观察，允许保留教学复用或删改，不要求为了递增步数重写关卡。

### G04-m03｜审计产物路径与实际权限不一致（CLOSED r2）

**位置：** [09_Implementation_Plan.md:9](F:/CoCreateGame/games/G04/09_Implementation_Plan.md:9)、tasks T00/T01 的 review/ 路径。**证据：** 冷读计划会寻找项目内 review/independent-audit.md，本次用户要求根 reviews/G04-audit.md，已有宪章也将本次审计置于根 reviews。**修法：** 主控/作者同步外部审计产物引用，或显式登记映射；审计员不越权写 games。**验法：** 状态页和 T01 能定位本报告/JSON，不以另造作者自查替代独立审计。

三项minor的r2关闭依据：m01按明确断点优先级独立算六种视口及过小屏，目标/棋盘/侧栏和控件满足文档尺寸；m02作者明确四对同见证、15/20关删门最短步不变，并设置未来12人机械重复识别证伪阈值，关闭披露与测试计划，不证明好玩；m03 T00实际引用`../../reviews/G04-audit.md/json`，任务schema/write域与审计员权限一致。细节和几何数值见160项复核结果，未重复完整状态搜索。

## 已关闭 Findings（保留历史）

**G04-M04｜MAJOR｜独立类型检查工具误锁 npm 不存在的 4.1.0。** 初轮07把 Cocos 文档语言标签当工具包；独立 GET npm registry 4.1.0 返回404、4.1.2返回200，记录在 [typescript-registry-check.json](F:/CoCreateGame/reviews/G04-checks/typescript-registry-check.json)。18:26补丁保留语言标签4.1.0，新增实际工具4.1.2并同步07/08与schema。独立重读、校验报告hash及重跑PASS；**CLOSED**。只关闭可获得性错号，不宣称安装/兼容已通过。[Cocos语言文档](https://docs.cocos.com/creator/3.8/manual/en/scripting/language-support.html)、[npm版本元数据](https://registry.npmjs.org/typescript/4.1.2)。

**G04-M05｜MAJOR｜campaign记录与实验版本校验漏检。** 初轮仅把原 L01.id 改为 G04-L99，或把其 variant 改 X2，作者完整 checker 都 PASS。原22关本身合法，此反例指验证护栏，不指原关无解。主控补 schema 与 campaign_semantic，限制 L01—L20/B0/无信标、记录顺序与集合一致、实验分离；新增四负例。18:24 独立重跑原数据仍PASS，两原反例均被拒，18:26新工具字段后再跑完整PASS；**CLOSED**。见 [复核1](F:/CoCreateGame/reviews/G04-checks/recheck-01/results.json)、[复核2](F:/CoCreateGame/reviews/G04-checks/recheck-02/results.json)。

## 十维结论与后续验收边界

市场：独立重开官方 Bloxorz、Liquid2、Paint Master 说明，支持所引公开玩法；它们不证明当期采购或净收益。[Bloxorz](https://www.coolmathgames.com/0-bloxorz)、[Liquid2](https://www.coolmathgames.com/0-liquid-2)、[Paint Master](https://www.coolmathgames.com/hi/0-paint-master)。后补局部实证已计入 M01；共享24卡的完整交付与研究证据充分性另行复核。

玩法/原创：可复述到胜负，双层持久棋子、位型门和精确终局不同于 G01 箭头移除依赖；未发现直接复制原作布局/素材的证据，但无全球原创性证明。X1/X2 可以独立消融，尚无玩家正向结论。数值/内容：20关有解、预算有效；作者现已如实标记四对同解，给出删门分布与可证伪的重复认知实验，未把配置数偷换成策略数。数值对照并不证明体验，通过的是规格披露与检验计划。

工程/体验：核心动作顺序闭合，输入、错误、减动效、色形编码有规格；M02/M03及小屏几何文档歧义已按r2消除。仍未有真实渲染、Cocos、真机或用户理解证据；它们属于后续任务，不能谎报已验，也不因本轮未获开发批准再添当前规格BLOCKER。

发行/统计/合同：P01干净包剔除广告/外链/开发者回传/姓名输入；P02无SDK Basic按全包50/20MB、有SDK按首可玩，Full强制SDK，总250MB/1500文件；规则与独立打开的官方页相符。[Coolmath投稿](https://www.coolmathgames.com/submit-a-game)、[CrazyGames技术规范](https://docs.crazygames.com/requirements/technical/)。P04只是未来条件，不能默认装Bridge/GA4。对SDK版本、网络与许可精确锁定留有门槛；不能从CSP或可加载域推导合同授权。

IP/商业：引擎tag的MIT可重核，不自动覆盖编辑器、传递库和素材；源文件/工具/运行库的权利保留有区分，P01 notices 中URL冲突不能删许可文字解决。[引擎tag许可](https://raw.githubusercontent.com/cocos/cocos-engine/3.8.7/LICENSE.md)。没有虚构价格、RPM、CPI、回款或成功率；实际合约、净回款和名字检索仍未知，但不自动阻止设计规格。

可证伪：12规定理解/误触/规划失败阈值、一次修订再测及单独舍弃X1/X2，退出仍进分母，小样本不作显著性主张；可以支持后续止损。第二套实验材料和玩家测试在获批后交付，不把它们不存在说成20关缺失。裁决为 **REVISE**：r2已关闭M02/M03及三项minor；M01继续开放，局部真实输入增量已纳入，但完整时间窗和Bloxorz/Liquid2核心交互仍未知。保留可行设计，不建议仅因有边界的研究缺口直接淘汰；在M01/Ready边界得到足够证据或明确收敛之前，不给无条件GO。
