# G02 对标操作研究｜官方说明间接重建

研究日 2026-10-21。**作者初轮范围**：当轮未实际启动、操作或录制对标游戏，只用公开web工具，未取得交互浏览器/触控录制/原始录像。本句记录初轮历史，不代表团队后来没有浏览器观察。团队同日后补单独记于第5节，不回填为作者亲自实玩。下面的操作骨架是官方说明的间接重建，不是测得回放。所有30秒/5分钟字段均保持 UNKNOWN；不使用其他作者的试玩冒充本作者观察。

## 1. Good Sort Master: Triple Match

身份：Playgama 的单作页 E01，https://playgama.com/game/good-sort-master ，访问2026-10-21，OFFICIAL_DESCRIPTION。准确版本标识、运行环境和计时均 UNKNOWN。

| 流程节点 | 官方可支持的操作骨架 | 本次实际观察 / 未知 |
|---|---|---|
| 进入 | 页面提供启动入口 | 游戏内加载、首屏、账号弹窗 UNKNOWN |
| 教程 | 未核实引导序列 | 文案、手指提示、是否强制 UNKNOWN |
| 首次整理 | 把相同物件拖至同一货架凑三件 | 本次无拖动；合法目标、误触规则 UNKNOWN |
| 首次成功 | 清完物品后过关 | 成功判定时刻、结算按钮和奖励量 UNKNOWN |
| 失败 | 官方说明强调收纳规划 | 是否死局、失败弹窗、救场与惩罚 UNKNOWN |
| 中后期 | 页面描述后续物件与难度变化 | 真实关数、密度、隐藏层、生成方式 UNKNOWN |
| 复玩/回归 | 本次没有回归操作 | 撤销、重开、存档准确行为 UNKNOWN |

前30秒真实轨迹：UNKNOWN。前5分钟真实轨迹：UNKNOWN。不得把官方页面的泛化流程、宣传的轻松感或示意物品排列转写成具体计时游玩。

## 2. Color Water Sort Puzzle Games

身份：TapNation 自家作品页 E02，https://www.tap-nation.io/games/color-water-sort-puzzle-games/ ，访问2026-10-21，OFFICIAL_DESCRIPTION + PORTFOLIO。E03目录也链接该作。它不是 Famobi 的 Color Water Sort 3D（E21）。

| 流程节点 | 官方可支持的操作骨架 | 本次实际观察 / 未知 |
|---|---|---|
| 进入/教程 | 提供商店入口；描述单指操作 | 没有安装；首屏/教程顺序 UNKNOWN |
| 首局 | 在试管间整理有色液体，移动前看空间 | 实际倾倒单位、空管规则、顶部限制原子顺序 UNKNOWN |
| 首次成功 | 同色归类；提及过关宝石 | 奖励数量、到账条件、结算与广告 UNKNOWN |
| 卡住/失败 | 官方提醒避免卡住 | 自动死局检测、撤销/重开成本 UNKNOWN |
| 中后期 | 官方称多关、无时间限制 | 确切关数、布局、难度分布 UNKNOWN |
| 复玩/提示 | 官方称宝石可用于提示 | 价格、提示质量、持久化和回访条件 UNKNOWN |

前30秒真实轨迹：UNKNOWN。前5分钟真实轨迹：UNKNOWN。宝石收益、广告频率、液体每段体积和恢复手段不进入 G02 的事实基础。

## 3. 可借用思想与必须自证的部分

收纳三件消除、水管颜色归类是不同规则家族，不能直接共享失败模型。G02 自拟为离散符号堆栈，匹配是 `type_id` 相等，不模拟液体或三消货架；容器退出、AND章锁、接收标签均 HYPOTHESIS。G02 所有需求量、动画时长、教程和经济免费策略均由本档案定义，不能称为从对标测得。

## 4. 后续实际试玩采集协议（未执行）

独立研究员分别录制：启动至首个输入、首30秒原始画面、连续5分钟、一次成功、一次失败或死局、撤销/重开、关闭重开后的状态。记录日期、官方URL/商店包标识、可见版本、设备、浏览器、屏幕、触控或鼠标；保存每步输入、前后状态、时间戳和视频对应帧。未触发的失败/中后期继续写 UNKNOWN；不为满足表格捏造。

建议只记录已见状态，不反编译资源、抓取专有源码或复制具体关卡。若广告/登录/区域限制阻断，保存阻断证据，不绕过权限。团队补证原件放共享research/playthroughs/G02/，本目录只引用、保存摘要索引和源hash；初轮说明保留历史版本范围。

## 5. 团队后补浏览器观察（与初轮分开）

来源：[observation.md](../../research/playthroughs/G02/observation.md)，仓库路径research/playthroughs/G02/observation.md；官方URL与访问日2026-10-21由原报告记录。类型DIRECT_BROWSER_OBSERVATION，仅涵盖入口/站点输入/加载路径。G02本地摘要与13图索引在evidence/team-browser-observation-index.json，含原报告、日志及manifest SHA256；纳入时只读复核13/13 PNG的bytes/SHA256均PASS。图片原件保留共享研究目录，未复制进生产资产或本ZIP，截图hash完整不证明核心行为。

新增浏览器观察对象Screw Out: Bolts and Nuts，官方URL https://www.crazygames.com/game/screw-out-bolts-and-nuts。这是后补观察对象，不替换初轮E02 TapNation的身份或把不同作品合并。本轮不扩大研究范围/重启浏览器。

| 节点 | Good Sort Master | Screw Out | 能支持的结论 / 仍缺什么 |
|---|---|---|---|
| 官方入口 | OBSERVED | OBSERVED | HTTP200、具名页面；不是可玩通过 |
| 正常界面输入 | OBSERVED：Ignore、Play Now | OBSERVED：Only Essential关闭隐私窗 | 总3次站点UI；核心输入各0 |
| 游戏内初始棋盘 | NOT_CONFIRMED | OBSERVED_PARTIAL：末帧Level1 | GoodSort封面货架不算运行棋盘；Screw只见静态棋盘 |
| 合法放置/拆取 | NOT_OBSERVED | NOT_OBSERVED | 无派发核心操作、无前后状态对照 |
| 非法放置/不可拆 | NOT_OBSERVED | NOT_OBSERVED | 不能把未派发点击解释为规则拒绝 |
| 同物/同色匹配 | NOT_OBSERVED | NOT_OBSERVED | 宣传图、颜色/教程手势不是匹配发生 |
| 非匹配进入暂存 | NOT_OBSERVED | NOT_OBSERVED | 无占槽变化；Screw四点外观不证明容量4 |
| 满槽及失败边界 | UNKNOWN | UNKNOWN | 无最后空位填入和满后再拆对照；官方满即输/再拆才输文字差异未解 |
| 成功 | NOT_OBSERVED | NOT_OBSERVED | Level1不是成功反馈 |
| 失败 | NOT_OBSERVED | NOT_OBSERVED | 加载/预算阻塞不是游戏失败 |
| 游戏内重试 | NOT_OBSERVED | NOT_OBSERVED | 重启浏览器不是重开关卡；重置图标未点 |
| 连续首30秒 | UNKNOWN / NOT_RECORDED | UNKNOWN / NOT_RECORDED | 无以首次有效核心输入为起点的连续记录 |
| 连续首5分钟 | UNKNOWN / NOT_RECORDED | UNKNOWN / NOT_RECORDED | 480.006秒总尝试含加载/排障/读图，不能充300秒实玩 |

原报告：GoodSort阶段驻留195.921秒、核心拖放0次；Screw末帧10:47:55.422 UTC为Level1，拟发点击在工具往返时预算耗尽，日志无input_start，因此核心输入0。总窗口10:40:12.727—10:48:12.733 UTC，截图离散13张、无连续录像；浏览器正常close及runtime清理由研究员记录。本作者只核引用/hash，不冒充自己执行浏览器。

环境为Windows、Chromium headless shell149.0.7827.55、1365×900、DPR1、桌面鼠标、SwiftShader软件渲染；不是物理手机/真实GPU性能。整体结论**BLOCKED_CORE_BEHAVIOR**，13图hashPASS与节点覆盖不足同时成立。初轮两样本的30秒/5分钟和所有缺失规则继续UNKNOWN；不能据此评原作玩法质量、输入永远不可用、留存或收益。
