# G01 本目录状态

2026-10-21，规格1.0.0：**SPEC_DRAFTED / ready_for_build=false / human_build_approval=false**。主控已确认资料/数据检查通过，独立审计进行中，正式结论仍PENDING。

本局部状态不修改根STATUS.md/shared/data。已完成00—12共13份实质文档、GameSpec/Tasks与两schema、20关具体初态/胜利/合法解、研究验证脚本与报告、证据摘要整理。没有最终游戏源码、Cocos项目、上架、合同、对外邮件。

## 已核实

- 两真实参考官方说明可读：Green Train Arrow Puzzle、SolvePlay Arrow Escape: Puzzle（西语页），访问2026-10-21；没有实际试玩。
- 官网列候选Cocos Creator3.8.8；P02/P04/P01隔离硬条件已进入技术/发行/QA档案。
- 实跑20关附解20/20、149可达状态、645候选移动双算法交叉核对、9边界案例、两schema与16任务DAG通过；输入hash见validation/report.json。
- 完整网页工具回执已移到内部research/raw/；research/evidence.json与raw-index.json保留URL、读取日期精度、标题、定位、摘要及hash。

## 未核实、下一步与真实阻断

|等级|项目|动作|
|---|---|---|
|BLOCKER（开工闸门）|主控独立审计尚无最终关闭结论|主控维护根reviews/G01-audit.md；作者不代写/代签，等待具体问题后定向整改|
|BLOCKER（开工闸门）|人类未批准G01及施工档案开发|保持ready=false，不开发最终游戏|
|MAJOR（研究）|原作真实30秒/5分钟、首局/失败/后期未直接观察|已明确UNKNOWN/间接重建，补证不能回填伪观察|
|MAJOR（工程）|编辑器EULA、精确安装build/TS、实际包体性能、SDK兼容未核|PATH未发现不等于全机未装；T03后实测，不冒称构建通过|
|MAJOR（渠道）|P04旧系统兼容、P05指定SDK支持未知|实测或书面确认，不满足则停该分支|
|MAJOR（效果）|资产未生产、浏览器/真机/真人未测，消融配对题未冻结|按任务生产/预注册；离线通过不证明体验|
|MAJOR（商业）|合同、报价、真实曝光、净回款未知|不承诺收入/成功率；正式授权后才可对外沟通|

核心自有规则/关卡已明确，不用UNKNOWN留白；未知为外部观察、工具执行、效果与商业证据。全项目ZIP由主控统一生成，**排除games/G01/research/raw/**及__pycache__/*.pyc；不生成单款ZIP。
