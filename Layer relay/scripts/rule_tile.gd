extends BoardView
class_name RuleTile

var kind := "switch"
var fulfilled := false

func _ready() -> void:
	custom_minimum_size = Vector2(148, 124)
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	set_process(false)
	level = LevelCatalog.get_level(1)
	level.lifts = []
	level.switches = []
	level.gates = []
	level.sealed_gates = []
	level.items = []
	level.beacons = []
	level.currents = []
	level.moving_rows = []
	level.bit_count = 2
	level.goal_bits = 3
	level.switch_mode_by_layer = ["instant","instant"]
	level.goal = [1, 3, 2]
	state = GameRules.create_state(level)
	state.bits = 3 if fulfilled else 0
	match kind:
		"switch": level.switches = [{"at": [0, 1, 1], "mask": 1}]
		"delayed":
			level.switches = [{"at": [0, 1, 1], "mask": 2}]
			level.switch_mode_by_layer[0] = "delayed"
		"lift": level.lifts = [[1, 1]]
		"gate": level.gates = [{"at": [0, 1, 1], "bit": 0, "value": 1}]
		"key": level.items = [{"id": "sample", "at": [0, 1, 1], "type": "key"}]
		"anchor": level.items = [{"id": "sample", "at": [0, 1, 1], "type": "anchor"}]
		"beacon":
			level.beacons = [[0, 1, 1]]
			state.beacon_index = 1 if fulfilled else 0
		"flow": level.currents = [{"at": [0, 1, 1], "dir": "R"}]
		"goal": level.goal = [0, 1, 1]
	queue_redraw()

func _draw() -> void:
	if state.is_empty():
		return
	_tile_w = 110
	_tile_h = 55
	var center := size * Vector2(0.5, 0.67)
	var moving := {"layer": 0, "direction": 1} if kind == "platform" else {}
	_draw_tile(0, 1, 1, center, kind != "void", moving, false, GENERATION_CELL_DURATION)
	if kind == "platform":
		_draw_inlay(center, Color("436f8a"))
		_draw_flow_mark(center, Vector2(1, 0.53).normalized())
	elif kind != "void":
		_draw_cell_marks([0, 1, 1], center, true, {})
	if kind == "beacon":
		_draw_beacon_marker(center, 0)
