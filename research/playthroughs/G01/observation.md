# G01 实际访问与输入补证｜2026-10-21

**结论：PARTIAL_TUTORIAL_VISIBLE_INPUT_UNCONFIRMED。** Playgama Arrow Puzzle 已实际显示教学箭头、三颗心和“Tap to release”；普通鼠标点击/小幅拖动后，没有取得可确认的箭头移除、扣心、胜利、失败或重试前后对照。CrazyGames Arrow Escape: Puzzle 的官方原URL在本次浏览器访问中转到分类页。本轮补充了实际加载/输入尝试证据，**尚未补齐G01核心规则的直接验证缺口**，不提升施工状态。

只写本目录。benchmarks历史快照、games和reviews均未修改；没有下载/安装、注册、付费、绕过访问控制、注入游戏状态或保存游戏代码。本文中的“重试点击”仅指再次发送鼠标事件，不代表触发游戏重开。

## URL、日期与版本

| 平台/作品 | 请求的精确官方URL | 本次浏览器最终URL | 日期与口径 |
|---|---|---|---|
| P04 Arrow Puzzle / Green Train | https://playgama.com/game/arrow-puzzle | https://playgama.com/game/arrow-puzzle | accessed_at=2026-10-21；页面发布日期UNKNOWN；官网列渠道发行2026-04、更新2026-06，不是本次构建号 |
| P02 Arrow Escape: Puzzle | https://www.crazygames.com/it/game/arrow-escape-puzzle | https://www.crazygames.com/it/t/brain | accessed_at=2026-10-21；页面发布日期UNKNOWN；本次未进入该作品，不能确认游戏当前版本 |

两个URL均用web工具重新访问；Playgama的教学文字仍可读取，CrazyGames的web访问与本机浏览器均落在分类页。此结果仅是这次访问事实，不足以认定作品全球下架或平台普遍不可用。浏览器记录的HTTP 200也可能对应最终分类页，不表示原游戏加载成功。

官方文字（SECONDARY_DESCRIPTION）：Playgama说明箭头前方无阻挡时点击移除，受阻时扣生命，清空棋盘通关。本轮只直接看见教学UI，**没有直接验证上述三条规则**。指标口径是单机单次页面可达性、可见UI和输入响应，不是用户量、通过率、性能基准或商业收益。来源信息另见[sources.json](sources.json)。

## 已观察／未观察逐节点表

时间为UTC，均在2026-10-21；北京时间=UTC+8。编号指截图文件前缀，操作的精确起止、坐标、按下时长和SHA-256见[operations.jsonl](operations.jsonl)。状态针对直接证据，不用官网说明补成亲测。

| 节点 | 状态 | 证据与实际可见结果 | 仍未知 |
|---|---|---|---|
| 平台入口与作品归属 | OBSERVED | 10:39:03，[01](screenshots/01-playgama-loaded.png)显示Arrow Puzzle及Play Now；最终URL未离开Playgama作品页 | 具体部署构建号、全球可用性 |
| 启动／广告加载 | OBSERVED | 10:39:29，[02](screenshots/02-playgama-play-click.png)为黑底Close Ad倒计时；第二会话[14](screenshots/14-held-tutorial-click.png)可见广告创意与Close Ad | 首次黑屏阶段是否完整播放了视频/音频、正常用户广告频次 |
| 关闭广告入口 | OBSERVED | 10:44:15—17，普通点击屏幕(781,576)，[15](screenshots/15-close-ad-button.png)回到游戏教学画面 | 其他广告是否相同流程；不据此认定游戏内激励广告规则 |
| 不登录继续 | OBSERVED_UI_TRANSITION | [03](screenshots/03-playgama-current.png)有保存进度登录条；点击Continue playing后，[05](screenshots/05-continue-without-login.png)登录条消失、三颗心可见 | 是否存档、跨会话进度是否保留 |
| 教学首屏 | OBSERVED | 10:40:13首次留存[03](screenshots/03-playgama-current.png)：三条直箭头、手指提示、Tap to release；[05](screenshots/05-continue-without-login.png)明确显示三颗红心 | 是否是实际首个可操作帧；教程限制、命中判定 |
| 核心鼠标输入尝试 | INPUT_SENT_RESULT_UNCONFIRMED | 第一会话点击(634,430)/(586,470)及微拖；第二会话[16](screenshots/16-resume-without-login.png)→[17](screenshots/17-held-game-arrow.png)在(634,430)按下700ms后仍见同一教学结构 | 输入是否由游戏接收、是否被覆盖层/教程/环境拦截，原因UNKNOWN |
| 无阻挡箭头合法移除 | NOT_OBSERVED | [05](screenshots/05-continue-without-login.png)→[06](screenshots/06-tutorial-release-retry.png)、[16](screenshots/16-resume-without-login.png)→[17](screenshots/17-held-game-arrow.png)、[19](screenshots/19-fullscreen-ui.png)→[20](screenshots/20-inline-arrow-click.png)均未形成可确认箭头数量变化 | 移除规则、动画时序、边界出界语义UNKNOWN；没有变化不等于非法移动 |
| 受阻箭头非法移动／扣心 | NOT_OBSERVED | 没有进入可核查的相互阻挡局面；留存的可见游戏帧仍是三颗心 | 是否扣心、具体扣几颗、碰撞回退、重复点击惩罚、无效输入分类UNKNOWN |
| 单关成功／过关反馈 | NOT_OBSERVED | 未见清空棋盘、成功面板或下一关 | 胜利触发条件/奖励/自动转场UNKNOWN |
| 失败／生命耗尽 | NOT_OBSERVED | 未见红心减少、失败面板或结束状态 | 失败阈值、可恢复/不可恢复状态UNKNOWN |
| 游戏内重试／重开 | NOT_OBSERVED | 没有进入游戏失败/重开按钮；仅正常关闭后重访同一URL | 重开是否重置棋盘、生命或消耗UNKNOWN；重访网页不能当作游戏重试 |
| 显示模式变化 | OBSERVED | 10:44:46点击底栏显示按钮，[19](screenshots/19-fullscreen-ui.png)从大画布切回站点内小画布；[20](screenshots/20-inline-arrow-click.png)按新坐标点击仍无确认规则变化 | 不能因此确定前次无响应是缩放或坐标问题 |
| CrazyGames备选入口 | OBSERVED_REDIRECT_ONLY | 10:45:55，[21](screenshots/21-crazygames-url-result.png)显示意大利语分类标题；最终URL为/it/t/brain | 原游戏可玩性、规则与输入全部UNKNOWN；未尝试域名外镜像或绕过重定向 |
| 连续首次30秒 | NOT_COVERED | 只有离散操作和截图，没有从首次可操作时刻开始的连续录像/完整连续观察 | 起点UNKNOWN；不能把会话持续超过30秒算覆盖 |
| 连续首次5分钟 | NOT_COVERED | 两会话之间有正常关闭重启；没有连续有效玩法轨迹 | UNKNOWN；不能把总尝试7分多钟算首5分钟 |

## 尝试时限与输入记录解释

第一条环境记录10:38:35.952，最后正常关闭10:45:56.204，共440.252秒（7分20.252秒，包含看图、工具开销和重开），低于8分钟。第一会话10:42:58.614正常关闭；第二会话10:43:00.937建立。`elapsed_s`在每次脚本启动时重置，跨会话排序用UTC，不能直接相加当连续玩法时长。

共21张截图、21条成功采集的操作记录、1条操作错误。第一会话Close Ad精确文本点击超时只证明当时定位器没有找到匹配，不证明广告被禁止关闭；第二会话使用实际可见关闭按钮正常返回游戏。14号截图采集时仍为广告，尽管文件名含tutorial，也不当成游戏输入证据。13号同理。06的retry只是重复点击，不是游戏重试。

第一会话默认短点击和无停顿小幅拖动；第二会话普通点击显式按下180—700ms。最终保留的browser-observe.cjs是第二会话版本，其固定截止时间属于这次历史运行，不能把它描述成第一会话逐字源文件或之后可直接复跑的通用工具。修改仅涉及研究采集脚本，未修改网页/游戏。

## 设备、观测与隐私限制

Windows本机，Chromium 149.0.7827.55，headless，viewport1365×900、deviceScaleFactor=1，locale=en-US，鼠标输入，不模拟触屏。借用已有 `F:/beautiful/node_modules/playwright-core` 和本机缓存Chromium，未修改F:\beautiful。请求SwiftShader软件渲染；实际GPU、FPS、CPU/内存性能UNKNOWN，不能外推真机体验。

第二会话读取到官方页面自行加载的游戏iframe以及canvas可见包围盒；只读取URL和DOM元数据，不执行游戏状态脚本。第一会话只检查前12个iframe，遗漏了游戏iframe，因此日志的canvas=[]是**采集范围限制，不能当没有画布/游戏未加载的证明**。第二会话修正为检查主frame和可见的游戏域frame。

日志不存cookies/storage/网络响应正文/游戏源码；广告iframe URL去掉query和fragment，游戏入口请求与最终页面URL完整保存。广告创意只作为页面访问证据，不作为G01对标玩法。没有录音、录像、移动真机或完整游戏回放。无响应原因未定位，不把它归因于平台禁止自动化、广告阻断、错误点击或具体规则。

自拟下一动作（HYPOTHESIS，未实施）：若后续获准再试，优先用可见桌面交互或另一真实设备核查输入命中，再取得一对合法移除、受阻扣心、生命耗尽和重开的连续证据；不要把这些预期写入本次已观察字段。

## 文件、哈希与打包

[operations.jsonl](operations.jsonl)保留命令及各PNG的SHA-256；[screenshot_hashes.json](screenshot_hashes.json)逐项复核；[validation.json](validation.json)记录自校验；[delivery_manifest.json](delivery_manifest.json)是含文件大小和SHA-256的交付白名单。文件名是采集标签，结论以可见画面、逐节点表和原始命令为准。

两个浏览器context均await close且脚本进程exit_code=0；关闭后未发现本次脚本或使用本目录profile的Chromium进程。**runtime/保存本机临时profile/cache/tmp，保留在本机但不属于交付；打包必须排除runtime/及全部子项，不得递归打包整个G01目录。** 排除与进程检查见[cleanup.json](cleanup.json)。截图、日志、脚本保留，不将自动生成的session cookies/cache放入交付包。
