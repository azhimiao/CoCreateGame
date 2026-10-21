# G01 信号港 / Signal Harbor：准备交付

2026-10-21，规格1.0.0。**SPEC_DRAFTED / ready_for_build=false / 独立审计由主控进行中**。只交研究、施工档案、原创关卡数据和离线验证；无最终游戏源码、Cocos工程、SDK接入或发行。

## 目录内容

- 00—12共13份独立实质文档：章程、市场、间接流程、完整GDD、系统数据、20关/经济、13屏UI与资产、技术、许可、任务、QA、发行商业、可证伪条件。
- game-spec.json / tasks.json，以及各自本地Draft2020-12 schema。
- validation/report.json / solution-traces.json：20关完整初态与给定解20/20通过，149可达状态、645候选移动、9边界案例；两schema与16任务DAG通过。
- research/evidence.json：16条自写证据卡，含官方URL、访问日2026-10-21、读取时间精度、标题、定位、摘要、hash；raw-index.json只记录内部回执hash。
- tools/prepare_data.py、prepare_evidence.py、validate.py、write_level_catalog.py及验证依赖版本；仅数据/文档研究工具。
- STATUS.md：本目录真实未验证项及阻断。

真实参考为Green Train Arrow Puzzle、SolvePlay Arrow Escape: Puzzle（官方西语页）。没有实际试玩，真实30秒/5分钟、首局与后期未观察字段明确UNKNOWN；03—05自有核心规则/初态/胜利/合法解已固定，所有设计参数为HYPOTHESIS。

## 复验

本轮Python3.11.15/jsonschema4.26.0，运行：

```powershell
python tools/validate.py
python tools/write_level_catalog.py
```

prepare_data.py改动后须重生成、复验及更新05；未来npm/Cocos测试尚不存在，未报告通过。PATH未发现Creator不代表全机未安装；没有引擎构建/真机/真人/商务验证。

## 统一打包与独立审计

**全项目ZIP由主控统一生成，不另制G01 ZIP。必须排除本目录research/raw/**；其中只有内部商业网页长文本回执，不能当产品素材分发。交付仅保留自写摘要、可追溯来源与hash。也排除__pycache__/与*.pyc。

独立审计统一在根reviews/G01-audit.md，作者不写该文件、不以本地自检代替。收到具体Findings后仅在G01定向修订；当前保持ready=false，人类开发批准尚未给。
