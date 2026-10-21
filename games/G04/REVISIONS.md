# 独立审计后的规格校正

2026-10-21。主控修复，审计员随后独立复核；本记录不代替审计通过。

1. 正式关卡记录必须按顺序一一对应campaign_order的G04-L01—L20，且全部B0、无实验信标。原验解器只检查20条及跨全部记录ID唯一，错误ID或把X2放正式关可能误报PASS。已同时收紧schema及campaign_semantic，并添加越界ID/重复ID/倒序/实验混入四项拒绝检查。
2. 官方Cocos语言页的4.1.0是语言支持标签，npm未发布同号稳定包。保留该文档标签，另将可安装类型检查工具明确固定为4.1.2，写入机器规格与schema。只查版本存在，未安装、未声明与Cocos组合已构建。

原20关与2个实验的规则、布局和解未改变，重新验解PASS。每次调整后更新validation-report、DELIVERY_MANIFEST和项目ZIP；当前机器规格hash由validation-report记录。真实对标、玩家/真机、商务和独立审计闸仍不能由此自动关闭。

## r2作者修订｜2026-10-21｜待原独立审查者Hypatia复核

此节为作者修复记录，不改独立审计也不宣称关闭。规则/地图/20+2解未改，主控campaign与TS4.1.2修正保留；spec新增合同r2索引，状态改REVISION_REQUIRED。元数据改变使game-spec原始字节contentHash改变，已重建合法存档夹具并走规定内容更新分支；实际新hash见validation-report.input_sha256，包hash见外部archive-verification，避免自引用摘要。

- M02：04和EVENT_CONTRACT拆分纯RuleFact、Session富化payload与Controller编号/提交/唯一广播。明确assisted/attempt/seq/source来源、旧token/锁/终态幂等、原子推进nextSeq；T03独占session/EventBus，T07独占Boot.scene/meta和app集成，T02仅探针；required_artifacts逐项验唯一owner。固定相同L01末步而不同提示/attempt/seq得到相同RuleWon、不同LevelWon的对照。
- M03：SAVE_CONTRACT穷举Envelope/Progress/Settings/ActiveSession/RuleState，唯一SaveEnvelope.settings，默认只给新档、坏档不捞设置；规定日期/安全整数/128路线/256KiB、版本保留、profile、最高revision/同号冲突、contentHash迁移、完整重放/FAILED撤销。CJ1明定排序、Unicode原样、UTF8、整数/控制字符及排除checksum摘要；新增2 Schema、2合法中文活动会话/FAILED会话和12反例或迁移样本。checksum仅损坏检测，不是防作弊签名。
- M01：02纳入P00—P22逐节点与原帧编号，observation-index钉6个来源文件和64张截图hash。14次核心输入/283.708秒离散跨度不冒充连续首30秒/5分钟；另两款本环境阻塞，M01仍部分未补。SELF_REVIEW保留原文并显式标历史，当前README/STATUS不会复用过期否认句。
- minor1：06断点优先级唯一，80高目标容纳72缩略图；600×400为单板312，844×390双板270，768×1024双板240，320×568单板208，过小只进恢复页不换分支。
- minor2：05公开四对同解、15/20删门最短不变及5题长度差，区分位型理解复习与新路线，补未来门消融/重复认知停止条件；未声称20种新策略或已验证难度。
- minor3：09/tasks/schema/REVIEW_REQUEST统一T00到../../reviews/G04-audit.md/json，作者不回写；原别名不再作为产物。新增本项目STATUS，包内状态与入口统一为修订待独立复核。

实际校验中第一次新增存档反例运行发现环境默认date-time格式检查没有拒绝13月（invalid_timestamp误得OK）；已用明确公历解析器替代，保留该反例，后续运行按SCHEMA_INVALID拒绝且总验解PASS。Node20.11.0仅交叉校验JSON/crypto，未装或运行TS4.1.2/Cocos。最终validation-report必须随本节和全部源文件hash刷新后才能打包；pack脚本核对全部输入、STATUS存在与r2合同PASS。仍需Hypatia独立复核，G04作者不自审、不签GO。
