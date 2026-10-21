# G04 官方浏览器实证｜2026-10-21

结论：**PARTIAL**。Paint Master 已取得真实输入 → 棋盘与计数变化 → 单关完成 → 故意耗尽步数失败 → 返回菜单重新开局 → 再次有效输入的证据。Bloxorz、Liquid2 为 **BLOCKED**，没有确认核心游戏输入生效。三款均不声明完成连续首 30 秒或连续 5 分钟实玩观察。

本轮只写 `research/playthroughs/G04/`。已先读根 `AGENTS.md` 和 `MASTER_HANDOFF.md`；不更新 games、benchmarks、根 STATUS 或 data，不构成施工批准。

## 来源、环境与量纲

访问日均为 **2026-10-21**。下列为官方站点的一手游戏页；页面说明属于 **OFFICIAL_DESCRIPTION**，下面逐步输入与截图属于 **DIRECT_BROWSER_OBSERVATION**。两类证据分开使用。

| 游戏 | 官方 URL | 官方说明的用途 | 本地浏览器响应 | 未知项 |
| --- | --- | --- | --- | --- |
| Bloxorz | https://www.coolmathgames.com/0-bloxorz | 定位对象；说明将方向键作为预期输入 | HTTP 200；出现 `/0-bloxorz/play` iframe | 实际移动、坠落、通关、重试均 UNKNOWN |
| Liquid 2 | https://www.coolmathgames.com/0-liquid-2 | 定位对象；说明 A/D 或左右键控制旋转 | HTTP 200；本轮**可见画面**显示浏览器不可玩提示 | 液体旋转、收集判定、失败与重试均 UNKNOWN |
| Paint Master | https://www.coolmathgames.com/0-paint-master | 官方首页的具名链接确认 URL；说明行列画笔、覆盖与步数 | HTTP 200；官方页内 `/sites/default/files/public_games/56412/` 游戏框架 | 后续关卡、完整计分公式、广告奖励是否兑现均 UNKNOWN |

来源定位记录见 [official-sources.json](official-sources.json)。网页抓取工具会展开隐藏的兼容性提示，因此仅凭网页文本中的 Flash 提示不能判断一款游戏不可玩。Liquid2 的阻塞依据是本轮截图中实际可见的提示；Paint Master 的同类隐藏网页文本没有阻止其真实运行。

运行环境：Node v20.11.0；本机 `F:/beautiful/node_modules/playwright-core`、`pngjs`；Chromium headless shell 149.0.7827.55，安装目录 `chromium_headless_shell-1228`；1365×900 视口、en-US、Asia/Shanghai、临时新 profile。参数含 SwiftShader 软件渲染，不作有头浏览器、手机真机或生产性能结论。脚本不拦截请求、不注入游戏状态、不调用游戏内部接口。DOM 读取限于界面/焦点/iframe/canvas 信息，核心变化由截图核查。

坐标单位是整个页面视口 CSS 像素；Move、Score、LEVEL 是**本次画面读数**，不是开发者内部经济参数，也不是玩家样本。日志时间为 UTC（`Z`），北京时间加 8 小时。截图像素差仅用于定位待复核变化，动画、广告和滚动都可能造成差异，不能独立证明有效输入。

## 范围与时间审计

| 对象 | 导航至最后输入后截图 | 最后主动输入 | 行政结束 | 核心玩法观察 |
| --- | --- | --- | --- | --- |
| Bloxorz | 10:09:12.024 → 10:10:40.482 UTC，88.458 秒 | 85.305 秒时发送方向键组 | 导航后 224.509 秒 | 0 次确认；时长不计 |
| Liquid2 | 10:12:56.536 → 10:13:28.801 UTC，32.265 秒 | 30.426 秒时发送 A/D | 导航后约 32.269 秒 | 0 次确认；时长不计 |
| Paint Master | 10:14:18.156 → 首次核心变化截图 10:16:36.157 UTC，138.001 秒 | 最后一次画笔输入为 10:21:16.008 UTC | 10:21:32.868 UTC | 首次有效画笔输入 10:16:34.090 至末次响应截图 10:21:17.798，跨度 **283.708 秒** |

Paint Master 的 283.708 秒只是**含读图、日志整理、菜单/结算等待的离散采样跨度**，不是 283.708 秒持续有效操作。核心画笔输入共 14 次：第一关 3 次、第二关故意错误涂色 10 次、重开后 1 次。没有录像或连续观测，连续首 30 秒/5 分钟证据仍缺。

边界执行偏差如实保留：Bloxorz 的最后操作和截图在 89 秒内完成，但页面在证据阅读期间继续保留，行政结束时已达 224.509 秒，超过约 3 分钟的目标；不将其总驻留时间缩写为 89 秒。207.960 秒处有 3 条命令错误：操作员误把命令键写成 `cmd`，脚本需要 `op`，这些命令没有派发游戏输入，随后用正确的 `op: finish` 结束。本轮未继续对该款排障。Liquid2 约 32 秒即止；Paint Master 在约 138 秒内取得核心输入，后续有效观察跨度不足 5 分钟，无机械空等凑时长。

## Bloxorz：BLOCKED

1. 导航官方游戏页后出现加载区域，稍后出现官方 `/play` iframe。点击游戏区域 `(480,325)`，再发送 Enter、Space；未出现棋盘、可移动方块或游戏内菜单。[点击前 003](screenshots/2026-10-21T10-08-52-583Z-bloxorz-003-before-click.png)、[点击后 004](screenshots/2026-10-21T10-08-52-583Z-bloxorz-004-after-click.png)、[按键后 006](screenshots/2026-10-21T10-08-52-583Z-bloxorz-006-after-key.png)。
2. 80.516 秒处页面报 `Cannot read properties of undefined (reading 'getContext')`。记录器只取得错误信息，没有可靠堆栈/归属；根因 **UNKNOWN**，不据此归罪于广告、GPU、游戏本体或整个 Coolmath 平台。
3. 85.305 秒发送 ArrowRight、ArrowDown、ArrowLeft。画面仍为加载动画，父页面发生滚动；这不算方块移动。[方向键前 007](screenshots/2026-10-21T10-08-52-583Z-bloxorz-007-before-key.png)、[方向键后 008](screenshots/2026-10-21T10-08-52-583Z-bloxorz-008-after-key.png)。

输入派发成功与游戏响应是两件事。本轮 **0 次确认生效**；胜、负、重试均 **NOT_OBSERVED**。这是本环境的一次加载阻塞，不是该作品商业失败或设计失败证据。

## Liquid2：BLOCKED

官方页在当前浏览器实际显示不可玩提示；检查中没有可见游戏 canvas 或游戏 iframe。[提示画面 010](screenshots/2026-10-21T10-08-52-583Z-liquid2-010-liquid-initial-load.png)。点击区域 `(479,316)` 后发送 `a`、`d`，截图仍是相同提示；像素阈值检查也没有发现实质画面变化。[点击后 012](screenshots/2026-10-21T10-08-52-583Z-liquid2-012-after-click.png)、[A/D 后 014](screenshots/2026-10-21T10-08-52-583Z-liquid2-014-after-key.png)。

这能证明本轮该页面未提供可操作游戏画面，不能推出所有浏览器永久不可玩。旋转、水流、胜负、重试均 **NOT_OBSERVED**。明确阻塞后改用用户允许的 Paint Master；没有转向第三方镜像或安装插件绕过限制。

## Paint Master：PARTIAL，有核心行为证据

**进入游戏。** 官方页内出现 PLAY。点击后加载，再出现 How to play；点击 Next 到开始菜单，点击 START 到棋盘。菜单输入可响应，但它们没有被提前计为核心玩法。入口/教程/初始棋盘见 [017](screenshots/2026-10-21T10-08-52-583Z-paintmaster-017-paint-load-check.png)、[021](screenshots/2026-10-21T10-08-52-583Z-paintmaster-021-paint-loading-recheck.png)、[026](screenshots/2026-10-21T10-08-52-583Z-paintmaster-026-after-click.png)。

**输入 → 变化 → 单关完成。** 第一局第一关初始 2×2 棋盘米色、Move 10、Score 0；目标为 `蓝 红 / 红 红`。坐标与颜色为本次页面布局和本次局面，不是永久固定关卡规格。

| 输入 | 直接看到的变化 | 证据 |
| --- | --- | --- |
| 蓝色列画笔 `(455,562)` | 左列变蓝；Move 10→9；Score 0→10 | [027 前](screenshots/2026-10-21T10-08-52-583Z-paintmaster-027-before-click.png) → [028 后](screenshots/2026-10-21T10-08-52-583Z-paintmaster-028-after-click.png) |
| 红色第二列画笔 `(522,561)` | 右列变红；Move 9→8；Score 显示 30 | [030](screenshots/2026-10-21T10-08-52-583Z-paintmaster-030-after-click.png) |
| 红色第二行画笔 `(597,487)` | 下行覆盖为红，棋盘与目标一致；随后进入 LEVEL 2，Score 180、Move 10 | [032 匹配/过渡](screenshots/2026-10-21T10-08-52-583Z-paintmaster-032-after-click.png) → [033 LEVEL 2](screenshots/2026-10-21T10-08-52-583Z-paintmaster-033-paint-level-progression.png) |

这里确认的是**一个关卡完成**，没有观察到整款游戏最终胜利。第一关最后一次点击前为 Move 8，过渡截图为 Move 10；奖励/计分细项、是否先扣再加及动画时序不能从两帧完整反推，均不填内部公式。

**具体对照：错误重复输入 → 失败。** 第二关目标为全蓝，棋盘保留上一关配色，Move 10。改为重复点击第二行黄色画笔 `(597,487)` 共 10 次。第一次将下行涂黄，第二次即使仍是黄色也继续消耗步数，见 [035 首次错误](screenshots/2026-10-21T10-08-52-583Z-paintmaster-035-after-click.png) 与 [037 重复后 Move 8](screenshots/2026-10-21T10-08-52-583Z-paintmaster-037-after-click.png)。最后出现 Move 0 和 **GAME OVER**，[053](screenshots/2026-10-21T10-08-52-583Z-paintmaster-053-after-click.png)。

这与第一关的成功输入构成明确对照：乱点/重复同色没有自动解决目标，而且会耗尽步数。此处为研究者故意制造的单次失败，不是自然玩家失败率、难度分布或市场失败案例。

**失败 → 结束本局 → 重试。** 耗尽步数后出现带视频标识的 Continue 补步选项和 End Game。[054](screenshots/2026-10-21T10-08-52-583Z-paintmaster-054-paint-game-over-controls.png)。未点击奖励视频选项，因此实际广告播放、补步到账 **UNKNOWN**。点击 End Game 后出现 Score 182 的结算，点击 Next 返回菜单，再点 START：

- [057 结算](screenshots/2026-10-21T10-08-52-583Z-paintmaster-057-paint-results-controls.png) → [060 菜单](screenshots/2026-10-21T10-08-52-583Z-paintmaster-060-paint-return-after-results.png) → [062 重开](screenshots/2026-10-21T10-08-52-583Z-paintmaster-062-after-click.png)：LEVEL 1、Score 0、Move 10，棋盘恢复米色，目标与首次开局不同。
- 再点击 `(455,562)`，该次局面对应黄色列画笔，左列变黄且 Move 10→9。[063 输入前](screenshots/2026-10-21T10-08-52-583Z-paintmaster-063-before-click.png) → [064 输入后](screenshots/2026-10-21T10-08-52-583Z-paintmaster-064-after-click.png)。这证明重开后可以再次操作，不能称为原题原状态的一键 Retry；是否随机生成、轮换题库或其他原因 **UNKNOWN**。

## 给 P0 的证据增量与剩余阻塞

已补：实际浏览器入口、核心点击因果、颜色覆盖与步数反馈、一个成功局部序列、故意错误对照、失败界面、结算/菜单重开及重开后输入。G04 可引用这些证据，但本任务没有修改其候选/施工档案。

尚缺：Bloxorz 核心操作、失败与重试；Liquid2 水流响应或可执行替代版本；连续首 30 秒和连续 5 分钟记录；更多关卡、撤销/提示实际效果、触屏与小屏、音频、跨浏览器、性能分布、受众理解/留存、市场/收入、素材许可。**没有任何玩家研究样本或收益结论。**

可供后续研究的 **HYPOTHESIS**：在原创行列覆盖谜题中，用可见预览提示下一步覆盖范围，可能减少“重复同色仍扣步”的误解。此想法未验证；需用自有抽象素材对比有/无预览版本，记录误操作和规则复述。Paint Master 的本次画面只支持“该误操作路径存在”，不能证明预览一定有效，也不授权复制其人物、美术、界面表达、源码或题目。

## 留存、清理与可复核性

[operations.jsonl](operations.jsonl) 保存操作、错误、时间和截图哈希；[operation-log.md](operation-log.md) 提供人读索引；[screenshots/manifest.json](screenshots/manifest.json) 列出 64 张截图与哈希，保留输入前后帧及重复帧以维持操作链。015 是结束 Liquid2 后补拍的站点画面，`game=null`，不计任何玩法时长；016 的跨导航像素差不用于因果判断。

日志整理移除了非游戏辅助 iframe 的 DOM 文本及挑战/分析标识路径，避免归档无关脚本；操作、时间、错误、官方游戏界面文本与截图哈希不改写。处理前后哈希、删减数量见 [evidence-audit.json](evidence-audit.json)，整理脚本见 [finalize-evidence.cjs](finalize-evidence.cjs)。没有保存游戏源码、抽取商业素材或网页资源包。

2026-10-21 **10:21:33.934 UTC / 18:21:33.934 北京时间**：关闭浏览器后删除本目录 `runtime/`，日志 `runtime_cleanup.removed=true`；后续再次检查目录不存在。截图中的游戏与站点内容属于第三方研究证据，不是自有资产，不进入生产素材清单。未注册、上传、发消息、联系发行商或提交作品。
