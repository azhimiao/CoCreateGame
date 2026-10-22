extends RefCounted
class_name MechanicFixtures

const LEVELS: Array[Dictionary] = [
	{
		"id": "G04-L01",
		"name": "第一束光",
		"chapter": "校准台",
		"subtitle": "翻转共享位，再穿过另一层的门。",
		"width": 3,
		"height": 3,
		"bit_count": 1,
		"floors": [["###", "...", "###"], ["###", "...", "###"]],
		"start": [0, 0, 1],
		"goal": [1, 2, 1],
		"start_bits": 0,
		"goal_bits": 1,
		"move_limit": 8,
		"par": 3,
		"time_limit": 45,
		"lifts": [[1, 1]],
		"switches": [{"at": [0, 1, 1], "mask": 1}],
		"switch_mode_by_layer": ["instant", "instant"],
		"gates": [{"at": [1, 1, 1], "bit": 0, "value": 1}],
		"sealed_gates": [],
		"items": [],
		"beacons": [],
		"currents": [],
		"environment": ["导电下层", "折射上层"],
		"rule_note": "开关位 A 在两层共用；X 只在升降台上切层。",
		"tutorial": [
			"移动：点击光标相邻的地面，或使用方向键。深色‘空’格没有地面，不能进入。",
			"踩到‘翻A’开关时，落地后机关位 A 会在 0 和 1 之间切换。",
			"‘A=1’表示只有 A 为 1 时门才有支撑。左上目标面板会显示 A 的当前值。",
			"站在‘升降’格按 X，可切到另一层同一坐标。到达出口且位型符合目标即可通关。"
		],
		"solution": ["R", "X", "R"]
	},
	{
		"id": "G04-L02",
		"name": "离子回声",
		"chapter": "相位温室",
		"subtitle": "先取钥匙，按序点亮信标，再等延迟位落定。",
		"width": 4,
		"height": 3,
		"bit_count": 2,
		"floors": [["####", "....", "####"], ["####", "....", "####"]],
		"start": [0, 0, 1],
		"goal": [1, 3, 1],
		"start_bits": 0,
		"goal_bits": 3,
		"move_limit": 12,
		"par": 8,
		"time_limit": 90,
		"lifts": [[0, 1]],
		"switches": [
			{"at": [0, 2, 1], "mask": 1},
			{"at": [1, 1, 1], "mask": 2}
		],
		"switch_mode_by_layer": ["instant", "delayed"],
		"gates": [{"at": [1, 3, 1], "bit": 1, "value": 1}],
		"sealed_gates": [{"id": "opal", "at": [1, 3, 1]}],
		"items": [{"id": "phase_key", "type": "key", "at": [0, 2, 1], "name": "棱镜钥匙"}],
		"beacons": [[1, 1, 1], [1, 2, 1]],
		"currents": [],
		"environment": ["导电层 · 即时翻位", "离子层 · 延迟一手"],
		"rule_note": "进入离子层开关会排队；下一步落位后才翻位。",
		"tutorial": [
			"先在下层取到‘钥匙’，然后返回升降台。钥匙只用于打开对应的钥匙门。",
			"按顺序踩亮‘信标1’、‘信标2’；提前踩到后一个信标会失败。",
			"下层导电开关在本次落地后翻位；上层离子开关会等下一次有效落地后才翻位。左上‘待生效’会提示排队中的位。",
			"‘门B=1’需要 B=1。抵达门格时钥匙会打开锁；出口还要求两个目标位都匹配。"
		],
		"solution": ["R", "R", "L", "L", "X", "R", "R", "R"]
	},
	{
		"id": "G04-L03",
		"name": "逆流锚点",
		"chapter": "矢量走廊",
		"subtitle": "锚定晶片只够一次，留给逆流离开的那一步。",
		"width": 4,
		"height": 3,
		"bit_count": 2,
		"floors": [["####", "....", "####"], ["####", "....", "####"]],
		"start": [0, 0, 1],
		"goal": [1, 0, 1],
		"start_bits": 0,
		"goal_bits": 3,
		"move_limit": 12,
		"par": 7,
		"time_limit": 90,
		"lifts": [[3, 1]],
		"switches": [{"at": [0, 1, 1], "mask": 3}],
		"switch_mode_by_layer": ["instant", "instant"],
		"gates": [],
		"sealed_gates": [],
		"items": [{"id": "anchor_shard", "type": "anchor", "at": [0, 1, 1], "name": "相位锚片"}],
		"beacons": [],
		"currents": [{"at": [1, 2, 1], "dir": "R"}],
		"environment": ["静稳平台", "矢量折流 · 只准顺流离开"],
		"rule_note": "逆流离开折流格会消耗一片锚片；切层不受风向限制。",
		"tutorial": [
			"踩到‘锚片’后会获得一次逆流通行机会，底部道具栏会显示剩余次数。",
			"带箭头的折流格只能顺箭头离开。逆向离开会消耗一片锚片；无锚片时该操作会被拒绝且不扣步。",
			"道具和机关可以在同一地块上，格内会同时显示。撤销会恢复位置、位型和道具状态。",
			"按 X 只会在升降台切层，不受折流方向影响。到达出口并匹配目标位型即可完成。"
		],
		"solution": ["R", "R", "R", "X", "L", "L", "L"]
	},
	{
		"id": "G04-L04",
		"name": "双轨摆渡",
		"chapter": "潮汐轨道",
		"subtitle": "上下两条轨道反向移动；落在平台上会被带着前进。",
		"width": 5,
		"height": 5,
		"bit_count": 1,
		"floors": [
			[".####", "#####", ".....", "#####", "###.."],
			["#####", "#####", ".....", "#####", "#####"]
		],
		"start": [0, 0, 0],
		"goal": [0, 3, 4],
		"start_bits": 0,
		"goal_bits": 0,
		"move_limit": 12,
		"par": 6,
		"time_limit": 90,
		"lifts": [[2, 2]],
		"switches": [],
		"switch_mode_by_layer": ["instant", "instant"],
		"gates": [],
		"sealed_gates": [],
		"items": [],
		"beacons": [],
		"currents": [],
		"moving_period": 5,
		"moving_rows": [
			{"layer": 0, "y": 1, "tiles": [0, 1], "direction": 1, "name": "上轨"},
			{"layer": 0, "y": 3, "tiles": [3, 4], "direction": -1, "name": "下轨"}
		],
		"environment": ["上轨 向右 · 下轨 向左", "中央缓冲台 · 可切层观察"],
		"rule_note": "每次有效移动后两条轨道各移动一格；棋子在轨道上时会随地块同行。",
		"tutorial": [
			"先看下层的‘上轨’和‘下轨’：每条由两个平台组成，初始方向相反。",
			"每次有效移动后，两条轨道都前进一步；上轨向右，下轨向左，到边缘后绕回。",
			"若落在移动地块上，棋子会随它一起走一格。左上目标面板会显示轨道相位；撤销也会倒回相位。",
			"从起点借上轨抵达中央，再观察相位搭上下轨到出口。深色空格没有支撑，不能走。"
		],
		"solution": ["D", "R", "D", "R", "D", "D"]
	}
]

static func get_level(index: int) -> Dictionary:
	return LEVELS[clampi(index, 0, LEVELS.size() - 1)].duplicate(true)

static func position_key(position: Array) -> String:
	return "%d,%d,%d" % [int(position[0]), int(position[1]), int(position[2])]
