# CoCreateGame｜批量游戏研发项目

CoCreateGame 是批量筛选、研究、设计、审核并逐款研发游戏的总项目。G01—G10 各有独立的游戏文件夹；另行获准的游戏也使用自己的具名目录，保存源码、关卡、美术、测试和渠道材料。跨游戏的平台研究、共享机制提案和总体验收集中放在公共目录。

AI Game Foundry 的 G01—G10 仍按各自的研究与审核状态推进。本仓库另含一款用户明确要求施工的独立游戏 Vector Shift，完整工程位于 [`games/VectorShift/`](games/VectorShift/README.md)；这项授权不改变 G01—G10 的审计结论。状态见 [STATUS.md](STATUS.md)，准备交付总览见 [DELIVERY_REPORT.md](DELIVERY_REPORT.md)，离线总览见 [index.html](index.html)。

## 仓库结构

| 路径 | 内容 |
| --- | --- |
| [`games/`](games/README.md) | G01—G10 准备档案，以及独立游戏工程 `VectorShift/`（已实现五张可玩密盘重做版，含同宽对照与操作实录） |
| `research/` | 六家渠道资料、候选研究、对标证据和跨游戏分析 |
| `reviews/` | 独立审核、复核决定和审计索引 |
| `shared-mechanics/` | 可复用机制提案；须经过审核后才能成为共享规范 |
| `data/` | 平台、游戏家族和当前准备状态的结构化登记 |
| `prompts/` | 研究、施工档案和审计阶段的任务说明 |
| `tools/`、`validation/` | 总项目检查、打包工具及验证记录 |
| `docs/` | 历史项目研究记录 |

每个游戏目录以自己的 `README.md` 为入口。完整项目背景和范围规则见 [MASTER_HANDOFF.md](MASTER_HANDOFF.md) 与 [AGENTS.md](AGENTS.md)。

## 项目轨道

- G01「信号港」、G02「签章收纳台」、G04「折光机关」各有完整施工档案和20关离线验解记录，但独立裁决均为 REVISE：每款仍有一项对标体验证据待补。
- G03、G05—G10 是候选研究，不是已完成的游戏规格。
- G01—G10 的开发边界继续按各自审批与审计要求执行。
- Vector Shift 是另行明确授权的实际游戏工程，不纳入 G01—G10 编号，不改变它们的研究状态；代码、渠道构建、试玩包及验证记录均保存在自己的文件夹。

## 检查与交付

从仓库根目录运行 `python tools/validate_preparation.py` 可检查准备资料。各优先项目的专属复验命令见其目录 README。运行 `python tools/build_delivery.py` 可重新生成离线总览和完整 ZIP。

完整 ZIP 约 109 MiB，因其与仓库源文件重复且接近 GitHub 的单文件限制，生成包保留在本机 `deliverables/`，不写入 Git 历史；构成 ZIP 的项目文件和重建脚本均在仓库中。

研究资料、独立审查、数据登记和验证日志按上表的公共目录集中维护，避免在十款游戏之间复制同一份平台证据。详细要求映射见 [REQUIREMENTS_CHECKLIST.md](REQUIREMENTS_CHECKLIST.md)，历史交接摘要见 `docs/`；原始演示保留为 [original-brief.html](original-brief.html)。

## 本轮新增交付入口

- `research/platforms/`：六家官方准入、技术、联系入口、结算和权利档案。
- `research/official-sources.json`、`claims.json`、`source-access-log.json`：来源、论点、正文定位、访问时间/响应hash。
- `research/benchmarks/`：每渠道作品证据卡、深度分析、浏览器尝试记录；观察与间接重建明确分开。
- `games/G01/`、`G02/`、`G04/`：00—12完整施工文档、20关机器规格、任务DAG、规格/任务Schema，以及修订中补充的存档/事件合同和离线验解器。
- 其余 `games/Gxx/`：本家族候选资料、实质研究问题及未完成规格结构，不能视为完成GDD。
- `research/adaptation-matrix.md`、`contracts-and-rights.md`、`business-model.md`、`discrepancies.md`：渠道/权利/成本及更正。
- `reviews/`：非作者独立审计、复述及复核；`validation/`：本轮结构/数据检查日志。
- `deliverables/`：完整交付ZIP及逐文件SHA256清单。

离线复查：`python tools/validate_preparation.py`。仅重核公开页面：`python tools/recheck_sources.py`。在最终审计和状态更新后重新打包：`python tools/build_delivery.py`。这些是研究和规格检查工具，不是游戏源码/引擎构建。

本轮终审：三款均为REVISE，各0个BLOCKER、1项对标研究MAJOR；已识别的可修规格问题均经非作者复核关闭。当前裁决看 `reviews/decisions.json` 和 `reviews/final-audit-integration.md`。项目包内送审状态是冻结时的历史快照，不为改词重新改变已审文件哈希。

`data/projects.json`、`platforms.json` 的原始范围和候选定义保留；本次逐项决定与状态另见 `data/preparation-status.json`。不得从原输入中的UNRESEARCHED误读当前交付状态。重要事实仍须在正式投稿/签约日重核。

---

以下为原包使用说明，保留其阶段边界。

**本包日期：2026-10-21**。这个资料包用于让 Codex 继续完成市场对标、十个游戏家族的独立 GDD/施工档案和独立审计。**目前不批准开发或实际投稿。**

## 文件说明

- **`MASTER_HANDOFF.md`**：全会话结论、纠偏、六个平台、十个游戏、工程技术、商业模型、证据和可证伪假设，**权威项目总纲**。
- **`index.html`**：与总纲内容一致的可离线阅读演示网页，便于向团队说明。
- **`AGENTS.md`**：Codex 项目工作规则和禁止事项。
- **`STATUS.md`**：已完成与尚未完成的明确边界。
- **`data/platforms.json`**：六个渠道的唯一白名单。
- **`data/projects.json`**：十个游戏家族编号与批次。
- **`data/sources.csv`**：2026-10-21 核实过的主要官方资料入口。
- **`prompts/PROMPT_01_启动市场与施工准备.md`**：首先交给 Codex 的任务。
- **`prompts/PROMPT_02_单游戏完整施工档案.md`**：每款游戏分配单独 Codex 会话。
- **`prompts/PROMPT_03_对抗审计与淘汰.md`**：独立审计。
- **`prompts/PROMPT_04_工程施工_需单独授权.md`**：**留作之后正式开工，本轮不得执行**。
- **`games/G01...G10/README.md`**：项目占位登记，不是 GDD。

## 怎么开始

解压后把整个文件夹交给 Codex，在该文件夹启动一个会话，复制并执行：

> 请先阅读 `README.md`、`MASTER_HANDOFF.md`、`AGENTS.md` 和数据目录。严格遵守本轮六渠道、G01–G10 十项目的范围锁。执行 `prompts/PROMPT_01_启动市场与施工准备.md`，先完成研究和 P0 项目可施工档案。禁止未经我的指示直接做游戏、投稿、签协议或扩平台。每次更新 STATUS.md。

完成 P0 研究后，分别为 G01、G02、G04 启动独立的项目会话执行 PROMPT_02，再让独立 Agent 执行 PROMPT_03。**先汇报审查结果供人决策**，不要自动进 PROMPT_04。

## 真实性与版本说明

本包是对既有会话的**纠偏后的方案总结**，不是对所有历史研究事实的重新独立取证。重点官方准入页面已在 2026-10-21 核对；动态热榜仅为当日快照，没证据的收入、通过率、合同条款不作确定断言。

原始准备输入不包含 Vector Shift 的完整源码；随后按用户直接要求导入并开发的可玩基线位于 `games/VectorShift/`。当前五张可玩密盘重做版已实现，原52关独立保留；实际画面、像素测量和连续操作见[重做验证记录](games/VectorShift/docs/10_密盘重做与验证.md)。整体竞品评审仍待试玩。它尚未商业发布，也未获平台批准，当前证据和待办见该目录。
