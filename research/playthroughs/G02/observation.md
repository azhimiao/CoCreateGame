# G02 实际浏览器补证｜2026-10-21

本轮结果：**BLOCKED_CORE_BEHAVIOR**。Good Sort Master 未确认进入棋盘；Screw Out 最后已出现 Level 1 棋盘，但八分钟预算在读图期间耗尽，未取得任何核心拆取输入或响应证据。只补到了官方入口、正常界面输入和加载路径，**没有补齐 G02 核心行为研究缺口**。

所有写入限于 `research/playthroughs/G02/`。已先读取根 `AGENTS.md`、`MASTER_HANDOFF.md` 和原 `research/benchmarks/benchmarks.json` 的对应记录；未改 games、reviews、benchmarks、根 STATUS 或 data。原 benchmarks 文件前后 SHA-256 一致，见 [evidence-audit.json](evidence-audit.json)。本报告可被研究档案引用，不是 G02 施工或构建批准。

## 官方来源与证据口径

访问日均为 **2026-10-21**，URL 从原快照读取，再经 web 工具打开、浏览器实际导航核对。官方说明是 **OFFICIAL_DESCRIPTION**，以下输入/截图是 **DIRECT_BROWSER_OBSERVATION**；不能相互替代。

| 对象 | 官方 URL / 类型 | 官方说明用于提出的检查问题 | 本轮实际核实 |
| --- | --- | --- | --- |
| Good Sort Master: Triple Match | https://playgama.com/game/good-sort-master / 官方游戏页 | 拖动物品、同架三件匹配、清空过关的实际条件是什么？ | HTTP 200、可见 Play Now、忽略登录保存提示后进入前置加载界面 |
| Screw Out: Bolts and Nuts | https://www.crazygames.com/game/screw-out-bolts-and-nuts / 官方游戏页 | 点击拆取、按色容器、额外暂存和失败边界如何实现？ | 两次导航均 HTTP 200；新浏览器内正常关闭隐私弹窗，加载后出现 Level 1 棋盘 |

官方 Screw Out 教学对“暂存刚满即输”和“无位置时再拆才输”的文字边界仍有差异，本轮**没有**直接验证其中任何一种。页面发布/版本与实际运行包的对应关系 UNKNOWN；动态评分、点赞、下载进度均不作游玩量、收入或性能结论。来源元数据和 UNKNOWN 清单见 [official-sources.json](official-sources.json)。

## 逐节点覆盖表

`OBSERVED` 仅表示有直接画面证据；`NOT_OBSERVED` 不表示该机制不存在。0 次确认输入也不能推出输入永远无法生效。

| 节点 | Good Sort Master | Screw Out | 本轮证据 / 限制 | 后续所需验收证据 |
| --- | --- | --- | --- | --- |
| 官方入口 | OBSERVED | OBSERVED | 两款 HTTP 200、具名页面；见日志与截图 | 已覆盖入口存在，不等于可玩 |
| 正常界面输入生效 | OBSERVED | OBSERVED | Good Sort：Ignore/Play Now；Screw：Only Essential 关闭弹窗 | 仅站点 UI，不能计核心输入 |
| 游戏内初始棋盘 | NOT_CONFIRMED | OBSERVED，PARTIAL | Screw 末帧显示 Level 1、容器、螺丝、教程指示 | 还需操作后变化 |
| 合法放置 / 可拆螺丝 | NOT_OBSERVED | NOT_OBSERVED | 核心派发日志 0 条；没有物件或螺丝状态前后对照 | 坐标/拖放轨迹 + 输入前后物件位置/容器变化 |
| 非法放置 / 被遮挡或不可拆 | NOT_OBSERVED | NOT_OBSERVED | 未对有效棋盘完成一次受控反例 | 已确认合法输入后，再测一个明确不合法目标及回弹/拒绝结果 |
| 三件同物 / 同色匹配 | NOT_OBSERVED | NOT_OBSERVED | 宣传图和初始颜色不算匹配发生 | 一组同物/同色输入、数量变动、清除/容器刷新画面 |
| 非匹配对象进入暂存 | NOT_OBSERVED | NOT_OBSERVED | Screw 初始棋盘仅可见点位，不认定实际容量或路由规则 | 不匹配颜色的拆取 → 新占槽截图 |
| 暂存/架位满及边界 | UNKNOWN | UNKNOWN | 无已占满状态，官方文字冲突未解决 | 最后一空位填入前后 + 满后再试一次的判定，分别记录 |
| 关卡成功 | NOT_OBSERVED | NOT_OBSERVED | 出现 Level 1 不算过关 | 清空目标前后、成功反馈和下一关 |
| 失败 | NOT_OBSERVED | NOT_OBSERVED | 本轮是运行/预算阻塞，不是游戏失败 | 有效局面中触发实际失败和失败 UI |
| 游戏内重试 | NOT_OBSERVED | NOT_OBSERVED | 重开浏览器只是排障；棋盘上重置图标未点击 | 从失败/重置按钮回到初始状态，再确认一次核心输入 |
| 连续首 30 秒 | NOT_RECORDED | NOT_RECORDED | 只有离散截图，无连续录像或逐帧记录 | 以首次有效核心输入为起点的连续计时记录 |
| 连续首 5 分钟 | NOT_RECORDED | NOT_RECORDED | 八分钟总排障不算五分钟实玩 | 同上，覆盖 300 秒且不中断地记录真实过程 |

## Good Sort Master 实际路径｜BLOCKED

2026-10-21 **10:40:12.727 UTC** 导航。网页提供登录保存提示和 Play Now；先点击 Ignore `(746,108)`，再点击 Play Now `(492,392)`。坐标为全视口 CSS 像素，不是游戏内部坐标。

- [001 官方入口](screenshots/2026-10-21T10-39-50-665Z-goodsort-001-official-page.png) 展示的是站点封面/宣传图；图中货架**不是已经确认可操作的运行棋盘**。
- [002 点击前](screenshots/2026-10-21T10-39-50-665Z-goodsort-002-before-click.png) → [003 Ignore 后](screenshots/2026-10-21T10-39-50-665Z-goodsort-003-after-click.png)：保存提示关闭。
- [004 Play Now 前](screenshots/2026-10-21T10-39-50-665Z-goodsort-004-before-click.png) → [005 点击后](screenshots/2026-10-21T10-39-50-665Z-goodsort-005-after-click.png)：黑底品牌加载层，提示需等待前置短广告。
- 后续两次截图请求在 10:42:36.092 和 10:43:09.545 UTC 超时。10:43:03.499 的 DOM 检查见全视口第三方广告 iframe，但缺少随后成功截图，**不能断言整个间隔一直停在同一帧**，也不能把广告网络失败当作确定根因。

10:43:28.648 UTC 结束该款阶段，总驻留 **195.921 秒**；2 次实际站点 UI 点击，核心拖放 **0 次**。记录器虽然支持拖放，未进入可确认棋盘，故没有盲拖封面或把未执行操作写为合法/非法结果。匹配、容量、胜败、重试均 UNKNOWN/NOT_OBSERVED。

## Screw Out 实际路径｜入口 PARTIAL，核心 BLOCKED

**第一阶段，同一浏览器。** 10:43:28.650 UTC 导航官方 URL，返回 200，但截图超时。日志记载一个游戏加载器请求连接关闭；它仅是诊断事件，不能单独确立阻塞根因。10:44:23.896 UTC 结束该阶段，随后正常关闭浏览器，10:44:24.474 清理第一份 runtime。此阶段没有成功截图或实际核心点击。

**第二阶段，新隔离浏览器。** 10:44:57.314 UTC 再次导航，沿用本轮原始八分钟总截止时间，剩余 195.413 秒。没有修改网站、请求、游戏状态、加载策略或浏览器身份。

| UTC / 全局尝试秒数 | 画面/输入 | 证据与解读 |
| --- | --- | --- |
| 10:45:02.824 / 290.097s | 官方页初始壳 | [001](screenshots/2026-10-21T10-44-40-833Z-screwout-001-official-page.png)，无游戏棋盘 |
| 10:45:30.178 / 317.451s | 隐私弹窗可见 | [002](screenshots/2026-10-21T10-44-40-833Z-screwout-002-screw-ui-check.png) |
| 10:45:52.347 / 339.620s | 点击 Only Essential `(535,522)` | [003 前](screenshots/2026-10-21T10-44-40-833Z-screwout-003-before-click.png) → [004 后](screenshots/2026-10-21T10-44-40-833Z-screwout-004-after-click.png)，弹窗消失；后帧显示 80% 加载。百分比前进不能全部归因为点击 |
| 10:46:25.324 / 372.597s | 加载显示 86% | [005](screenshots/2026-10-21T10-44-40-833Z-screwout-005-screw-after-essential-load.png)；检查发现游戏框架 canvas，但 canvas 不是输入证据 |
| 10:46:52.233 / 399.506s | 显示后续加载提示 | [006](screenshots/2026-10-21T10-44-40-833Z-screwout-006-screw-final-loading-check.png) |
| 10:47:30.042 / 437.315s | 仍显示解析/准备提示 | [007](screenshots/2026-10-21T10-44-40-833Z-screwout-007-screw-ready-or-blocked.png)；不是棋盘操作 |
| 10:47:55.422 / 462.695s | 首次成功截到 Level 1 棋盘 | [008](screenshots/2026-10-21T10-44-40-833Z-screwout-008-last-budget-check.png)；看到两组彩色容器外框、下方四个点位、彩色螺丝和指向黄色螺丝的教程手势，仅为静态视觉读数 |
| 10:48:12.733 / 480.006s | 总预算触发正常 close | 日志 `attempt_cap_reached`、`browser_closing`；10:48:12.927 清理完成 |

末帧后拟发送三次螺丝点击，但读图和工具往返期间触发了截止；工具返回进程已退出，日志**没有**对应 `input_start`，也没有响应截图。它们未计入实际派发操作。不能由教程指示、三孔外观或四点位推导“已拆取”“三个同色已匹配”“暂存容量就是四个”“已被规则拒绝”。图中的重置图标未点击，浏览器重启不是游戏内重试。

Screw Out 的节点结果为 **PARTIAL_ENTRY_ONLY_CORE_BLOCKED**；整个补证任务的核心行为目标仍为 BLOCKED。末阶段因预算直接 close，没有伪造一次实时 `game_finished`；[outcome-assessment.json](outcome-assessment.json) 明确标为结束后的读图/日志评估。

## 时间、设备与限制

总尝试窗口从首次导航 **10:40:12.727 UTC / 18:40:12.727 北京时间** 开始，至预算触发 **10:48:12.733 UTC / 18:48:12.733 北京时间**，共 **480.006 秒**；context 关闭与清理在 480.200 秒处完成。加载、排障、正常浏览器重启、读图和工具间隔都计入总预算，不因重启重置，也没有通过后台空等凑实玩时间。实际派发输入共 **3 次**，全部为站点 UI：Ignore、Play Now、Only Essential。确认核心游戏输入 **0 次**，连续有效玩法时长 **未建立**。

设备详细记录见 [device.json](device.json)：Windows / Node v20.11.0；Chromium headless shell **149.0.7827.55**（本机既有目录 `chromium_headless_shell-1228`）；1365×900、DPR 1、桌面鼠标、无触屏、en-US、Asia/Shanghai。使用与 G04 相同的现有 Playwright 和 SwiftShader 软件渲染方式，没有新增安装或资源导出。这里的正常浏览器路径仍是 **headless 桌面环境**，不冒称物理手机、有头浏览器或真实 GPU 性能结果。

限制：单环境与单日结果；截图超时造成采样缺口；无连续录像；无确定的加载阻塞根因；对核心操作完全缺证。不能据此判断原作玩法质量、所有用户可玩性、玩家失败率、留存、收益或平台成功率。

## 文件、证据完整性与后续边界

- [operations.jsonl](operations.jsonl)：两次浏览器会话、三次导航阶段的事件；保留真实时间、派发命令、错误、截图哈希和正常关闭事件。
- [operation-log.md](operation-log.md)：按日志生成的 3 次实际输入前后索引。[screenshots/manifest.json](screenshots/manifest.json)：13 张 PNG 的逐文件时间、尺寸、字节数和 SHA-256。失败的截图编号没有伪造或补帧。
- [evidence-audit.json](evidence-audit.json)：日志处理前后哈希、辅助 URL/iframe 元数据删减数、原 benchmark 哈希不变、runtime 不存在。日志删减仅去除无关辅助框架元数据和外部路径/参数，不改变输入、时间、截图哈希和错误结果。原始无关副本不额外保留。
- [browser-session.cjs](browser-session.cjs) 与 [finalize-evidence.cjs](finalize-evidence.cjs)：可审阅记录与整理逻辑；未收集游戏源码、注入状态或导出商业素材。截图里的游戏/站点内容属于第三方研究证据，不是自有生产资产。

`runtime/` 已隔离于本目录并由 `.gitignore` 排除；两次 context 均正常 close 后清理，最终路径不存在。未注册、付费、上传、联系他人、跳过广告控制、绕过访问限制或另找镜像。游戏在正常浏览器运行所需的网络资源加载不另存为源码或素材档案。

后续若再次授权，应优先给已经能够显示棋盘的 Screw Out 单独分配观察窗口，先确认一个合法拆取，再做明确拒绝反例、颜色匹配、暂存最后一空位与满后再拆对照，最后取得胜败/游戏内重试。**本轮不再尝试、不修改已有研究快照，也不将尚未验证的边界升级为规格。**
