# G09｜目录索引与缺口说明

2026-10-21。本目录只有候选研究：project_status=EVIDENCE_COLLECTED，status=SPEC_NOT_COMPLETE，ready_for_build=false。文件存在不等于对应施工模块已经完成。

| 文件 | 本轮内容状态 | 内容/为什么仍有空缺 |
|---|---|---|
| [00_Project_Charter.md](00_Project_Charter.md) | 实质准备内容；非施工完成 | 候选定位、原创假设、范围与成本停止线 |
| [01_Market_Evidence.md](01_Market_Evidence.md) | 实质准备内容；非施工完成 | 已核官方作品页/渠道说明及事实边界 |
| [02_Benchmark_Playthrough.md](02_Benchmark_Playthrough.md) | 诚实研究骨架；未完成 | 无直接运行记录，接触与终局仅有页面文字。 |
| [03_Full_GDD.md](03_Full_GDD.md) | 诚实研究骨架；未完成 | 合成、队列、隔板与越界规则未定。 |
| [04_Systems_and_Data.md](04_Systems_and_Data.md) | 诚实研究骨架；未完成 | 接触事务、事件顺序、物体层级和存档契约缺失。 |
| [05_Levels_Economy.md](05_Levels_Economy.md) | 诚实研究骨架；未完成 | 没有实测或自拟冻结数值，不能填伪装经济表。 |
| [06_UI_Art_Audio.md](06_UI_Art_Audio.md) | 诚实研究骨架；未完成 | 最终UI、等级轮廓与动效许可缺失。 |
| [07_Tech_Architecture.md](07_Tech_Architecture.md) | 诚实研究骨架；未完成 | 物理库、性能预算及真机结果UNKNOWN。 |
| [08_OpenSource_Licenses.md](08_OpenSource_Licenses.md) | 诚实研究骨架；未完成 | 未选用合法库和原创素材，权利链UNKNOWN。 |
| [09_Implementation_Plan.md](09_Implementation_Plan.md) | 诚实研究骨架；未完成 | 核心事件不完整，不能生成工程tasks。 |
| [10_QA_Test_Plan.md](10_QA_Test_Plan.md) | 诚实研究骨架；未完成 | 无规则阈值、运行或玩家证据，QA未执行。 |
| [11_Distribution_Business.md](11_Distribution_Business.md) | 诚实研究骨架；未完成 | 合同相容性、SDK需求与真实回款UNKNOWN。 |
| [12_Falsifiability.md](12_Falsifiability.md) | 实质准备内容；非施工完成 | 原创主张、对照/反例、否决与停止线 |
| [research-gaps.json](research-gaps.json) | 机器可读缺口台账 | SPEC_NOT_COMPLETE；开放问题、验收证据、阻断与停止线 |
| [README.md](README.md) | 项目入口 | 参考与当前阻断摘要 |
| [STATUS.md](STATUS.md) | 目录内局部状态 | 已核实/未核实/下一动作/阻塞；根状态未写入 |
| game-spec.json（未创建） | 有意留缺 | 核心规则、类型与数值未冻结，编造schema通过不等于可施工 |
| tasks.json（未创建） | 有意留缺 | 缺完整输入和DoD，不能伪造工程任务依赖 |

- BLOCKER：两款物理合成参考无首投/连锁/越界直接记录。
- BLOCKER：接触配对、合成原子提交、队列及终局规则未定。
- BLOCKER：密堆叠性能/回放范围与胶囊素材许可未核。
- BLOCKER：P01/P04构建差异与合同相容性未确认。

这些空缺来自实际缺证据和本轮非P0的阶段范围；不能由施工Agent自行猜测填补。独立反向审计尚未执行。根研究可引用但本项目补证不依赖其他Agent；规则冲突以MASTER_HANDOFF.md与本轮人类范围限制为准。
