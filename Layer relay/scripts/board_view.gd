extends Control
class_name BoardView

signal cell_pressed(layer: int, x: int, y: int)
signal preview_pressed(layer: int)
signal layer_changed(layer: int)
signal animation_finished
signal completion_finished
signal environment_changed
signal failure_finished

const FLOOR_TOP := Color("d5e1df")
const FLOOR_EDGE := Color("7f9695")
const FLOOR_VOID := Color("101b21")
const FLOOR_LINE := Color("455b61")
const ACCENT := Color("66dec9")
const GOLD := Color("f2cc72")
const GENERATION_WAVE_DELAY := 0.105
const GENERATION_EDGE_DURATION := 0.32
const GENERATION_WHITE_HOLD := GENERATION_WAVE_DELAY * 3.5
const GENERATION_BLUE_HOLD := 0.07
const GENERATION_CELL_DURATION := GENERATION_EDGE_DURATION + GENERATION_WHITE_HOLD + GENERATION_BLUE_HOLD + 0.03
const VIEW_TRANSITION_DURATION := 0.52
const ROW_TRANSITION_DURATION := 0.48
const COMPLETION_DURATION := 1.6
const ENVIRONMENT_DURATION := 0.28
const STATUS_FADE_DURATION := 0.6
const PLAYER_SPAWN_DURATION := 0.72
const FAILURE_DURATION := 1.15

var level: Dictionary = {}
var state: Dictionary = {}
var selected_layer := 0
var hint_action := ""
var busy := false
var paused := false
var _environment_before: Dictionary = {}
var _status_fade_active := false
var _status_fade_elapsed := 0.0
var _switch_fade_from: Dictionary = {}
var _beacon_fade_from: Dictionary = {}
var _player_spawn_active := false
var _player_spawn_elapsed := 0.0

var _mode := ""
var _elapsed := 0.0
var _duration := 0.0
var _from_pos: Array = []
var _to_pos: Array = []
var _move_axis := "x"
var _move_action := "R"
var _carry_from: Array = []
var _carry_to: Array = []
var _stage := 0
var _layer_switched := false
var _pending_state: Dictionary = {}
var _pending_layer := 0
var _sink_pos: Array = []
var _hover := Vector2i(-1, -1)
var _preview_rect := Rect2()
var _tile_w := 96.0
var _tile_h := 50.0
var _board_origin := Vector2.ZERO
var _generation_level_id := ""
var _generation_elapsed := 0.0
var _generation_duration := 0.0
var _generation_active := false
var _view_transition_active := false
var _view_transition_elapsed := 0.0
var _view_from_layer := 0
var _view_to_layer := 0
var _view_switched := false
var _row_transition_pending := false
var _row_transition_active := false
var _phase_before := 0
var _phase_after := 0
var _visual_time := 0.0
var _completion_active := false
var _completion_elapsed := 0.0
var _failure_active := false
var _failure_elapsed := 0.0

func _ready() -> void:
	custom_minimum_size = Vector2(680, 520)
	mouse_filter = Control.MOUSE_FILTER_STOP
	set_process(true)

func set_context(level_data: Dictionary, game_state: Dictionary, layer: int, hint: String) -> void:
	var incoming_id := String(level_data.get("id", ""))
	if incoming_id != _generation_level_id:
		_completion_active = false
		_completion_elapsed = 0.0
		_generation_level_id = incoming_id
		_generation_elapsed = 0.0
		var last_wave := maxi(0, int(level_data.get("width", 1)) + int(level_data.get("height", 1)) - 2)
		_generation_duration = float(last_wave) * GENERATION_WAVE_DELAY + GENERATION_CELL_DURATION
		_generation_active = true
		_player_spawn_active = false
		_player_spawn_elapsed = 0.0
		_status_fade_active = false
		_switch_fade_from.clear()
		_beacon_fade_from.clear()
	level = level_data
	hint_action = hint
	if not state.is_empty() and state.pos != game_state.pos:
		_hover = Vector2i(-1, -1)
	if busy:
		_pending_state = game_state.duplicate(true)
		_pending_layer = int(game_state.pos[0])
		return
	if not state.is_empty() and not _generation_active and (state.bits != game_state.bits or state.beacon_index != game_state.beacon_index):
		_start_status_fade(game_state)
	state = game_state.duplicate(true)
	if not _view_transition_active:
		selected_layer = layer
	queue_redraw()

func animate_layer_view(layer: int) -> void:
	if is_animating() or layer == selected_layer or layer < 0 or layer >= level.floors.size():
		return
	_begin_view_transition(layer)
	queue_redraw()

func reset_view(layer: int, spawn_player := false) -> void:
	_failure_active = false
	_failure_elapsed = 0.0
	_completion_active = false
	_completion_elapsed = 0.0
	_view_transition_active = false
	_view_transition_elapsed = 0.0
	_view_from_layer = layer
	_view_to_layer = layer
	_view_switched = false
	selected_layer = layer
	_hover = Vector2i(-1, -1)
	if spawn_player:
		_start_player_spawn()
	queue_redraw()

func _begin_view_transition(layer: int) -> void:
	_view_transition_active = true
	_view_transition_elapsed = 0.0
	_view_from_layer = selected_layer
	_view_to_layer = layer
	_view_switched = false

func play_action(level_data: Dictionary, before: Dictionary, after: Dictionary, action: String, hint: String) -> void:
	if is_animating():
		return
	level = level_data
	hint_action = hint
	busy = true
	_elapsed = 0.0
	_pending_state = after.duplicate(true)
	_environment_before = before.duplicate(true)
	_phase_before = int(before.get("phase", 0))
	_phase_after = int(after.get("phase", _phase_before))
	_row_transition_pending = not level.get("moving_rows", []).is_empty() and _phase_before != _phase_after
	_row_transition_active = false
	if before.pos == after.pos and after.status == "failed":
		state = before.duplicate(true)
		_begin_environment()
		return
	var old_layer := int(before.pos[0])
	var new_layer := int(after.pos[0])
	_pending_layer = new_layer
	if action == "X":
		_mode = "layer"
		_stage = 0
		_layer_switched = false
		_duration = 0.52
		state = before.duplicate(true)
		selected_layer = old_layer
		_from_pos = before.pos.duplicate()
		_to_pos = after.pos.duplicate()
		_sink_pos = before.pos.duplicate()
		_carry_from = after.pos.duplicate()
		_carry_to = after.pos.duplicate()
	else:
		_mode = "hop"
		_stage = 0
		_duration = 0.40
		state = before.duplicate(true)
		if selected_layer != old_layer:
			selected_layer = old_layer
			layer_changed.emit(selected_layer)
		_from_pos = before.pos.duplicate()
		_to_pos = after.pos.duplicate()
		_move_axis = "x" if int(before.pos[1]) != int(after.pos[1]) else "y"
		_move_action = action
		_sink_pos = after.pos.duplicate()
		_carry_from = after.pos.duplicate()
		var carry_to: Array = after.pos.duplicate()
		if _row_transition_pending and action != "X":
			var delta: Vector2i = GameRules.DIRECTIONS[action]
			var landing: Array = before.pos.duplicate()
			landing[1] = int(landing[1]) + delta.x
			landing[2] = int(landing[2]) + delta.y
			var ride_row := GameRules._moving_row_at_position(level, landing, _phase_before)
			if not ride_row.is_empty():
				_carry_from = landing
				_to_pos = landing
				_sink_pos = landing.duplicate()
			_carry_to = carry_to
	if _view_transition_active:
		_view_transition_active = false
	queue_redraw()

func is_animating() -> bool:
	return busy or is_revealing() or _status_fade_active or _view_transition_active or _completion_active or _failure_active

func is_revealing() -> bool:
	return _generation_active or _player_spawn_active

func _start_player_spawn() -> void:
	_player_spawn_active = true
	_player_spawn_elapsed = 0.0

func _player_spawn_amount() -> float:
	if _generation_active:
		return 0.0
	return _ease_in_out(_player_spawn_elapsed / PLAYER_SPAWN_DURATION) if _player_spawn_active else 1.0

func _start_status_fade(after: Dictionary) -> void:
	# Sample what is currently visible, including a partially completed reverse transition.
	var switch_sources: Dictionary = {}
	var beacon_sources: Dictionary = {}
	for switch in level.switches:
		var mask := int(switch.mask)
		var visible := _switch_match_amount(mask)
		var target := float((int(after.bits) & mask) == (int(level.goal_bits) & mask))
		if not is_equal_approx(visible, target):
			switch_sources[mask] = visible
	for index in range(level.beacons.size()):
		var visible := _beacon_light_amount(index)
		var target := float(index < int(after.beacon_index))
		if not is_equal_approx(visible, target):
			beacon_sources[index] = visible
	_switch_fade_from = switch_sources
	_beacon_fade_from = beacon_sources
	_status_fade_elapsed = 0.0
	_status_fade_active = not switch_sources.is_empty() or not beacon_sources.is_empty()

func _status_amount(source: Dictionary, key: int, target: float) -> float:
	if not _status_fade_active or not source.has(key):
		return target
	return lerpf(float(source[key]), target, _ease_in_out(_status_fade_elapsed / STATUS_FADE_DURATION))

func _switch_match_amount(mask: int) -> float:
	return _status_amount(_switch_fade_from, mask, float(_switch_goal_matched(mask)))

func _beacon_light_amount(index: int) -> float:
	return _status_amount(_beacon_fade_from, index, float(index < int(state.get("beacon_index", 0))))

func start_completion() -> void:
	if is_animating() or state.get("status", "playing") != "won":
		return
	selected_layer = int(state.pos[0])
	_completion_elapsed = 0.0
	_completion_active = true
	queue_redraw()

func display_phase() -> int:
	return _board_phase()

func start_failure() -> void:
	if is_animating() or state.get("status", "playing") != "failed":
		return
	selected_layer = int(state.pos[0])
	_failure_active = true
	_failure_elapsed = 0.0
	queue_redraw()

func _process(delta: float) -> void:
	if paused:
		return
	_visual_time += delta
	var needs_redraw := true
	if _failure_active:
		_failure_elapsed += delta
		if _failure_elapsed >= FAILURE_DURATION:
			_failure_active = false
			failure_finished.emit()
	if _status_fade_active:
		_status_fade_elapsed += delta
		if _status_fade_elapsed >= STATUS_FADE_DURATION:
			_status_fade_active = false
	if _player_spawn_active:
		_player_spawn_elapsed += delta
		if _player_spawn_elapsed >= PLAYER_SPAWN_DURATION:
			_player_spawn_active = false
	if _completion_active:
		_completion_elapsed += delta
		if _completion_elapsed >= COMPLETION_DURATION:
			_completion_active = false
			completion_finished.emit()
	if _generation_active:
		_generation_elapsed += delta
		if _generation_elapsed >= _generation_duration:
			_generation_active = false
			_start_player_spawn()
			_player_spawn_elapsed = maxf(0.0, _generation_elapsed - _generation_duration)
			_player_spawn_active = _player_spawn_elapsed < PLAYER_SPAWN_DURATION
		needs_redraw = true
	if _view_transition_active:
		_view_transition_elapsed += delta
		needs_redraw = true
		if not _view_switched and _view_transition_elapsed >= VIEW_TRANSITION_DURATION * 0.5:
			_view_switched = true
			selected_layer = _view_to_layer
			if busy and _mode == "layer":
				state.pos = _to_pos.duplicate()
			layer_changed.emit(selected_layer)
		if _view_transition_elapsed >= VIEW_TRANSITION_DURATION:
			_view_transition_active = false
			selected_layer = _view_to_layer
			needs_redraw = true
	if not busy:
		if needs_redraw:
			queue_redraw()
		return
	_elapsed += delta
	if _mode == "layer" and _stage == 0 and _elapsed >= _duration:
		_elapsed = 0.0
		_stage = 1
		_duration = VIEW_TRANSITION_DURATION
		_layer_switched = false
		_begin_view_transition(_pending_layer)
		queue_redraw()
		return
	if _mode == "layer" and _stage == 1:
		if _elapsed >= _duration:
			_elapsed -= _duration
			_stage = 2
			_duration = 0.72
			queue_redraw()
			return
	if _mode == "hop" and _elapsed >= _duration and _elapsed < _duration + 0.20:
		queue_redraw()
		return
	if _mode == "hop" and _elapsed >= _duration + 0.20 and _row_transition_pending:
		_begin_row_transition()
		return
	if _mode == "layer" and _stage == 2 and _elapsed >= _duration and _row_transition_pending:
		_begin_row_transition()
		return
	if _mode == "rows" and _elapsed >= _duration:
		_begin_environment()
		return
	if _elapsed >= _duration:
		if _mode == "environment":
			_finish_animation()
		else:
			_begin_environment()
		return
	queue_redraw()

func _begin_row_transition() -> void:
	_mode = "rows"
	_elapsed = 0.0
	_duration = ROW_TRANSITION_DURATION
	_row_transition_active = true
	queue_redraw()

func _begin_environment() -> void:
	# Rules calculate a complete next state; presentation commits it only after all travel.
	var changed := false
	for key in ["bits", "pending", "beacon_index", "key_owned", "opened_gates", "anchor_charges", "collected"]:
		if _environment_before.get(key) != _pending_state.get(key):
			changed = true
	_start_status_fade(_pending_state)
	state = _pending_state.duplicate(true)
	_row_transition_active = false
	_row_transition_pending = false
	_mode = "environment"
	_elapsed = 0.0
	_duration = STATUS_FADE_DURATION if _status_fade_active else ENVIRONMENT_DURATION
	environment_changed.emit()
	if not changed:
		_finish_animation()
	else:
		queue_redraw()

func _finish_animation() -> void:
	state = _pending_state.duplicate(true)
	selected_layer = int(state.pos[0])
	busy = false
	_mode = ""
	_row_transition_pending = false
	_row_transition_active = false
	_pending_state.clear()
	queue_redraw()
	animation_finished.emit()

func _draw() -> void:
	if level.is_empty() or state.is_empty():
		return
	var panel := StyleBoxFlat.new()
	panel.bg_color = Color("111c22")
	panel.border_color = Color("34484f")
	panel.set_border_width_all(1)
	panel.set_corner_radius_all(8)
	draw_style_box(panel, Rect2(Vector2(3, 3), size - Vector2(6, 6)))
	_draw_ambient_grid()
	if _view_transition_active:
		_draw_view_transition()
		_draw_heading()
		return
	else:
		_draw_board(selected_layer, _main_grid_area(), 1.0, false, false)
		_draw_heading()
		_draw_preview()
	if is_revealing():
		if _player_spawn_active and int(state.pos[0]) == selected_layer:
			_draw_player_spawn()
	elif _mode == "hop":
		_draw_hop()
	elif _mode == "layer":
		_draw_layer_transition()
	elif _mode == "rows":
		_draw_carried_player()
	elif state.status == "failed" and _failure_elapsed > 0.0:
		_draw_failure_player()
	elif int(state.pos[0]) == selected_layer:
		_draw_player(_cell_center(state.pos) + Vector2(0, -24), 0.0, 1.0, 1.0)
	_draw_floating_beacons()
	if _mode == "environment":
		_draw_environment_effects()
	if _completion_active:
		_draw_completion()
	if _failure_active:
		_draw_failure_effects()

func _draw_player_spawn() -> void:
	var amount := _player_spawn_amount()
	var ground := _cell_center(state.pos)
	var center := ground + Vector2(0, -24.0 - 42.0 * (1.0 - amount))
	var glow := sin(PI * amount)
	_draw_ellipse(ground, _tile_w * (0.12 + amount * 0.20), _tile_h * (0.08 + amount * 0.12), Color(0.38, 0.95, 0.84, glow * 0.15))
	_draw_ellipse_outline(ground, _tile_w * (0.12 + amount * 0.20), _tile_h * (0.08 + amount * 0.12), Color(0.61, 1.0, 0.90, glow * 0.65), 1.5)
	_draw_player(center, 0.0, amount, 1.0)

func _draw_ambient_grid() -> void:
	var origin := Vector2(22, 0)
	for i in range(1, 8):
		var x := origin.x + size.x * float(i) / 8.0
		draw_line(Vector2(x, 0), Vector2(x, size.y), Color(0.24, 0.36, 0.39, 0.09), 1.0)
	for i in range(1, 6):
		var y := size.y * float(i) / 6.0
		draw_line(Vector2(0, y), Vector2(size.x, y), Color(0.24, 0.36, 0.39, 0.08), 1.0)

func _draw_heading() -> void:
	var font: Font = ThemeDB.fallback_font
	var layer_name := "下层" if selected_layer == 0 else "上层"
	var env: Array = level.get("environment", [])
	var subtitle := String(env[selected_layer]) if selected_layer < env.size() else ""
	draw_string(font, Vector2(24, 38), "主视图  /  " + layer_name, HORIZONTAL_ALIGNMENT_LEFT, -1, 18, Color("edf3ee"))
	draw_string(font, Vector2(24, 59), subtitle, HORIZONTAL_ALIGNMENT_LEFT, -1, 12, Color("9eb1b1"))

func _draw_view_transition() -> void:
	var t := clampf(_view_transition_elapsed / VIEW_TRANSITION_DURATION, 0.0, 1.0)
	var eased := t * t * (3.0 - 2.0 * t)
	var main_area := _main_grid_area()
	var mini_area := _preview_mini_area()
	var outgoing := _lerp_rect(main_area, mini_area, eased)
	var incoming := _lerp_rect(mini_area, main_area, eased)
	_draw_board(_view_from_layer, outgoing, 1.0, true, false, false)
	_draw_board(_view_to_layer, incoming, 1.0, true, false, false)
	_draw_player_marker(_view_from_layer, outgoing, true)
	_draw_player_marker(_view_to_layer, incoming, true)
	draw_rect(outgoing.grow(4), Color(0.43, 0.77, 0.72, 0.28 + (1.0 - eased) * 0.45), false, 1.5)
	draw_rect(incoming.grow(4), Color(0.43, 0.77, 0.72, 0.28 + eased * 0.45), false, 1.5)

func _lerp_rect(from_rect: Rect2, to_rect: Rect2, t: float) -> Rect2:
	return Rect2(from_rect.position.lerp(to_rect.position, t), from_rect.size.lerp(to_rect.size, t))

func _draw_player_marker(layer: int, area: Rect2, _thumbnail: bool) -> void:
	if int(state.pos[0]) != layer or busy or is_revealing():
		return
	var previous_w := _tile_w
	var previous_h := _tile_h
	var previous_origin := _board_origin
	_configure_board(layer, area, 1.0, true, false)
	var marker_scale := clampf(_tile_w / 96.0, 0.18, 1.0)
	var center := _cell_center(state.pos) + Vector2(0, -24.0 * marker_scale)
	_draw_player(center, 0.0, 1.0, marker_scale, marker_scale)
	_tile_w = previous_w
	_tile_h = previous_h
	_board_origin = previous_origin

func _draw_board(layer: int, area: Rect2, scale_factor: float, thumbnail: bool, reserve_preview: bool = true, show_marks: bool = true) -> void:
	var previous_w := _tile_w
	var previous_h := _tile_h
	var previous_origin := _board_origin
	_configure_board(layer, area, scale_factor, thumbnail, reserve_preview)
	var width := int(level.width)
	var height := int(level.height)
	var highlights := _action_highlights(layer) if show_marks else {}
	if not thumbnail and show_marks and _hover_is_movable(layer):
		highlights[Vector2i(_hover.x, _hover.y)] = "hover"
	var entries: Array[Dictionary] = []
	for y in range(height):
		for x in range(width):
			var cell := Vector2i(x, y)
			var position: Array = [layer, x, y]
			var moving := GameRules._moving_row_at_position(level, position, _board_phase())
			if _row_transition_active:
				moving = {}
			var supported := _is_floor(layer, x, y) or not moving.is_empty()
			if supported:
				entries.append({"cell": cell, "x": float(x), "y": float(y), "moving": moving, "animated": false, "depth": _entry_depth(float(x), float(y), false)})
			else:
				var cell_elapsed := _generation_elapsed - float(x + y) * GENERATION_WAVE_DELAY
				if not _generation_active or cell_elapsed >= 0.0:
					_draw_tile(layer, x, y, _cell_center(position), false, {}, thumbnail, cell_elapsed)
	if _row_transition_active:
		entries.append_array(_moving_row_entries(layer))
	entries.sort_custom(func(a: Dictionary, b: Dictionary) -> bool:
		return float(a.depth) < float(b.depth) if not is_equal_approx(float(a.depth), float(b.depth)) else float(a.x) < float(b.x))
	for entry in entries:
		if entry.animated:
			_draw_moving_tile(layer, Vector2(entry.x, entry.y), entry.moving, thumbnail)
			continue
		var cell: Vector2i = entry.cell
		var wave := cell.x + cell.y
		var cell_elapsed := _generation_elapsed - float(wave) * GENERATION_WAVE_DELAY
		if _generation_active and cell_elapsed < 0.0:
			continue
		var position: Array = [layer, cell.x, cell.y]
		var center := _cell_center(position)
		var moving: Dictionary = entry.moving
		var sink := 0.0
		if _mode == "hop" and position == _sink_pos:
			var land := clampf((_elapsed - _duration) / 0.20, 0.0, 1.0)
			sink = sin(PI * land) * 8.0
		center.y += sink
		_draw_tile(layer, cell.x, cell.y, center, true, moving, thumbnail, cell_elapsed, String(highlights.get(cell, "")))
		if not thumbnail and show_marks and (not _generation_active or cell_elapsed >= GENERATION_CELL_DURATION):
			_draw_cell_marks(position, center, true, moving)
		elif thumbnail and not is_revealing() and not busy and int(state.pos[0]) == layer and int(state.pos[1]) == cell.x and int(state.pos[2]) == cell.y:
			draw_circle(center + Vector2(0, -4), maxf(3.0, _tile_w * 0.12), ACCENT)
	if thumbnail:
		_tile_w = previous_w
		_tile_h = previous_h
		_board_origin = previous_origin

func _configure_board(layer: int, area: Rect2, scale_factor: float, thumbnail: bool, reserve_preview: bool) -> void:
	var width := int(level.width)
	var height := int(level.height)
	var wh_sum := maxi(1, width + height)
	var preview_width := minf(222.0, size.x * 0.31)
	var main_width := maxf(1.0, area.size.x - preview_width - 34.0) if not thumbnail and reserve_preview else area.size.x
	var max_w := main_width * 2.0 / float(wh_sum)
	var max_h := area.size.y * 2.0 / (float(wh_sum) * 0.54)
	_tile_w = minf(140.0 * scale_factor, minf(max_w, max_h))
	_tile_h = _tile_w * 0.53
	var origin_x := area.position.x + main_width * 0.5 if not thumbnail and reserve_preview else area.position.x + area.size.x * 0.5
	_board_origin = Vector2(origin_x, area.position.y + area.size.y * 0.5)

func cell_global_rect(position: Array) -> Rect2:
	var previous_w := _tile_w
	var previous_h := _tile_h
	var previous_origin := _board_origin
	_configure_board(int(position[0]),_main_grid_area(),1.0,false,false)
	var center := _cell_center(position)
	var local_rect := Rect2(center-Vector2(_tile_w*0.5,_tile_h*0.7),Vector2(_tile_w,_tile_h*1.5))
	var transform := get_global_transform_with_canvas()
	var top_left := transform * local_rect.position
	var bottom_right := transform * local_rect.end
	_tile_w = previous_w
	_tile_h = previous_h
	_board_origin = previous_origin
	return Rect2(top_left,bottom_right-top_left)

func preview_global_rect() -> Rect2:
	var local_rect := _preview_bounds()
	var transform := get_global_transform_with_canvas()
	var top_left := transform * local_rect.position
	var bottom_right := transform * local_rect.end
	return Rect2(top_left,bottom_right-top_left)

func board_global_rect() -> Rect2:
	var previous_w := _tile_w
	var previous_h := _tile_h
	var previous_origin := _board_origin
	_configure_board(selected_layer,_main_grid_area(),1.0,false,false)
	var span := float(int(level.width)+int(level.height))
	var half := Vector2(span*_tile_w*0.25,span*_tile_h*0.25)
	var local_rect := Rect2(_board_origin-half,half*2)
	if int(state.pos[0]) == selected_layer:
		local_rect = local_rect.expand(_cell_center(state.pos)-Vector2(0,60.0*_tile_w/96.0))
	var transform := get_global_transform_with_canvas()
	var top_left := transform * local_rect.position
	var bottom_right := transform * local_rect.end
	_tile_w = previous_w
	_tile_h = previous_h
	_board_origin = previous_origin
	return Rect2(top_left,bottom_right-top_left)

func _action_highlights(layer: int) -> Dictionary:
	var highlights := {}
	if state.is_empty() or is_animating():
		return highlights
	for action in GameRules.DIRECTIONS:
		var result := GameRules.try_action(level, state, String(action))
		if not result.accepted or result.state.status == "failed" or int(result.state.pos[0]) != layer:
			continue
		var delta: Vector2i = GameRules.DIRECTIONS[action]
		var landing := Vector2i(int(state.pos[1]) + delta.x, int(state.pos[2]) + delta.y)
		highlights[landing] = "hint" if hint_action == String(action) else "jump"
	var layer_result := GameRules.try_action(level, state, "X")
	if layer_result.accepted and int(layer_result.state.pos[0]) == layer:
		highlights[Vector2i(layer_result.state.pos[1], layer_result.state.pos[2])] = "lift"
	elif layer_result.accepted and int(state.pos[0]) == layer:
		highlights[Vector2i(state.pos[1], state.pos[2])] = "hint" if hint_action == "X" else "lift"
	return highlights

func _highlight_fill(base: Color, kind: String) -> Color:
	var amount: float = {"jump": 0.30, "lift": 0.44, "hint": 0.62, "hover": 0.76}.get(kind, 0.0)
	return base.lightened(float(amount))

func _hover_is_movable(layer: int) -> bool:
	if is_animating() or _hover.x < 0 or _hover.y < 0 or int(state.pos[0]) != layer:
		return false
	for action in GameRules.DIRECTIONS:
		var result := GameRules.try_action(level, state, String(action))
		if not result.accepted or result.state.status == "failed":
			continue
		var delta: Vector2i = GameRules.DIRECTIONS[action]
		if int(state.pos[0]) == layer and int(state.pos[1]) + delta.x == _hover.x and int(state.pos[2]) + delta.y == _hover.y:
			return true
	var layer_result := GameRules.try_action(level, state, "X")
	return layer_result.accepted and int(state.pos[1]) == _hover.x and int(state.pos[2]) == _hover.y

func _board_phase() -> int:
	if _row_transition_active or (busy and _mode != "environment"):
		return _phase_before
	return int(state.get("phase", 0))

func _moving_row_entries(layer: int) -> Array[Dictionary]:
	var entries: Array[Dictionary] = []
	var p := clampf(_elapsed / _duration, 0.0, 1.0)
	var rows: Array = level.get("moving_rows", [])
	for row in rows:
		if int(row.layer) != layer:
			continue
		for start_x in row.tiles:
			var from_x := posmod(int(start_x) + int(row.direction) * _phase_before, int(level.width))
			for x in _wrapped_row_centers(float(from_x), int(row.direction), p):
				entries.append({"x": x, "y": float(row.y), "moving": row, "animated": true, "depth": _entry_depth(x, float(row.y), true)})
	return entries

func _entry_depth(x: float, y: float, animated: bool) -> float:
	return x + y + (0.01 if animated else 0.0)

func _wrapped_row_centers(from_x: float, direction: int, progress: float) -> Array[float]:
	var centers: Array[float] = []
	var x := from_x + float(direction) * _ease_in_out(progress)
	for offset in [-int(level.width), 0, int(level.width)]:
		var copy_x := x + float(offset)
		if copy_x + 0.5 > -0.5 and copy_x - 0.5 < float(level.width) - 0.5:
			centers.append(copy_x)
	return centers

# Clip in grid coordinates so the top and the vertical faces wrap at the same boundary.
func _clip_row_polygon(points: PackedVector3Array) -> PackedVector3Array:
	if points.size() == 2:
		var from := points[0]
		var to := points[1]
		var dx := to.x - from.x
		if is_zero_approx(dx):
			return points if from.x >= -0.5 and from.x <= float(level.width) - 0.5 else PackedVector3Array()
		var start := (-0.5 - from.x) / dx
		var end := (float(level.width) - 0.5 - from.x) / dx
		var lower := maxf(0.0, minf(start, end))
		var upper := minf(1.0, maxf(start, end))
		if upper <= lower:
			return PackedVector3Array()
		return PackedVector3Array([from.lerp(to, lower), from.lerp(to, upper)])
	var result := points
	for side in [0, 1]:
		var boundary := -0.5 if side == 0 else float(level.width) - 0.5
		var clipped := PackedVector3Array()
		if result.is_empty():
			return clipped
		var previous := result[result.size() - 1]
		var previous_inside := previous.x >= boundary if side == 0 else previous.x <= boundary
		for point in result:
			var inside := point.x >= boundary if side == 0 else point.x <= boundary
			if inside != previous_inside:
				clipped.append(previous.lerp(point, (boundary - previous.x) / (point.x - previous.x)))
			if inside:
				clipped.append(point)
			previous = point
			previous_inside = inside
		result = clipped
	return result

func _project_row_polygon(layer: int, points: PackedVector3Array) -> PackedVector2Array:
	var projected := PackedVector2Array()
	for point in _clip_row_polygon(points):
		projected.append(_cell_center_xy(layer, point.x, point.y) + Vector2(0, point.z))
	return projected

func _draw_row_polygon(layer: int, points: PackedVector3Array, color: Color) -> void:
	var polygon := _project_row_polygon(layer, points)
	if polygon.size() >= 3:
		draw_colored_polygon(polygon, color)

func _draw_moving_tile(layer: int, cell: Vector2, row: Dictionary, thumbnail: bool) -> void:
	var x := cell.x
	var y := cell.y
	var top := Vector3(x - 0.5, y - 0.5, 0)
	var right := Vector3(x + 0.5, y - 0.5, 0)
	var bottom := Vector3(x + 0.5, y + 0.5, 0)
	var left := Vector3(x - 0.5, y + 0.5, 0)
	var edge := Color("668ca1")
	var depth := 3.0 if thumbnail else 12.0
	var down := Vector3(0, 0, depth)
	_draw_row_polygon(layer, PackedVector3Array([right, bottom, bottom + down, right + down]), edge.darkened(0.20))
	_draw_row_polygon(layer, PackedVector3Array([bottom, left, left + down, bottom + down]), edge.darkened(0.06))
	_draw_row_polygon(layer, PackedVector3Array([top, right, bottom, left]), Color("b9d4e5"))
	for segment in [[top, right], [right, bottom], [bottom, left], [left, top]]:
		var line := _project_row_polygon(layer, PackedVector3Array(segment))
		if line.size() >= 2:
			draw_line(line[0], line[line.size() - 1], edge, 1.5, true)
	_draw_row_inlay(layer, cell, thumbnail)
	_draw_row_arrow(layer, cell, int(row.direction), thumbnail)

func _draw_row_inlay(layer: int, cell: Vector2, thumbnail: bool) -> void:
	if thumbnail:
		return
	var corners := [Vector3(cell.x - 0.34, cell.y - 0.34, 0), Vector3(cell.x + 0.34, cell.y - 0.34, 0), Vector3(cell.x + 0.34, cell.y + 0.34, 0), Vector3(cell.x - 0.34, cell.y + 0.34, 0)]
	for i in range(4):
		var corner: Vector3 = corners[i]
		for next_index in [posmod(i - 1, 4), (i + 1) % 4]:
			var line := _project_row_polygon(layer, PackedVector3Array([corner, corner.lerp(corners[next_index], 0.25)]))
			if line.size() >= 2:
				draw_line(line[0], line[line.size() - 1], Color("436f8a", 0.65), 1.1, true)

func _draw_row_arrow(layer: int, cell: Vector2, direction: int, thumbnail: bool) -> void:
	var length := 0.13 if thumbnail else 0.18
	var tip := Vector3(cell.x + float(direction) * length, cell.y, 0)
	var tail := Vector3(cell.x - float(direction) * length, cell.y, 0)
	var wing_a := tip + Vector3(-float(direction) * length * 0.65, -length * 0.55, 0)
	var wing_b := tip + Vector3(-float(direction) * length * 0.65, length * 0.55, 0)
	for segment in [[tail, tip], [wing_a, tip], [wing_b, tip]]:
		var points := _project_row_polygon(layer, PackedVector3Array(segment))
		if points.size() >= 2:
			draw_line(points[0], points[points.size() - 1], Color("294b61"), 1.3 if thumbnail else 2.0, true)

func _draw_carried_player() -> void:
	if _carry_from.is_empty() or _carry_to.is_empty() or _carry_from == _carry_to:
		if int(_pending_state.pos[0]) == selected_layer:
			_draw_player(_cell_center(_pending_state.pos) + Vector2(0, -24), 0.0, 1.0, 1.0)
		return
	var p := clampf(_elapsed / _duration, 0.0, 1.0)
	var row := GameRules._moving_row_at_position(level, _carry_from, _phase_before)
	var direction := int(row.get("direction", 1))
	var layer := int(_carry_from[0])
	var y := float(_carry_from[2])
	for x in _wrapped_row_centers(float(_carry_from[1]), direction, p):
		_draw_wrapped_player(layer, x, y)

# Keep the capsule in screen space. Only its horizontal world position is clipped at the seam.
func _wrapped_screen_polygon(layer: int, x: float, y: float, points: PackedVector2Array) -> PackedVector2Array:
	var world := PackedVector3Array()
	for point in points:
		world.append(Vector3(x + point.x / (_tile_w * 0.5), y, point.y - point.x * _tile_h / _tile_w))
	return _project_row_polygon(layer, world)

func _capsule_outline() -> PackedVector2Array:
	var points := PackedVector2Array()
	for i in range(17):
		var angle := PI + PI * float(i) / 16.0
		points.append(Vector2(cos(angle) * 10.0, -39.0 + sin(angle) * 10.0))
	for i in range(17):
		var angle := PI * float(i) / 16.0
		points.append(Vector2(cos(angle) * 10.0, -9.0 + sin(angle) * 10.0))
	return points

func _draw_wrapped_player(layer: int, x: float, y: float) -> void:
	var shadow := PackedVector2Array()
	var ring := PackedVector2Array()
	for i in range(49):
		var angle := TAU * float(i) / 48.0
		shadow.append(Vector2(cos(angle) * 16.0, -6.0 + sin(angle) * 5.76))
		ring.append(Vector2(cos(angle) * 22.0, -24.0 + sin(angle) * 22.0))
	for shape in [{"points": shadow, "color": Color(0.01, 0.05, 0.06, 0.35)}, {"points": _capsule_outline(), "color": Color("48d1bd")}]:
		var polygon := _wrapped_screen_polygon(layer, x, y, shape.points)
		if polygon.size() >= 3:
			draw_colored_polygon(polygon, shape.color)
	for accent in [{"center": Vector2(-3, -41), "radius": 3.0, "color": Color("e7fff8")}, {"center": Vector2(0, -47), "radius": 2.3, "color": Color("ffd163")}]:
		var dot := PackedVector2Array()
		for i in range(25):
			dot.append(accent.center + Vector2.from_angle(TAU * float(i) / 24.0) * float(accent.radius))
		var polygon := _wrapped_screen_polygon(layer, x, y, dot)
		if polygon.size() >= 3:
			draw_colored_polygon(polygon, accent.color)
	# Clip each arc segment separately so crossing a boundary never draws a false closing edge.
	for i in range(ring.size() - 1):
		var line := _wrapped_screen_polygon(layer, x, y, PackedVector2Array([ring[i], ring[i + 1]]))
		if line.size() == 2:
			draw_line(line[0], line[1], Color(0.37, 0.98, 0.84, 0.42), 1.2, true)

func _ease_in_out(value: float) -> float:
	var t := clampf(value, 0.0, 1.0)
	return t * t * (3.0 - 2.0 * t)

func _draw_tile(layer: int, x: int, y: int, center: Vector2, supported: bool, moving: Dictionary, thumbnail: bool, cell_elapsed: float, highlight: String = "") -> void:
	var points := _diamond_points(center)
	var generating := _generation_active and not thumbnail and cell_elapsed < GENERATION_CELL_DURATION
	var edge := FLOOR_LINE if not supported else _tile_edge(layer, x, y, moving)
	var fill := FLOOR_VOID if not supported else _tile_fill(layer, x, y, moving)
	if generating:
		_draw_generation_tile(points, edge, fill, cell_elapsed)
		return
	if not supported:
		_draw_diamond(center + Vector2(0, 4), _tile_w, _tile_h, FLOOR_VOID, FLOOR_LINE, 1.0, 0.0)
		return
	edge = _tile_edge(layer, x, y, moving)
	fill = _highlight_fill(fill, highlight)
	if _completion_active and _is_goal(layer, x, y):
		var flash := pow(maxf(0.0, sin(_completion_elapsed * 9.0)), 2.0) * (1.0 - _completion_elapsed / COMPLETION_DURATION)
		fill = fill.lerp(Color("f3fff8"), 0.5 + flash * 0.5)
	var depth := 12.0 if not thumbnail else 3.0
	var right_side := PackedVector2Array([points[1], points[2], points[2] + Vector2(0, depth), points[1] + Vector2(0, depth)])
	var left_side := PackedVector2Array([points[2], points[3], points[3] + Vector2(0, depth), points[2] + Vector2(0, depth)])
	draw_colored_polygon(right_side, edge.darkened(0.20))
	draw_colored_polygon(left_side, edge.darkened(0.06))
	draw_colored_polygon(points, fill)
	draw_polyline(PackedVector2Array([points[0], points[1], points[2], points[3], points[0]]), edge, 1.5 if not thumbnail else 0.8, true)

func _tile_fill(layer: int, x: int, y: int, moving: Dictionary) -> Color:
	var switch := _switch_at([layer, x, y])
	if not switch.is_empty():
		var base := Color("b9d4e5") if not moving.is_empty() else (Color("b9d6e8") if _is_lift(x, y) else Color("ecd7a4"))
		return base.lerp(Color("a6e6cf"), _switch_match_amount(int(switch.mask)))
	if not moving.is_empty() or _is_lift(x, y):
		return Color("b9d4e5") if not moving.is_empty() else Color("b9d6e8")
	var gate := _gate_at([layer, x, y])
	if not gate.is_empty():
		return Color("b2d9cd") if _gate_open(gate) else Color("e1b3ad")
	if not _item_at([layer, x, y]).is_empty():
		return Color("efdcaa")
	var beacon := _beacon_at([layer, x, y])
	if beacon >= 0:
		return Color("d3ccec").lerp(Color("a6e6cf"), _beacon_light_amount(beacon))
	if not _flow_at([layer, x, y]).is_empty():
		return Color("c0dce6")
	if _is_goal(layer, x, y):
		return Color("b9dec0")
	return FLOOR_TOP

func _tile_edge(layer: int, x: int, y: int, moving: Dictionary) -> Color:
	var switch := _switch_at([layer, x, y])
	if not switch.is_empty():
		var base := Color("668ca1") if not moving.is_empty() else (Color("668ba0") if _is_lift(x, y) else Color("aa8a50"))
		return base.lerp(Color("438d77"), _switch_match_amount(int(switch.mask)))
	if not moving.is_empty() or _is_lift(x, y):
		return Color("668ca1") if not moving.is_empty() else Color("668ba0")
	var gate := _gate_at([layer, x, y])
	if not gate.is_empty():
		return Color("668d82") if _gate_open(gate) else Color("9b6159")
	if not _item_at([layer, x, y]).is_empty():
		return Color("a9884d")
	var beacon := _beacon_at([layer, x, y])
	if beacon >= 0:
		return Color("8a7fa5").lerp(Color("438d77"), _beacon_light_amount(beacon))
	if not _flow_at([layer, x, y]).is_empty():
		return Color("6b94a6")
	return Color("679071") if _is_goal(layer, x, y) else FLOOR_EDGE

func _draw_generation_tile(points: PackedVector2Array, edge: Color, final_fill: Color, elapsed: float) -> void:
	var first_phase := clampf(elapsed / 0.16, 0.0, 1.0)
	var second_phase := clampf((elapsed - 0.16) / 0.16, 0.0, 1.0)
	var top := points[0]
	var right := points[1]
	var bottom := points[2]
	var left := points[3]
	var line_color := edge.lightened(0.18)
	if elapsed < 0.16:
		draw_line(top, top.lerp(left, first_phase), line_color, 2.0, true)
		draw_line(top, top.lerp(right, first_phase), line_color, 2.0, true)
		return
	draw_line(top, left, line_color, 2.0, true)
	draw_line(top, right, line_color, 2.0, true)
	if elapsed < 0.32:
		draw_line(left, left.lerp(bottom, second_phase), line_color, 2.0, true)
		draw_line(right, right.lerp(bottom, second_phase), line_color, 2.0, true)
		return
	var fill := _generation_fill(elapsed, final_fill)
	draw_colored_polygon(points, fill)
	draw_polyline(PackedVector2Array([top, right, bottom, left, top]), edge, 1.5, true)

func _generation_fill(elapsed: float, final_fill: Color) -> Color:
	if elapsed < GENERATION_EDGE_DURATION + GENERATION_WHITE_HOLD:
		return Color.WHITE
	if elapsed < GENERATION_EDGE_DURATION + GENERATION_WHITE_HOLD + GENERATION_BLUE_HOLD:
		return Color("a9ddf2")
	return final_fill

func _draw_failure_player() -> void:
	var t := clampf(_failure_elapsed / FAILURE_DURATION,0.0,1.0)
	var center := _cell_center(state.pos) + Vector2(sin(t*70.0)*3.0*(1.0-t),-24.0+t*t*42.0)
	_draw_player(center,0.0,1.0-t,1.0)

func _draw_failure_effects() -> void:
	var t := clampf(_failure_elapsed / FAILURE_DURATION,0.0,1.0)
	var center := _cell_center(state.pos)
	_draw_ellipse_outline(center,_tile_w*(0.2+t),_tile_h*(0.12+t*0.5),Color(1.0,0.3,0.47,(1.0-t)*0.85),2.5)
	for i in range(26):
		var angle := float(i)*2.39996
		var point := center + Vector2(cos(angle)*(20.0+t*70.0),-25.0+sin(angle)*t*35.0+t*t*36.0)
		draw_rect(Rect2(point,Vector2(3+(i%3)*2,2)),Color(1.0,0.47,0.62,(1.0-t)*0.8))
	draw_rect(Rect2(Vector2.ZERO,size),Color(0.55,0.05,0.19,sin(PI*t)*0.13))

func _draw_completion() -> void:
	var center := _cell_center(state.pos)
	var t := _completion_elapsed
	for i in range(3):
		var pulse := clampf((t - float(i) * 0.19) / 0.85, 0.0, 1.0)
		var radius := _tile_w * (0.25 + pulse * 0.85)
		_draw_ellipse_outline(center, radius, radius * 0.38, Color(0.58, 1.0, 0.83, (1.0 - pulse) * 0.8), 2.5 - pulse)
	# Deterministic ballistic particles keep capture frames and replays reproducible.
	var colors := [Color("7ef1d2"), Color("f4d58b"), Color("b8afff"), Color("effbff")]
	for i in range(58):
		var delay := float(i % 7) * 0.017
		var age := t - delay
		if age < 0.0:
			continue
		var angle := TAU * float(i) * 0.618034
		var speed := 65.0 + float(i % 8) * 13.0
		var velocity := Vector2(cos(angle) * speed, -135.0 - float(i % 6) * 18.0)
		var position := center + Vector2(0, -10) + velocity * age + Vector2(0, 125 * age * age)
		var opacity := clampf((COMPLETION_DURATION - age) / 0.65, 0.0, 1.0)
		var color: Color = colors[i % colors.size()]
		color.a = opacity
		draw_set_transform(position, age * (float(i % 5) + 2) + angle)
		draw_rect(Rect2(Vector2(-3, -2), Vector2(6, 4)), color)
		draw_set_transform(Vector2.ZERO)

func _draw_cell_marks(position: Array, center: Vector2, supported: bool, moving: Dictionary) -> void:
	if not supported:
		return
	# Keep symbols proportional when a large map reduces the diamond size.
	var symbol_scale := minf(1.0,_tile_w/96.0)
	if symbol_scale >= 0.99 or not moving.is_empty():
		_draw_cell_symbols(position,center,moving)
		return
	var previous_w := _tile_w
	var previous_h := _tile_h
	_tile_w /= symbol_scale
	_tile_h /= symbol_scale
	draw_set_transform(center,0.0,Vector2(symbol_scale,symbol_scale))
	_draw_cell_symbols(position,Vector2.ZERO,moving)
	draw_set_transform(Vector2.ZERO)
	_tile_w = previous_w
	_tile_h = previous_h

func _draw_cell_symbols(position: Array, center: Vector2, moving: Dictionary) -> void:
	if not moving.is_empty():
		_draw_row_inlay(int(position[0]), Vector2(position[1], position[2]), false)
		_draw_row_arrow(int(position[0]), Vector2(position[1], position[2]), int(moving.direction), false)
	elif _is_lift(int(position[1]), int(position[2])):
		_draw_lift_mark(center)
	var item := _item_at(position)
	var has_item: bool = not item.is_empty() and not state.get("collected", []).has(String(item.id))
	var switch := _switch_at(position)
	if not switch.is_empty():
		var delayed := String(level.switch_mode_by_layer[int(position[0])]) == "delayed"
		_draw_switch_mark(center, int(switch.mask), delayed)
	var gate := _gate_at(position)
	if not gate.is_empty():
		_draw_gate_mark(center, gate)
	var beacon_index := _beacon_at(position)
	if beacon_index >= 0:
		_draw_beacon_mark(center, beacon_index)
	if has_item:
		_draw_item_mark(center - Vector2(0, 13) if not switch.is_empty() else center, item.type == "key")
	var flow := _flow_at(position)
	if not flow.is_empty():
		var delta: Vector2i = GameRules.DIRECTIONS[String(flow.dir)]
		var direction := Vector2(float(delta.x - delta.y), float(delta.x + delta.y) * 0.53).normalized()
		_draw_flow_mark(center, direction)
	if _is_goal(int(position[0]), int(position[1]), int(position[2])):
		_draw_goal_mark(center)
	# A composite cell keeps the two independent checks inside the same central circle.
	if not switch.is_empty() and beacon_index >= 0:
		_draw_composite_checks(center, _switch_match_amount(int(switch.mask)), _beacon_light_amount(beacon_index))
	elif not switch.is_empty():
		_draw_center_check(center, _switch_match_amount(int(switch.mask)))
	elif beacon_index >= 0:
		_draw_center_check(center, _beacon_light_amount(beacon_index))
func _draw_inlay(center: Vector2, color: Color) -> void:
	var points := _diamond_points(center)
	var inset := PackedVector2Array()
	for point in points:
		inset.append(center.lerp(point, 0.73))
	draw_colored_polygon(inset, Color(color, 0.075))
	for i in range(4):
		var corner := inset[i]
		draw_line(corner.lerp(inset[posmod(i - 1, 4)], 0.23), corner, Color(color, 0.5), 1.0, true)
		draw_line(corner, corner.lerp(inset[(i + 1) % 4], 0.23), Color(color, 0.5), 1.0, true)

func _draw_lift_mark(center: Vector2) -> void:
	var ink := Color("3b6684")
	_draw_inlay(center, ink)
	var origin := center - Vector2(0, 3)
	_draw_ellipse(origin, _tile_w * 0.24, _tile_h * 0.20, Color("61b9e2", 0.12))
	_draw_ellipse_outline(origin, _tile_w * 0.24, _tile_h * 0.20, Color(ink, 0.7), 1.4)
	_draw_ellipse_outline(origin, _tile_w * 0.18, _tile_h * 0.14, Color("effaff", 0.8), 1.0)
	for direction in [-1, 1]:
		var x := float(direction) * 5
		var tip := origin + Vector2(x, -float(direction) * 7)
		draw_line(origin + Vector2(x, float(direction) * 6), tip, ink, 1.8, true)
		draw_polyline(PackedVector2Array([tip + Vector2(-3, float(direction) * 3), tip, tip + Vector2(3, float(direction) * 3)]), ink, 1.8, true)

func _draw_switch_mark(center: Vector2, mask: int, delayed: bool) -> void:
	var amount := _switch_match_amount(mask)
	var ink := Color("8c632d").lerp(Color("23785c"), amount)
	_draw_inlay(center, ink)
	var origin := center
	var r := _tile_w * 0.13
	_draw_ellipse(origin, r + 6, (r + 6) * 0.4, Color(ink, 0.11 + amount * 0.08))
	_draw_ellipse_outline(origin, r, r * 0.42, Color("fff5d2").lerp(Color("effff7"), amount), 3)
	_draw_ellipse_outline(origin, r, r * 0.42, ink, 1)
	for direction in [-1, 1]:
		var node := origin + Vector2(float(direction) * _tile_w * 0.27, 0)
		draw_polyline(PackedVector2Array([origin + Vector2(float(direction) * r, 0), node - Vector2(0, 3), node]), Color(ink, 0.6), 1.2, true)
		draw_circle(node, 2.3, ink)
	_draw_ellipse(origin, 6, 3, Color("9a7b48").lerp(Color("e5fff3"), amount))
	if delayed:
		draw_arc(origin + Vector2(21, -7), 4, -PI * 0.5, PI * 1.5, 24, ink, 1, true)
		draw_line(origin + Vector2(21, -7), origin + Vector2(21, -10), ink, 1, true)
	var channels: Array[int] = []
	for bit in range(3):
		if mask & (1 << bit):
			channels.append(bit)
	var spacing := minf(12.0,_tile_w*0.16)
	for index in range(channels.size()):
		_draw_channel_glyph(center+Vector2((index-(channels.size()-1)*0.5)*spacing,_tile_h*0.28),channels[index],true,maxf(2.4,_tile_w*0.038))

func _draw_channel_glyph(center: Vector2, bit: int, filled: bool, radius: float) -> void:
	var ink: Color = [Color("3878a0"),Color("8d5798"),Color("987238")][bit]
	if bit == 0:
		if filled:
			draw_circle(center,radius,ink)
		else:
			draw_arc(center,radius,0,TAU,20,ink,1.4,true)
		return
	var points := PackedVector2Array()
	var count := 4 if bit == 1 else 3
	for index in range(count):
		var angle := -PI*0.5+TAU*float(index)/float(count)
		points.append(center+Vector2(cos(angle),sin(angle))*radius)
	if filled:
		draw_colored_polygon(points,ink)
	else:
		points.append(points[0])
		draw_polyline(points,ink,1.4,true)

func _draw_center_check(center: Vector2, amount: float) -> void:
	if amount <= 0.001:
		return
	var radius_x := _tile_w * 0.105
	var radius_y := _tile_h * 0.14
	_draw_ellipse(center, radius_x, radius_y, Color(0.12, 0.44, 0.33, amount))
	_draw_ellipse_outline(center, radius_x, radius_y, Color(0.79, 1.0, 0.90, amount * 0.9), 1.0)
	_draw_check_glyph(center, radius_x, radius_y, amount)

func _draw_check_glyph(center: Vector2, radius_x: float, radius_y: float, amount: float) -> void:
	var check := PackedVector2Array([center + Vector2(-radius_x * 0.47, -radius_y * 0.05), center + Vector2(-radius_x * 0.10, radius_y * 0.40), center + Vector2(radius_x * 0.53, -radius_y * 0.44)])
	draw_polyline(check, Color(0.91, 1.0, 0.96, amount), 1.8, true)

func _draw_composite_checks(center: Vector2, switch_amount: float, beacon_amount: float) -> void:
	var radius_x := _tile_w * 0.15
	var radius_y := _tile_h * 0.18
	for side in range(2):
		var amount := switch_amount if side == 0 else beacon_amount
		var polygon := PackedVector2Array([center])
		for i in range(25):
			var angle := (PI * 0.5 if side == 0 else -PI * 0.5) + PI * float(i) / 24.0
			polygon.append(center + Vector2(cos(angle) * radius_x, sin(angle) * radius_y))
		var dormant := Color("927b4c", 0.35) if side == 0 else Color("8875b2", 0.35)
		draw_colored_polygon(polygon, dormant.lerp(Color("217155"), amount))
		var check_center := center + Vector2(radius_x * (-0.48 if side == 0 else 0.48), 0)
		_draw_check_glyph(check_center, radius_x * 0.56, radius_y * 0.76, amount)
	_draw_ellipse_outline(center, radius_x, radius_y, Color("d7f4e8", 0.8), 1.0)
	draw_line(center - Vector2(0, radius_y * 0.85), center + Vector2(0, radius_y * 0.85), Color("d7f4e8", 0.55), 1.0, true)

func _draw_gate_mark(center: Vector2, gate: Dictionary) -> void:
	var opened := _gate_open(gate)
	var ink := Color("43806f") if opened else Color("a45663")
	_draw_inlay(center, ink)
	var span := _tile_w * 0.20
	var origin := center - Vector2(0, 3)
	for side in [-1, 1]:
		var foot := origin + Vector2(float(side) * span, 0)
		var top := foot - Vector2(0, 16)
		draw_line(foot, top, Color(ink, 0.23), 7, true)
		draw_line(foot, top, ink, 2.2, true)
		draw_circle(top, 2.6, Color("effff7") if opened else Color("ffe3e6"))
	var bar_y := origin.y - 12
	if opened:
		for side in [-1, 1]:
			draw_line(Vector2(origin.x + float(side) * span, bar_y), Vector2(origin.x + float(side) * (span - 7), bar_y - 4), ink, 2, true)
	else:
		var glass := PackedVector2Array([origin + Vector2(-span, 0), origin + Vector2(span, 0), origin + Vector2(span, -15), origin + Vector2(-span, -15)])
		draw_colored_polygon(glass, Color(ink, 0.16))
		draw_line(Vector2(origin.x - span, bar_y), Vector2(origin.x + span, bar_y), Color(ink, 0.8), 1.5, true)
		for i in range(4):
			var x := origin.x - span + float(i + 1) * span * 0.4
			draw_line(Vector2(x, origin.y - 2), Vector2(x + 5, origin.y - 11), Color(ink, 0.4), 1, true)
	if gate.has("bit"):
		_draw_channel_glyph(center+Vector2(0,_tile_h*0.24),int(gate.bit),int(gate.value) == 1,maxf(3.0,_tile_w*0.047))
	else:
		# A keyhole distinguishes a sealed key gate from a bit gate.
		var at := center+Vector2(0,_tile_h*0.24)
		draw_circle(at-Vector2(0,2),2.2,ink)
		draw_line(at,at+Vector2(0,4),ink,2.3,true)

func _draw_beacon_mark(center: Vector2, index: int) -> void:
	var amount := _beacon_light_amount(index)
	var ink := Color("7964a9").lerp(Color("23785c"), amount)
	_draw_inlay(center, ink)
	var origin := center
	var glow := Color("b6a0fb").lerp(Color("8cffd9"), amount)
	_draw_ellipse(origin, _tile_w * 0.20, _tile_h * 0.15, Color(glow, lerpf(0.13, 0.32, amount)))
	_draw_ellipse_outline(origin, _tile_w * 0.20, _tile_h * 0.15, Color(ink, 0.65), 1)

func _switch_goal_matched(mask: int) -> bool:
	return (int(state.get("bits", 0)) & mask) == (int(level.get("goal_bits", 0)) & mask)

func _beacon_marker_center(center: Vector2) -> Vector2:
	return center - Vector2(0, 69)

func _draw_floating_beacons() -> void:
	for index in range(level.beacons.size()):
		var at: Array = level.beacons[index]
		if int(at[0]) != selected_layer:
			continue
		if _generation_active and _generation_elapsed - float(int(at[1]) + int(at[2])) * GENERATION_WAVE_DELAY < GENERATION_CELL_DURATION:
			continue
		_draw_beacon_marker(_cell_center(at), index)

func _draw_beacon_marker(center: Vector2, index: int) -> void:
	var amount := _beacon_light_amount(index)
	var tip := _beacon_marker_center(center)
	var ink := Color("b5a2ef").lerp(Color("8cffd9"), amount)
	draw_line(center - Vector2(0, 8), tip + Vector2(0, 17), Color(ink, 0.4 + amount * 0.2), 1.2, true)
	_draw_diamond(tip, 27, 38, Color("332f55").lerp(Color("247d68"), amount), ink, 2.0, 0)
	_draw_diamond(tip, 17, 26, Color(ink, 0.18), Color(ink, 0.45), 1.0, 0)
	# Ordered beacons use small pips; the board contains no text labels.
	for pip in range(index+1):
		draw_circle(tip+Vector2((float(pip)-float(index)*0.5)*6,0),1.7,Color("edfff9"))
	_draw_diamond(tip, 35, 48, Color.TRANSPARENT, Color(ink, amount * 0.30), 1.0, 0)

func _draw_environment_effects() -> void:
	var t := clampf(_elapsed / _duration, 0.0, 1.0)
	for y in range(int(level.height)):
		for x in range(int(level.width)):
			var at := [selected_layer, x, y]
			var special := not _switch_at(at).is_empty() or not _gate_at(at).is_empty() or _beacon_at(at) >= 0 or _same_cell(at, state.pos)
			if special:
				_draw_ellipse_outline(_cell_center(at), _tile_w * (0.18 + t * 0.32), _tile_h * (0.12 + t * 0.18), Color(0.52, 1.0, 0.83, (1.0 - t) * 0.7), 2.0)

func _draw_item_mark(center: Vector2, key: bool) -> void:
	var ink := Color("987232") if key else Color("74639d")
	_draw_inlay(center, ink)
	_draw_ellipse(center, _tile_w * 0.18, _tile_h * 0.14, Color(ink, 0.15))
	var origin := center - Vector2(0, 12 + sin(_visual_time * 1.8) * 2)
	if key:
		draw_arc(origin - Vector2(5, 4), 5, 0, TAU, 24, Color("fff7d8"), 4, true)
		draw_arc(origin - Vector2(5, 4), 5, 0, TAU, 24, ink, 1.5, true)
		draw_polyline(PackedVector2Array([origin - Vector2(1, 0), origin + Vector2(8, 8), origin + Vector2(12, 4)]), ink, 2, true)
		draw_line(origin + Vector2(5, 5), origin + Vector2(8, 2), ink, 2, true)
	else:
		var diamond := PackedVector2Array([origin - Vector2(0, 10), origin + Vector2(9, 0), origin + Vector2(0, 10), origin - Vector2(9, 0), origin - Vector2(0, 10)])
		draw_colored_polygon(diamond, Color("eee5ff"))
		draw_polyline(diamond, ink, 1.2, true)
		draw_arc(origin, 4, 0, TAU, 24, ink, 1.2, true)
		draw_line(origin - Vector2(0, 6), origin + Vector2(0, 6), ink, 1, true)
		draw_line(origin - Vector2(6, 0), origin + Vector2(6, 0), ink, 1, true)

func _draw_flow_mark(center: Vector2, direction: Vector2) -> void:
	var ink := Color("3e7794")
	_draw_inlay(center, ink)
	var normal := Vector2(-direction.y, direction.x)
	for side in [-1, 1]:
		var point := center + normal * float(side) * 6 - Vector2(0, 3)
		draw_line(point - direction * 19, point + direction * 19, Color(ink, 0.24), 1, true)
	for i in range(3):
		var point := center - Vector2(0, 3) + direction * float(i - 1) * 10
		draw_polyline(PackedVector2Array([point - direction * 3 - normal * 4, point + direction * 2, point - direction * 3 + normal * 4]), Color(ink, 0.5 + float(i) * 0.2), 1.8, true)

func _draw_goal_mark(center: Vector2) -> void:
	var ink := Color("3d8265")
	_draw_inlay(center, ink)
	var origin := center - Vector2(0, 4)
	var pulse := (sin(_visual_time * 2) + 1) * 0.5
	_draw_ellipse(origin, _tile_w * 0.24, _tile_h * 0.21, Color("64d6a4", 0.15 + pulse * 0.06))
	_draw_ellipse_outline(origin, _tile_w * 0.24, _tile_h * 0.21, Color(ink, 0.7), 1.3)
	_draw_ellipse_outline(origin, _tile_w * 0.17, _tile_h * 0.14, Color("f2fff4"), 1.5)
	for side in [-1, 1]:
		var foot := origin + Vector2(float(side) * _tile_w * 0.21, 0)
		draw_line(foot, foot - Vector2(0, 8), Color(ink, 0.45), 2, true)
		draw_circle(foot - Vector2(0, 8), 2, Color("effff3"))

func _draw_direction_arrow(center: Vector2, direction: Vector2, color: Color) -> void:
	var normal := Vector2(-direction.y, direction.x)
	var tip := center + direction * 13.0
	draw_line(center - direction * 13.0, tip, color, 2.0, true)
	draw_line(tip, tip - direction * 7.0 + normal * 4.0, color, 2.0, true)
	draw_line(tip, tip - direction * 7.0 - normal * 4.0, color, 2.0, true)

func _draw_preview() -> void:
	var preview_layer := 1 - selected_layer
	_preview_rect = _preview_bounds()
	var box := StyleBoxFlat.new()
	box.bg_color = Color("19272d", 0.97)
	box.border_color = Color("51716e")
	box.set_border_width_all(1)
	box.set_corner_radius_all(7)
	draw_style_box(box, _preview_rect)
	var title := "下一層預覽  ·  點擊展開" if preview_layer != selected_layer else "上一層預覽  ·  點擊展開"
	if selected_layer == 0:
		title = "上層預覽  ·  點擊查看"
	else:
		title = "下層預覽  ·  點擊查看"
	draw_string(ThemeDB.fallback_font, _preview_rect.position + Vector2(10, 20), title, HORIZONTAL_ALIGNMENT_LEFT, _preview_rect.size.x - 18, 11, Color("cfddda"))
	_draw_board(preview_layer, _preview_mini_area(), 1.0, true, false)

func _draw_hop() -> void:
	var t := clampf(_elapsed / _duration, 0.0, 1.0)
	var start := _cell_center(_from_pos) + Vector2(0, -24)
	var finish := _cell_center(_to_pos) + Vector2(0, -24)
	var height := _tile_w * 0.58 if _move_axis == "x" else _tile_h * 1.9
	var center := start.lerp(finish, t) - Vector2(0, 4.0 * height * t * (1.0 - t))
	var rotation := TAU * t * _roll_sign(_move_action)
	var squeeze := maxf(0.18, absf(cos(rotation)))
	var scale_x := squeeze if _move_axis == "x" else 1.0
	var scale_y := squeeze if _move_axis == "y" else 1.0
	if t < 1.0:
		_draw_player(center, rotation, 1.0, scale_x, scale_y)
	else:
		var landing := clampf((_elapsed - _duration) / 0.20, 0.0, 1.0)
		_draw_player(finish + Vector2(0, sin(PI * landing) * 7.0), 0.0, 1.0, 1.0)

func _roll_sign(action: String) -> float:
	return 1.0 if action in ["R", "D"] else -1.0

func _draw_layer_transition() -> void:
	var t := clampf(_elapsed / _duration, 0.0, 1.0)
	if _stage == 0:
		var ground := _cell_center(_from_pos)
		_draw_portal(ground, t, 1.0)
		var player_pos := ground + Vector2(0, -24.0 + t * 44.0)
		_draw_player(player_pos, 0.0, 1.0 - t, maxf(0.08, 1.0 - t))
		if t > 0.36:
			_draw_portal_front(ground, t, 0.92)
		if t > 0.38:
			var cover := clampf((t - 0.38) / 0.56, 0.0, 0.96)
			var rx := _tile_w * 0.43 * t
			var ry := _tile_h * 0.34 * t
			_draw_ellipse(ground, rx, ry, Color(0.04, 0.19, 0.22, cover))
			_draw_ellipse_outline(ground, rx, ry, Color(0.55, 1.0, 0.9, 0.90), 2.6)
	elif _stage == 1:
		_draw_layer_handoff(t)
	else:
		var ground := _cell_center(_to_pos)
		var high_portal := ground + Vector2(0, -156.0)
		_draw_portal(high_portal, minf(1.0, t * 1.8), 1.0 - maxf(0.0, t - 0.72) / 0.28)
		var player_pos := ground + Vector2(0, -24.0 - 150.0 * (1.0 - t))
		_draw_player(player_pos, 0.0, clampf((t - 0.08) * 1.35, 0.0, 1.0), 1.0)
		if t > 0.70:
			_draw_portal_front(ground, (t - 0.70) / 0.30, 0.8)

func _draw_layer_handoff(t: float) -> void:
	var ground := _cell_center(_from_pos)
	var upper := ground + Vector2(0, -104.0)
	var pulse := sin(PI * t)
	_draw_portal(ground, 1.0 - t * 0.45, 0.72)
	_draw_portal(upper, t, 0.85)
	draw_line(ground, upper, Color(0.49, 0.96, 0.85, 0.25 + pulse * 0.55), 2.0 + pulse * 2.0, true)
	var energy := ground.lerp(upper, t)
	draw_circle(energy, 5.0 + pulse * 3.0, Color(0.72, 1.0, 0.89, 0.92))
	draw_circle(energy, 11.0 + pulse * 5.0, Color(0.36, 0.88, 0.79, 0.16))
	draw_string(ThemeDB.fallback_font, ground + Vector2(0, -121), "层间跃迁", HORIZONTAL_ALIGNMENT_CENTER, -1, 13, Color(0.82, 1.0, 0.94, 0.78 + pulse * 0.22))

func _draw_portal(center: Vector2, amount: float, opacity: float) -> void:
	var scale_factor := clampf(amount, 0.001, 1.0)
	var rx := _tile_w * 0.43 * scale_factor
	var ry := _tile_h * 0.34 * scale_factor
	_draw_ellipse(center, rx, ry, Color(0.22, 0.91, 0.78, 0.15 * opacity))
	_draw_ellipse_outline(center, rx, ry, Color(0.48, 1.0, 0.88, 0.86 * opacity), 3.0 * scale_factor)
	_draw_ellipse_outline(center, rx * 0.72, ry * 0.70, Color(0.58, 0.72, 1.0, 0.70 * opacity), 1.4 * scale_factor)

func _draw_portal_front(center: Vector2, amount: float, opacity: float) -> void:
	var rx := _tile_w * 0.43 * clampf(amount, 0.001, 1.0)
	var ry := _tile_h * 0.34 * clampf(amount, 0.001, 1.0)
	var points := PackedVector2Array()
	for index in range(17):
		var angle := PI * float(index) / 16.0
		points.append(center + Vector2(cos(angle) * rx, sin(angle) * ry))
	draw_colored_polygon(points, Color(0.06, 0.22, 0.25, 0.93 * opacity))
	var arc := PackedVector2Array()
	for index in range(17):
		var angle := PI * float(index) / 16.0
		arc.append(center + Vector2(cos(angle) * rx, sin(angle) * ry))
	draw_polyline(arc, Color(0.55, 1.0, 0.9, opacity), 3.0, true)

func _draw_player(center: Vector2, rotation: float, opacity: float, scale_x: float, scale_y: float = 1.0) -> void:
	if opacity <= 0.01:
		return
	draw_set_transform(center + Vector2(0, 18.0 * scale_y), 0.0, Vector2(scale_x, 0.36 * scale_y))
	draw_circle(Vector2.ZERO, 16.0, Color(0.01, 0.05, 0.06, 0.35 * opacity))
	draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)
	draw_set_transform(center, rotation, Vector2(scale_x, scale_y))
	var body := Color("48d1bd")
	body.a = opacity
	var highlight := Color("e7fff8")
	highlight.a = opacity
	var outline := _capsule_outline()
	for index in range(outline.size()):
		outline[index] += Vector2(0, 24)
	draw_colored_polygon(outline, body)
	draw_circle(Vector2(-3, -17), 3.0, highlight)
	draw_circle(Vector2(0, -23), 2.3, Color(1.0, 0.82, 0.39, opacity))
	draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)
	draw_arc(center, 22.0 * maxf(scale_x, scale_y), 0.0, TAU, 48, Color(0.37, 0.98, 0.84, 0.42 * opacity), maxf(0.5, 1.2 * minf(scale_x, scale_y)), true)

func _draw_diamond(center: Vector2, width: float, height: float, fill: Color, outline: Color, line_width: float, _depth: float) -> void:
	var points := PackedVector2Array([
		center + Vector2(0, -height * 0.5), center + Vector2(width * 0.5, 0),
		center + Vector2(0, height * 0.5), center + Vector2(-width * 0.5, 0)
	])
	if fill.a > 0.0:
		draw_colored_polygon(points, fill)
	draw_polyline(PackedVector2Array([points[0], points[1], points[2], points[3], points[0]]), outline, line_width, true)

func _draw_ellipse(center: Vector2, rx: float, ry: float, color: Color) -> void:
	if rx < 1.0 or ry < 1.0:
		return
	var points := PackedVector2Array()
	for index in range(48):
		var angle := TAU * float(index) / 48.0
		points.append(center + Vector2(cos(angle) * rx, sin(angle) * ry))
	draw_colored_polygon(points, color)

func _draw_ellipse_outline(center: Vector2, rx: float, ry: float, color: Color, width: float) -> void:
	var points := PackedVector2Array()
	for index in range(49):
		var angle := TAU * float(index) / 48.0
		points.append(center + Vector2(cos(angle) * rx, sin(angle) * ry))
	draw_polyline(points, color, width, true)

func _board_area() -> Rect2:
	return Rect2(Vector2(16, 76), Vector2(size.x - 32, size.y - 94))

func _main_grid_area() -> Rect2:
	# Reserve the objective column at every window size, including short wide maps.
	var top := maxf(230.0 if size.x < 850 else 246.0,_preview_bounds().end.y+54.0)
	if int(level.get("width",0))+int(level.get("height",0)) >= 12:
		top = _preview_bounds().end.y+54.0
	return Rect2(Vector2(246, top), Vector2(size.x - 266, maxf(120, size.y - top - 132)))

func _preview_bounds() -> Rect2:
	if int(level.get("width",0))+int(level.get("height",0)) >= 12:
		return Rect2(Vector2(size.x-210.0,26.0),Vector2(192.0,132.0))
	var preview_size := Vector2(minf(222.0, size.x * 0.31), minf(172.0, size.y * 0.30))
	return Rect2(Vector2(size.x - preview_size.x - 18.0, 52.0), preview_size)

func _preview_mini_area() -> Rect2:
	var bounds := _preview_bounds()
	return Rect2(bounds.position + Vector2(8, 27), bounds.size - Vector2(16, 34))

func _cell_center(position: Array) -> Vector2:
	var width := int(level.get("width", 1))
	var height := int(level.get("height", 1))
	var center_x := float(position[1]) - float(position[2]) - float(width - height) * 0.5
	var center_y := float(position[1]) + float(position[2]) - float(width + height - 2) * 0.5
	return _board_origin + Vector2(center_x * _tile_w * 0.5, center_y * _tile_h * 0.5)

func _cell_center_xy(_layer: int, x: float, y: float) -> Vector2:
	var width := int(level.get("width", 1))
	var height := int(level.get("height", 1))
	var center_x := x - y - float(width - height) * 0.5
	var center_y := x + y - float(width + height - 2) * 0.5
	return _board_origin + Vector2(center_x * _tile_w * 0.5, center_y * _tile_h * 0.5)

func _diamond_points(center: Vector2) -> PackedVector2Array:
	return PackedVector2Array([
		center + Vector2(0, -_tile_h * 0.5), center + Vector2(_tile_w * 0.5, 0),
		center + Vector2(0, _tile_h * 0.5), center + Vector2(-_tile_w * 0.5, 0)
	])

func _is_floor(layer: int, x: int, y: int) -> bool:
	return layer >= 0 and layer < level.floors.size() and y >= 0 and y < level.height and x >= 0 and x < level.width and String(level.floors[layer][y]).substr(x, 1) == "."

func _same_cell(a: Array, b: Array) -> bool:
	return LevelCatalog.position_key(a) == LevelCatalog.position_key(b)

func _switch_at(position: Array) -> Dictionary:
	for item in level.switches:
		if _same_cell(item.at, position):
			return item
	return {}

func _gate_at(position: Array) -> Dictionary:
	for gate in level.gates:
		if _same_cell(gate.at, position):
			return gate
	for gate in level.sealed_gates:
		if _same_cell(gate.at, position):
			return gate
	return {}

func _gate_open(gate: Dictionary) -> bool:
	if gate.has("id"):
		return state.get("opened_gates", []).has(String(gate.id)) or bool(state.get("key_owned", false))
	return ((int(state.get("bits", 0)) >> int(gate.bit)) & 1) == int(gate.value)

func _item_at(position: Array) -> Dictionary:
	for item in level.items:
		if _same_cell(item.at, position):
			return item
	return {}

func _beacon_at(position: Array) -> int:
	for index in range(level.beacons.size()):
		if _same_cell(level.beacons[index], position):
			return index
	return -1

func _flow_at(position: Array) -> Dictionary:
	for flow in level.currents:
		if _same_cell(flow.at, position):
			return flow
	return {}

func _is_goal(layer: int, x: int, y: int) -> bool:
	return _same_cell([layer, x, y], level.goal)

func _is_lift(x: int, y: int) -> bool:
	for lift in level.lifts:
		if int(lift[0]) == x and int(lift[1]) == y:
			return true
	return false

func _gui_input(event: InputEvent) -> void:
	if paused:
		return
	if is_animating():
		return
	if event is InputEventMouseMotion:
		var hover := _cell_at((event as InputEventMouseMotion).position)
		if hover != _hover:
			_hover = hover
			queue_redraw()
	elif event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
		var mouse := (event as InputEventMouseButton).position
		if _preview_rect.has_point(mouse):
			preview_pressed.emit(1 - selected_layer)
			accept_event()
			return
		var cell := _cell_at(mouse)
		if cell.x >= 0 and cell.y >= 0:
			cell_pressed.emit(selected_layer, cell.x, cell.y)
			accept_event()

func _cell_at(point: Vector2) -> Vector2i:
	for y in range(int(level.get("height", 0))):
		for x in range(int(level.get("width", 0))):
			var center := _cell_center([selected_layer, x, y])
			var distance := absf(point.x - center.x) / maxf(1.0, _tile_w * 0.5) + absf(point.y - center.y) / maxf(1.0, _tile_h * 0.5)
			if distance <= 1.0:
				return Vector2i(x, y)
	return Vector2i(-1, -1)
