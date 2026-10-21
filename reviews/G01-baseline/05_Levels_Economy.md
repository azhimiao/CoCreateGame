# G01 关卡、进度与经济

版本1.0.0。全部关卡、时间目标、奖励与预算为 **HYPOTHESIS**。本章坐标来自本项目独立编写的数据，没有复制参考关卡、截图或专有表达。20关均非随机生成；seed只用于内容来源标识。

## 数据解释与胜利

坐标原点左上，x右y下。每条cells按尾→头排列，单格使用显式direction。门initial_open为初态；toggles在该箭条完整合法出港后翻转。manifest为空禁用船期，否则一项对应一次出港。所有关初态removed=[]、cursor=0；门取initial_open。胜利统一为全部箭条移除且船期消费完。表中解序列是合法解之一，不宣称唯一。

整体平移的扫掠、错误不扣资源、死锁免费撤销见03。任何新关改动必须重新运行验证，不能只凭所附解声称全分支可玩。

## 内容节奏与经济

L01—04基础；L05—10仅门；L11—15仅船期；L16—20组合。只在首次进入L01/L05/L11/L16显示一条可关闭规则提示。未完成前一关锁下一关，已完成关可免费重玩。L20后是全通页，不制造虚假待开放内容。

每关首次完成+1印章，总数=completed集合大小，上限20；重玩+0。没有金币、升级、商店、体力、时间限制、付费提示或广告救援。提示/撤销/重来成本均0，暂停与后台不产生收益或损失。数值经济不借用任何对标未证实参数。

关卡target_seconds是自拟试验观察窗口，不是实测时长或玩家承诺。前5分钟体验目标是理解移除、完成至少数个基础关；实际能到哪关UNKNOWN，不按时间强制跳关。真人试验若L05理解困难，修订关卡编排后升级版本再测。

## 离线检查与限制

运行 `python tools/validate.py`：两份Draft2020-12 schema、几何/引用、20条给定解、所有可达状态、第二种逐步平移算法交叉核对、任务DAG与对抗边界。结果见validation/report.json，逐步门状态见solution-traces.json。

状态数/死锁数是此离散模型的实算事实，不是难度或满意度。每条成功解都必须移除n条箭，故最短步天然n；本包不以最短步定义难度。含故意可达死锁的关卡必须保留免费撤销与明确反馈。没有真人难度排序、引擎帧率或收益验证。

## 20关总表

|关|名称|版本|尺寸|箭条|附解|可达状态|解序列总数|死锁状态|
|---|---|---|---|---|---|---|---|---|
|L01|开港|BASE|4×4|2|a b|3|1|0|
|L02|先疏后发|BASE|5×4|3|b a c|6|3|0|
|L03|弯条也要净空|BASE|5×5|4|b a c d|12|12|0|
|L04|交叉码头|BASE|6×6|5|b a d c e|18|30|0|
|L05|第一盏信号|RELAY|5×5|2|b a|3|1|0|
|L06|开门之前|RELAY|6×5|3|c b a|5|2|0|
|L07|双灯串联|RELAY|6×6|3|c b a|4|1|0|
|L08|不要连按开关|RELAY|5×5|3|b a c|7|2|1|
|L09|两门交替|RELAY|6×6|4|c a b d|10|4|1|
|L10|弯桥继电|RELAY|7×6|5|c a b d e|20|20|1|
|L11|船期单|MANIFEST|5×5|3|a b c|4|1|0|
|L12|先清航线|MANIFEST|5×5|3|b a c|4|1|0|
|L13|同向二选一|MANIFEST|5×5|3|b c a|5|1|1|
|L14|两次交接|MANIFEST|6×6|5|b c a d e|7|1|1|
|L15|曲线船期|MANIFEST|7×6|5|b a c d e|6|1|0|
|L16|灯号与船期|COMBINED|5×5|3|b a c|4|1|0|
|L17|同向不同信号|COMBINED|6×6|3|b c a|5|1|1|
|L18|双灯船队|COMBINED|6×6|4|c a b d|5|1|0|
|L19|双信号分流|COMBINED|7×7|6|c a b d e f|9|2|0|
|L20|最后一班|COMBINED|7×7|7|b c a d e f z|12|4|1|

## 逐关完整初态与合法解

以下JSON可直接和game-spec中同ID对照；没有省略坐标。

### L01 开港

教学目标：点击整条箭头，清空棋盘。目标时间 13—31秒，仅HYPOTHESIS。

```json
{"id":"L01","width":4,"height":4,"mode":"BASE","arrows":[{"id":"a","direction":"E","cells":[[1,1],[2,1]],"toggles":[]},{"id":"b","direction":"N","cells":[[1,3],[1,2]],"toggles":[]}],"gates":[],"walls":[],"manifest":[],"initial_state":{"removed":[],"manifest_cursor":0},"win":{"all_arrows_removed":true,"manifest_consumed":true},"solution":[{"type":"EXIT","arrow_id":"a"},{"type":"EXIT","arrow_id":"b"}]}
```

初始合法：a；其中仍可通关：a。

### L02 先疏后发

教学目标：路径被另一箭条占用时先移除阻挡者。目标时间 16—37秒，仅HYPOTHESIS。

```json
{"id":"L02","width":5,"height":4,"mode":"BASE","arrows":[{"id":"a","direction":"E","cells":[[0,1],[1,1]],"toggles":[]},{"id":"b","direction":"N","cells":[[3,2],[3,1]],"toggles":[]},{"id":"c","direction":"W","cells":[[2,3],[1,3]],"toggles":[]}],"gates":[],"walls":[],"manifest":[],"initial_state":{"removed":[],"manifest_cursor":0},"win":{"all_arrows_removed":true,"manifest_consumed":true},"solution":[{"type":"EXIT","arrow_id":"b"},{"type":"EXIT","arrow_id":"a"},{"type":"EXIT","arrow_id":"c"}]}
```

初始合法：b, c；其中仍可通关：b, c。

### L03 弯条也要净空

教学目标：弯条整体平移，尾部的扫掠也算碰撞。目标时间 19—43秒，仅HYPOTHESIS。

```json
{"id":"L03","width":5,"height":5,"mode":"BASE","arrows":[{"id":"a","direction":"E","cells":[[0,1],[0,2],[1,2]],"toggles":[]},{"id":"b","direction":"N","cells":[[3,2],[3,1]],"toggles":[]},{"id":"c","direction":"S","cells":[[4,3],[4,4]],"toggles":[]},{"id":"d","direction":"W","cells":[[2,4],[1,4]],"toggles":[]}],"gates":[],"walls":[],"manifest":[],"initial_state":{"removed":[],"manifest_cursor":0},"win":{"all_arrows_removed":true,"manifest_consumed":true},"solution":[{"type":"EXIT","arrow_id":"b"},{"type":"EXIT","arrow_id":"a"},{"type":"EXIT","arrow_id":"c"},{"type":"EXIT","arrow_id":"d"}]}
```

初始合法：b, c, d；其中仍可通关：b, c, d。

### L04 交叉码头

教学目标：两组依赖、可自由交换的独立操作。目标时间 22—49秒，仅HYPOTHESIS。

```json
{"id":"L04","width":6,"height":6,"mode":"BASE","arrows":[{"id":"a","direction":"E","cells":[[0,1],[1,1]],"toggles":[]},{"id":"b","direction":"N","cells":[[3,2],[3,1]],"toggles":[]},{"id":"c","direction":"W","cells":[[5,4],[4,4]],"toggles":[]},{"id":"d","direction":"S","cells":[[2,3],[2,4]],"toggles":[]},{"id":"e","direction":"E","cells":[[0,5],[1,5]],"toggles":[]}],"gates":[],"walls":[[5,0]],"manifest":[],"initial_state":{"removed":[],"manifest_cursor":0},"win":{"all_arrows_removed":true,"manifest_consumed":true},"solution":[{"type":"EXIT","arrow_id":"b"},{"type":"EXIT","arrow_id":"a"},{"type":"EXIT","arrow_id":"d"},{"type":"EXIT","arrow_id":"c"},{"type":"EXIT","arrow_id":"e"}]}
```

初始合法：b, d, e；其中仍可通关：b, d, e。

### L05 第一盏信号

教学目标：带 g 印记箭条离港后翻转 g 门。目标时间 25—55秒，仅HYPOTHESIS。

```json
{"id":"L05","width":5,"height":5,"mode":"RELAY","arrows":[{"id":"a","direction":"E","cells":[[0,1],[1,1]],"toggles":[]},{"id":"b","direction":"E","cells":[[2,3],[3,3]],"toggles":["g"]}],"gates":[{"id":"g","cells":[[3,1]],"initial_open":false}],"walls":[],"manifest":[],"initial_state":{"removed":[],"manifest_cursor":0},"win":{"all_arrows_removed":true,"manifest_consumed":true},"solution":[{"type":"EXIT","arrow_id":"b"},{"type":"EXIT","arrow_id":"a"}]}
```

初始合法：b；其中仍可通关：b。

### L06 开门之前

教学目标：几何遮挡和门遮挡同时检查。目标时间 28—61秒，仅HYPOTHESIS。

```json
{"id":"L06","width":6,"height":5,"mode":"RELAY","arrows":[{"id":"a","direction":"E","cells":[[0,1],[1,1]],"toggles":[]},{"id":"b","direction":"N","cells":[[3,2],[3,1]],"toggles":[]},{"id":"c","direction":"E","cells":[[0,4],[1,4]],"toggles":["g"]}],"gates":[{"id":"g","cells":[[5,1]],"initial_open":false}],"walls":[],"manifest":[],"initial_state":{"removed":[],"manifest_cursor":0},"win":{"all_arrows_removed":true,"manifest_consumed":true},"solution":[{"type":"EXIT","arrow_id":"c"},{"type":"EXIT","arrow_id":"b"},{"type":"EXIT","arrow_id":"a"}]}
```

初始合法：b, c；其中仍可通关：b, c。

### L07 双灯串联

教学目标：g 放行 b，b 再打开 h 给 a。目标时间 31—67秒，仅HYPOTHESIS。

```json
{"id":"L07","width":6,"height":6,"mode":"RELAY","arrows":[{"id":"a","direction":"E","cells":[[0,1],[1,1]],"toggles":[]},{"id":"b","direction":"N","cells":[[3,5],[3,4]],"toggles":["h"]},{"id":"c","direction":"E","cells":[[0,2],[1,2]],"toggles":["g"]}],"gates":[{"id":"g","cells":[[3,3]],"initial_open":false},{"id":"h","cells":[[4,1]],"initial_open":false}],"walls":[],"manifest":[],"initial_state":{"removed":[],"manifest_cursor":0},"win":{"all_arrows_removed":true,"manifest_consumed":true},"solution":[{"type":"EXIT","arrow_id":"c"},{"type":"EXIT","arrow_id":"b"},{"type":"EXIT","arrow_id":"a"}]}
```

初始合法：c；其中仍可通关：c。

### L08 不要连按开关

教学目标：两次翻转关门；合法操作也可能造成残局死锁。目标时间 34—73秒，仅HYPOTHESIS。

```json
{"id":"L08","width":5,"height":5,"mode":"RELAY","arrows":[{"id":"a","direction":"E","cells":[[0,1],[1,1]],"toggles":[]},{"id":"b","direction":"E","cells":[[2,3],[3,3]],"toggles":["g"]},{"id":"c","direction":"W","cells":[[2,4],[1,4]],"toggles":["g"]}],"gates":[{"id":"g","cells":[[3,1]],"initial_open":false}],"walls":[],"manifest":[],"initial_state":{"removed":[],"manifest_cursor":0},"win":{"all_arrows_removed":true,"manifest_consumed":true},"solution":[{"type":"EXIT","arrow_id":"b"},{"type":"EXIT","arrow_id":"a"},{"type":"EXIT","arrow_id":"c"}]}
```

初始合法：b, c；其中仍可通关：b, c。
实际枚举死锁见证（这不是附解）：`{"accepted_exits":["b","c"],"remaining":["a"],"gate_open":{"g":false}}`；撤销最后一步可离开该死锁，未必一步即回到可通关状态。

### L09 两门交替

教学目标：先用 g 通行，再交付 h；提前 d 会关 g。目标时间 37—79秒，仅HYPOTHESIS。

```json
{"id":"L09","width":6,"height":6,"mode":"RELAY","arrows":[{"id":"a","direction":"E","cells":[[0,1],[1,1]],"toggles":["h"]},{"id":"b","direction":"N","cells":[[4,5],[4,4]],"toggles":[]},{"id":"c","direction":"E","cells":[[0,3],[1,3]],"toggles":["g"]},{"id":"d","direction":"W","cells":[[2,5],[1,5]],"toggles":["g"]}],"gates":[{"id":"g","cells":[[3,1]],"initial_open":false},{"id":"h","cells":[[4,2]],"initial_open":false}],"walls":[],"manifest":[],"initial_state":{"removed":[],"manifest_cursor":0},"win":{"all_arrows_removed":true,"manifest_consumed":true},"solution":[{"type":"EXIT","arrow_id":"c"},{"type":"EXIT","arrow_id":"a"},{"type":"EXIT","arrow_id":"b"},{"type":"EXIT","arrow_id":"d"}]}
```

初始合法：c, d；其中仍可通关：c, d。
实际枚举死锁见证（这不是附解）：`{"accepted_exits":["c","d"],"remaining":["a","b"],"gate_open":{"g":false,"h":false}}`；撤销最后一步可离开该死锁，未必一步即回到可通关状态。

### L10 弯桥继电

教学目标：弯条尾部、两组门和独立安全出口。目标时间 40—85秒，仅HYPOTHESIS。

```json
{"id":"L10","width":7,"height":6,"mode":"RELAY","arrows":[{"id":"a","direction":"E","cells":[[0,1],[0,2],[1,2]],"toggles":["h"]},{"id":"b","direction":"N","cells":[[5,5],[5,4]],"toggles":[]},{"id":"c","direction":"E","cells":[[0,0],[1,0]],"toggles":["g"]},{"id":"d","direction":"W","cells":[[2,5],[1,5]],"toggles":["g"]},{"id":"e","direction":"S","cells":[[6,4],[6,5]],"toggles":[]}],"gates":[{"id":"g","cells":[[4,1]],"initial_open":false},{"id":"h","cells":[[5,3]],"initial_open":false}],"walls":[],"manifest":[],"initial_state":{"removed":[],"manifest_cursor":0},"win":{"all_arrows_removed":true,"manifest_consumed":true},"solution":[{"type":"EXIT","arrow_id":"c"},{"type":"EXIT","arrow_id":"a"},{"type":"EXIT","arrow_id":"b"},{"type":"EXIT","arrow_id":"d"},{"type":"EXIT","arrow_id":"e"}]}
```

初始合法：c, d, e；其中仍可通关：c, d, e。
实际枚举死锁见证（这不是附解）：`{"accepted_exits":["c","d","e"],"remaining":["a","b"],"gate_open":{"g":false,"h":false}}`；撤销最后一步可离开该死锁，未必一步即回到可通关状态。

### L11 船期单

教学目标：必须按右、上、左出港。目标时间 43—91秒，仅HYPOTHESIS。

```json
{"id":"L11","width":5,"height":5,"mode":"MANIFEST","arrows":[{"id":"a","direction":"E","cells":[[0,1],[1,1]],"toggles":[]},{"id":"b","direction":"N","cells":[[3,4],[3,3]],"toggles":[]},{"id":"c","direction":"W","cells":[[2,4],[1,4]],"toggles":[]}],"gates":[],"walls":[],"manifest":["E","N","W"],"initial_state":{"removed":[],"manifest_cursor":0},"win":{"all_arrows_removed":true,"manifest_consumed":true},"solution":[{"type":"EXIT","arrow_id":"a"},{"type":"EXIT","arrow_id":"b"},{"type":"EXIT","arrow_id":"c"}]}
```

初始合法：a；其中仍可通关：a。

### L12 先清航线

教学目标：船期和几何依赖一致，错误方向不会消耗步数。目标时间 46—97秒，仅HYPOTHESIS。

```json
{"id":"L12","width":5,"height":5,"mode":"MANIFEST","arrows":[{"id":"a","direction":"E","cells":[[0,1],[1,1]],"toggles":[]},{"id":"b","direction":"N","cells":[[3,2],[3,1]],"toggles":[]},{"id":"c","direction":"S","cells":[[4,3],[4,4]],"toggles":[]}],"gates":[],"walls":[],"manifest":["N","E","S"],"initial_state":{"removed":[],"manifest_cursor":0},"win":{"all_arrows_removed":true,"manifest_consumed":true},"solution":[{"type":"EXIT","arrow_id":"b"},{"type":"EXIT","arrow_id":"a"},{"type":"EXIT","arrow_id":"c"}]}
```

初始合法：b；其中仍可通关：b。

### L13 同向二选一

教学目标：第一步两条朝上，先 a 会让下一条朝右无法离港。目标时间 49—103秒，仅HYPOTHESIS。

```json
{"id":"L13","width":5,"height":5,"mode":"MANIFEST","arrows":[{"id":"a","direction":"N","cells":[[1,1]],"toggles":[]},{"id":"b","direction":"N","cells":[[3,3],[3,2]],"toggles":[]},{"id":"c","direction":"E","cells":[[0,2],[1,2]],"toggles":[]}],"gates":[],"walls":[],"manifest":["N","E","N"],"initial_state":{"removed":[],"manifest_cursor":0},"win":{"all_arrows_removed":true,"manifest_consumed":true},"solution":[{"type":"EXIT","arrow_id":"b"},{"type":"EXIT","arrow_id":"c"},{"type":"EXIT","arrow_id":"a"}]}
```

初始合法：a, b；其中仍可通关：b。
实际枚举死锁见证（这不是附解）：`{"accepted_exits":["a"],"remaining":["b","c"],"gate_open":{}}`；撤销最后一步可离开该死锁，未必一步即回到可通关状态。

### L14 两次交接

教学目标：同向选择后再处理另一组阻挡。目标时间 52—109秒，仅HYPOTHESIS。

```json
{"id":"L14","width":6,"height":6,"mode":"MANIFEST","arrows":[{"id":"a","direction":"N","cells":[[1,1]],"toggles":[]},{"id":"b","direction":"N","cells":[[4,3],[4,2]],"toggles":[]},{"id":"c","direction":"E","cells":[[0,2],[1,2]],"toggles":[]},{"id":"d","direction":"S","cells":[[2,4],[2,5]],"toggles":[]},{"id":"e","direction":"W","cells":[[5,4],[4,4]],"toggles":[]}],"gates":[],"walls":[],"manifest":["N","E","N","S","W"],"initial_state":{"removed":[],"manifest_cursor":0},"win":{"all_arrows_removed":true,"manifest_consumed":true},"solution":[{"type":"EXIT","arrow_id":"b"},{"type":"EXIT","arrow_id":"c"},{"type":"EXIT","arrow_id":"a"},{"type":"EXIT","arrow_id":"d"},{"type":"EXIT","arrow_id":"e"}]}
```

初始合法：a, b；其中仍可通关：b。
实际枚举死锁见证（这不是附解）：`{"accepted_exits":["a"],"remaining":["b","c","d","e"],"gate_open":{}}`；撤销最后一步可离开该死锁，未必一步即回到可通关状态。

### L15 曲线船期

教学目标：弯条放行后按五项船期完成。目标时间 55—115秒，仅HYPOTHESIS。

```json
{"id":"L15","width":7,"height":6,"mode":"MANIFEST","arrows":[{"id":"a","direction":"E","cells":[[0,1],[0,2],[1,2]],"toggles":[]},{"id":"b","direction":"N","cells":[[4,2],[4,1]],"toggles":[]},{"id":"c","direction":"S","cells":[[6,4],[6,5]],"toggles":[]},{"id":"d","direction":"W","cells":[[3,4],[2,4]],"toggles":[]},{"id":"e","direction":"N","cells":[[1,5]],"toggles":[]}],"gates":[],"walls":[],"manifest":["N","E","S","W","N"],"initial_state":{"removed":[],"manifest_cursor":0},"win":{"all_arrows_removed":true,"manifest_consumed":true},"solution":[{"type":"EXIT","arrow_id":"b"},{"type":"EXIT","arrow_id":"a"},{"type":"EXIT","arrow_id":"c"},{"type":"EXIT","arrow_id":"d"},{"type":"EXIT","arrow_id":"e"}]}
```

初始合法：b；其中仍可通关：b。

### L16 灯号与船期

教学目标：上港开灯、右港通行、左港收灯。目标时间 58—121秒，仅HYPOTHESIS。

```json
{"id":"L16","width":5,"height":5,"mode":"COMBINED","arrows":[{"id":"a","direction":"E","cells":[[0,1],[1,1]],"toggles":[]},{"id":"b","direction":"N","cells":[[4,4],[4,3]],"toggles":["g"]},{"id":"c","direction":"W","cells":[[2,4],[1,4]],"toggles":["g"]}],"gates":[{"id":"g","cells":[[3,1]],"initial_open":false}],"walls":[],"manifest":["N","E","W"],"initial_state":{"removed":[],"manifest_cursor":0},"win":{"all_arrows_removed":true,"manifest_consumed":true},"solution":[{"type":"EXIT","arrow_id":"b"},{"type":"EXIT","arrow_id":"a"},{"type":"EXIT","arrow_id":"c"}]}
```

初始合法：b；其中仍可通关：b。

### L17 同向不同信号

教学目标：两条朝上只有 b 能打开下一班的门。目标时间 61—127秒，仅HYPOTHESIS。

```json
{"id":"L17","width":6,"height":6,"mode":"COMBINED","arrows":[{"id":"a","direction":"N","cells":[[1,1]],"toggles":[]},{"id":"b","direction":"N","cells":[[4,5],[4,4]],"toggles":["g"]},{"id":"c","direction":"E","cells":[[0,2],[1,2]],"toggles":[]}],"gates":[{"id":"g","cells":[[3,2]],"initial_open":false}],"walls":[],"manifest":["N","E","N"],"initial_state":{"removed":[],"manifest_cursor":0},"win":{"all_arrows_removed":true,"manifest_consumed":true},"solution":[{"type":"EXIT","arrow_id":"b"},{"type":"EXIT","arrow_id":"c"},{"type":"EXIT","arrow_id":"a"}]}
```

初始合法：a, b；其中仍可通关：b。
实际枚举死锁见证（这不是附解）：`{"accepted_exits":["a"],"remaining":["b","c"],"gate_open":{"g":false}}`；撤销最后一步可离开该死锁，未必一步即回到可通关状态。

### L18 双灯船队

教学目标：第一班同向但必须先信号船。目标时间 64—133秒，仅HYPOTHESIS。

```json
{"id":"L18","width":6,"height":6,"mode":"COMBINED","arrows":[{"id":"a","direction":"E","cells":[[0,1],[1,1]],"toggles":["h"]},{"id":"b","direction":"N","cells":[[4,5],[4,4]],"toggles":[]},{"id":"c","direction":"E","cells":[[0,3],[1,3]],"toggles":["g"]},{"id":"d","direction":"W","cells":[[2,5],[1,5]],"toggles":["g"]}],"gates":[{"id":"g","cells":[[3,1]],"initial_open":false},{"id":"h","cells":[[4,2]],"initial_open":false}],"walls":[],"manifest":["E","E","N","W"],"initial_state":{"removed":[],"manifest_cursor":0},"win":{"all_arrows_removed":true,"manifest_consumed":true},"solution":[{"type":"EXIT","arrow_id":"c"},{"type":"EXIT","arrow_id":"a"},{"type":"EXIT","arrow_id":"b"},{"type":"EXIT","arrow_id":"d"}]}
```

初始合法：c；其中仍可通关：c。

### L19 双信号分流

教学目标：多门翻转发生在离港提交后，不会救自己。目标时间 67—139秒，仅HYPOTHESIS。

```json
{"id":"L19","width":7,"height":7,"mode":"COMBINED","arrows":[{"id":"a","direction":"E","cells":[[0,1],[0,2],[1,2]],"toggles":["h"]},{"id":"b","direction":"N","cells":[[5,6],[5,5]],"toggles":[]},{"id":"c","direction":"E","cells":[[0,4],[1,4]],"toggles":["g"]},{"id":"d","direction":"W","cells":[[3,6],[2,6]],"toggles":["g","h"]},{"id":"e","direction":"S","cells":[[6,5],[6,6]],"toggles":[]},{"id":"f","direction":"W","cells":[[3,0],[2,0]],"toggles":[]}],"gates":[{"id":"g","cells":[[4,1]],"initial_open":false},{"id":"h","cells":[[5,3]],"initial_open":false}],"walls":[],"manifest":["E","E","N","W","S","W"],"initial_state":{"removed":[],"manifest_cursor":0},"win":{"all_arrows_removed":true,"manifest_consumed":true},"solution":[{"type":"EXIT","arrow_id":"c"},{"type":"EXIT","arrow_id":"a"},{"type":"EXIT","arrow_id":"b"},{"type":"EXIT","arrow_id":"d"},{"type":"EXIT","arrow_id":"e"},{"type":"EXIT","arrow_id":"f"}]}
```

初始合法：c；其中仍可通关：c。

### L20 最后一班

教学目标：两次同向选择与门闭合时机；计划七次离港。目标时间 70—145秒，仅HYPOTHESIS。

```json
{"id":"L20","width":7,"height":7,"mode":"COMBINED","arrows":[{"id":"a","direction":"N","cells":[[1,1]],"toggles":[]},{"id":"b","direction":"N","cells":[[4,4],[4,3]],"toggles":["g"]},{"id":"c","direction":"E","cells":[[0,2],[1,2]],"toggles":["h"]},{"id":"d","direction":"N","cells":[[6,6],[6,5]],"toggles":[]},{"id":"e","direction":"W","cells":[[3,6],[2,6]],"toggles":["g"]},{"id":"f","direction":"S","cells":[[1,4],[1,5]],"toggles":[]},{"id":"z","direction":"W","cells":[[3,0],[2,0]],"toggles":["h"]}],"gates":[{"id":"g","cells":[[3,2]],"initial_open":false},{"id":"h","cells":[[6,3]],"initial_open":false}],"walls":[],"manifest":["N","E","N","N","W","S","W"],"initial_state":{"removed":[],"manifest_cursor":0},"win":{"all_arrows_removed":true,"manifest_consumed":true},"solution":[{"type":"EXIT","arrow_id":"b"},{"type":"EXIT","arrow_id":"c"},{"type":"EXIT","arrow_id":"a"},{"type":"EXIT","arrow_id":"d"},{"type":"EXIT","arrow_id":"e"},{"type":"EXIT","arrow_id":"f"},{"type":"EXIT","arrow_id":"z"}]}
```

初始合法：a, b；其中仍可通关：b。
实际枚举死锁见证（这不是附解）：`{"accepted_exits":["a"],"remaining":["b","c","d","e","f","z"],"gate_open":{"g":false,"h":false}}`；撤销最后一步可离开该死锁，未必一步即回到可通关状态。

## 生产约束

未来关卡作者仅在本G01目录提交提案；检查不同解分支、可触达门、船期与阻挡的可视解释。不得为了“有解”偷偷忽略尾部、允许自开门、增加橡皮擦或改胜利条件。玩家测试若证明同向选择过于隐晦，先修改教学/布局并复验，不把付费救援当修复。
