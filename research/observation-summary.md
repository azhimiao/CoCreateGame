# 实际操作证据汇总

2026-10-21，Asia/Shanghai。这里合并不同研究员的观察边界；不能把后补局部操作算成完整定时回放。

| 作品/渠道 | 本次取得 | 明确没有取得 | 原始依据 |
|---|---|---|---|
| Drive Mad / P03 | 核心驾驶输入与车辆画面变化的局部观察 | 完整连续首30秒/5分钟、胜败重试全链、手机性能 | `benchmarks/evidence/session.json`及对应截图 |
| Paint Master / P01 | 14次核心画笔输入、一次单关完成、故意耗尽步数失败、重新开局和再次有效操作 | 从首次可操作开始连续30秒/5分钟、全部后期规则、真机 | `playthroughs/G04/observation.md`、operations.jsonl及64张截图的hash |
| Level Devil / P03 | 页面、菜单/入口与输入尝试 | 未确证完整核心游玩，不把菜单截图当游戏流程 | `benchmarks/evidence/session.json` |
| Bloxorz、Liquid2 / P01 | 官方页、加载/输入尝试及受阻记录 | 未确认核心输入生效，不给“已实玩”标签 | `playthroughs/G04/observation.md` |
| Arrow Puzzle / P04、Arrow Escape / P02 | Arrow Puzzle教学棋盘、三颗心及实际点击/微拖尝试；Arrow Escape重定向分类页 | 未确认箭头移除/扣心、胜败/游戏重开；没有完整连续时间窗 | `playthroughs/G01/observation.md`、operations.jsonl及21张截图 |
| Good Sort Master / P04、Screw Out / P02 | Good Sort入口及前置加载；Screw Out末帧Level 1棋盘，站点隐私弹窗正常关闭 | 核心操作派发为0；未确认匹配、暂存满、胜败、游戏重试及完整时间窗 | `playthroughs/G02/observation.md`、operations.jsonl及13张截图 |
| 其余对标 | 官方具名页/教学说明；12份按规则重建的分析 | 本次实际定时操作、隐藏数值、真实留存和收入 | `benchmarks/benchmarks.json`及各Pxx.md |

作品库的summary是该批研究记录的快照；Paint Master的后补结果保存在独立目录，未回写为原研究员当时已经观察。全项目当前仍为 **0份完整连续首30秒/5分钟试玩**。14次点击和驻留分钟数不能替代定时有效游玩。

G04补证能支持Paint Master公开规则中覆盖、步数耗尽、单关推进和重开的局部真实性，不能证明G04原创层间机关好玩，也不能把Bloxorz/Liquid2的操作缺口自动关闭。G01/G02对标的直接核心状态轨迹仍缺。

查看详细：[G01访问与输入尝试](playthroughs/G01/observation.md)、[G02访问与加载](playthroughs/G02/observation.md)、[G04实际操作报告](playthroughs/G04/observation.md)、[G04操作记录](playthroughs/G04/operation-log.md)、[作品研究方法](benchmarks/methodology.md)。三批后补合计98张截图，逐文件hash保存并纳入总体验证。截图仅为研究证据，不是可复用产品素材；原运行缓存/raw抓取文本不进入最终交付ZIP。
