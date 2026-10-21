# G01 可立即并行整改的独立 Findings

2026-10-21 18:38（Asia/Shanghai）。完整终审报告随后交付；这里先提供可复核的规格问题。只读当前最终 00—12/JSON/schema/QA 后独立建模；20关全部有解，149个可达状态、645次可达动作比较、2344次全子集动作比较均与作者一致，未把验解缺口说成原关无解。

## G01-M02｜MAJOR｜campaign唯一性及规则声明与验解语义脱节

位置：`games/G01/game-spec.schema.json` 的 progression.order/levels、`tools/validate.py:162` 及规则元数据校验。

证据：仅把最后关记录ID由L20改L19，并同步order末项L19，当前完整checker仍PASS；留下重复L19、丢失L20。另只把rules.commit_order反转，仍PASS，因为验解写死另一顺序。负例和stdout见 `reviews/G01-checks/mutation-probes/duplicate_campaign_id/`、`reversed_commit_order/`；总记录见 `independent-results.json`。

修法：固定正式L01—L20的集合、顺序和唯一性；将当前规范化规则标签/优先级/commit_order与机器校验绑定，或明确它是非执行说明并校验其与固定规则版本一致。无需重写关卡。

验法：原20关和9规则反例仍PASS；重复/缺失/乱序/错号的campaign与逆序提交分别拒绝；schema和checker同步，拒绝用更新报告hash替代语义检查。

## G01-M03｜MAJOR｜规则返回事件缺少会话/进度输入，集成责任需明确

位置：`games/G01/04_Systems_and_Data.md` 的 commitExit/事件表，`07_Tech_Architecture.md` 的 Rules/Session，`tasks.json` 的T04/T06/T08。

证据：commitExit只接Level/Attempt/arrowId/expectedRevision，Attempt仅levelId/log/revision，返回events[]；每事件却规定session-local eventId，LevelCompleted还需firstClear/stampCount。相同Level/Attempt在不同历史completed集合的两局应产生不同首通载荷，纯规则接口没有这些输入。Session模块明确存在，但16任务没有明确的Session/应用总线/进度事件组装交接物；T04只有future/rules，T06只有ui/scenes，T08只有content/tutorial。

修法：作者确定纯规则事实与Session/Progress富化事件边界、序号和首通的唯一发布者；为Session/应用状态机/事件组装分配明确任务、目录和验收。可以保持既定玩法。

验法：两份相同局面、不同completed历史，冷读实现者能唯一列出规则返回及最终事件/保存；同一次完成只增一个章，胜利撤销重做不再首通，动画中断不二次提交；明确由哪个任务实现。

G01-M01对标证据覆盖仍需结合后补观察复核：允许官方说明等间接分析，不能据此宣称完整首30秒/5分钟已实测。该项不妨碍作者先修以上两项。
