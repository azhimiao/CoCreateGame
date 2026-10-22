extends RefCounted
class_name GameRules

const DIRECTIONS := {
	"U": Vector2i(0, -1),
	"R": Vector2i(1, 0),
	"D": Vector2i(0, 1),
	"L": Vector2i(-1, 0)
}

static func create_state(level: Dictionary) -> Dictionary:
	return {
		"pos": level.start.duplicate(),
		"phase": 0,
		"bits": int(level.start_bits),
		"pending": 0,
		"beacon_index": 0,
		"key_owned": false,
		"opened_gates": [],
		"anchor_charges": 0,
		"collected": [],
		"used": 0,
		"status": "playing",
		"failure": "",
		"assisted": false
	}

static func try_action(level: Dictionary, state: Dictionary, action: String) -> Dictionary:
	if state.status != "playing":
		return _reject("本局已結束")
	if not DIRECTIONS.has(action) and action != "X":
		return _reject("未知操作")

	var destination: Array = state.pos.duplicate()
	if action == "X":
		var lift_found := false
		for lift in level.lifts:
			if int(lift[0]) == int(state.pos[1]) and int(lift[1]) == int(state.pos[2]):
				lift_found = true
				break
		if not lift_found:
			return _reject("此處沒有升降台")
		destination[0] = 1 - int(destination[0])
	else:
		var current_key := LevelCatalog.position_key(state.pos)
		var current_flow: Dictionary = _current_at(level, current_key)
		if not current_flow.is_empty() and action != String(current_flow.dir):
			if int(state.anchor_charges) <= 0:
				return _reject("折流場只允許沿箭頭離開")
			var delta: Vector2i = DIRECTIONS[action]
			var flow_delta: Vector2i = DIRECTIONS[String(current_flow.dir)]
			if delta != -flow_delta:
				return _reject("折流場只限制逆向離開")
		destination[1] = int(destination[1]) + int(DIRECTIONS[action].x)
		destination[2] = int(destination[2]) + int(DIRECTIONS[action].y)

	if not _is_supported(level, destination, int(state.bits), state):
		return _reject("目的格沒有支撐，或門尚未開啟")

	var next: Dictionary = state.duplicate(true)
	var from: Array = state.pos.duplicate()
	next.pos = destination
	next.used = int(next.used) + 1
	var ride_row := _moving_row_at_position(level, destination, int(state.phase))
	if not level.get("moving_rows", []).is_empty():
		next.phase = posmod(int(state.phase) + 1, int(level.moving_period))
		if not ride_row.is_empty():
			next.pos[1] = posmod(int(next.pos[1]) + int(ride_row.direction), int(level.width))

	if action != "X":
		var flow: Dictionary = _current_at(level, LevelCatalog.position_key(from))
		if not flow.is_empty() and action != String(flow.dir):
			next.anchor_charges = int(next.anchor_charges) - 1

	if int(next.pending) != 0:
		next.bits = int(next.bits) ^ int(next.pending)
		next.pending = 0
		if not _is_supported(level, next.pos, int(next.bits), next):
			next.status = "failed"
			next.beacon_index = 0
			next.failure = "延遲翻位關閉了腳下地板"
			return {"accepted": true, "state": next, "message": next.failure}

	_collect_items(level, next)
	_open_key_gate(level, next)

	for switch in level.switches:
		if LevelCatalog.position_key(switch.at) == LevelCatalog.position_key(next.pos):
			var layer_mode: String = String(level.switch_mode_by_layer[int(next.pos[0])])
			if layer_mode == "delayed":
				next.pending = int(next.pending) ^ int(switch.mask)
			else:
				next.bits = int(next.bits) ^ int(switch.mask)
			if not _is_supported(level, next.pos, int(next.bits), next):
				next.status = "failed"
				next.beacon_index = 0
				next.failure = "開關翻位關閉了腳下地板"
				return {"accepted": true, "state": next, "message": next.failure}
			break

	var beacon_result := _advance_beacon(level, next)
	if not beacon_result.ok:
		next.status = "failed"
		next.beacon_index = 0
		next.failure = "信標順序錯誤：先點亮下一枚信標"
		return {"accepted": true, "state": next, "message": next.failure}

	if _is_goal(level, next):
		next.status = "won"
		return {"accepted": true, "state": next, "message": "折光裝置已校準"}

	if int(next.used) >= int(level.move_limit):
		next.status = "failed"
		next.beacon_index = 0
		next.failure = "步数耗尽，未能抵达出口"
		return {"accepted": true, "state": next, "message": next.failure}

	return {"accepted": true, "state": next, "message": _arrival_message(level, next)}

static func find_hint(level: Dictionary, start_state: Dictionary) -> String:
	return HintSearch.find_action(level,start_state)

static func _reject(message: String) -> Dictionary:
	return {"accepted": false, "message": message}

static func _is_supported(level: Dictionary, position: Array, bits: int, state: Dictionary) -> bool:
	var layer := int(position[0])
	var x := int(position[1])
	var y := int(position[2])
	if layer < 0 or layer >= level.floors.size() or x < 0 or x >= int(level.width) or y < 0 or y >= int(level.height):
		return false
	if String(level.floors[layer][y]).substr(x, 1) != "." and _moving_row_at_position(level, position, int(state.phase)).is_empty():
		return false
	for gate in level.gates:
		if LevelCatalog.position_key(gate.at) == LevelCatalog.position_key(position):
			if ((bits >> int(gate.bit)) & 1) != int(gate.value):
				return false
	for sealed_gate in level.sealed_gates:
		if LevelCatalog.position_key(sealed_gate.at) == LevelCatalog.position_key(position):
			if state.opened_gates.has(String(sealed_gate.id)):
				continue
			if state.key_owned:
				continue
			return false
	return true

static func _moving_row_at_position(level: Dictionary, position: Array, phase: int) -> Dictionary:
	for row in level.get("moving_rows", []):
		if int(row.layer) != int(position[0]) or int(row.y) != int(position[2]):
			continue
		for start_x in row.tiles:
			var tile_x := posmod(int(start_x) + int(row.direction) * phase, int(level.width))
			if tile_x == int(position[1]):
				return row
	return {}

static func _current_at(level: Dictionary, position_key: String) -> Dictionary:
	for current in level.currents:
		if LevelCatalog.position_key(current.at) == position_key:
			return current
	return {}

static func _collect_items(level: Dictionary, state: Dictionary) -> void:
	for item in level.items:
		if LevelCatalog.position_key(item.at) != LevelCatalog.position_key(state.pos) or state.collected.has(String(item.id)):
			continue
		state.collected.append(String(item.id))
		if item.type == "key":
			state.key_owned = true
		elif item.type == "anchor":
			state.anchor_charges = int(state.anchor_charges) + 1

static func _open_key_gate(level: Dictionary, state: Dictionary) -> void:
	if not state.key_owned:
		return
	for gate in level.sealed_gates:
		if LevelCatalog.position_key(gate.at) == LevelCatalog.position_key(state.pos) and not state.opened_gates.has(String(gate.id)):
			state.key_owned = false
			state.opened_gates.append(String(gate.id))
			return

static func _advance_beacon(level: Dictionary, state: Dictionary) -> Dictionary:
	if level.beacons.is_empty():
		return {"ok": true}
	var current_key := LevelCatalog.position_key(state.pos)
	for index in range(level.beacons.size()):
		if LevelCatalog.position_key(level.beacons[index]) != current_key:
			continue
		if index < int(state.beacon_index):
			return {"ok": true}
		if index > int(state.beacon_index):
			return {"ok": false}
		state.beacon_index = int(state.beacon_index) + 1
		return {"ok": true}
	return {"ok": true}

static func _is_goal(level: Dictionary, state: Dictionary) -> bool:
	return state.status != "failed" \
		and LevelCatalog.position_key(state.pos) == LevelCatalog.position_key(level.goal) \
		and int(state.bits) == int(level.goal_bits) \
		and int(state.pending) == 0 \
		and int(state.beacon_index) == level.beacons.size()

static func _state_key(state: Dictionary) -> String:
	var opened: Array = state.opened_gates.duplicate()
	var collected: Array = state.collected.duplicate()
	opened.sort()
	collected.sort()
	return "%s|%d|%d|%d|%s|%s|%d|%d|%s" % [
		LevelCatalog.position_key(state.pos), int(state.bits), int(state.pending), int(state.beacon_index),
		str(state.key_owned), ",".join(opened), int(state.anchor_charges), int(state.phase), ",".join(collected)
	]

static func _arrival_message(level: Dictionary, state: Dictionary) -> String:
	if int(state.pending) != 0:
		return "延迟翻位将在下一步落位后生效"
	if state.key_owned:
		return "棱镜钥匙已就位"
	return "继续规划折射路径"
