# G04状态｜作者r2修订待独立复核

2026-10-21；规则/spec1.0.0、合同修订r2；当前REVISION_REQUIRED，ready_for_build=false。作者已定稿可复核，未代签GO。候选仍仅P01/P02，不生成最终游戏/场景/正式资产，不投稿、签约或外联。本状态随项目包交付，不修改根STATUS。

已发生：Hypatia独立审计结论REVISE（0 BLOCKER、3 MAJOR、3 MINOR）；权威位置../../reviews/G04-audit.md/json。主控已修campaign一一对应/B0约束与TS4.1.2版本说明；本次保留，四项campaign反例仍必须拒绝。G04作者本轮没有修改独立审计报告，修复是否闭合由原审计员复核。

| 审计项 | 作者本次修订 | 当前判断权限 |
|---|---|---|
| M01 | 02逐节点纳入研究代理Paint Master真实局部输入/成功/失败/菜单重开证据，observation-index记录原帧与hash | 部分补证；连续首30秒/5分钟、另两款核心输入仍缺，不自行关闭研究MAJOR |
| M02 | 纯RuleFact与Session富化分层，来源/seq/assisted明定；SessionController唯一提交/发布；T03 Session、T07 Boot/app、T02探针写域和依赖闭合 | 作者修复候选，待Hypatia独立复核 |
| M03 | 完整Envelope/Progress/Settings/活动会话，唯一设置位置、CJ1字节/摘要、Schema与合法中文/坏档样本、恢复优先级 | 作者修复候选，待Hypatia独立复核 |
| minor1/2/3 | 唯一断点与几何；四对重复解和删门消融诚实边界；T00审计外部路径 | 作者修复候选，待Hypatia独立复核 |

实际离线验证：20正式关+2实验合法最短解、21固定规则向量、2个B0实验对照、4 Schema负例、4 campaign语义负例、16任务DAG；新增2合同Schema、2合法/12损坏或迁移存档、7严格JSON拒绝、3双槽选择模型、2个Session富化对照、10关键产物唯一owner和2归属反例、6种几何、20题删门消融。Python3.11.15/jsonschema4.26.0；Node20.11.0仅用于实际JSON/crypto字节哈希交叉核对。最终结果、时点及源hash以validation-report为准；ZIP CRC、全成员与manifest逐字节SHA核对以archive-verification为准。命令先python -B validate_spec.py，再python -B pack-preparation.py，最后收据只读核查。

未执行：G04 Cocos/TS产品、SDK、浏览器/真机、产品网络/性能、音画成品、真人盲测、平台审核/合同/收入；不是准备阶段已跑项目。研究代理的Paint Master浏览器是参考证据，不属于G04产品。Cocos3.8.7固定官方基线，4.1.0为语言页标签、4.1.2为可安装类型检查版本；组合构建未证。

历史与当前：SELF_REVIEW原文是未读Play/Paint Master后补证、未收到Hypatia报告的初版快照；其“全部间接重建/未独立审计”不能当当前事实。当前证据读02/E15，历史边界和修复读REVISIONS，不能把离散283.708秒包装为连续时间窗。缺市场/采购/付款证据单列UNKNOWN，准备ZIP不是商业化资产或游戏安装包。

下一步：立即交Hypatia以现行hash只读独立复核，结果写原reviews/G04-audit.md/json；任何未闭合BLOCKER禁止GO。由人类决定是否批准G04及具体施工档案，没有明确批准不得进入T02以后。作者同时承担G02独立复核时只读G02、仅写其审计文件，角色与本项目作者分离。
