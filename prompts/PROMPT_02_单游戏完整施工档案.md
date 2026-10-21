# PROMPT 02｜给每个 Gxx 独立设计研究 Agent

你负责 **{GAME_ID}**，仅能编辑 `games/{GAME_ID}/`，不能修改其他游戏或跨平台范围。

阅读 `MASTER_HANDOFF.md`、官方平台档案、具体对标资料。先确认至少 2 个真实参考游戏的完整可观察玩法流程。如资料不足，先补证据，不编造实际游戏机制。

完成以下 14 个交付：

- `00_Project_Charter.md`：用户、发行渠道、可验证需求、主要风险
- `01_Market_Evidence.md`：对标链接、当前/历史证据、反证
- `02_Benchmark_Playthrough.md`：真实逐步流程（进入/教程/首局/失败/中后期/复玩），未知明确标出
- `03_Full_GDD.md`：输入/规则/循环/系统/成长/关卡/剧情（如有）/失败成功/教程
- `04_Systems_and_Data.md`：实体、状态机、事件、接口、游戏规格与异常处理
- `05_Levels_Economy.md`：关卡游戏前 20 关具体规格或经营游戏前 30 分钟数值/升级曲线
- `06_UI_Art_Audio.md`：每屏精确 UI、动效、素材清单、配色字体及技术规格
- `07_Tech_Architecture.md`：引擎、版本、模块、构建、性能、SDK 包装
- `08_OpenSource_Licenses.md`：可用 GitHub 源码、算法、资产许可证与限制
- `09_Implementation_Plan.md`：独立可执行任务、依赖、DoD 与测试命令
- `10_QA_Test_Plan.md`：单元、无头仿真、回放、真机、玩家盲测
- `11_Distribution_Business.md`：平台进入、SDK、截图/视频、协议限制、ROI 假设
- `12_Falsifiability.md`：玩家与商业反证标准、淘汰条件
- `game-spec.json`、`tasks.json`：可机读完整规则/任务；必须做 schema 校验

为原创点出具至少两个与成熟机制可分离的测试版本，避免只改美术。不得复制对标游戏特定表达。禁止以 GDD 中「之后再精修」跳过产品完成要求。

最后让另一个 Agent 在不阅读对话的情况下只凭上述施工文档解释全部操作流程、系统接口和失败/成功条件；若复述失败，则施工档案不合格。不要在本任务编写游戏源码。
