# G01 独立审计｜REVISE（audit-r1复核）

## audit-r1当前结论｜2026-10-21 19:18 +08:00

**0项未解决BLOCKER、1项MAJOR、0项MINOR；REVISE。** M02/M03及m01/m02已独立关闭，唯一开放项为M01研究证据。当前40文件冻结快照见[AUDIT_SNAPSHOT.json](F:/CoCreateGame/reviews/G01-recheck-r1-final/AUDIT_SNAPSHOT.json)，game-spec SHA-256 `f7ae41c19422324a29c99bf5fd7bbd4d53a364d44aed9f85152701d35f89832f`，tasks SHA-256 `238506feaca4885bcaad69b578499575efb869283f1b65a2aec042d25a52410e`。

[291项独立复核结果](F:/CoCreateGame/reviews/G01-checks/r1/results.json)全部通过：[脚本](F:/CoCreateGame/reviews/recheck_g01_r1.py)独立重放20关见证、27存档样例、3组11步Session事件/保存序列和唯一模块责任；在reviews隔离副本重跑作者validate及audit mutants，两份完整报告逐字段复现。原4个审计变异与8个新增负例全部被拒；另10项合同变异被schema与语义检查双拒。20关布局/规则/解与首审一致，保留原149可达状态、645可达动作/2344全子集比较证据，不重复全图搜索。作者源文件前后hash不变。

初次r1快照恰逢作者刷新validation/report.json：仅此报告变更，其他输入未变；最终报告34个输入hash全部吻合并可精确复现，不据交付时序新增Finding。[首审原文](F:/CoCreateGame/reviews/G01-audit-first-round.md)及原JSON、旧快照保留。下列Finding的原证据/修法是发现历史，关闭依据单列，不以作者自行PASS替代独立关闭。

作者STATUS/REVISIONS中的RECHECK_PENDING等为交接时快照；当前闭合结论以本报告/JSON为准。不为改历史状态词回写作者源或重打包，不将未来开发授权、引擎/真实Storage/真机/合同未取得判为当前规则缺失。

审计者未参与 G01 写作。已冷读当前 00—12、game-spec/tasks 及两份 schema、20关正文与机器数据、作者验证器、全部结果/逐步轨迹和证据台账；初始快照18:20，首审核对快照2026-10-21 18:38（Asia/Shanghai）。任务/打包说明等后续更正已纳入，未以旧版 package.py 缺失作问题。审计只写 reviews，不重写作者设计或开发游戏。

**首审历史：0个BLOCKER、3个MAJOR、2个MINOR。当前r1：0/1/0，仍REVISE。** 原始20关全部有解，149个可达状态和作者吻合；不能将下面的校验防漏问题描述成原关卡无解。

## 只凭施工档案复述

启动 BOOT 读内容并验存档，成功到 HOME，异常去 RECOVERY/ERROR。新档“开始”进 L01；棋盘4×4，两条箭：a向右、b向上。只有a能先合法离开，随后b；首次完成给一个印章，保存后可下一关/重玩/地图，也能撤销最后一步返回棋盘，已经获得的章保留。加载、输入反馈和动画有设计目标，首30秒是否一定完成首关尚无测量。

后续依次完成L02、L03……，未完成前关不能跳关，已完成可重玩。L05首次引入信号门，L11船期，L16组合；前五分钟具体到哪关 UNKNOWN，不能把解长换算成玩家时长。非法点选只指出原因，不扣生命/时间/币。仍有箭但没有合法EXIT时弹可关闭死锁页，免费撤销或确认重来；还有合法操作但最终无解时允许继续，提示会说撤销/重来。全部20关后显示全通，只有地图/重玩/首页，没有伪造每日、无限模式或后续内容。

棋盘4—7格、2—8条箭，箭是有序连续折线或单格；尾到头最后段决定方向。EXIT使**整条形状沿方向刚性平移**至全部出界，不沿折线蛇行；全身体扫掠碰到其他未移除箭、墙或关闭门即拒绝，忽略自身初态占格。拒绝优先级为未知/已移除、船期不符、箭碰撞、墙、关闭门，同类高亮按最近步数、y/x、对象ID取一个。

合法性先使用旧门状态验证完整扫掠，再移除、XOR该箭列出的门一次、消费一个船期、判断胜利/死锁、保存逻辑、播放动画。不能靠自己离开后开门救自己。门初态XOR已移除箭的toggle，船期游标为已移除数；空船期关闭该规则。BASE没有两机制，RELAY仅门，MANIFEST仅船期，COMBINED兼有；无计时/随机运行、无隐藏出口。清空全部箭且船期耗尽才胜。每条成功路线都移除n条箭，最短步天然n，不把它当难度。

撤销免费删接受日志尾项并重算，胜利后也允许；重来确认清本局日志并保留历史完成与设置。提示从当前可通关后继按ID字典序选第一条，不自动走棋、无次数/广告门。指针同一对象按下抬起且位移≤10CSSpx才提交，多指/取消作废；动画中棋盘输入丢弃不排队。Tab按ID、Enter/Space激活，U撤销、H提示、R确认重来、Escape暂停/返回。小触区冲突出44px候选选择条，不能自动猜最近箭。

接口包括validateLevel、derive、evaluateExit、commitExit、undo、solve、save。Attempt只存levelId/log/revision，mask/gates/cursor从日志导出，期望revision不符无改变。相同mask未来规则相同，可合并搜索；历史仍须逐步合法。r1中commitExit/undo仅返回纯规则事实；SessionCoordinator唯一更新Attempt/Progress/revision/应用状态、分配sessionId:seq并发布富化事件。firstClear取提交前完成历史、stampCount取提交后集合。每次新接受的持久变更只排一次新revision保存；胜利是EXIT的一部分，不额外加一次保存，撤销再胜不重复章但保存新局面。动画中断不再提交；重复Save ACK无事件，过期命令拒绝且不保存。SavePort串行传输不可变快照，只回结果、不改进度或发布总线。T06/T07/T08责任及依赖已明确。

存档key按渠道隔离，上限64KiB，字段为version/content_version/revision/completed/active_level/accepted_exits/tutorial_seen/settings；不存权威门状态或印章数。r1规定revision为0至9007199254740991整数，拒绝bool/小数及指数词法；严格JSON拒绝任意层重复键/非有限数，所有必需字段拒绝额外键。完成集须是L01起有序连续前缀，active只可重玩或最高已解锁关，日志无重复且逐步合法；全清未登记时补章/revision+1，第二次读取不再修复，最大revision需修复则转恢复。写tmp→回读→备份旧main→替换main→验证→清tmp；恢复main/tmp/bak中合法最大revision，同rev不同内容由用户选择。任何候选为未知更高版本先保留只读，内容版本无映射不套旧日志。失败可内存继续并提示。云仅确认同渠道能力后启用，完成集并集、活动局高rev，同rev冲突提示；合并升至max+1，超界恢复。无跨站同步或账号依赖。页面隐藏先存已提交状态，取消动画，回归重绘不再提交。

## 实际独立核验

[audit_g01.py](F:/CoCreateGame/reviews/audit_g01.py) 用frozenset记录已移除ID，以箭条身体与障碍的同轴距离判扫掠，不用作者的扫掠并集或逐格平移产生期望值；随后才比对作者算法。[完整结果](F:/CoCreateGame/reviews/G01-checks/independent-results.json)、[冻结输入](F:/CoCreateGame/reviews/G01-final-snapshot/audit-manifest.json)。这是离线审计工具，不是游戏源码。

- 两份schema本身合法，当前数据通过；20条给定解合法，逐步mask、门、船期与solution-traces逐项相等，05的20段JSON投影完全一致。
- 独立得到149可达状态、645次可达动作比较，并扩展至2344次全部子集动作比较，拒绝原因及门状态无分歧；作者报告输入hash一致，reviews副本重跑PASS，9个作者语义反例已逐条检查。
- 所有死锁见证逐输入重放核实，包括L08双翻门、L13/L14同向误选、L17门与船期、L20首选a。L10还有2个losing状态，故“撤销一步不保证回到可通关态”的披露正确。无扣币、无限印章或由规则推进导致无限循环；免费撤销/重玩是设计能力，不是获利漏洞。
- 16节点DAG无环、依赖存在，所有未来施工任务祖先均含独立审计和人类批准；独立切断T04批准祖先确实被当前checker拒绝。没有因授权尚未取得而指档案缺失。Session集成责任另见M03。
- 首审主动变异发现两种错误规格仍获完整PASS（r1均已拒绝，旧证据保留）：重复campaign ID及反转commit_order；负坐标、批准祖先断裂均被拒绝。通过数量不等于所有语义已受保护。

| 关 | 附解 | 可达状态 | 成功序列数 | 死锁数 |
|---|---|---:|---:|---:|
| L01 | ab | 3 | 1 | 0 |
| L02 | bac | 6 | 3 | 0 |
| L03 | bacd | 12 | 12 | 0 |
| L04 | badce | 18 | 30 | 0 |
| L05 | ba | 3 | 1 | 0 |
| L06 | cba | 5 | 2 | 0 |
| L07 | cba | 4 | 1 | 0 |
| L08 | bac | 7 | 2 | 1 |
| L09 | cabd | 10 | 4 | 1 |
| L10 | cabde | 20 | 20 | 1 |
| L11 | abc | 4 | 1 | 0 |
| L12 | bac | 4 | 1 | 0 |
| L13 | bca | 5 | 1 | 1 |
| L14 | bcade | 7 | 1 | 1 |
| L15 | bacde | 6 | 1 | 0 |
| L16 | bac | 4 | 1 | 0 |
| L17 | bca | 5 | 1 | 1 |
| L18 | cabd | 5 | 1 | 0 |
| L19 | cabdef | 9 | 2 | 0 |
| L20 | bcadefz | 12 | 4 | 1 |

## BLOCKER

当前未发现未知胜负条件、原关无解或不能消解的核心规则矛盾。MAJOR未关闭仍不签无条件GO。

## MAJOR（含修复历史；当前仅M01开放）

### G01-M01｜对标流程覆盖不足，不能据档案齐全签Ready

**位置：** [02_Benchmark_Playthrough.md](F:/CoCreateGame/games/G01/02_Benchmark_Playthrough.md)“方法声明/时间维度”；[01_Market_Evidence.md](F:/CoCreateGame/games/G01/01_Market_Evidence.md)两参考；共享观察汇总。

**证据/影响：** 初轮两参考是官方说明的间接重建，清场骨架可追溯，作者未编造实玩。r1的O01覆盖索引已并入后补观察：21张截图大小/hash独立全验，Playgama到三箭/三心教学棋盘，但点/微拖/按住未确认箭或心变化；不能把无响应判成非法操作。CrazyGames转分类页，7分20.252秒包含广告、排障和两会话，不是连续玩法。箭形实际碰撞、轻点/拖动、失败惩罚、胜负/游戏内重试、进度回归及完整首30秒/5分钟仍缺。Arrow Escape官方正文和Controls互相矛盾，作者诚实列UNKNOWN；当前重定向不能重证所有原摘录。市场取舍依据仍不足以无条件Ready。见[观察完整性结果](F:/CoCreateGame/reviews/observation-recheck.json)，不将后补努力说成只有网页说明。

**修法：** 合并后补操作证据的节点覆盖及来源定位，保留原批次“无直接观察”历史；用可复核实际操作、官方教学/合法公开视频补关键取舍，无法确认的仍写UNKNOWN。PROMPT_01允许间接方法，不要求十二份真人录像，也不把所有SECONDARY_RECONSTRUCTION判伪。不能用驻留时长或自拟访问脚本回填完整时间窗。

**验法：** 第三人能区分每项真实输入/反馈、来源说明与未知，完整成功失败/重试/回归及定时覆盖有出处；未覆盖节点明确影响Ready的边界。缺失商业条件不自动阻止设计；缺证流程也不能直接改标签为已验证。

### G01-M02｜campaign唯一性及规则声明未绑定验解语义（CLOSED audit-r1）

**位置：** [game-spec.schema.json](F:/CoCreateGame/games/G01/game-spec.schema.json) progression.order/levels/rules；[validate.py:162](F:/CoCreateGame/games/G01/tools/validate.py:162)。

**证据/影响：** 只把最后L20记录和order末项均改为L19，完整checker仍PASS，丢失L20并重复L19；仅反转rules.commit_order也PASS。前者将影响按ID索引/关序/20章，后者使机器宣告的顺序与验解实际固定顺序矛盾。当前原20关本身正确，问题是错误规格未被拒绝。负例输入、日志在[mutation-probes](F:/CoCreateGame/reviews/G01-checks/independent-results.json)。

**修法：** 明确正式L01—L20集合/顺序/唯一性，校验规范化规则优先级和提交顺序与固定规则版本一致；可使用const/枚举或语义检查，无需改变关卡布局。更新生成源而非只改生成JSON。

**验法：** 原数据/9规则反例仍PASS，重复、缺失、错号、乱序campaign及反转commit_order必须分别拒绝；报告记录负例结果，不能只更新hash。

**19:18独立关闭依据：** contracts.py/生成源/schema const与独立语义检查共同绑定L01—L20有序唯一集合、合法性优先级和7阶段commit顺序。隔离副本重放原duplicate_campaign_id/reversed_commit_order精确delta，以及原另两负例和新增8负例，均被完整checker拒绝；正控制20关仍PASS。完整audit-mutants报告与冻结交付逐字段相等，非仅更新hash。

### G01-M03｜纯规则返回与会话/进度事件的来源及交接责任不闭合（CLOSED audit-r1）

**位置：** [04_Systems_and_Data.md:27](F:/CoCreateGame/games/G01/04_Systems_and_Data.md:27)及事件表；[07_Tech_Architecture.md:18](F:/CoCreateGame/games/G01/07_Tech_Architecture.md:18)；tasks T04/T06/T08。

**证据/影响：** commitExit只接Level/Attempt/arrowId/expectedRevision，Attempt只有levelId/log/revision，却返回events[]；所有事件要求session-local eventId，LevelCompleted还需firstClear/stampCount。相同规则输入在不同历史completed中应产生不同首通载荷，接口没有这些数据。Session模块虽明确存在，任务也有集成意图，但没有明确Session/总线/事件富化的产物及owner；规则、UI/scene、content/tutorial的写域不能自动代替交接合同。

**修法：** 作者明确纯规则事实与Session/Progress富化事件边界、序号和首通唯一发布者，为应用状态机/Session/总线组装分配任务、目录及验收。保持现有玩法即可，不要求本轮实现。

**验法：** 相同Level/Attempt、不同completed历史，冷读实现者可唯一列出规则返回和最终事件/存档；完成只加一次章，胜利撤销再完成不再首通，中断动画不重复提交。每个产物有责任任务且依赖可追踪。

**19:18独立关闭依据：** 当前04/07、session_contract和T06唯一publisher/状态写者、T07 SavePort、T08集成写域一致；8项关键产物均有唯一owner，16节点批准祖先有效。独立用原解析碰撞模型生成RuleFacts，再按提交前历史富化3局11步事件，逐项核对eventId/revision/firstClear/stampCount、Context和SaveEnvelope；胜利→ACK→中断→撤销→再胜→重复ACK及过期命令序列吻合。同局面不同历史得到相同规则事实、不同正确首通载荷；未运行产品Session或真实Storage，不冒称运行时验证。

## MINOR（audit-r1均已关闭）

### G01-m01｜组合不总是增加策略，教学目标需按实际分支验收（CLOSED audit-r1：披露/测试规格）

**位置：** [05_Levels_Economy.md](F:/CoCreateGame/games/G01/05_Levels_Economy.md) L16/L18/L19；[12_Falsifiability.md](F:/CoCreateGame/games/G01/12_Falsifiability.md)。**证据：** L16/L18全程只有一条合法路线，移除船期后反而各出现1个losing状态；L19移除船期有16个losing状态，组合后为0。L18初始只c合法，不是有两条合法同向可供误选的情形。所有含门关卡去门均增加解序列，机制确有规则效果，但组合有时替玩家排除了风险。**修法：** 将教学目标区分“辨认被挡原因”和“同向规划选择”，保留组合保护作用作为待测反证，不能以复杂度或关数宣称原创体验有效。**验法：** 按独立分支/消融表定位每项选择；12的四组盲测按预注册执行，承认样本不足或组合不增益，允许保留教学复用，不要求强行加难。

**关闭依据：** 05/生成数据把L16/L18改为辨认被挡原因；12明确L19组合保护效应及去船期16个losing反证。20布局字段逐关保持一致，原消融结果仍适用；未来四组实验允许判无增益或保留教学复用，不再将单一路线当两候选规划。关闭的是不实教学表述与检验计划，不是证明原创机制更好玩。

### G01-m02｜存档要求严格验证，尚缺可交换的完整边界样本（CLOSED audit-r1）

**位置：** [04_Systems_and_Data.md](F:/CoCreateGame/games/G01/04_Systems_and_Data.md)“存档格式与恢复算法”。**证据：** 现有示例和恢复算法足以确定主体流程，但“schema/类型通过”尚无SaveEnvelope schema或等价完整边界表，revision整数范围、tutorial_seen枚举/重复键、额外字段、active_level与解锁前缀关系的接受/拒绝示例不齐。与G04不同，本项目没有重复settings权威位置或checksum歧义，故不升同级问题。**修法：** 补字段边界与少量合法/非法存档固定样本，供独立Save/UI工程师共享。**验法：** 依据文档对新版、超界rev、重复日志、锁定活动关和已胜未记章作一致判定；真实Web Storage故障注入留未来T07，不假报已测。

**关闭依据：** 新SaveEnvelope schema、04完整边界及27固定样例一致；本审计独立解析/重放并逐个产生相同判定，覆盖重复键/额外字段、前缀与解锁、重复/非法日志、新版本/内容版本、最大rev和超界、全清未记章修复及二次读取幂等。Schema本身合法，作者完整报告可复现。真实Storage故障/配额测试仍诚实NOT_RUN，属未来T07。

## 十维审查与裁决

市场：Arrow Puzzle官方页支持家族说明、发行身份及存在性，不证明单款收益；Arrow Escape当前重开受重定向限制，保留原取证hash并补可定位证据。[Arrow Puzzle](https://playgama.com/game/arrow-puzzle)、[当前Arrow Escape地址](https://www.crazygames.com/es/game/arrow-escape-puzzle)。没有混用同名Bravestars/SolvePlay，未把Azur历史作品或总体流量当G01采购概率。

玩法/内容：完整流程可复述，20关与异常通过独立有限模型；无限撤销/提示为明示设计，无经济漏项被偷偷借参数填充。原创性：门XOR和方向船期是可分离假设，消融实际改变路线，不只是改名/皮肤；不提供全球新颖性或法律清白保证。未发现拷贝具体关卡/素材证据，玩家是否更喜欢仍未知。

工程/体验：输入取消、非法优先级、全身扫掠、后台中断、原子逻辑和撤销已固定；r1的M02/M03已独立关闭。13屏/资产/动画/44px冲突方案具体，尚无渲染、真机和误触实证；这是未来T05/T06/T09/T10工作，不能按文件存在宣告通过，也不因它们尚未开发直接KILL。

工具/权利：独立重核官网下载确有3.8.8/2025-12-16；对应引擎tag为MIT，Cocos命令行成功码36/参数32/构建34与档案一致。官方Noto许可证为OFL1.1、TypeScript主分支Apache2.0；未来精确文件锁定另核。编辑器EULA/SDK/资产的未知已分层，不将引擎MIT扩张至全包。[官方版本](https://www.cocos.com/en/creator-download)、[引擎许可](https://raw.githubusercontent.com/cocos/cocos-engine/v3.8.8/LICENSE.md)、[CLI](https://docs.cocos.com/creator/3.8/manual/en/editor/publish/publish-in-command-line.html)、[字体许可](https://raw.githubusercontent.com/notofonts/noto-cjk/main/Sans/LICENSE)、[TS许可](https://raw.githubusercontent.com/microsoft/TypeScript/main/LICENSE.txt)。

渠道：P02 Basic无SDK按全包50/20MB，内部保守总20MB；Full必须SDK，总250MB/1500文件。P04须Bridge且禁第三方统计，旧系统兼容明确未证实且可停该分支；P05不承诺Cocos直接转合格APK。独立profile不能免合同排他、SDK数据/许可义务，CSP允许也不是授权。[P02技术要求](https://docs.crazygames.com/requirements/technical/)、[P04技术要求](https://wiki.playgama.com/playgama/game-requirements/technical-requirements)。

商业/证伪：RPM/CPI/报价/净回款均UNKNOWN，失败成本进入同一预算口径，80等价人时与12000元仅双重止损假设、非获批预算。四组24人设计可测两机制及组合，退出进分母、小样本不宣称显著或D1/D7成立；实验材料和真测为未来门槛，不伪装现成商业验证。

裁决保持 **REVISE**：r1已独立关闭M02/M03及两项minor，未发现新缺口；M01的后补21图已计入，核心输入响应、关键节点及连续时间窗仍未知。保留可行设计，不建议因本轮证据缺口直接淘汰；未关闭前不得以20关PASS替代无条件GO。
