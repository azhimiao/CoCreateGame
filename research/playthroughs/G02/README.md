# G02 有边界浏览器补证包

访问日 2026-10-21。总状态 **BLOCKED_CORE_BEHAVIOR**；有边界的尝试已完成。先读 [observation.md](observation.md) 的逐节点覆盖表。

Good Sort Master 到达前置加载层，未确认棋盘。Screw Out 在末帧显示 Level 1 棋盘，八分钟总预算随后正常关闭浏览器；未派发任何核心操作。3 次实际输入都是站点 UI。无连续首 30 秒/5 分钟记录，不声称合法/非法放置拆取、匹配、暂存满、胜败或游戏重试已验证。

| 文件/目录 | 用途 |
| --- | --- |
| `observation.md` | 节点覆盖、截图链、八分钟口径、UNKNOWN、环境与后续缺口 |
| `operations.jsonl` | 真实事件/派发操作/截图哈希/错误/正常 close；辅助元数据已删减 |
| `operation-log.md` | 实际派发的 3 次 UI 输入前后截图索引 |
| `screenshots/` | 13 张第三方研究 PNG；`manifest.json` 为哈希与时间清单 |
| `device.json` | 桌面 headless / 版本 / 视口 / 软件渲染 / 非移动测试限制 |
| `official-sources.json` | 原 benchmarks 关联、官方 URL、描述与未核实项 |
| `outcome-assessment.json` | 浏览器关闭后的最终节点评估，不是伪造实时事件 |
| `evidence-audit.json` | 原快照不变、截图哈希、日志整理及 runtime 清理核验 |
| `browser-session.cjs` | 两次会话使用的输入/截图记录器，支持 drag，但本次未实际执行 drag |
| `finalize-evidence.cjs` | 正常关闭后的一次性日志删减与清单生成 |
| `STATUS.md` | 本目录局部状态，不改根 STATUS |
| `.gitignore` | 排除 task-local `runtime/`；本次 runtime 已清理 |

## 审阅与复现

依赖沿用现有 `F:/beautiful/node_modules/playwright-core`、`pngjs`，浏览器 executable 位于 `%LOCALAPPDATA%/ms-playwright/chromium_headless_shell-1228/chrome-headless-shell-win64/chrome-headless-shell.exe`。无需安装、注册或付费。仅在本目录写证据与临时 profile。

```powershell
node research/playthroughs/G02/browser-session.cjs
```

交互命令使用 `op`，逐行 JSON。例如：

```json
{"op":"navigate","game":"screwout"}
{"op":"shot","label":"visible-ui-check"}
{"op":"inspect"}
{"op":"finish","status":"BLOCKED","summary":"Describe verified observations and unknowns"}
{"op":"close"}
```

仅 `goodsort`、`screwout` 的官方 URL 可以导航。`click`、`click-text`、`drag`、`key`、`scroll` 派发真实浏览器输入；先看界面再选择坐标。`confirm-input` 要求截图路径和人工描述，仅用于确认核心响应，不生成连续时长证据。DOM 检查仅读可见界面文本与几何，不读游戏内部状态或源码，不修改页面。

最终脚本从 `operations.jsonl` 中**首次 navigation_start** 读取总预算起点，重启浏览器仍沿用八分钟截止；截止使用 `context.close()`，不会强杀浏览器进程。初始会话使用同样的 480000ms 计时；在重启前补上从日志恢复起点的逻辑，避免重置预算。当前证据包已经耗尽该窗口，直接重跑会按旧截止退出；不得为复现悄悄清空本次日志或更改证据。后续会话应先获得新的研究边界并独立保留会话来源。

两次正常 close 都在本目录 `runtime/` 做路径验证后清理；禁止并行争用同一 profile。`finalize-evidence.cjs` 已执行一次，交付后不要为检查重复执行，否则处理前哈希会变成已处理日志。用 manifest 或审计 JSON 验证即可。

失败请求与 canvas 存在都不能证明核心输入生效；加载和读图时间不算实玩。截图及站点游戏文字仅作研究佐证，不是取得商业源码/素材/许可。
