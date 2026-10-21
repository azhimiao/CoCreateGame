# 可执行施工计划与依赖

本页是**未来施工任务合同**，不是当前执行记录。`tasks.json` 的16项状态全部PLANNED。T00独立审查现在可做；T01必须人类作决定；T02以后未经该批准不能执行。本轮唯一实际代码是离线规格数据核对，不是这些游戏实现任务。

## DAG与责任边界

| ID | 前置 | 工作与负责角色 | 输出/验收关键点 |
|---|---|---|---|
| T00 | 无 | 独立Agent只读本目录盲审 | review/independent-audit.md；复述规则/接口/失败/异常，列严重度；作者不得代签 |
| T01 | T00 | 人类决定选品与施工 | review/build-approval.md；明确G04、spec1.0.0和hash，未批准停止 |
| T02 | T01 | 构建工程师固定环境 | implementation/project-settings、包锁与build-evidence；实际3.8.7探针构建/版本路径/许可 |
| T03 | T02 | 规则工程师实现纯规则 | rules及对应tests；21向量逐字段一致，20+2关最短步一致 |
| T04 | T03 | 内容工程师做导入/检查 | data与tools/content；Schema/关联/有解/预算与地图预览 |
| T05 | T03 | UI工程师棋盘/输入 | board脚本/prefab；键鼠触摸同命令，动画期间规则不漂移 |
| T06 | T02 | 资产作者原创音画 | art/audio/licenses；06所有必要资产可编辑源/导出/版权链 |
| T07 | T05,T06 | UI工程师完整屏幕 | screens、i18n；U00—U12适当profile可达，错误/返回/焦点/安全区 |
| T08 | T03 | 存档工程师回放恢复 | persistence与tests；双槽、损坏、版本、配额、撤销pending |
| T09 | T04,T08 | 规则工程师提示/成长 | progression；从当前态求解、星数/assisted/幂等完成 |
| T10 | T07,T08,T09 | 平台工程师local/P01 | local/p01 adapters、profiles；移除统计/外链/广告/姓名输入 |
| T11 | T10 | 平台工程师P02分包 | p02 adapter/tests；Basic禁变现、Full SDK、各包体/文件限制 |
| T12 | T10,T11 | QA浏览器/设备/网络 | device/performance原始记录；真机与冷启动，缺设备不代签 |
| T13 | T07,T09,T12 | 研究员机制盲测 | research协议/真实匿名本地数据；B0/X1/X2隔离、预登记阈值 |
| T14 | T06,T12,T13 | 制片与权利审查 | release/materials、rights；真实截图/视频、完整IP链/合同字段 |
| T15 | T14 | 独立复核+人类提交决定 | release/final-review；当日重核规则，未另行授权不提交 |

完整输入、write_scope、DoD、验证命令和每项1—3人日的假设估计在tasks.json。合计16—48人日只是粗规划，不是报价、实支或承诺；T00/T01等待时间、玩家招募、平台审查与外部合同时间没有计算，UNKNOWN。可并行T03/T06以及T04/T05/T08；其他按依赖。并行Agent不能改共同package-lock，T02拥有工具配置；需要新增依赖时写提案由该owner合并。

## 任务准入与完成定义

T00输入是只读的全部施工档案与机器数据，不需读对话/根目录。审计者先自行复述，再运行现有Python核对器，不根据作者摘要直接签通过。T01由人类明确版本与批准文字，口头“继续准备”不能推断批准最终游戏。

T02先做空工程证明构建链可用，不把探针空场景性能当产品。T03以独立TS实现对照Python和固定golden，不能只移植同一个函数再用同源测试证明正确。关卡作者如发现捷径需登记理由，改内容须重跑所有关与save contentHash策略。

T07必须交实际渲染截图与触控视频，不接受仅CSS数值/占位图声称视觉通过。T08的存档故障注入是正式运行测试，Python JSON round-trip不能代替。T10/T11必须检查打出的文件和HAR而非配置标志；P01对外数据请求为零，P02仅允许官方SDK必要域，第三方统计均不装。

T13的完成可以得出REVISION_REQUIRED或KILLED，并不要求实验正向；负面结果同样必须保留原始数据。T14合同缺报价与条款时写UNKNOWN，材料可以准备但不发出。T15仍需另获投稿/签约授权；任何构建成功都不能自动成为发行批准。

## 当前可运行命令与未来命令

当前已存在并执行的命令仅：`python -B validate_spec.py`。它校验两个Schema、20+2关合法最短解、21条golden、反例Schema与任务DAG，写validation-report。压缩包另以Python zipfile测试CRC和manifest哈希，见README/验包报告。

tasks里的npm命令是T02以后必须创建的脚本名称，现阶段没有package.json，不可执行、也没有测试成功记录。具体引擎CLI等安装后按07冻结，不虚构环境路径。任务失败记录实际stderr、构建hash、复现步骤、责任模块；BLOCKER不得改个状态跳过，修复后只补相关回归再推进。

## 交接与变更

每个任务提交输入hash、输出清单、完成证据与未决问题。规则/数据改动提高spec版本并重验全部golden和关卡；UI纯布局变更重验对应屏幕/触控，平台profile修改必须重查网络与包体。未经过独立复述的新增玩法不进入施工范围。本轮不改共享模块或其他游戏目录，所有可交接成果留在G04。
