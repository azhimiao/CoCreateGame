# G07｜目录索引与缺口说明

2026-10-21。本目录只有候选研究：project_status=EVIDENCE_COLLECTED，status=SPEC_NOT_COMPLETE，ready_for_build=false。文件存在不等于对应施工模块已经完成。

| 文件 | 本轮内容状态 | 内容/为什么仍有空缺 |
|---|---|---|
| [00_Project_Charter.md](00_Project_Charter.md) | 实质准备内容；非施工完成 | 候选定位、原创假设、范围与成本停止线 |
| [01_Market_Evidence.md](01_Market_Evidence.md) | 实质准备内容；非施工完成 | 已核官方作品页/渠道说明及事实边界 |
| [02_Benchmark_Playthrough.md](02_Benchmark_Playthrough.md) | 诚实研究骨架；未完成 | 仅有网页说明，没有经济事件或后台/退出对照。 |
| [03_Full_GDD.md](03_Full_GDD.md) | 诚实研究骨架；未完成 | 服务主题、调度/缓冲变体和时间规则未选择。 |
| [04_Systems_and_Data.md](04_Systems_and_Data.md) | 诚实研究骨架；未完成 | 事件/时间/存档模型缺失，不能造GameSpec。 |
| [05_Levels_Economy.md](05_Levels_Economy.md) | 诚实研究骨架；未完成 | 参考数值和自有经济均UNKNOWN，无可守恒模拟表。 |
| [06_UI_Art_Audio.md](06_UI_Art_Audio.md) | 诚实研究骨架；未完成 | 最终屏幕、动画数量、负载反馈和许可缺失。 |
| [07_Tech_Architecture.md](07_Tech_Architecture.md) | 诚实研究骨架；未完成 | 底座、SDK、离线权限和性能没有确认。 |
| [08_OpenSource_Licenses.md](08_OpenSource_Licenses.md) | 诚实研究骨架；未完成 | 尚未选用任何开源组件或可许可资产。 |
| [09_Implementation_Plan.md](09_Implementation_Plan.md) | 诚实研究骨架；未完成 | 经济设计未闭合，不生成tasks.json或虚假工期。 |
| [10_QA_Test_Plan.md](10_QA_Test_Plan.md) | 诚实研究骨架；未完成 | 无规则模型或测试记录，无法声称经济稳定。 |
| [11_Distribution_Business.md](11_Distribution_Business.md) | 诚实研究骨架；未完成 | 未取得合同、测试预算、真实收益和工具保留条款。 |
| [12_Falsifiability.md](12_Falsifiability.md) | 实质准备内容；非施工完成 | 原创主张、对照/反例、否决与停止线 |
| [research-gaps.json](research-gaps.json) | 机器可读缺口台账 | SPEC_NOT_COMPLETE；开放问题、验收证据、阻断与停止线 |
| [README.md](README.md) | 项目入口 | 参考与当前阻断摘要 |
| [STATUS.md](STATUS.md) | 目录内局部状态 | 已核实/未核实/下一动作/阻塞；根状态未写入 |
| game-spec.json（未创建） | 有意留缺 | 核心规则、类型与数值未冻结，编造schema通过不等于可施工 |
| tasks.json（未创建） | 有意留缺 | 缺完整输入和DoD，不能伪造工程任务依赖 |

- BLOCKER：三参考缺首次自动化与回归直接观察。
- BLOCKER：资源/工人/队列/升级/离线规则与前30分钟经济未定。
- BLOCKER：设备工人动画成本、模拟方案及素材许可未核。
- BLOCKER：P03/P04 Web互斥路径及P06移动权利未审。

这些空缺来自实际缺证据和本轮非P0的阶段范围；不能由施工Agent自行猜测填补。独立反向审计尚未执行。根研究可引用但本项目补证不依赖其他Agent；规则冲突以MASTER_HANDOFF.md与本轮人类范围限制为准。
