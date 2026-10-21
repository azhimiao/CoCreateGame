# 共享研究独立反方审计

> **当前结论以19:00补丁复核、19:22元数据更新的[共享研究复核](F:/CoCreateGame/reviews/shared-research-recheck.md)为准。** 当前24来源/30claims、24卡/12析；SRA-B01交付缺失、SRA-M01、SRA-m01/m02/m03已独立关闭。当前0 BLOCKER/1 MAJOR/0 MINOR，仅SRA-M02关键流程/时间窗证据不足，仍REVISE。最后622检查数与清单hash已记录，未重复语义。三款审计/复核及[decisions汇总](F:/CoCreateGame/reviews/decisions.json)均已完成。下文仅为首轮历史，不能当当前欠交付、补丁未闭合或三款未审状态。

**首轮结论：REVISE，修复待复核。** 当前公开渠道事实可以作为继续规格设计的带边界输入；首轮共享研究包尚不能宣称对标研究已经完成，也不能据此给 G01/G02/G04 无条件 GO。主要阻断来自对标卡及可核查深度分析未交付，不来自尚未取得报价、分成协议或买量预算。

审计员为独立反方，非作者。已阅读 `MASTER_HANDOFF.md`、`AGENTS.md` 和 `prompts/PROMPT_03_对抗审计与淘汰.md`。范围仅 P01–P06 的已出现共享研究、claims、discrepancies、rights/business，以及它们引用的既存浏览器证据；没有进入三款项目完整审计，没有替作者设计或实现游戏。

**版本边界：2026-10-21 17:56:41+08:00 的共享研究快照。** 作者并行写作中，本审计不是对其最终交付的推定。原文只读；全部审计写入 `reviews/`。基线副本、SHA256及结构/算术检查见 [manifest-and-checks.json](F:/CoCreateGame/reviews/shared-research-baseline/manifest-and-checks.json)，逐来源独立核查见 [source-checks](F:/CoCreateGame/reviews/shared-research-source-checks.md)。后续新交付只能通过复核关闭问题，不能自动继承本报告判断。

## 口径更正与主控修复通知

2026-10-21 主控澄清后，审计员补读 [PROMPT_01 第二步](F:/CoCreateGame/prompts/PROMPT_01_启动市场与施工准备.md)，确认其中明确允许在操作能力受限时说明限制，用官方教学、公开视频或合法开放源码交叉验证，标明不是直接观察。上一版 B01 将验收过度限定为实际操作记录，现更正如下：**每平台至少两项深度分析，不等于必须有十二份真人录像。** 有来源且覆盖充分的间接分析可支持相应研究项；不能证实的完整首五分钟或关键机制继续列缺口，按其对规格与决策的实际影响判断 READY，不能仅因“间接”二字认定伪造或阻断。

主控报告已补 S31/S32（现 24 源、29 论点）、source_locator、Poki 三阶段权利边界、默认零第三方统计及 CSP 与合同许可的区分，并修正截图/缓存表述、让打包脚本排除 runtime。上述属于**主控报告已修复，独立复核待进行**，未据此自动关闭 SRA-M01、SRA-m01、SRA-m02。按主控安排，等 benchmarks 交付后统一复核共享问题；本次未重新检查研究作者目录，也未启动三款项目审计。首轮快照与来源核查记录保持原版本。

## Findings

### SRA-B01 [BLOCKER] 共享对标卡及可核查的深度分析未交付

**路径/段落：** [P01.md:25](F:/CoCreateGame/research/platforms/P01.md:25)、[P02.md:29](F:/CoCreateGame/research/platforms/P02.md:29)、[P03.md:29](F:/CoCreateGame/research/platforms/P03.md:29)、[P04.md:31](F:/CoCreateGame/research/platforms/P04.md:31)、[P05.md:25](F:/CoCreateGame/research/platforms/P05.md:25)、[P06.md:26](F:/CoCreateGame/research/platforms/P06.md:26) 的“作品证据卡与间接流程分析”；[discrepancies.md:15](F:/CoCreateGame/discrepancies.md:15) D09；[methodology.md:27](F:/CoCreateGame/research/methodology.md:27)“深度分析边界”。

**证据：** 六份档案分别指向 `research/benchmarks/P01.md`—`P06.md`，快照时 6/6 不存在。D09 称已由 P05 真实具名卡替代，但其目标文件也未交付，故该更正的落地证据当前不可复核。现存 `browser-session.json` 有 23 次操作记录，只涉及 Level Devil 18 次、Drive Mad 4 次、Paint Master 1 次；操作次数不是有效游玩时长。

视觉抽查中，`p03-level-devil-stage-start.png` 和 `p03-level-devil-enter-pits.png` 显示地图/press space；`p03-level-devil-after-move.png`、`p03-level-devil-pits-right.png` 显示更新弹窗；`p01-paint-master-loaded.png` 的游戏区域未见可玩内容。`p03-drive-mad-forward-2s.png` 显示车辆与赛道，可支持有限局部观察。没有据这些证据确认各平台至少两个完整深度流程，更没有 G01/G02/G04 所需对标操作链的共享交付。文件名里的 start/right 或存在 canvas 都不证明输入已经生效。

**影响：** 首轮快照尚未满足总纲 §9 T1、§10 及 PROMPT_01 第二步的具名对标与深度分析交付要求。该问题阻断“共享对标完成”和依赖这部分证据的最终准备 GO；**允许作者继续写 HYPOTHESIS 规格**。这不是认定作者伪造实玩：`methodology.md` 的间接分析/UNKNOWN 标签原则本身诚实，根 STATUS 也没有宣布全部试玩完成。间接分析自身不构成 BLOCKER；本项依据是当时引用的卡片缺失、现有局部证据不足，后续须按交付内容重新评估。

**修法：** 由研究作者交付每渠道 3–5 张具名、有来源/日期/口径的卡，区别展示榜单与历史目录；每渠道至少 2 个深度分析按总纲及 PROMPT_01 补证。对 P0 尤须给出各家族至少 2 个可靠对标的输入→状态变化→反馈→成功/失败→复玩→退出/回归分析。优先亲自操作；受限时说明限制，接受官方教学/公开视频/合法开放源码的交叉验证，逐项标明来源类型和覆盖范围。间接分析若证据充分可支持对应规则与流程，但不能冒充审计员或作者本人的实玩，也不能凭教学概述编造真实五分钟节奏。未覆盖的后期/广告/存档等继续 UNKNOWN。D09 在目标卡出现前应写待交付。不得为补流程直接复制商业关卡或资产。

**验法：** 审计员逐卡打开来源，按直接操作、官方教学、公开视频、合法开放源码分别核对其能证明的事实。对有连续操作画面的记录，核对相对可玩起点的 t=0、30秒、300秒及输入/反馈/结果；对间接分析，核对教学段落、视频时间码或源码版本，检查交叉验证及未覆盖项，不要求每项另有真人录像。加载等待不能算可玩时间，网页说明不能标为本人实际操作。核对清单数量与引用目标，确认直接观察、官方介绍、间接重建与自有假设互不混写。若间接证据足以支撑流程与机制，可通过相应研究项；无法确认的完整首五分钟和关键机制继续明确影响 READY。若只先补 P0 证据，须明确其余平台研究仍未完结。

### SRA-M01 [MAJOR] Poki 测试使用条款与正式发行协议尚未分层入账

**路径/段落：** [P03.md:23](F:/CoCreateGame/research/platforms/P03.md:23)“流量”、[P03.md:25](F:/CoCreateGame/research/platforms/P03.md:25)“结算”、[P03.md:33](F:/CoCreateGame/research/platforms/P03.md:33)“仍需证据”；[contracts-and-rights.md:9](F:/CoCreateGame/research/contracts-and-rights.md:9) A/B 路线；`claims.json` C09/C11/C14 及 `official-sources.json` 的来源集合。

**证据：** 当前档案正确说明正式合作的独家风险及未知条款，但没有收录从当前 [Requirements](https://developers.poki.com/guide/requirements-quality) 直接可取得的 [测试使用条款](https://app.poki.dev/2024.03.13_Terms_and_Conditions_Poki_for_Developers.pdf)。其 §1.4–1.5、§4.2–4.3、§5.1 区分：使用测试平台即可涉及条款；测试不保证发生、没有测试报酬；上传涉及测试目的 Web 许可；长期合作另议。§3.3 还限制竞争平台使用其预览链接及第三方 trackers。另有当前 [外部资源政策](https://developers.poki.com/guide/external-resources-policy) 允许部分统计逐案获批，形成需要记录的政策/条款适用边界。

**影响：** 如果只按未来正式排他协议划分 A/B 路线，容易遗漏测试阶段已存在的许可、预览链接和统计限制。此处不是说现有跨平台设计违法，也不是要求现在签合同；它是可取得的公开研究输入缺口。所有报价继续 UNKNOWN 合理，但“实际协议未知”不能代替记录已经读得到的测试条款。

**修法：** 增加测试平台使用条款来源及版本状态，将注册/测试、正式发行、买断分成三个阶段分开列；把测试无报酬、非保证测试、预览链接不可作为竞品分发链接、第三方统计默认关闭写入 P03 边界。记录旧 PDF 与当前统计例外政策的适用问题为未确认；不得假定 CSP 技术放行就等于条款豁免，也不得把该 PDF 称为本项目已签商业协议。

**验法：** 不登录、不注册即可从 Requirements 的实际链接重新取得 PDF，按页码/条款复查版本；三阶段分别标出权利触发点、可用链接、统计开关、付费含义。商业协议/特殊统计批准继续保持 UNKNOWN；纯本地设计采用零外部统计时不受此项阻止。投稿前再核实际适用版本。

### SRA-m01 [MINOR] 高置信 claim 缺少正文定位，hash 无法保存语义证据

**路径/段落：** `research/claims.json` C01–C27、`research/official-sources.json` 的 `WEB_CONTENT_READ`、[methodology.md:7](F:/CoCreateGame/research/methodology.md:7)“可复核链”、`research/source-access-log.json`。

**证据：** 27 条 claims 与 22 个来源的 ID/URL 连接检查通过，独立打开相应官方正文后未发现关键数字相反。但作者日志保存的是 HTTP 状态、标题、字节数及 hash；claims 没有正文节标题/段落定位或短引文。作者已正确承认 HTTP 200 不证明语义，故不把此项升级为虚假核实。动态页面更新后，仅旧 hash 无法恢复支撑过往结论的句子。

**修法：** 为重要数字、排他边界、统计禁用和条款更正补节标题、短引文或有权限保留的摘录、读取时间及变更记录。来源日期不明继续 UNKNOWN；不要把 Last-Modified 自动当政策生效日。本审计的 source-checks 可供作者参考，不能当作作者本人实玩或合同批准。

**验法：** 另一人从 claim_id 能在来源中定位对应语句，区别访问、正文读取和实际操作；变更时能比较旧依据与新依据。无需为了此项保存商业游戏源码或整套浏览器缓存。

### SRA-m02 [MINOR] “本地仅元数据/没有下载资产”的范围表述与实际浏览器证据不一致

**路径/段落：** [methodology.md:9](F:/CoCreateGame/research/methodology.md:9)、[contracts-and-rights.md:25](F:/CoCreateGame/research/contracts-and-rights.md:25)；`research/benchmarks/evidence/screenshots/` 与 `research/benchmarks/evidence/runtime/profile/Default/Code Cache/`。

**证据：** 实际保存了商业游戏画面的研究截图及浏览器运行缓存；并非只有元数据/自写摘要。正常浏览器加载缓存不等于取用专有源码开发，也未发现本轮将其导入游戏资产包的证据，因此不作侵权结论。

**修法：** 准确限定为“未将对标专有代码/美术/音频/关卡导入自有产品；截图仅作研究证据”；把浏览器临时运行目录与可交付研究资料分开列入交付清单。不要把整个 profile 缓存当作合法可复用的素材库或施工依赖。

**验法：** 检查研究交付清单保留需要的自写记录/证据引用，排除临时 profile；随后项目许可审查核对实际资产清单、来源及哈希。无需删除作者运行中的文件，本审计未进行清理。

## 可以保留的研究结论及工程边界

| 对象 | 本次独立判断 | 后续规格必须保持的边界 |
|---|---|---|
| P01 | 非独家许可采购方式及 clean 版要求有官方支持 | 名称输入、外链、广告、开发者回传禁用；采购方式不代表本团队成交。 |
| P02 | Basic/Full、7天/500 plays/21天、包体及付款门槛有支持 | Basic 不能依赖看广告才能继续；Full SDK 与 Basic 分阶段；play 数不替代 unique players。 |
| P03 | 500玩家测试、C2P阶段、示意网页独家及AI政策有支持 | 多设备/16:9、存储失败仍可玩、事件成对及广告期间隔离；补 SRA-M01。 |
| P04 | Bridge 必需、不代投两家、两类分成及提现门槛有支持 | 禁外部 GA4 等；若采集自有事件，需明确用 Bridge 内置 analytics 或禁用，不能把本地 QA 日志直接外发。Bridge 版本与能力在项目中锁定。 |
| P05 | 表单和有条件测试流程有支持 | 公开集成提供商名称不是已锁定 SDK；当前版本、签名、隐私、样本、预算仍需确认。 |
| P06 | 概念可投、必填数据字段、两周/7工作日分别表述有支持 | 未测值不能用 0% 或行业数冒充；N/A 是否被表单接受仍未知，买断是可能选项。 |

完整来源链接及定位在 [source-checks](F:/CoCreateGame/reviews/shared-research-source-checks.md)。这是公开政策的支持状态，不是发行成功率；六家“本团队进入资格”尚未实证的标注可保留。

`discrepancies.md` D01–D08/D10 的主要修正能在官方正文找到依据；D09 的概念纠正方向合理，但目标证据卡尚未交付，已计入 B01。TapNation 两周评估与七个工作日回复不能自动合并成保证 SLA，也不能仅凭差别认定两者必然互斥；目前分别记录是合理做法。

`business-model.md` 的组合成本包含失败、研究、维护等成本，区分应计/预估/开票/实收，没有把未知成功率补成行业均值。Playgama 累进公式通过两处分界附近的独立算术检查；该函数只计算公开口径的假设份额，Net Revenue 定义、实际 N、税费与到账仍未知，不是实测 RPM 或净回款。未发现应凭此 Kill 全部候选的证据。

`contracts-and-rights.md` 将技术分包与合同相容性分开、保留通用工具/运行时边界、要求源码许可与素材许可分审，方向正确。当前没有实际依赖锁定或合同全文，不给“权利已清理”“SDK已兼容”的通过标签；这些未知本身不阻止编写一个有明确范围的纯本地规格。

## 本轮验证与限制

- 27 条 claim 全部对应到 22 个独立打开的官方来源，ID/URL 链无断点；未将作者 HTTP 日志当独立实证。
- 检查 Playgama 公开公式的 6 个边界/代表值，数学表达一致；没填入任何假设成功率或实际营收。
- 视觉抽查 6 张既存截图；这是证据审阅，不是审计员完成的真实对标试玩。其余操作是否有效、完整五分钟、存档返回等均未由本轮证明。
- 快照时 `tools/validate_preparation.py` 已存在，**本轮未运行也未审定其结果**。没有运行可能写回作者材料的重核/验证脚本。
- 未审 G01/G02/G04 的 00–12、schema、规则、任务 DAG、20关或 QA 结果；因此三款状态为 **NOT_REVIEWED**，不是 GO/REVISE/KILL 的项目裁决。

## 主控收到三款完整档案后才启动的下一轮

届时逐款只依施工档案先复述：入口到首 30 秒、前五分钟输入/状态/反馈、所有核心规则与 API、成功/失败/重试、存档/回归与异常；找不到定义就列未知，不能用对标或代码替作者补规则。之后读完 00–12、game-spec/tasks/schema、关卡数据及 QA 实际结果，再作完整独立裁决。

至少独立检验 20 条关卡的可解析性/合法性、解序列重放、机制约束与可达性；核对验解器是否偷换规则、只验作者提供答案或漏掉失败状态。任务 DAG 要有全部前置节点、无环、明确 I/O/DoD/文件归属及可并行边界。原创机制须给可对比的行为差异、测试向量与证伪标准，不能以名字和美术区别算原创。

同时核 SDK 初始化/失败/广告回调/存储故障/统计白名单，实际依赖和资产许可、排他路线及通用库保留；区分数据验证 PASS、真实实玩、间接分析、真人偏好、平台批准和商业回款。对标首五分钟或关键机制缺乏充分证据时必须诚实列缺口并影响最终 GO；间接分析按 PROMPT_01 验其证据充分性，不作一律否决。未知核心规则或任何 BLOCKER 未关闭均不能 GO。

**当前处置：共享研究 REVISE；不建议仅因未报价而 KILL；继续允许研究与规格设计。完成本报告后停止，不轮询作者目录，等待主控明确通知三款施工档案完成。**
