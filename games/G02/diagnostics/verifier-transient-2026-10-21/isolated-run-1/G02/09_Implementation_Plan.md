# G02 实施计划与任务DAG

2026-10-21｜**只计划，全部未来开发任务NOT_EXECUTED**。当前可执行工作仅离线规格工具和交付打包。tasks.json含每任务输入、独占输出、角色、前置、DoD、验证命令与门禁；本地tasks.schema.json验证结构，verify.py额外验证无环、依赖存在和输出不撞写。

## 1. 任务表

| ID | 前置 | 独立工作/交付 | DoD与验证 |
|---|---|---|---|
| T01 | 无 | 同一独立审查者修订复核，本目录audit/independent-review-receipt.md | 首审REVISE原件只读；REVISIONS逐条提供作者闭合主张与证据，复核未完成 |
| T02 | T01 | 用户批准游戏ID、版本hash、预算，audit/human-build-approval.md | 所有阻断项关闭；没有记录不开发 |
| T03 | T02 | 候选工具链实际验证，implementation/toolchain/toolchain-lock.json | Creator安装build/hash、类型声明、tsc与Web构建日志；官方exit36和真实可玩 |
| T04 | T03 | RuleCore.ts | 03规则、离线向量一致；拒绝无副作用；`npm run test:rules` |
| T05 | T04 | Persistence.ts，含RunStore/Undo/Replay/Hint合同 | 04总序、失败缓存不重复副作用、v2恢复新epoch、128窗口/撤销、4096终点checkpoint、UNKNOWN；移植protocol-vectors后`test:persistence`、`test:replay` |
| T06 | T03 | 原创源图/音/字体及asset-ledger.json | 06尺寸、08权利；`check:assets`+人工逐项确认 |
| T07 | T04,T06 | GameShell.ts及其11屏 | PLAY全尺寸无滚动、320×568安全区/font1.3/小横屏；菜单唯一pointer owner、44热区；`test:ui` |
| T08 | T04,T05,T07 | experiment-config.json与20关内容 | 不更改GameSpec；V0/X1/X2开关；`test:levels`+离线verify |
| T09 | T03 | P02 Adapter.ts | Basic禁变现、Full SDK、包限制/生命周期；`test:platform -- P02`、`check:bundle -- P02` |
| T10 | T03 | P04 Adapter.ts | Bridge，零外部统计、方向/保存；`test:platform -- P04`、`test:network -- P04` |
| T11 | T05,T07,T08,T09,T10 | web-results.json与真机记录 | 集成、浏览器、性能和包体实际检查，不填估测PASS |
| T12 | T11 | player-study.md | 12盲测分母/退出/变体数据，作REVISION/KILL决策 |
| T13 | T02 | P05 audit/p05-sdk-confirmation.md | 另行外部联系授权后核实P05书面SDK条件；不代表P06 |
| T14 | T03,T04,T05,T06,T13 | P05 implementation/mobile/p05/native-feasibility.md | P05引擎可行性、完整移动UI、SDK/签名安装/真机QA/性能/移动盲测 |
| T15 | T11,T12 | 仅P02/P04 audit/web-release-gate.md | 分渠道网页权利/QA/条款/人类提交批准；不代表任何移动审批 |
| T16 | T02 | P06 audit/p06-sdk-confirmation.md | P06单独书面条件与另行外部联系授权；不继承P05答复 |
| T17 | T03,T04,T05,T06,T16 | P06 implementation/mobile/p06/native-feasibility.md | P06专属引擎/移动UI/SDK/签名真机/隐私/性能/移动盲测 |
| T18 | T13,T14 | 仅P05 audit/p05-release-gate.md | P05五条件：书面SDK、原生QA、移动研究、清晰权利、人类提交批准 |
| T19 | T16,T17 | 仅P06 audit/p06-release-gate.md | P06同类五条件必须自己的凭证；不能拿Web/P05批准顶替 |

所有文件目标均加`games/G02/`前缀，详细路径见tasks.json。T04/T05/T07等可在自身子目录增补实现文件，但不能跨目录改别人输出；公共package.json与Cocos工程配置由T03指定集成者单写、审查后合并。共享根/别的Gxx/通用库无写权限。

## 2. 并行和关键路径

T01→T02→T03→T04→T05/T07→T08→T11→T12→T15是网页主要门禁路径；T06可在T03后与规则并行，T09/T10各自单写独立adapter；最终由T11集成检查。P05支线T13→T14→T18与P06支线T16→T17→T19各自独立，依赖共用纯规则/资产不等于复用SDK批准。tasks每项增加platform_ids/required_conditions/verified_conditions；当前verified_conditions全空。离线模拟只让网页前置与批准条件满足时，T15可达而T18/T19均不可达；只补P05时仍不能达到P06。这里是门禁语义校验，不是真批准。

每个角色估时为HYPOTHESIS，tasks中的单值仅容量规划，非实际工时/合同。网页垂直切片实施预算先以80人时封顶（需人类批准），实际发现SDK/资产/返工需额外成本时停止扩范围并重新决策；不为命中预算删测试或伪造完成。

## 3. 开始任务前的可独立施工检查

执行者应能只靠00—12及JSON回答：每种托盘能进出什么、封箱为何需要主动、锁如何AND判断、标签是否改变顶层规则、何时死局、undo会不会重锁、选中态非法点击会不会换源、提示超时是不是无解、P04能否放GA4、无SDK Basic包限多少。任何一个答不清先开finding，不能自由补设计。

设计变更须同时更新03、04、05/06相关表、game-spec与Schema、测试向量和tasks依赖；修改20关后重新解验证并重打包。不能改渲染层“自动消除”绕过RuleCore。

## 4. 命令与证据

当前真实命令：`python -B tools/verify.py --all`，输出verification/verification-report.json；打包命令见README。未来npm/Creator命令在07/10定义，**当前不存在其工程**；T03负责提供可重现脚本，T11留原始stdout/stderr、退出码、设备和产物hash。P05具体命令等T13，P06具体命令等T16才能定，不能将APK路径占位符称可用构建。

T01当前PENDING_RE_REVIEW：独立首审已写reviews/G02-audit.md和.json，结论REVISE（1B/2M/3N）。原件不修改，hash见REVISIONS.md；作者修订与复核索引已交回同一审查者。作者自检和离线PASS不能关闭T01，更不能提升READY_FOR_BUILD；T02仍需真实人类批准。

两个移动条件支线不包含在网页80人时上限中；是否启动和额外预算需各自批准。tasks逐项估时为假设，不能把19节点估时求和冒充已承诺全平台预算。
