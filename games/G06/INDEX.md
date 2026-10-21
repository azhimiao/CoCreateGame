# G06｜目录索引与缺口说明

2026-10-21。本目录只有候选研究：project_status=EVIDENCE_COLLECTED，status=SPEC_NOT_COMPLETE，ready_for_build=false。文件存在不等于对应施工模块已经完成。

| 文件 | 本轮内容状态 | 内容/为什么仍有空缺 |
|---|---|---|
| [00_Project_Charter.md](00_Project_Charter.md) | 实质准备内容；非施工完成 | 候选定位、原创假设、范围与成本停止线 |
| [01_Market_Evidence.md](01_Market_Evidence.md) | 实质准备内容；非施工完成 | 已核官方作品页/渠道说明及事实边界 |
| [02_Benchmark_Playthrough.md](02_Benchmark_Playthrough.md) | 诚实研究骨架；未完成 | 无直接试玩；目标函数和操作语义未实测。 |
| [03_Full_GDD.md](03_Full_GDD.md) | 诚实研究骨架；未完成 | 维度、成功/失败目标和两变体未选择。 |
| [04_Systems_and_Data.md](04_Systems_and_Data.md) | 诚实研究骨架；未完成 | 状态、判定优先级、随机及回放契约缺失。 |
| [05_Levels_Economy.md](05_Levels_Economy.md) | 诚实研究骨架；未完成 | 物理模型未定，无法诚实给关卡坐标与速度阈值。 |
| [06_UI_Art_Audio.md](06_UI_Art_Audio.md) | 诚实研究骨架；未完成 | 没有维度对应资产规范和最终控件。 |
| [07_Tech_Architecture.md](07_Tech_Architecture.md) | 诚实研究骨架；未完成 | 架构选择及性能/稳定性结果UNKNOWN。 |
| [08_OpenSource_Licenses.md](08_OpenSource_Licenses.md) | 诚实研究骨架；未完成 | 未取得任何库或车型/声音资产许可。 |
| [09_Implementation_Plan.md](09_Implementation_Plan.md) | 诚实研究骨架；未完成 | 没有稳定物理定义，不能建立执行任务JSON。 |
| [10_QA_Test_Plan.md](10_QA_Test_Plan.md) | 诚实研究骨架；未完成 | 关键终局规则、设备预算与实际运行证据缺失。 |
| [11_Distribution_Business.md](11_Distribution_Business.md) | 诚实研究骨架；未完成 | 无测试资格、合同或专用版本定义。 |
| [12_Falsifiability.md](12_Falsifiability.md) | 实质准备内容；非施工完成 | 原创主张、对照/反例、否决与停止线 |
| [research-gaps.json](research-gaps.json) | 机器可读缺口台账 | SPEC_NOT_COMPLETE；开放问题、验收证据、阻断与停止线 |
| [README.md](README.md) | 项目入口 | 参考与当前阻断摘要 |
| [STATUS.md](STATUS.md) | 目录内局部状态 | 已核实/未核实/下一动作/阻塞；根状态未写入 |
| game-spec.json（未创建） | 有意留缺 | 核心规则、类型与数值未冻结，编造schema通过不等于可施工 |
| tasks.json（未创建） | 有意留缺 | 缺完整输入和DoD，不能伪造工程任务依赖 |

- BLOCKER：三个驾驶参考没有直接控制/失败/重试记录。
- BLOCKER：2D或3D、货物规则及回放误差契约未定。
- BLOCKER：成熟物理方案/性能与原创车路素材许可未核。
- BLOCKER：P03网页独家与P02发行路径未消冲突。

这些空缺来自实际缺证据和本轮非P0的阶段范围；不能由施工Agent自行猜测填补。独立反向审计尚未执行。根研究可引用但本项目补证不依赖其他Agent；规则冲突以MASTER_HANDOFF.md与本轮人类范围限制为准。
