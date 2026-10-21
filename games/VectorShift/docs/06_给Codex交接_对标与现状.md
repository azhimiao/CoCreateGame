# 给 Codex 的交接｜对标产品是谁 · 我们产品在哪

> 日期：2026-10-21（Asia/Shanghai）  
> 仓库：`/workspace/game-review/Vector_Shift_v02`  
> 当前试玩包：`delivery/Vector_Shift_playtest.zip`（标注 V0.8.1-dense-mid）  
> 本文只陈述事实与差距，供 Codex 接手工程；**不要复制竞品美术/关卡/商标**。

> **历史快照提示（2026-10-21）**：本文的“当前缺少”状态记录于实现前，随后用户单独授权把 Vector Shift 作为 `games/VectorShift/` 独立项目完成。缩放、全出口指引、每日结算、局内续玩与自动化浏览器验证现已实现；详见 `docs/07_2026-10-21_implementation-update.md`。真人盲测、真机、商标和平台审核仍未完成。

---

## 1. 对标产品（说清楚「对的是谁」）

品类：**蛇形/长箭头滑出解谜**（tap arrow/snake → slide off board when path clear）。  
原子规则公开、可同品类，差异靠形状、密度、质感、难度节奏、运营壳、变现。

| 优先级 | 产品 | 厂商 | 入口 | 量级（商店公开） | 为什么对标 |
|---|---|---|---|---|---|
| **P0 视觉/手感** | Snake Arrows Puzzles Escape | 8Great Games | iOS `id6757818523`；Android `com.eightgreatgames.snakearrowsescapepuzzleout` | iOS ~4.6★ | **长管状彩色蛇、眼睛、几乎铺满、Hint+、缩放、3 心** —— 用户反复说「要这个质感」 |
| **P0 视觉/手感** | Snake Arrow : Puzzle Escape | Tech X Solution | Play `com.snake.arrow.puzzle.game` | 50K+；~4.7★ | 异形剪影、长蛇、3 心+金币、手指教程+绿出路；商店写无惩罚但截图有心 |
| **P0 形状/结算** | Arrow Out: Arrow Escape Puzzle | AppBurst | Play `com.appburst.arrowout` | 小体量但截图优质 | **心形等异形盘**、挡住弹回扣心、Daily **CLEARED + streak + TIME/MISSES/HINTS + Share** |
| **P1 品类头部（短箭头）** | Arrow Puzzle | Easybrain | `com.easybrain.arrow.puzzle.game` | **50M+** | 3 心、关间广告、Remove Ads、Hint；规则同品类但多为短箭头 |
| **P1 品类头部（长箭头）** | Arrows – Puzzle Escape | Lessmore | iOS `id6748397500`；`com.ecffri.arrows` | iOS 评分极高 | 长箭头、生命/补心、去广告、Daily 奖杯 |
| **P1 中文爆款** | Amaze GO!™ 箭头解谜 | Oakever | `com.oakever.arrows` | **1亿+** | 中文市场心智；长按指导等 |
| **P2** | Tap Escape / Arrow Out Puzzle（Pixel King）等 | 多家 | 见 `docs/竞品流程对照.md` | 不一 | 同循环变体；Pixel King 偏线稿+计时，**不是**我们要的彩色长蛇 |
| **P2 CN** | 箭头-逃脱大师 等 | 见 CN App Store | `artifacts/competitors/cn_*.png` | 小 | 3 心、Hint、Undo、主题关名 |

### 竞品共有玩家流程（截图+商店可证实部分）

```
开局 → 观察密盘长蛇 → 点畅通者滑出（绿/出路提示）
     → 堵住：弹回 + 常扣 1 心
     → 清空 → 结算壳（下一关 / Daily streak / 分享）
卡住：Hint（常带 + 广告或金币）/ Undo / Restart / 有时 Zoom
```

### 本地截图证据（必看）

目录：`artifacts/competitors/`

| 文件 | 看什么 |
|---|---|
| `snake_arrows_ios_ss2.png` | **质感标杆**：长弯管、眼睛、近满盘、3 心、Hint+、缩放 |
| `snake_arrow_ss3.png` | 教程手势 + 绿出路 + 3 心 + 金币 + 异形剪影 |
| `arrow_out_ss1.png` | 心形盘 + 长折线滑出边缘 |
| `arrow_out_ss4.png` | Daily 结算：CLEARED、streak、统计、Share |
| `cn_ss1.png` | 主题关 + 3 心 + Hint/Undo |

详细流程表：`docs/竞品流程对照.md`（含缺口与优先 5 项）  
形状/密度/复用策略：`docs/竞争力-形状密度难度复用.md`

---

## 2. 我们的产品：Vector Shift（现状说清楚）

### 2.1 一句话

离线 HTML5 解谜：**多格蛇/箭头滑出**；**蓝色相位群旋转**（蓝蛇随相位绕头顺时针 90° + 朝向 +1）是 USP；金色固定。目标渠道曾规划 Coolmath / CrazyGames（构建已分 channel）。

### 2.2 代码与数据位置

| 路径 | 内容 |
|---|---|
| `src/game-core.js` | 规则：相位、遮罩 mask、虚空出界、求解/校验 |
| `src/app.js` | UI、SVG 长管渲染（描边高光+眼睛）、滑出/阻挡 |
| `src/styles.css` | 休闲风壳，非 SaaS 顶栏 |
| `src/generate_levels.py` | 生成器 v7：形状模板 + 密度/覆盖门控 |
| `src/build.py` | demo / coolmath / crazygames-basic |
| `data/levels.json` | **52 关** |
| `tests/core.test.cjs` | 必过 |
| `delivery/Vector_Shift_playtest.zip` | 给玩家/策划的试玩包 |
| `artifacts/*.png` | 我方最新自检截图 |
| `index.html` | 构建产物入口 |

原始交接时的 BUILD 字符串曾为 `0.7.0-shape`；此值与本次实施前的关卡说明均为历史快照。当前版本见根目录 `manifest.json`、`README.md` 与 `docs/07_2026-10-21_implementation-update.md`。

### 2.3 已实现（相对竞品）

| 维度 | Vector Shift 现状 |
|---|---|
| 核心循环 | 点畅通蛇滑出；堵则红闪/抖动；**不扣心** |
| USP | **蓝色相位旋转**（竞品表中基本没有） |
| 棋盘形状 | mask：square / plus / diamond / heart / ring / blob / letter_t / letter_c；出界=滑入虚空 |
| 关卡量 | 52；约 **30/52 非方盘**；L10+ 多数异形 |
| 密度 | L1 教学疏；L20 **~88%**；后期长管 fill 高 |
| 蛇长 | 中后期常见 5–12 格弯管；教学仍短 |
| 渲染 | 粗管 + 描边 + 高光 + 三角头 + **卡通眼**（用户仍认为逊于 8Great） |
| 辅助 | 撤销 / 重开 / 提示（目前偏**免费无限**）/ 悬停出路预览 |
| 每日 | 本地日期种子有；**无 streak / 奖杯壳** |
| 变现 | **无广告、无 IAP、无去广告漏斗** |
| 生命 | **无** |
| 缩放 / Visualizer | **无**（仅射线预览） |
| 结算页 | 弱（最短解文案）；**无 CLEARED 大结算 + Share** |
| 语言 | 中英 UI 字符串 |
| 测试 | `node tests/core.test.cjs` PASS；smoke 有桌面/移动/coolmath |

### 2.4 关键自检截图（我方）

| 文件 | 内容 |
|---|---|
| `artifacts/level20.png` | 方盘密铺长管（补密度后） |
| `artifacts/shape_heart.png` | 心形 + 长管 |
| `artifacts/square_dense_long.png` | 终章长管 |
| `artifacts/competitors/snake_arrows_ios_ss2.png` | 并排放对照用 |

### 2.5 用户（Hazel）已明确的不满

1. 「不是一个水准」— 早期细线/短胶囊像演示站  
2. 「换形状、密度、美观、难度、复用」才有竞争力，**同逻辑不够**  
3. 「质感太糟糕，也不是长箭头」— 必须长管玩具感，且要用截屏自检  
4. 当前交付仍承认：**颜色跳度、满盘程度、HUD 品类语言（3 心）不及 8Great**

---

## 3. 差距清单（Codex 可当 backlog）

按转化/观感优先级（与 `竞品流程对照.md` §6 对齐，并加上用户强调的内容竞争力）：

| # | 差距 | 竞品怎么做 | VS 现在 | 建议 |
|---|---|---|---|---|
| 1 | **长蛇管状质感** | 8Great 近满盘、管状高光、眼睛、多色 | 有管+眼，仍偏「SVG 描边游戏」 | 继续逼近参考图；可考虑 per-cell mesh / 更好渐变 / 更多色相 |
| 2 | **异形剪影质量** | 心/树/超轮廓「蛇拼成蛇」 | 有几何 mask，轮廓偏「缺格方盘」 | 更平滑的主题剪影；商店级造型 |
| 3 | **密度与蛇长节奏** | 中后期几乎无空洞 | L20 已 ~88%；小 mask 仍易出短蛇 | 门控：minAvgLen、maxEmptyBlob、spread |
| 4 | **难度曲线可感** | 交错深度 + 心 + 提示代价 | 主要靠 fill + 相位次数 | 度量：首次可移数、出口竞争、强制相位次数 |
| 5 | **复用** | 主题包、换皮、Daily 种子 | 生成器有 shape 模板，缺主题/皮肤管线 | 轮廓×配色×朝向镜像 打包 |
| 6 | 过关结算壳 | CLEARED / streak / Share | 弱 | 结算页 + 下一关主按钮 |
| 7 | 3 心或失误语言 | 标配 HUD | 无 | 可选生命 / 失误徽章（保留禅模式） |
| 8 | Hint 有限 + 激励位 | Hint+ | 无限免费 | UI 先做次数，Web 可灰「商店版」 |
| 9 | Zoom + 全方向可视化 | 8Great / Amaze | 无 | 密集盘防误触 |
| 10 | 相位教学不破坏美观 | — | 有 coach | 保持 USP，勿被生命/广告冲掉前 3 关教学 |

---

## 4. 硬约束（给 Codex）

1. **保留相位 USP**（蓝绕头旋转 + 朝向变化；金固定）。  
2. **碰撞/可解性只认 `game-core`**，动画不能改判定。  
3. 改关卡后必须 `node tests/core.test.cjs` PASS，再 `python3 src/build.py`。  
4. 不抄竞品资产；参考仅限公开商店图与本文描述。  
5. Coolmath 构建继续无外链/遥测；CrazyGames 仅 GameplayStart 级。  
6. 用户要「截屏自检」：改视觉后必须更新 `artifacts/` 并与 `competitors/` 并排看，再交包。

---

## 5. 建议 Codex 下一刀（若只做一件）

**视觉+关卡：逼近 `snake_arrows_ios_ss2.png` 的长管满盘观感**（色相更跳、空格更少、头脸更「玩具」），同时保持相位与 mask。  
流程壳（3 心 / 结算 / Hint+）可并行，但用户最近火的是**质感与长箭头**，先过这一关再堆商业 HUD。

---

## 6. 相关文档索引

- `docs/竞品流程对照.md` — 10 款流程 A–H、总表、缺口  
- `docs/竞争力-形状密度难度复用.md` — 形状/密度/难度指标/复用 P0–P2  
- `docs/01_机制与对标边界.md` — 机制规格（部分段落已过时：关卡数/每日/渲染；**以本文件与代码为准**）  
- `delivery/PLAYTEST.md` — 当前包验收点  

*交接文档结束*
