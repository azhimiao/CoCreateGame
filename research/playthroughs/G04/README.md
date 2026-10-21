# G04 浏览器实证包

访问日 2026-10-21；总状态 **PARTIAL**。先读 [observation.md](observation.md)。Paint Master 有核心输入/单关完成/故意失败/重新开局后的响应；Bloxorz 与 Liquid2 为 BLOCKED。没有连续 30 秒或 5 分钟完整实玩记录。

本目录是研究证据，不是游戏实现、完整 benchmark、施工档案或构建准许。只允许在此目录追加；不修改 `games/`、`benchmarks/`、根状态和项目注册数据。

| 文件/目录 | 内容 |
| --- | --- |
| `observation.md` | 结论、时长口径、直接观察、具体对照、UNKNOWN 与边界执行偏差 |
| `operation-log.md` | 操作时间、输入和截图编号的人工阅读索引 |
| `official-sources.json` | 三款官方 URL 的核查方式、日期、类型与未知项 |
| `browser-session.cjs` | 本次实际运行的交互式 Playwright 记录器 |
| `operations.jsonl` | 已做最小删减处理的操作与诊断日志；非游戏辅助 DOM 不保留 |
| `finalize-evidence.cjs` | 浏览器关闭后的日志删减、截图哈希检查与索引生成 |
| `evidence-audit.json` | 状态、输入计数、处理前后日志哈希、截图核验、清理结果 |
| `screenshots/` | 64 张研究截图；`manifest.json` 为逐文件清单/尺寸/哈希 |
| `STATUS.md` | 本目录局部进度、阻塞与后续证据需求 |
| `runtime/` | **已清理，不随证据交付**；仅重跑时生成的 profile/cache |

## 运行与命令

前置：本机 Node；`F:/beautiful/node_modules/playwright-core` 和 `pngjs`；`%LOCALAPPDATA%/ms-playwright/chromium_headless_shell-1228/chrome-headless-shell-win64/chrome-headless-shell.exe`。安装目录编号与实际浏览器版本不是同一个量纲；本次版本 149.0.7827.55。无需登录。

从仓库根目录运行：

```powershell
node research/playthroughs/G04/browser-session.cjs
```

之后向标准输入逐行发送 JSON；命令键为 **`op`**：

```json
{"op":"navigate","game":"paintmaster"}
{"op":"shot","label":"inspect-current-ui"}
{"op":"inspect"}
{"op":"click-text","text":"PLAY","frame_url_contains":"/public_games/56412/","settle_ms":1200}
{"op":"click","x":489,"y":626,"settle_ms":900}
{"op":"finish","status":"PARTIAL","summary":"Write the observed outcome and remaining gaps"}
{"op":"close"}
```

示例坐标不是无条件重放方案；先查看当时 UI 再输入。`navigate` 仅支持 `bloxorz`、`liquid2`、`paintmaster` 三个官方页。`key`、`hold`、`scroll`、`note` 也有支持；坐标按全视口 CSS 像素记录。`confirm-input` 只能在人工对比截图确认核心游戏响应后使用，需传 `evidence` 数组与 `description`；标记本身不是时长证据。

记录器从导航起约 180 秒后拒绝进一步排障输入；确认有效输入后约 300 秒后拒绝进一步观察输入。它在收到命令时检查预算，**没有后台强制退出计时器**，所以必须主动按实际首次有效输入时间结束，不能把浏览器驻留/读图时间充作实玩。`finish` 和 `close` 不受该闸门阻止。Bloxorz 本次行政结束延迟与误用 `cmd` 的错误已在观察报告中保留。

使用 `close` 或 Ctrl+C 关闭 context 后，脚本验证路径并只清理本目录的 `runtime/`。不要并行启动多个记录器争用同一 profile。待进程退出、runtime 不存在后执行：

```powershell
node research/playthroughs/G04/finalize-evidence.cjs
```

整理脚本保留事件与输入序列，省略非游戏辅助 iframe DOM 和部分挑战/分析路径，并核验每张截图哈希。现有 `operations.jsonl` 已整理过，交付后不要为“检查”重复整理，否则处理前哈希会指向已整理日志；重新运行应作为新的研究会话另行审计。记录器自身会追加日志并使用会话前缀命名截图，不会覆盖旧 PNG。

截图保留第三方可见内容，仅作研究佐证；没有游戏源码、提取的图像/音乐包、账号或 cookies。64 张 PNG 包含重复画面，用于证明输入派发前后未变化或追踪失败路径；关键帧链接见报告，其余逐文件索引见 manifest。网络诊断中的失败请求不等于游戏根因或平台故障。
