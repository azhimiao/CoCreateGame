# G01 audit-r1 修订与独立复核入口

2026-10-21；玩法/内容版本1.0.0，合同修订audit-r1。**REVISION_REQUIRED / RECHECK_PENDING / ready_for_build=false / human_build_approval=false**。只写games/G01；不改reviews、根STATUS/shared/data，不开发游戏，不另做ZIP。以下为作者整改记录，不是独立结论。

| Finding | 已做修订 | 复核入口 / 当前边界 |
|---|---|---|
| G01-M01 | 01/02区分作者初轮web文字快照与团队后来浏览器尝试；O01逐节点覆盖表关联原观察/操作/21截图hash；CrazyGames历史西语正文与后来重定向分开 | 02及research/observation-coverage.json；**仍OPEN**：核心合法/非法、胜败重试、保存回归及完整首30秒/5分钟未确认，7m20s只是总尝试时长；不能签Ready |
| G01-M02 | 正式集合/数组/order唯一且精确L01..L20；规则优先级/7阶段提交顺序绑定文档、生成源、JSON、schema const及独立语义检查 | tools/contracts.py、prepare_data.py、validate.py；validation/report.json及audit-mutants.json。作者复验通过，待Hypatia确认 |
| G01-M03 | 纯规则只出RuleFacts/UndoFacts，不读历史/发事件；SessionCoordinator唯一publisher/序号/进度写入者，SavePort只传输；事件/保存去重与中断闭合 | 04、07、09、game-spec.session_contract、tasks T04/T06/T07/T08及contracts/session-vectors.json。3局11步、2组同输入异历史，胜利撤销再完成不加章，仍须保存新rev；待独立确认 |
| G01-m01 | L16/L18目标改为辨认，不再当两个合法同向候选；L19保护效应/去船期16个losing反证加入12 | 05、12、生成源学习目标；几何/机关/初态/胜利/解/seed未变，20逐关hash吻合。待独立确认 |
| G01-m02 | 加SaveEnvelope schema、27边界样例；安全rev、重复JSON键/教程/log、额外字段、解锁前缀、版本/重放与已胜未登记修复边界固定 | 04、06、contracts/save-vectors.json、save-envelope.schema.json。表数据检查通过，真实Web Storage故障注入NOT_RUN；待独立确认 |

复验：python -B tools/validate.py；python -B tools/check_audit_mutants.py。当前结果：原20关20/20，149可达状态、645候选动作、9规则反例；3份schema、16任务DAG与Session任务写域/依赖通过；10项合同变异被schema与语义双拒；完整checker原4审计mutant及8新增负例全拒。原始两漏洞的delta及其来源hash保留在audit-mutants.json，避免仅改状态/hash就宣布修复。

准备源prepare_data.py、prepare_evidence.py、write_level_catalog.py已同步。research/raw/仍仅本地内部完整工具长文本，不进入资料ZIP；正式交付只含URL/日期/标题/定位/hash/自写摘要。团队原观察由根包按其delivery_manifest白名单收一次，排除runtime/；本目录只索引，不复制网页长文/截图。

Hypatia复核从本页开始，依次读04、tasks T04/T06/T07/T08、两个contracts JSON及两个验证报告，再看02/O01和12教学反证。独立结论仍由主控reviews/G01-audit.md/json管理；作者不关闭M01、不自签Ready。自有游戏未构建、未实机/真人/SDK/商务验证，不能把离线PASS称本地构建性能验证。
