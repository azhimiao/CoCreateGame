# Agent 工作约定｜AI Game Foundry

优先读取 `MASTER_HANDOFF.md`。本目录用于项目准备，不是立即编码。

## 不可违反的三条范围锁

1. 本轮仅 P01–P06：Coolmath Games、CrazyGames、Poki、Playgama、Azur Games、TapNation。
2. 候选编号仅 G01–G10；可以对某编号建议淘汰或修正，不得随意新增编号或平台。
3. 在人类批准游戏 ID 及施工档案前：**研究、审查、设计，不开发最终游戏、不上架、不签合同、不对外发邮件**。

## 目标不是做更多游戏

不是每平台制作 4 款互不相同作品，而是每平台收集 3–5 项有证据的对标和候选；去重后积累 10 个游戏家族，最后依证据淘汰、选择要制造的产品。

## 证据纪律

- 对每个事实记录 URL、观察/发布日期、指标口径；重要事实必须能重新核查。
- 严格区分：平台热榜/首页 → 用户关注信号；公司历史作品 → 发行经验；正式投稿规则 → 准入；实际交易/付款 → 资产商业化证据。
- 缺证据请写 `UNKNOWN`；不得编造游戏内部经济参数、平台分成、对标回放或开发者收益。
- 所有原创机制为 **HYPOTHESIS**，不能因为有游戏设计灵感而视作已验证。
- 不得直接复制专有源码、美术、音乐、人物、具体关卡表达。

## 施工标准与审计

参考 `MASTER_HANDOFF.md` 第 4 节。每个项目独立 GDD、机制接口、关卡/经济、UI/资产、技术、测试、发行合同风险和证伪条件。任何模块空缺均不可标为 `READY_FOR_BUILD`。

要让独立 Codex Agent 能**只阅读施工档案**就准确实现需求。编码之前先跑一次逆向审计，检查其是否存在模糊部分，列出 `BLOCKER`、`MAJOR`、`MINOR`，阻断项不能忽略。

## 并行工作与状态

- 每个 Agent 仅写自己负责的项目目录；共享 `shared-mechanics/` 采用提案/审查后合并。
- 每次工作应更新 `STATUS.md`，包括已核实、未核实、下一动作、阻塞。
- 不轻易用其他家的数据估算本平台成功率。
- 旧版 Vector Shift 技术原型不是强制设计。

## 项目工作状态

`UNRESEARCHED → EVIDENCE_COLLECTED → BENCHMARKED → SPEC_DRAFTED → INDEPENDENT_REVIEW → READY_FOR_BUILD`，以及 `REVISION_REQUIRED`、`KILLED`。

没有批准不能从 `READY_FOR_BUILD` 自动进入开发/提交。
