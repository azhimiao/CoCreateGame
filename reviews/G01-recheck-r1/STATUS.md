# G01 本目录状态

2026-10-21，内容1.0.0、合同修订audit-r1：**REVISION_REQUIRED / RECHECK_PENDING / ready_for_build=false / human_build_approval=false**。Hypatia首审REVISE；本次修订和作者复验已备妥，等待独立复核。M01仍OPEN。复核入口见REVISIONS.md；独立结论只由主控reviews/G01-audit.md/json管理。

本局部状态不修改根STATUS.md/shared/data。00—12共13份文档、GameSpec/Tasks及其schema、SaveEnvelope schema、20关初态/胜利/合法解、离线规则/存档/Session合同和报告齐。没有最终游戏源码、Cocos项目、上架、合同、对外邮件；全项目ZIP由主控生成，不另做单款包。

## 已核实

- 作者初轮通过官方正文间接重建Green Train与SolvePlay流程；该轮无浏览器交互工具仅是方法快照。后续团队实际O01到Playgama教学棋盘但核心点击结果未确认；CrazyGames转分类。21张截图SHA-256核验通过，见research/observation-coverage.json。
- 官网列候选Cocos Creator3.8.8；P02/P04/P01隔离硬条件已进入技术/发行/QA档案。
- 20关附解20/20、149状态、645候选动作、9规则反例，三schema、16任务DAG、10合同变异、27存档向量、3局11步Session合同通过；布局/解冻结hash匹配。完整checker拒绝原4个审计mutant及8个新增负例，见validation/audit-mutants.json。
- 完整网页工具回执已移到内部research/raw/；research/evidence.json与raw-index.json保留URL、读取日期精度、标题、定位、摘要及hash。

## 未核实、下一步与真实阻断

|等级|项目|动作|
|---|---|---|
|MAJOR（研究）|M01对标合法/非法输入、胜败重试、完整首30秒/5分钟仍缺|保留UNKNOWN及O01局部覆盖；由Hypatia复核是否仍阻断Ready，作者不关闭|
|BLOCKER（开工闸门）|M02/M03及两minor修订待独立复核|Hypatia按REVISIONS.md复验；作者记录自检但不代写/代签reviews|
|BLOCKER（开工闸门）|人类未批准G01及施工档案开发|保持ready=false，不开发最终游戏|
|MAJOR（工程）|编辑器EULA、精确安装build/TS、实际包体性能、SDK兼容未核|PATH未发现不等于全机未装；T03后实测，不冒称构建通过|
|MAJOR（渠道）|P04旧系统兼容、P05指定SDK支持未知|实测或书面确认，不满足则停该分支|
|MAJOR（效果）|自有游戏未构建/设备实测/真人试验，配对题未冻结|按任务和预注册执行；离线通过不证明体验|
|MAJOR（商业）|合同、报价、真实曝光、净回款未知|不承诺收入/成功率；正式授权后才可对外沟通|

核心自有规则/关卡已明确，不用UNKNOWN留白。未知是外部观察、构建/性能、效果与商业证据；未声称本地游戏性能已验证。全项目包排除games/G01/research/raw/、__pycache__/和*.pyc；根团队观察按delivery_manifest白名单纳入一次、runtime/排除。下一步仅独立复核。
