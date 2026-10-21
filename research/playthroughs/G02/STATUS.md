# G02 本目录补证状态

更新日：2026-10-21。**BLOCKED_CORE_BEHAVIOR**；尝试已在约八分钟总预算内结束，只写 `research/playthroughs/G02/`。

已核实：原快照两款官方 URL；Good Sort Master 的 Ignore/Play Now 入口变化；Screw Out 的 Only Essential 正常关闭弹窗、加载阶段以及末帧 Level 1 棋盘。实际派发 3 次 UI 输入；13 张截图 SHA-256 通过；benchmarks 原快照哈希不变；两次 browser context 正常 close，runtime 已清理。

未核实/阻塞：核心游戏输入 0 次确认；合法/非法放置或拆取、匹配、暂存占满与满后再拆、成功、失败、游戏内重试均缺证。Screw Out 棋盘出现时总尝试已到 462.695 秒，读图期间 480 秒截止触发；拟发送的螺丝点击没有派发日志，未计入观察。Good Sort Master 后续截图超时，不能推断整段停留于相同画面。阻塞根因 UNKNOWN。

没有连续首 30 秒/5 分钟实玩、手机真机、正常玩家样本或收益数据。单次运行阻塞不是游戏规则失败或商业失败。现有 G02 文档审计问题由其作者处理，本目录不替代修订、不更改 games/reviews/benchmarks。

下一研究边界：另次授权后，为能显示棋盘的 Screw Out 单独取得核心操作前后证据，再验证暂存满的争议边界和失败重试。本轮不继续、不等待其他 agent、不将未知项标为已验证规格。可引用 [observation.md](observation.md) 与 [outcome-assessment.json](outcome-assessment.json) 的有限结论。
