# G04 浏览器补证局部状态

更新日：2026-10-21。**PARTIAL**；仅研究补证，非施工或发布批准。本文件只覆盖 `research/playthroughs/G04/`。

已核实：三款 Coolmath 官方 URL；25 组浏览器输入派发；Paint Master 核心画笔变色/扣步、LEVEL 1→2、故意错误重复直到 GAME OVER、End Game/结算/菜单/START 重开与重开后有效画笔。64 张截图 SHA-256 核验通过。浏览器关闭，runtime/profile 已清理。

阻塞：Bloxorz 加载区域无确认游戏响应，getContext 错误根因 UNKNOWN；Liquid2 本浏览器可见不可玩提示。两款胜负/重试均 NOT_OBSERVED。Paint Master 为离散截图观察，完整连续首 30 秒/5 分钟、后续关卡、撤销/提示/广告补步兑现、触屏/性能/受众数据均缺失。

边界偏差：Bloxorz 最后主动输入后截图在导航后 88.458 秒，但证据阅读期间页面继续驻留，224.509 秒才行政结束；3 条误用 `cmd` 的命令被拒绝，无新增游戏输入。全部保留在报告与日志，不以驻留时间冒充实玩。

下一动作仅供后续研究：在另一次有边界的正常浏览器环境补 Bloxorz 核心输入与失败重试，或取得有权访问的可运行 Liquid2 环境；为 Paint Master 连续记录首 30 秒/5 分钟并检验更多关卡。当前不继续排障、不等待其他 agent、不改 games/benchmarks 或根数据。P0 可直接引用 [observation.md](observation.md) 的已观察证据和限制。
