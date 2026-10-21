# 关卡、成长与经济规格

版本1.0.0，原创关卡设计为 **HYPOTHESIS**。20关均为本目录独立撰写的离散布局，没有从参考游戏导出地图、路径或专有资产。`game-spec.json` 是可机读真源；本页将每关初态/目标/机关/解完整投影，验证日志在 `validation-report.json`。

## 记法与关卡作者约束

位置固定为 `[层,x,y]`，0下层/1上层；所有图以左上为原点。`floors` 每层是逐行字符串，`.`地面、`#`空缺；gate.at 仅在指定 bit 等于 value 时开放；switch.mask 是进入时XOR值；lifts是两层共享同位升降坐标。初始pending/nextBeacon/used为0，PLAYING，history为空。victory还强制pending=0、全部信标完成；正式20关无信标。解中的U/R/D/L为一步，X为升降，数组严格逐步执行。

先固定手工设计意图与地图，再用BFS验解。没有按求解器输出宣称好玩、唯一解或经验难度。某些题可能存在同长解，固定遍历U/R/D/L/X只为重现。后10关较长但L20最短步少于L19，**不假装难度单调**；难度以盲测正确率/犹豫/撤销原因再排序，关卡ID和存档迁移须另审。

## 内容与成长

正式内容只有20关。无生成器在线填充、日历关、体力、硬软币、随机奖励、支付、广告换提示。每关免费撤销与提示，步数是单关规划约束，不是跨关生命池。解锁与星级按03；最佳路线步数是最终撤销后保留路线长度。每次重开恢复本关初始位型和完整预算，保留历史最佳星级。

关卡章节为1—4认识移动/位型/升降；5—7复位与跨层；8—10多位与脚下关闭；11—16长路径/联合掩码；17—20综合规划。这是教学分组假设，实际时间、留存与误触UNKNOWN。首3关只有对应机制出现时展示一次可关闭文字；后续关提供可点开的机制图例，不强制长教程。

## 逐关摘要

| ID / 名称 | 设计意图（不保证新策略） | 最短步par / 预算 | 合法最短解 |
|---|---|---:|---|
| G04-L01 第一束光 | 进入开关触发一次；走到目标还需位型相同 | 2 / 6 | RR |
| G04-L02 绕行不是答案 | 目标位型排除绕开开关的假捷径 | 4 / 8 | RRDD |
| G04-L03 同位升降 | 观察层切换不移动棋子；必须走到升降台 | 5 / 9 | RRXLL |
| G04-L04 上层来信 | 下层开关控制上层出口 | 5 / 9 | DRRXD |
| G04-L05 互补走廊 | 开下层通道后需在上层恢复相反位型 | 9 / 14 | LURRXUDLL |
| G04-L06 双井返回 | 上层开关要求经双升降井返回 | 8 / 12 | UUXRRXDD |
| G04-L07 回踩复位 | 两个同组开关相抵；位型目标为零仍需操作 | 7 / 11 | RRDDXLL |
| G04-L08 两枚锁芯 | 两组独立位与两扇独立门 | 11 / 17 | RRRDDLRXLLL |
| G04-L09 一踏双响 | 掩码3同时翻转A和B，再单独复位A | 11 / 17 | RRRDDLRXLLL |
| G04-L10 安全落脚 | 门上开关关闭脚下会失败；安全绕行需要识别陷阱 | 9 / 14 | RRRDDXLLL |
| G04-L11 反相渡口 | 跨层前后需要相反A位，长走廊规划 | 17 / 26 | RRRRDDXLLRRDDLLLL |
| G04-L12 反向初值 | 初始非零；第二次A翻转修复终局位型 | 15 / 23 | RRRRDDXDDLLLRLL |
| G04-L13 断桥与旁路 | 先从另一层取得B，再经不同升降台返回 | 26 / 39 | RRRRXLLRRDDLLLLDDRRRRXLLLL |
| G04-L14 位型不是颜色 | A+B与B+C组合得到A+C，不能按单色猜 | 17 / 26 | RRRRDDXLLRRDDLLLL |
| G04-L15 目标下的门 | 三位累积且出口自身是门；抵达不是唯一胜利条件 | 19 / 29 | RRRRDDLRXLLRRDDLLLL |
| G04-L16 提前复位的代价 | A只承担运输用途，终局必须复位，B保留 | 19 / 29 | RRRRDDLRXLLRRDDLLLL |
| G04-L17 借道上层 | 掩码3与5的结果6；下层直路初始被阻 | 22 / 33 | RRRRXLLRRDDLLRRDDXLLLL |
| G04-L18 上下互换 | 反向进入蛇形棋盘；终点层与位型共同约束 | 15 / 23 | UURRLLXUURLRRRR |
| G04-L19 三组循环锁 | 两次联合翻转后补A，需检查所有目标位 | 26 / 39 | RRRRXLLRRDDLLLLDDRRRRXLLLL |
| G04-L20 折光总控 | 直路和跨层多候选，组合掩码与终局复位综合题 | 18 / 27 | RRRRDDLLLLXRRLLXDD |

## 20关精确初态与胜利条件

每段可按字段定位到game-spec，不是示意图。开关/门允许跨类重叠，同类禁止重复。

### G04-L01 第一束光

```json
{"id":"G04-L01","variant":"B0","width":3,"height":3,"bit_count":1,"floors":[["###","...","###"],["###","###","###"]],"initial":{"position":[0,0,1],"bits":0},"victory":{"position":[0,2,1],"bits":1,"pending":0,"all_beacons":true},"lifts":[],"switches":[{"at":[0,1,1],"mask":1}],"gates":[],"beacons":[],"move_limit":6,"par":2,"solution":["R","R"]}
```

### G04-L02 绕行不是答案

```json
{"id":"G04-L02","variant":"B0","width":3,"height":3,"bit_count":1,"floors":[["...",".#.","..."],["###","###","###"]],"initial":{"position":[0,0,0],"bits":0},"victory":{"position":[0,2,2],"bits":1,"pending":0,"all_beacons":true},"lifts":[],"switches":[{"at":[0,1,0],"mask":1}],"gates":[{"at":[0,2,1],"bit":0,"value":1}],"beacons":[],"move_limit":8,"par":4,"solution":["R","R","D","D"]}
```

### G04-L03 同位升降

```json
{"id":"G04-L03","variant":"B0","width":3,"height":3,"bit_count":1,"floors":[["###","...","###"],["###","...","###"]],"initial":{"position":[0,0,1],"bits":0},"victory":{"position":[1,0,1],"bits":0,"pending":0,"all_beacons":true},"lifts":[[2,1]],"switches":[],"gates":[],"beacons":[],"move_limit":9,"par":5,"solution":["R","R","X","L","L"]}
```

### G04-L04 上层来信

```json
{"id":"G04-L04","variant":"B0","width":3,"height":3,"bit_count":1,"floors":[[".##","...","###"],["###","...","##."]],"initial":{"position":[0,0,0],"bits":0},"victory":{"position":[1,2,2],"bits":1,"pending":0,"all_beacons":true},"lifts":[[2,1]],"switches":[{"at":[0,0,1],"mask":1}],"gates":[{"at":[1,2,2],"bit":0,"value":1}],"beacons":[],"move_limit":9,"par":5,"solution":["D","R","R","X","D"]}
```

### G04-L05 互补走廊

```json
{"id":"G04-L05","variant":"B0","width":3,"height":3,"bit_count":1,"floors":[["...","...","..."],["...","...","###"]],"initial":{"position":[0,1,2],"bits":0},"victory":{"position":[1,0,1],"bits":0,"pending":0,"all_beacons":true},"lifts":[[2,1]],"switches":[{"at":[0,0,1],"mask":1},{"at":[1,2,0],"mask":1}],"gates":[{"at":[0,1,1],"bit":0,"value":1},{"at":[1,1,1],"bit":0,"value":0},{"at":[0,2,1],"bit":0,"value":1}],"beacons":[],"move_limit":14,"par":9,"solution":["L","U","R","R","X","U","D","L","L"]}
```

### G04-L06 双井返回

```json
{"id":"G04-L06","variant":"B0","width":3,"height":3,"bit_count":1,"floors":[["...",".#.","..."],["...","###","###"]],"initial":{"position":[0,0,2],"bits":0},"victory":{"position":[0,2,2],"bits":1,"pending":0,"all_beacons":true},"lifts":[[0,0],[2,0]],"switches":[{"at":[1,1,0],"mask":1}],"gates":[{"at":[0,2,1],"bit":0,"value":1}],"beacons":[],"move_limit":12,"par":8,"solution":["U","U","X","R","R","X","D","D"]}
```

### G04-L07 回踩复位

```json
{"id":"G04-L07","variant":"B0","width":3,"height":3,"bit_count":1,"floors":[["...",".#.","..."],["###","###","..."]],"initial":{"position":[0,0,0],"bits":0},"victory":{"position":[1,0,2],"bits":0,"pending":0,"all_beacons":true},"lifts":[[2,2]],"switches":[{"at":[0,1,0],"mask":1},{"at":[1,1,2],"mask":1}],"gates":[{"at":[0,2,1],"bit":0,"value":1},{"at":[0,0,1],"bit":0,"value":1}],"beacons":[],"move_limit":11,"par":7,"solution":["R","R","D","D","X","L","L"]}
```

### G04-L08 两枚锁芯

```json
{"id":"G04-L08","variant":"B0","width":4,"height":4,"bit_count":2,"floors":[["....","###.","....","####"],["####","####","....","####"]],"initial":{"position":[0,0,0],"bits":0},"victory":{"position":[1,0,2],"bits":3,"pending":0,"all_beacons":true},"lifts":[[3,2]],"switches":[{"at":[0,1,0],"mask":1},{"at":[0,2,2],"mask":2}],"gates":[{"at":[0,3,1],"bit":0,"value":1},{"at":[1,1,2],"bit":1,"value":1}],"beacons":[],"move_limit":17,"par":11,"solution":["R","R","R","D","D","L","R","X","L","L","L"]}
```

### G04-L09 一踏双响

```json
{"id":"G04-L09","variant":"B0","width":4,"height":4,"bit_count":2,"floors":[["....","###.","....","####"],["####","####","....","####"]],"initial":{"position":[0,0,0],"bits":0},"victory":{"position":[1,0,2],"bits":2,"pending":0,"all_beacons":true},"lifts":[[3,2]],"switches":[{"at":[0,1,0],"mask":3},{"at":[0,2,2],"mask":1}],"gates":[{"at":[0,3,1],"bit":0,"value":1},{"at":[1,1,2],"bit":1,"value":1}],"beacons":[],"move_limit":17,"par":11,"solution":["R","R","R","D","D","L","R","X","L","L","L"]}
```

### G04-L10 安全落脚

```json
{"id":"G04-L10","variant":"B0","width":4,"height":4,"bit_count":1,"floors":[["....",".#..","....","####"],["####","####","....","####"]],"initial":{"position":[0,0,0],"bits":0},"victory":{"position":[1,0,2],"bits":1,"pending":0,"all_beacons":true},"lifts":[[3,2]],"switches":[{"at":[0,1,0],"mask":1},{"at":[0,2,1],"mask":1}],"gates":[{"at":[0,2,1],"bit":0,"value":1},{"at":[1,1,2],"bit":0,"value":1},{"at":[0,0,1],"bit":0,"value":1}],"beacons":[],"move_limit":14,"par":9,"solution":["R","R","R","D","D","X","L","L","L"]}
```

### G04-L11 反相渡口

```json
{"id":"G04-L11","variant":"B0","width":5,"height":5,"bit_count":1,"floors":[[".....","####.",".....",".####","....."],[".....",".####",".....","####.","....."]],"initial":{"position":[0,0,0],"bits":0},"victory":{"position":[1,0,4],"bits":0,"pending":0,"all_beacons":true},"lifts":[[4,2]],"switches":[{"at":[0,2,0],"mask":1},{"at":[1,2,2],"mask":1}],"gates":[{"at":[0,4,1],"bit":0,"value":1},{"at":[1,4,3],"bit":0,"value":0}],"beacons":[],"move_limit":26,"par":17,"solution":["R","R","R","R","D","D","X","L","L","R","R","D","D","L","L","L","L"]}
```

### G04-L12 反向初值

```json
{"id":"G04-L12","variant":"B0","width":5,"height":5,"bit_count":2,"floors":[[".....","####.",".....",".####","....."],[".....",".####",".....","####.","....."]],"initial":{"position":[0,0,0],"bits":3},"victory":{"position":[1,0,4],"bits":1,"pending":0,"all_beacons":true},"lifts":[[4,2]],"switches":[{"at":[0,2,0],"mask":2},{"at":[1,2,2],"mask":1},{"at":[1,1,4],"mask":1}],"gates":[{"at":[0,4,1],"bit":0,"value":1},{"at":[1,4,3],"bit":1,"value":0}],"beacons":[],"move_limit":23,"par":15,"solution":["R","R","R","R","D","D","X","D","D","L","L","L","R","L","L"]}
```

### G04-L13 断桥与旁路

```json
{"id":"G04-L13","variant":"B0","width":5,"height":5,"bit_count":2,"floors":[[".....",".###.",".....","####.","....."],[".....","####.",".....",".####","....."]],"initial":{"position":[0,0,0],"bits":0},"victory":{"position":[0,0,4],"bits":3,"pending":0,"all_beacons":true},"lifts":[[4,0],[0,2],[4,4]],"switches":[{"at":[1,2,0],"mask":1},{"at":[1,2,4],"mask":2}],"gates":[{"at":[0,4,3],"bit":1,"value":1},{"at":[0,0,1],"bit":0,"value":1}],"beacons":[],"move_limit":39,"par":26,"solution":["R","R","R","R","X","L","L","R","R","D","D","L","L","L","L","D","D","R","R","R","R","X","L","L","L","L"]}
```

### G04-L14 位型不是颜色

```json
{"id":"G04-L14","variant":"B0","width":5,"height":5,"bit_count":3,"floors":[[".....","####.",".....",".####","....."],[".....",".####",".....","####.","....."]],"initial":{"position":[0,0,0],"bits":0},"victory":{"position":[1,0,4],"bits":5,"pending":0,"all_beacons":true},"lifts":[[4,2]],"switches":[{"at":[0,2,0],"mask":3},{"at":[1,2,2],"mask":6}],"gates":[{"at":[0,4,1],"bit":0,"value":1},{"at":[1,4,3],"bit":2,"value":1}],"beacons":[],"move_limit":26,"par":17,"solution":["R","R","R","R","D","D","X","L","L","R","R","D","D","L","L","L","L"]}
```

### G04-L15 目标下的门

```json
{"id":"G04-L15","variant":"B0","width":5,"height":5,"bit_count":3,"floors":[[".....","####.",".....",".####","....."],[".....",".####",".....","####.","....."]],"initial":{"position":[0,0,0],"bits":0},"victory":{"position":[1,0,4],"bits":7,"pending":0,"all_beacons":true},"lifts":[[4,2]],"switches":[{"at":[0,2,0],"mask":1},{"at":[0,3,2],"mask":2},{"at":[1,2,2],"mask":4}],"gates":[{"at":[0,4,1],"bit":0,"value":1},{"at":[1,4,3],"bit":1,"value":1},{"at":[1,0,4],"bit":2,"value":1}],"beacons":[],"move_limit":29,"par":19,"solution":["R","R","R","R","D","D","L","R","X","L","L","R","R","D","D","L","L","L","L"]}
```

### G04-L16 提前复位的代价

```json
{"id":"G04-L16","variant":"B0","width":5,"height":5,"bit_count":2,"floors":[[".....","####.",".....",".####","....."],[".....",".####",".....","####.","....."]],"initial":{"position":[0,0,0],"bits":0},"victory":{"position":[1,0,4],"bits":2,"pending":0,"all_beacons":true},"lifts":[[4,2],[0,4]],"switches":[{"at":[0,2,0],"mask":1},{"at":[0,3,2],"mask":2},{"at":[1,2,2],"mask":1}],"gates":[{"at":[0,4,1],"bit":0,"value":1},{"at":[1,4,3],"bit":0,"value":0},{"at":[1,0,4],"bit":1,"value":1}],"beacons":[],"move_limit":29,"par":19,"solution":["R","R","R","R","D","D","L","R","X","L","L","R","R","D","D","L","L","L","L"]}
```

### G04-L17 借道上层

```json
{"id":"G04-L17","variant":"B0","width":5,"height":5,"bit_count":3,"floors":[[".....",".###.",".....",".####","....."],[".....","####.",".....","####.","....."]],"initial":{"position":[0,0,0],"bits":0},"victory":{"position":[0,0,4],"bits":6,"pending":0,"all_beacons":true},"lifts":[[4,0],[4,2],[4,4]],"switches":[{"at":[1,2,0],"mask":3},{"at":[1,2,2],"mask":5}],"gates":[{"at":[0,0,1],"bit":0,"value":1},{"at":[0,0,3],"bit":1,"value":1},{"at":[0,0,4],"bit":2,"value":1}],"beacons":[],"move_limit":33,"par":22,"solution":["R","R","R","R","X","L","L","R","R","D","D","L","L","R","R","D","D","X","L","L","L","L"]}
```

### G04-L18 上下互换

```json
{"id":"G04-L18","variant":"B0","width":5,"height":5,"bit_count":2,"floors":[[".....","####.",".....",".####","....."],[".....",".####",".....","####.","....."]],"initial":{"position":[0,0,4],"bits":1},"victory":{"position":[1,4,0],"bits":2,"pending":0,"all_beacons":true},"lifts":[[0,2],[4,4]],"switches":[{"at":[0,2,2],"mask":3},{"at":[1,2,2],"mask":1},{"at":[1,0,0],"mask":1}],"gates":[{"at":[0,0,3],"bit":0,"value":1},{"at":[1,0,1],"bit":1,"value":1},{"at":[1,4,0],"bit":0,"value":0}],"beacons":[],"move_limit":23,"par":15,"solution":["U","U","R","R","L","L","X","U","U","R","L","R","R","R","R"]}
```

### G04-L19 三组循环锁

```json
{"id":"G04-L19","variant":"B0","width":5,"height":5,"bit_count":3,"floors":[[".....",".###.",".....","####.","....."],[".....","####.",".....",".####","....."]],"initial":{"position":[0,0,0],"bits":0},"victory":{"position":[0,0,4],"bits":7,"pending":0,"all_beacons":true},"lifts":[[4,0],[0,2],[4,4]],"switches":[{"at":[1,2,0],"mask":3},{"at":[1,2,2],"mask":5},{"at":[1,2,4],"mask":1}],"gates":[{"at":[0,0,1],"bit":0,"value":1},{"at":[0,4,3],"bit":2,"value":1},{"at":[0,0,4],"bit":1,"value":1}],"beacons":[],"move_limit":39,"par":26,"solution":["R","R","R","R","X","L","L","R","R","D","D","L","L","L","L","D","D","R","R","R","R","X","L","L","L","L"]}
```

### G04-L20 折光总控

```json
{"id":"G04-L20","variant":"B0","width":5,"height":5,"bit_count":3,"floors":[[".....",".###.",".....",".###.","....."],[".....","####.",".....",".####","....."]],"initial":{"position":[0,0,0],"bits":0},"victory":{"position":[0,0,4],"bits":7,"pending":0,"all_beacons":true},"lifts":[[4,0],[0,2],[4,4]],"switches":[{"at":[1,2,0],"mask":3},{"at":[1,2,2],"mask":6},{"at":[1,2,4],"mask":2},{"at":[0,2,2],"mask":1}],"gates":[{"at":[0,0,1],"bit":0,"value":1},{"at":[0,0,3],"bit":2,"value":1},{"at":[0,0,4],"bit":1,"value":1},{"at":[1,4,1],"bit":1,"value":1}],"beacons":[],"move_limit":27,"par":18,"solution":["R","R","R","R","D","D","L","L","L","L","X","R","R","L","L","X","D","D"]}
```

## 可分离实验的精确夹具

### G04-X1-A 顺序双信标

相同位置输入在不同信标进度可能失败。

```json
{"id":"G04-X1-A","name":"顺序双信标","variant":"X1","width":3,"height":3,"bit_count":1,"floors":[["...","...","..."],["###","...","###"]],"initial":{"position":[0,0,1],"bits":0},"victory":{"position":[1,0,1],"bits":0,"pending":0,"all_beacons":true},"lifts":[[2,1]],"switches":[],"gates":[],"beacons":[[0,1,0],[0,1,2]],"move_limit":14,"par":9,"solution":["U","R","D","D","U","R","X","L","L"],"design_intent":"相同位置输入在不同信标进度可能失败"}
```

### G04-X2-A 一拍后生效

门在开关后一格；延迟版必须借旁路等待一次合法移动，不能用空等或无效输入推进。

```json
{"id":"G04-X2-A","name":"一拍后生效","variant":"X2","width":4,"height":3,"bit_count":1,"floors":[["....","....","####"],["....","####","####"]],"initial":{"position":[0,0,0],"bits":0},"victory":{"position":[1,0,0],"bits":1,"pending":0,"all_beacons":true},"lifts":[[3,0]],"switches":[{"at":[0,1,0],"mask":1}],"gates":[{"at":[0,2,0],"bit":0,"value":1}],"beacons":[],"move_limit":14,"par":9,"solution":["R","D","R","U","R","X","L","L","L"],"design_intent":"门在开关后一格；延迟版必须借旁路等待一次合法移动，不能用空等或无效输入推进"}
```

X1同几何B0对照：复制G04-X1-A、variant设B0、beacons清空，其他目标不变。X2同几何B0对照：复制G04-X2-A、variant设B0。对照先重新求解par再给相同相对宽松度的预算，不拿不同最短步数直接比较耗时优劣。二者各自与B0比较，绝不混为X1+X2。

## 作者工具建议与内容验收

未来工具最低范围是导入/导出本地JSON、并排两层编辑、位开关预览、门/开关详情、完整目标面板、解路径/可达态可视化、BFS验解；不需要通用引擎或云协作。导出必须标记ruleVersion/contentHash，保存前检查Schema、地面引用、起点支撑、有效目标、重叠、掩码越位、解合法、预算及最短步。以hash区分关卡改版，不能按名字相同静默覆盖。

验收关注两类错误：无解/语义冲突为BLOCKER；存在捷径绕过计划教学为MAJOR，需人工审查求解器路径再决定是否修图。L20存在较短综合路线，当前保留为审计题，不宣称复杂度最高。目标要同时有位置和位型；可达出口但位型不对是设计内假终点，UI须显示缺哪一位。

## 无虚构收益的成本模型

没有参考游戏内部经济参数。G04无玩家付费经济；制作成本变量为人力天数×日成本+AI工具+原创资产+设备测试+法务+维护，值均待实支。预算估计仅任务HYPOTHESIS，不能当真实投入。项目净贡献=实际净许可+实际净分成-全部成本；无收入证据时只填UNKNOWN，不用平台总体流量倒推。各渠道净收益口径见11。

## 重跑

在本目录执行 `python -B validate_spec.py`。成功才会更新validation-report；检查其中result、输入SHA-256、每关终态/最短步。报告不代表Cocos构建、浏览器回放、实机性能或真人难度通过。

## r2重复解与机关消融的诚实边界（minor2）

20个ID是20份具体原创配置，不等于20种独立策略。固定最短见证有四对完全相同：L08/09、L11/14、L13/19、L15/16。保留的意图如下；这些是事后明确的内容假设，不伪称最初已预登记的实验。

| 重复对 / 同解长度 | 配置差别与拟考察理解 | 不能据此声称 |
|---|---|---|
| L08/09 / 11 | L08掩码1再2得到3；L09掩码3再1得到2；同走法对照独立翻位与联合翻位 | 新路线策略、不同难度或联合掩码更有趣 |
| L11/14 / 17 | L11运输阶段A反相；L14掩码3 XOR 6得到5，位型解释由单组变联合组 | 走路更复杂，三位必然更难 |
| L13/19 / 26 | 同几何见证；L13终值3，L19经3/5/1得到7，重新解释每个位是否满足 | 后者路线新颖或必然是更难综合题 |
| L15/16 / 19 | L15保留7且出口门C1；L16运输A最终复位到B=1/A=0，另有升降台可选 | 同解就毫无规则差别，或差别已被玩家理解 |

离线删门对照只把gates置空，保留地形、开关、初值、精确目标与预算；逐关重求最短，记录于validation-report.contracts.gate_ablation。15/20最短长度不变。变化为L05 9→5、L11 17→15、L13 26→24、L16 19→15、L20 18→14。这说明门对其中5题的最短路线有约束，**不能证明15题门没有任何作用**（支路/失败状态仍可能改变），也不能声称门是20题最短解的必要机制。L20原18步比L19的26步短，不拿关号或掩码数冒充难度。

未来T13独立于X1/X2机制实验，在local-qa用原创抽象界面做“原门/无门”理解观察：同几何版本先重新验解，顺序平衡，按各自par比较；记录能否在行动前解释门受哪位控制、是否只复述上一题走法、四对中能否说出终值与翻位的差别。此为H02内容诊断，不是已完成的预览/门效果证明。若12个有效观察中至少4人把后题描述为机械照走且说不出位型差别，则重复对不计新增认知内容，先合并/重画后两题并重新求解；若删门也不影响解释/决策，不再宣传这些题“依赖门规划”。未经批准本轮不开发实验界面。体验结果目前UNKNOWN，具体重画由研究结果与独立审计决定，不为凑20题改名自证。
