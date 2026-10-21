# 共享研究独立复核｜REVISE

2026-10-21 18:45首轮复核；19:00补丁复核，19:22记录最终元数据（Asia/Shanghai）。只写reviews，首审原文及基线均保留。已读当前官方渠道档案、claims、discrepancies、rights/business、24卡及12份深析，独立重开新增关键官方来源和各组对标入口。[冻结输入与核对结果](F:/CoCreateGame/reviews/shared-recheck-01/results.json)；[SRA-m03补丁独立复验](F:/CoCreateGame/reviews/shared-recheck-03/results.json)。

**24卡/12析的档案交付完成；旧“对标卡缺失”BLOCKER关闭。SRA-m03已独立复核关闭，当前0项BLOCKER、1项MAJOR、0项MINOR。公开渠道修正可作有边界的设计输入，研究仍不足以支持无条件Ready。** 不因商业条件未知阻止设计，不将间接分析一律判伪，不要求十二份真人录像。

## 旧Finding修复闭环

| Finding | 当前状态 | 独立复核依据 |
|---|---|---|
| SRA-B01 卡片/深析缺失 | **CLOSED：交付部分** | 24个唯一平台—作品键，每渠道4卡；12份有内容深析，每渠道2份，P01—P06正文与引用齐。证据充分性另列SRA-M02，不继续叫卡片未交付。 |
| SRA-M01 Poki测试条款未分层 | **CLOSED** | S31/C28、S32/C29、P03、rights、D12/D13一致记录测试/长期/资产交易，零第三方统计，CSP不等于合同豁免。 |
| SRA-m01 claim缺正文定位 | **CLOSED** | 24来源/30claims的source_id/URL/locator连接通过，新项定位到PDF条款或§5.2/§5.5；hash不替代语义。 |
| SRA-m02 截图/缓存边界 | **CLOSED：文档和打包规则** | methodology/rights承认浏览缓存和研究截图，未导入产品；根打包与benchmark清单排除runtime/raw。最终ZIP须按实际成员复核，本审计未清理作者目录。 |
| SRA-m03 观察索引越界/清单过期 | **CLOSED：19:00独立复验** | 显式只读白名单仅observation-summary.md；35项payload与1项非payload关联hash/大小相符；冻结副本622项PASS，25项独立路径检查通过。作者目录未写回。 |

旧SRA-B01的交付阻断不应延续为“所有间接分析都无效”。PROMPT_01允许受限时用官方教学、公开视频或合法源码交叉验证并披露限制。本次深析有实质内容；可以验收结构交付，无法证明的流程按实际影响保留。

## 新增渠道事实

独立重开Poki Requirements所链S31，读取PDF第1—3页§1.4—1.5、3.3、4.2—4.3、5.1，支持使用平台条款、测试不保证/无报酬、预览链接限制、测试目的许可和长期合作另议；不是本项目已经注册/签约。S32允许部分非Google统计逐案审批，需资源审批及隐私政策。PDF默认限制与例外适用仍须协调，当前零第三方统计可保留；文件名日期不当实际生效版本。[要求页](https://developers.poki.com/guide/requirements-quality)、[测试PDF](https://app.poki.dev/2024.03.13_Terms_and_Conditions_Poki_for_Developers.pdf)、[外部资源政策](https://developers.poki.com/guide/external-resources-policy)。

新增C30沿用S26，当前为**24来源、30claims**。Playgama §5.2禁浏览器页滚动、允许内部内容滚动，§5.5同时要求单手完成主场景且无需额外滚动/滑动；大型场地例外不能默认套六盘谜题。claims/P04/D14同步。正文成功读取，`.md`变体一次工具访问失败不否定正文。[技术要求](https://wiki.playgama.com/playgama/game-requirements/technical-requirements)。

首审22来源结论继续保留：Basic plays与Poki players不同、Basic无变现、Full SDK/包体、付款与独家口径均不等于本团队获批/成交；Playgama两个收入流不叠算，公式不填假设新作营收；TapNation两周评估与七工作日响应不合并SLA。合同、收款资格、预算、净回款继续UNKNOWN。

## SRA-M02 [MAJOR]：关键流程和时间窗证据仍不足

**路径：** [benchmarks.json](F:/CoCreateGame/research/benchmarks/benchmarks.json) deep_analysis/summary/gaps；[methodology.md](F:/CoCreateGame/research/benchmarks/methodology.md)“流程重建和时间纪律”；[观察汇总](F:/CoCreateGame/research/observation-summary.md)及P0后补观察。

**证据/影响：** 12份均SECONDARY_RECONSTRUCTION，含100条带来源已知陈述、197个UNKNOWN字段；32个benchmark来源ID的230次引用可解析。完整首30秒/5分钟为0，视频观看0。原批仅Drive Mad有局部核心输入，Level Devil入口命令名不证明角色移动。Paint Master后补已确认14次核心输入、单关成功、耗步失败、重开再操作，审计读日志并核对关键画面，不能说G04全部只有网页说明；仍无完整连续时间窗，Bloxorz/Liquid2仍受阻。

尚影响取舍的具体未知有：Arrow Escape点/拖及失败重试、Good Sort满槽/交换/隐藏层、Screw Out满槽即败还是下一次败、Color Sort Puz现版撤销与历史实验冲突、Paint Master最后步与耗尽优先级、Bloxorz/Liquid2核心交互。未知不等于没有。自有规格固定规则可独立检验，不能称对标相同边界也已确认。G01/G02后补报告和原日志已读，抽看G01教学/按住后画面及G02末帧棋盘，与未确认核心输入的报告边界一致。三批98张截图（21/13/64）逐文件大小/SHA-256全部相符，见[独立完整性结果](F:/CoCreateGame/reviews/observation-recheck.json)；截图完整性不证明完整实玩，当前仍为0份完整连续首30秒/5分钟，不把尝试秒数当实玩。

**修法：** 合并跨批次节点覆盖表，标来源/方法/定位、真实输入响应、未知和设计影响；补能消解冲突的操作、官方教学或有时间码的合规视频。保留旧批快照和后补证据边界，不能用驻留、自拟脚本或官网宣传补首五分钟。无法取得则维持受限研究/Ready判断。

**验法：** 第三人能复核输入→反馈→成功/失败→重试/回归；完整时间窗须可操作起点和持续轨迹，间接来源须有定位/版本和未覆盖项。充分覆盖的节点可单独关闭，未覆盖的时间窗仍留缺口。本项不要求开发游戏、签合同或十二份录像。

## SRA-m03 [MINOR · CLOSED]：观察索引新增后交付校验失败、manifest过期

**路径：** [validate_delivery.py:24](F:/CoCreateGame/research/benchmarks/validate_delivery.py:24)、methodology首段、delivery_manifest.json。

**证据：** 18:45冻结副本运行checker，`../observation-summary.md`被`target.is_relative_to(ROOT)`拒绝；链接真实存在、属于合法研究汇总，但脚本只允许benchmarks内部。旧manifest的methodology哈希与现内容不符，validation.json的616项PASS早于此次修改。失败和差异在results.json，没有在作者目录运行写回脚本。

**修法：** 显式允许受控只读研究根引用，或区分交付内链接/关联证据，继续拒绝任意越界；按最终内容刷新验证与清单，保持runtime/raw排除。

**验法：** 当前最终内容validator可复现通过、链接可达、所有清单哈希相等，越界负例拒绝；最终ZIP无runtime/raw。结构PASS不能改写研究充分性结论。

**19:00关闭依据：** 当前`ASSOCIATED_READ_ONLY`只含解析后的`research/observation-summary.md`，未放开research或工作区。独立保存输入manifest后逐项核对：35项payload全部大小/hash匹配，且无runtime/raw；另1项`associated_read_only`匹配观察汇总、`included_in_this_subpackage=false`，未冒充包内payload。仅在reviews冻结副本运行原validator，得到**622 checks PASS**（以当前实际内容为准，不沿用早先620数）；25项独立路径检查全部通过，包括4项作者负例、相邻研究文档、白名单近似名、编码越界和规范化路径。实际存在的Windows runtime大小写别名规范化后仍被拒；不存在的大小写路径由完整入口的存在性检查拒绝，未据单独predicate误判漏洞。初次探针的这一假设已在最终results中纠正，保留诊断历史。原validate_delivery/validation/manifest/观察汇总的前后hash相同，未运行作者目录的写回流程。最终总ZIP尚待主控定稿，本关闭不冒称已验最终ZIP。

**19:22最终清单元数据：** 独立逐字比较validator与19:00已审快照，唯一差异为新增`manifest.validation_check_count = report['check_count']`，原只读白名单/路径控制未改。当前manifest与validation均622；35项payload和1项`relative_to: research/`只读关联的大小/hash相符。本次只核元数据，未重跑已经闭合的整批语义，SRA-m03保持CLOSED。当前validator SHA-256 `00df7afa01e362b9fdb9a0e791783af6cc38e6e27aaba9e054762461af1fc4cd`、validation `45c046a1457e6b2455a7d52a7e0beb968391693f4ad31554cc5e557e860f2449`、manifest `ba450a2e2a2f3479484ae79dcca7fa5dbbfe779fee8cbacfdf011b5e4ee013bf`；[记录及冻结副本](F:/CoCreateGame/reviews/shared-final-metadata/results.json)。SRA-M02及研究充分性结论不变。

## 对标内容与来源核查

已重开24卡对应的具名入口（P05多卡共享官方目录），官方说明可支持公开骨架，未发现将目录存在性当新作收益。Arrow Escape意大利/西语本次均转分类页，卡片已诚实列缓存/版本风险，不能由当前地址重证原细节；Screw Out官方同页确有满槽失败的两种表述。[Screw Out](https://www.crazygames.com/game/screw-out-bolts-and-nuts)、[Good Sort](https://playgama.com/game/good-sort-master)、[Suika](https://www.coolmathgames.com/0-suika-watermelon-game)。

Azur已用Color Sort Puz/Tower Craft/Stack Ball/Bottle Jump具名证据替代类别占位，D09落地。2023案例自述收入/支出不能相减作开发者利润，历史撤销实验不无条件套现版；商店安装门槛不是DAU。[Azur目录](https://azurgames.com/games/)、[历史案例](https://azurgames.com/blog/how-unconventional-setting-affects-the-success-of-a-hyper-casual-game-in-an-occupied-niche/)。

TapNation四作属历史作品，水排序官方页和商店只支持颜色/空间骨架与宝石提示，不补隐藏容量；Guess Their Answer实时/离线和人群采样来源仍未知。两个同名Piece of Cake只按标题暂计23组，未声称版本/权利等价。G10未进24卡已披露，候选研究可继续补，不为凑数新增平台/编号。[水排序](https://www.tap-nation.io/games/color-water-sort-puzzle-games/)、[Guess案例](https://tap-nation.io/blog/guess-their-answer-a-case-study-of-a-top-trivia-mobile-game/)。

共享裁决保持 **REVISE**：档案交付完成与证据足以Ready分别验收。旧问题及SRA-m03按上述关闭，仅SRA-M02保留；不替逐款独立裁决，不构成开发/投稿/签约授权。
