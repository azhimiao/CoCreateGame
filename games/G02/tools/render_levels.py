"""Render the exact original level data as a human-readable construction table."""
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
spec = json.loads((root / "game-spec.json").read_text(encoding="utf-8"))
lines = ["# G02 前20关、经济与可解性", "",
"2026-10-21｜所有关卡和目标时长为 **HYPOTHESIS 原创设计**。game-spec.json 是机器可读源，本表由 tools/render_levels.py 导出；不是对标关卡转录。", "",
"## 1. 读表与全局胜利条件", "",
"每个初态 `Tn:底→顶/容量/接收集合/开锁所需章/可封`。`-`为空堆栈或无锁，`是/否`为sealable。所有初态都未封箱。所有层可见；一次MOVE仅一件。每关胜利为列出的颜色各封一次且全台无物件；只有配齐不封不能赢。锁采用AND，封箱退出该盘。", "",
"合法解是数组顺序执行的前进动作：`T0>T2`等价于 `move(src=T0,dst=T2)`；`封T1`等价于 `seal(at=T1)`。JSON中保存完整对象，不依赖中文缩写。par为BFS最短前进动作数，包含封箱，不包含选中/取消/动画/撤销。", "",
"## 2. 具体施工表", "",
"| 关卡/变体 | 教学决策 | 需求/胜利颜色 | 原创初态 | 一条完整合法最短解 | par / 目标秒（假设） |",
"|---|---|---|---|---|---|"]
for level in spec["levels"]:
    trays = []
    for t in level["containers"]:
        trays.append(f"{t['id']}:{''.join(t['items']) or '-'}/{t['capacity']}/{''.join(t['accepts'])}/{''.join(t['unlock_after']) or '-'}/{'是' if t['sealable'] else '否'}")
    solution = [a['src']+'>'+a['dst'] if a['op']=='move' else '封'+a['at'] for a in level['solution']]
    demands = ','.join(f"{c}×{v}" for c,v in level['demand'].items())
    lines.append(f"| {level['id']} {level['name']} / {level['variant']} | {level['intent']} | {demands}；封{''.join(level['demand'])} | {'；'.join(trays)} | {'，'.join(solution)} | {level['par_actions']} / {level['target_seconds']} |")
lines += ["", "## 3. 教学与难度解释", "",
"L01单类入箱，L02交叉双类，L03三类闭环，L04逐件三层，L05双缓冲；L06—10逐一展示锁内现成箱、锁内单件、同时开两柜、锁空位、三层解锁；L11—15展示单签、双签、不能封箱的容量1浅盘、多层双路、四色环；L16—20组合两机制、AND双章与三层多类。L13的T3是容量1且不可封的浅盘，必须画浅盘标记。L09锁空盘T4与L13浅盘T3均为可选展示：已给最短解不引用它们，删除该盘后原序列仍合法获胜；不能以完成这两关证明掌握锁空位或浅盘不可封。", "",
"最短步数不保证体验难度递增：L04比L03短，但每种需求更多；L09与L03结构相近是锁空位的单因子对照，L11与L02是接收标签对照，L16与L06比较额外标签。刻意保留成组对照，不虚报20种完全不同机制。每关feature_coverage均不宣称必然掌握；L09/T4、L13/T3列为optional_container_ids，并在verify中删盘重放。未来教学检查分别直接问“何时可用T4”“能否在T3封箱、为什么”，回答对错单独记录，不用关卡完成率替代。玩家难度分档需首解时间、撤销率、放弃原因验证；目标秒数不是实测。", "",
"不使用运行期随机关卡。未来生成器只能在另行批准后离线生成并经有解+独立读图+真人质量审查入库；禁止只因求解器有解自动发布。", "",
"## 4. 经济和进度账本", "",
"每次完成：completed[Lnn]=true；若下一关存在则开放。重玩不新增币、次数或随机奖励。提示0成本、撤销0成本、重开0成本。无体力、付费道具、价格、离线产出；因此不需要虚构前30分钟经营数值。单次封箱章只在本关作锁条件，过关清零；收藏完成章仅显示布尔完成，不是可交易货币。", "",
"内部未来预算示例：准备累计≤16人时；获准垂直切片≤80人时，资产/测试采购现金≤3000元，均HYPOTHESIS且未经批准，不代表已经花费。实际成本、总组合失败成本和净回款在11记录。游戏内容无靠广告改变解空间的付费容量。", "",
"## 5. 验证证据与局限", "",
"执行 `python -B tools/verify.py --all`，检查JSON Schema、逐步合法性、每步数量守恒、终局、BFS最短性、变体消融及任务DAG。实际结果以 verification/verification-report.json 为准；每步保存SHA-256状态摘要。脚本不读外部网络，不生成引擎代码。搜索上限超过返回SEARCH_LIMIT_UNKNOWN；只有穷尽无解图才证明该模型无解。", "",
"这20关已验证的是给定规则的有限模型；没有证明真实触控正确、屏幕可读、难度合理、关卡足够长、玩家愿意回访或有商业收益。独立审计仍须从03重述规则，再检查模型是否忠实。"]
(root / "05_Levels_Economy.md").write_text("\n".join(lines)+"\n", encoding="utf-8")
