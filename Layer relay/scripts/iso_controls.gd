extends Control
class_name IsoControls

signal action_pressed(action: String)

const ACTIONS := ["L", "U", "D", "R", "X"]
const LABELS := {"L": "左 · A", "U": "上 · W", "D": "下 · S", "R": "右 · D", "X": "升降 · X"}
const OFFSETS := {"L": Vector2(-58, -31), "U": Vector2(58, -31), "D": Vector2(-58, 31), "R": Vector2(58, 31), "X": Vector2.ZERO}
var _hover_action := ""

func _ready() -> void:
	custom_minimum_size = Vector2(236, 166)
	mouse_filter = Control.MOUSE_FILTER_STOP
	mouse_exited.connect(func() -> void:
		_hover_action = ""
		queue_redraw())

static func screen_direction(action: String) -> Vector2:
	var delta: Vector2i = GameRules.DIRECTIONS.get(action, Vector2i.ZERO)
	return Vector2(float(delta.x - delta.y), float(delta.x + delta.y) * 0.53).normalized()

func _center(action: String) -> Vector2:
	return Vector2(size.x * 0.5, 78) + Vector2(OFFSETS[action])

func action_at(point: Vector2) -> String:
	for action in ACTIONS:
		var relative := point - _center(action)
		if absf(relative.x) / 53.0 + absf(relative.y) / 28.0 <= 1.0:
			return action
	return ""

func _draw() -> void:
	for action in ACTIONS:
		var center := _center(action)
		var points := PackedVector2Array([center + Vector2(0, -28), center + Vector2(53, 0), center + Vector2(0, 28), center + Vector2(-53, 0)])
		var accent := Color("f1c86b") if action == "X" else Color("62d6c3")
		var fill := Color("304e56") if action == _hover_action else Color("20343c")
		draw_colored_polygon(PackedVector2Array([points[1], points[2], points[3], points[3] + Vector2(0, 5), points[2] + Vector2(0, 5), points[1] + Vector2(0, 5)]), Color("102028"))
		draw_colored_polygon(points, fill)
		draw_polyline(PackedVector2Array([points[0], points[1], points[2], points[3], points[0]]), accent.darkened(0.35), 1.0, true)
		if action == "X":
			_arrow(center + Vector2(-6, -8), Vector2.UP, accent, 8)
			_arrow(center + Vector2(6, -8), Vector2.DOWN, accent, 8)
		else:
			_arrow(center + Vector2(0, -7), screen_direction(action), accent, 13)
		var text := String(LABELS[action])
		var font := ThemeDB.fallback_font
		var text_width := font.get_string_size(text, HORIZONTAL_ALIGNMENT_LEFT, -1, 11).x
		draw_string(font, center + Vector2(-text_width * 0.5, 15), text, HORIZONTAL_ALIGNMENT_LEFT, -1, 11, Color("d6e4e0"))

func _arrow(center: Vector2, direction: Vector2, color: Color, length: float) -> void:
	var perpendicular := Vector2(-direction.y, direction.x)
	var tip := center + direction * length
	draw_line(center - direction * length, tip, color, 2.0, true)
	draw_line(tip, tip - direction * 6.0 + perpendicular * 3.5, color, 2.0, true)
	draw_line(tip, tip - direction * 6.0 - perpendicular * 3.5, color, 2.0, true)

func _gui_input(event: InputEvent) -> void:
	if event is InputEventMouseMotion:
		var action := action_at(event.position)
		if action != _hover_action:
			_hover_action = action
			tooltip_text = "沿棋盘%s方向移动" % LABELS[action] if not action.is_empty() and action != "X" else "在升降台切换楼层 · X / 空格"
			queue_redraw()
	elif event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
		var action := action_at(event.position)
		if not action.is_empty():
			action_pressed.emit(action)
			accept_event()
