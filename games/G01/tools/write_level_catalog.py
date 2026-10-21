"""Generate a readable ORIGINAL level appendix from the frozen data; not a game."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=json.loads((ROOT/'game-spec.json').read_text(encoding='utf-8'))
report=json.loads((ROOT/'validation/report.json').read_text(encoding='utf-8'))
stats={l['id']:l for l in report['levels']}
text='''# G01 关卡、进度与经济

版本1.0.0。全部关卡、时间目标、奖励与预算为 **HYPOTHESIS**。本章坐标来自本项目独立编写的数据，没有复制参考关卡、截图或专有表达。20关均非随机生成；seed只用于内容来源标识。

## 数据解释与胜利

坐标原点左上，x右y下。每条cells按尾→头排列，单格使用显式direction。门initial_open为初态；toggles在该箭条完整合法出港后翻转。manifest为空禁用船期，否则一项对应一次出港。所有关初态removed=[]、cursor=0；门取initial_open。胜利统一为全部箭条移除且船期消费完。表中解序列是合法解之一，不宣称唯一。

整体平移的扫掠、错误不扣资源、死锁免费撤销见03。任何新关改动必须重新运行验证，不能只凭所附解声称全分支可玩。

## 内容节奏与经济

L01—04基础；L05—10仅门；L11—15仅船期；L16—20组合。只在首次进入L01/L05/L11/L16显示一条可关闭规则提示。未完成前一关锁下一关，已完成关可免费重玩。L20后是全通页，不制造虚假待开放内容。

每关首次完成+1印章，总数=completed集合大小，上限20；重玩+0。没有金币、升级、商店、体力、时间限制、付费提示或广告救援。提示/撤销/重来成本均0，暂停与后台不产生收益或损失。数值经济不借用任何对标未证实参数。

关卡target_seconds是自拟试验观察窗口，不是实测时长或玩家承诺。前5分钟体验目标是理解移除、完成至少数个基础关；实际能到哪关UNKNOWN，不按时间强制跳关。真人试验若L05理解困难，修订关卡编排后升级版本再测。

## 离线检查与限制

运行 `python tools/validate.py`：game-spec/tasks及SaveEnvelope三份Draft2020-12 schema、几何/引用、20条给定解、全可达、第二种逐步平移交叉核对、任务DAG与合同反例。结果见validation/report.json，逐步门状态见solution-traces.json。

状态数/死锁数是此离散模型的实算事实，不是难度或满意度。每条成功解都必须移除n条箭，故最短步天然n；本包不以最短步定义难度。含故意可达死锁的关卡必须保留免费撤销与明确反馈。没有真人难度排序、引擎帧率或收益验证。

组合教学须区分辨认和规划：L16/L18全程各唯一合法路线，L18初态仅c合法；L19船期排除去船期的16个losing状态。详见12审计反证表，不将组合复杂度当体验增益。

## 20关总表

|关|名称|版本|尺寸|箭条|附解|可达状态|解序列总数|死锁状态|
|---|---|---|---|---|---|---|---|---|
'''
for l in spec['levels']:
    s=stats[l['id']]; sol=' '.join(x['arrow_id'] for x in l['solution'])
    text+=f"|{l['id']}|{l['name']}|{l['mode']}|{l['width']}×{l['height']}|{len(l['arrows'])}|{sol}|{s['reachable_states']}|{s['winning_solution_count']}|{s['deadlock_states']}|\n"
text+='\n## 逐关完整初态与合法解\n\n以下JSON可直接和game-spec中同ID对照；没有省略坐标。\n'
for l in spec['levels']:
    s=stats[l['id']]
    text+=f"\n### {l['id']} {l['name']}\n\n教学目标：{l['learning_objective']}。目标时间 {l['target_seconds'][0]}—{l['target_seconds'][1]}秒，仅HYPOTHESIS。\n\n"
    data={k:l[k] for k in ['id','width','height','mode','arrows','gates','walls','manifest','initial_state','win','solution']}
    text+='```json\n'+json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n```\n\n'
    text+='初始合法：'+', '.join(s['first_legal'])+'；其中仍可通关：'+', '.join(s['first_winning'])+'。\n'
    if s['deadlock_witness']:
        text+='实际枚举死锁见证（这不是附解）：`'+json.dumps(s['deadlock_witness'],ensure_ascii=False,separators=(',',':'))+'`；撤销最后一步可离开该死锁，未必一步即回到可通关状态。\n'
text+='''
## 生产约束

未来关卡作者仅在本G01目录提交提案；检查不同解分支、可触达门、船期与阻挡的可视解释。不得为了“有解”偷偷忽略尾部、允许自开门、增加橡皮擦或改胜利条件。玩家测试若证明同向选择过于隐晦，先修改教学/布局并复验，不把付费救援当修复。
'''
(ROOT/'05_Levels_Economy.md').write_text(text,encoding='utf-8')
print('05_Levels_Economy.md generated with 20 full initial states and verified solutions.')
