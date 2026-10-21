# G01 信号港 / Signal Harbor：准备交付

2026-10-21，内容1.0.0、合同修订audit-r1。**REVISION_REQUIRED / RECHECK_PENDING / ready_for_build=false**。Hypatia首审REVISE；作者修订就绪，独立复核入口为[REVISIONS.md](REVISIONS.md)。无游戏源码、Cocos工程、SDK、游戏构建/性能验证或发行。

## 目录内容

- 00—12共13份独立实质文档：章程、市场、间接流程、完整GDD、系统数据、20关/经济、13屏UI与资产、技术、许可、任务、QA、发行商业、可证伪条件。
- game-spec.json / tasks.json及两schema；save-envelope.schema.json和contracts/固定样例。
- validation/report.json / solution-traces.json：20关初态与解20/20、149可达状态、645动作、9边界案例；三schema、16任务DAG、10合同变异、27存档向量、3场景11步Session表通过。
- validation/audit-mutants.json：原4审计变异与8新增负例被完整checker拒绝；几何/初态/胜利/解的冻结hash未变。
- research/evidence.json：16条自写证据卡，含官方URL、访问日2026-10-21、读取时间精度、标题、定位、摘要、hash；raw-index.json只记录内部回执hash。
- tools/prepare_data.py、prepare_evidence.py、validate.py、write_level_catalog.py及验证依赖版本；仅数据/文档研究工具。
- STATUS.md：本目录真实未验证项及阻断。

作者初轮只读官方正文；团队O01后来实际到Playgama教学棋盘并发送输入但核心结果未确认，CrazyGames转分类。7m20s是两会话总跨度。**M01仍开：合法/非法、胜败重试及完整首30秒/5分钟UNKNOWN**，部分补证不能签Ready。设计参数均为HYPOTHESIS。

## 复验

本轮Python3.11.15/jsonschema4.26.0，运行：

```powershell
python tools/validate.py
python tools/write_level_catalog.py
python tools/check_audit_mutants.py
```

prepare_data.py改动后须重生成、复验及更新05；未来npm/Cocos测试尚不存在，未报告通过。PATH未发现Creator不代表全机未安装；没有引擎构建/真机/真人/商务验证。

## 统一打包与独立审计

**全项目ZIP由主控统一生成，不另制G01 ZIP。必须排除本目录research/raw/**；其中只有内部商业网页长文本回执，不能当产品素材分发。交付仅保留自写摘要、可追溯来源与hash。也排除__pycache__/与*.pyc。

全项目ZIP由主控统一生成，不另制单款ZIP。排除research/raw/、__pycache__/、*.pyc；根团队观察按其delivery_manifest白名单纳入、runtime/排除。独立审计统一在根reviews/G01-audit.md/json；作者不改不代签，当前ready=false，人类开发批准未给。
