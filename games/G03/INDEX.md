# G03｜目录索引与缺口说明

2026-10-21。本目录只有候选研究：project_status=EVIDENCE_COLLECTED，status=SPEC_NOT_COMPLETE，ready_for_build=false。文件存在不等于对应施工模块已经完成。

| 文件 | 本轮内容状态 | 内容/为什么仍有空缺 |
|---|---|---|
| [00_Project_Charter.md](00_Project_Charter.md) | 实质准备内容；非施工完成 | 候选定位、原创假设、范围与成本停止线 |
| [01_Market_Evidence.md](01_Market_Evidence.md) | 实质准备内容；非施工完成 | 已核官方作品页/渠道说明及事实边界 |
| [02_Benchmark_Playthrough.md](02_Benchmark_Playthrough.md) | 诚实研究骨架；未完成 | 缺实玩与订单资源观测，无法按网页宣传反推经济。 |
| [03_Full_GDD.md](03_Full_GDD.md) | 诚实研究骨架；未完成 | 产品分支与资源规则未冻结。 |
| [04_Systems_and_Data.md](04_Systems_and_Data.md) | 诚实研究骨架；未完成 | 缺类型、事务边界和存档版本，不生成 game-spec.json。 |
| [05_Levels_Economy.md](05_Levels_Economy.md) | 诚实研究骨架；未完成 | 真实参考经济与自有平衡参数 UNKNOWN。 |
| [06_UI_Art_Audio.md](06_UI_Art_Audio.md) | 诚实研究骨架；未完成 | 资产数量、最终屏幕与规格未定。 |
| [07_Tech_Architecture.md](07_Tech_Architecture.md) | 诚实研究骨架；未完成 | 引擎、SDK及性能预算尚无测量；本轮不造实验游戏。 |
| [08_OpenSource_Licenses.md](08_OpenSource_Licenses.md) | 诚实研究骨架；未完成 | 未选任何开源包或资产，全部许可 UNKNOWN。 |
| [09_Implementation_Plan.md](09_Implementation_Plan.md) | 诚实研究骨架；未完成 | 需求前置未满足，未建立任务ID/工时承诺或 tasks.json。 |
| [10_QA_Test_Plan.md](10_QA_Test_Plan.md) | 诚实研究骨架；未完成 | 规则、数值及真机样本均不足，未执行测试。 |
| [11_Distribution_Business.md](11_Distribution_Business.md) | 诚实研究骨架；未完成 | 无正式测试资格、报价、合同或实际收入。 |
| [12_Falsifiability.md](12_Falsifiability.md) | 实质准备内容；非施工完成 | 原创主张、对照/反例、否决与停止线 |
| [research-gaps.json](research-gaps.json) | 机器可读缺口台账 | SPEC_NOT_COMPLETE；开放问题、验收证据、阻断与停止线 |
| [README.md](README.md) | 项目入口 | 参考与当前阻断摘要 |
| [STATUS.md](STATUS.md) | 目录内局部状态 | 已核实/未核实/下一动作/阻塞；根状态未写入 |
| game-spec.json（未创建） | 有意留缺 | 核心规则、类型与数值未冻结，编造schema通过不等于可施工 |
| tasks.json（未创建） | 有意留缺 | 缺完整输入和DoD，不能伪造工程任务依赖 |

- BLOCKER：两款参考缺直接试玩与库存/订单事件记录。
- BLOCKER：自有生成/配方/订单/修复经济和满盘解法未定。
- BLOCKER：原创装修/零件资产工时与许可未核。
- BLOCKER：Web/移动独家及SDK边界未明确。

这些空缺来自实际缺证据和本轮非P0的阶段范围；不能由施工Agent自行猜测填补。独立反向审计尚未执行。根研究可引用但本项目补证不依赖其他Agent；规则冲突以MASTER_HANDOFF.md与本轮人类范围限制为准。
