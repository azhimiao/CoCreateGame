# G10｜目录索引与缺口说明

2026-10-21。本目录只有候选研究：project_status=EVIDENCE_COLLECTED，status=SPEC_NOT_COMPLETE，ready_for_build=false。文件存在不等于对应施工模块已经完成。

| 文件 | 本轮内容状态 | 内容/为什么仍有空缺 |
|---|---|---|
| [00_Project_Charter.md](00_Project_Charter.md) | 实质准备内容；非施工完成 | 候选定位、原创假设、范围与成本停止线 |
| [01_Market_Evidence.md](01_Market_Evidence.md) | 实质准备内容；非施工完成 | 已核官方作品页/渠道说明及事实边界 |
| [02_Benchmark_Playthrough.md](02_Benchmark_Playthrough.md) | 诚实研究骨架；未完成 | 只有官方功能说明，没有直接创作或保存体验。 |
| [03_Full_GDD.md](03_Full_GDD.md) | 诚实研究骨架；未完成 | 部位/层级/主题规则与保存/导出未冻结。 |
| [04_Systems_and_Data.md](04_Systems_and_Data.md) | 诚实研究骨架；未完成 | 无完整部件模型、约束或资产ID契约，不生成GameSpec。 |
| [05_Levels_Economy.md](05_Levels_Economy.md) | 诚实研究骨架；未完成 | 未定衣橱与内容序列，不能编造经济或组合产能。 |
| [06_UI_Art_Audio.md](06_UI_Art_Audio.md) | 诚实研究骨架；未完成 | 美术风格、部件数量、样张/工时和最终UI均缺失。 |
| [07_Tech_Architecture.md](07_Tech_Architecture.md) | 诚实研究骨架；未完成 | 引擎/资源规格/导出能力与真机性能UNKNOWN。 |
| [08_OpenSource_Licenses.md](08_OpenSource_Licenses.md) | 诚实研究骨架；未完成 | 未取得完整素材许可，也未选用开源组件。 |
| [09_Implementation_Plan.md](09_Implementation_Plan.md) | 诚实研究骨架；未完成 | 部件契约与成本未立，不能承诺任务工时或造tasks。 |
| [10_QA_Test_Plan.md](10_QA_Test_Plan.md) | 诚实研究骨架；未完成 | 没有完整部件、截图基线、规则或玩家样本。 |
| [11_Distribution_Business.md](11_Distribution_Business.md) | 诚实研究骨架；未完成 | 合同、转授权/导出许可、实际素材成本与净回款UNKNOWN。 |
| [12_Falsifiability.md](12_Falsifiability.md) | 实质准备内容；非施工完成 | 原创主张、对照/反例、否决与停止线 |
| [research-gaps.json](research-gaps.json) | 机器可读缺口台账 | SPEC_NOT_COMPLETE；开放问题、验收证据、阻断与停止线 |
| [README.md](README.md) | 项目入口 | 参考与当前阻断摘要 |
| [STATUS.md](STATUS.md) | 目录内局部状态 | 已核实/未核实/下一动作/阻塞；根状态未写入 |
| game-spec.json（未创建） | 有意留缺 | 核心规则、类型与数值未冻结，编造schema通过不等于可施工 |
| tasks.json（未创建） | 有意留缺 | 缺完整输入和DoD，不能伪造工程任务依赖 |

- BLOCKER：三参考缺首次创作/结算/保存直接记录。
- BLOCKER：单人/主题/叠层/保存规则和部件锚点契约未定。
- BLOCKER：原创衣橱成本与改编/分发/用户导出权缺失，TB World归属歧义未清。
- BLOCKER：P03独家与P04分销路径未消冲突。

这些空缺来自实际缺证据和本轮非P0的阶段范围；不能由施工Agent自行猜测填补。独立反向审计尚未执行。根研究可引用但本项目补证不依赖其他Agent；规则冲突以MASTER_HANDOFF.md与本轮人类范围限制为准。
