extends Button
class_name GlyphButton

var glyph := "home"
var accent := Color("80e4d0")

func _ready() -> void:
	text = ""
	for state_name in ["normal", "hover", "pressed", "disabled", "focus"]:
		add_theme_stylebox_override(state_name, StyleBoxEmpty.new())
	mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
	mouse_entered.connect(queue_redraw)
	mouse_exited.connect(queue_redraw)
	focus_entered.connect(queue_redraw)
	focus_exited.connect(queue_redraw)
	button_down.connect(queue_redraw)
	button_up.connect(queue_redraw)

func _has_point(point: Vector2) -> bool:
	return point.distance_to(size * 0.5) <= minf(size.x, size.y) * 0.5

func _draw() -> void:
	var radius := minf(size.x, size.y) * 0.5 - 2.0
	var center := size * 0.5
	var hot := not disabled and (is_hovered() or has_focus())
	var tint := Color("5c7283") if disabled else accent
	draw_circle(center + Vector2(0, 3), radius, Color("030b13", 0.35))
	draw_circle(center, radius, Color("25444f") if hot else Color("172a38", 0.96))
	draw_arc(center, radius, 0, TAU, 64, Color(tint, 0.92 if hot else 0.42), 1.6, true)
	draw_arc(center, radius - 4, -PI * 0.76, -PI * 0.22, 24, Color(tint, 0.28), 1.0, true)
	if has_focus() and not disabled:
		draw_arc(center, radius + 2, 0, TAU, 64, Color("e8f8ff"), 1.4, true)
	var scale_value := radius / 23.0 * (0.92 if button_pressed else 1.0)
	draw_set_transform(center, 0, Vector2.ONE * scale_value)
	_draw_glyph(tint)
	draw_set_transform(Vector2.ZERO)

func _line(points: Array[Vector2], color: Color, width := 1.8) -> void:
	draw_polyline(PackedVector2Array(points), color, width, true)

func _draw_glyph(color: Color) -> void:
	match glyph:
		"pause":
			draw_line(Vector2(-5, -10), Vector2(-5, 10), color, 4, true)
			draw_line(Vector2(5, -10), Vector2(5, 10), color, 4, true)
		"resume":
			draw_colored_polygon(PackedVector2Array([Vector2(-6, -11), Vector2(12, 0), Vector2(-6, 11)]), color)
		"hint":
			draw_arc(Vector2(0, -4), 8, -PI * 0.1, PI * 1.1, 30, color, 1.8, true)
			_line([Vector2(-7.5, -1.5), Vector2(-4, 5), Vector2(-4, 9), Vector2(4, 9), Vector2(4, 5), Vector2(7.5, -1.5)], color)
			draw_line(Vector2(-3, 13), Vector2(3, 13), color, 1.8, true)
			for i in range(5):
				var direction := Vector2.from_angle(PI + float(i) * PI / 4)
				draw_line(Vector2(0, -4) + direction * 12, Vector2(0, -4) + direction * 15, Color(color, 0.7), 1.3, true)
		"about":
			draw_circle(Vector2(0, -8), 1.8, color)
			_line([Vector2(-3, -1), Vector2(0, -1), Vector2(0, 10)], color, 2.2)
			draw_line(Vector2(-4, 10), Vector2(5, 10), color, 2.2, true)
		"settings":
			draw_arc(Vector2.ZERO, 8, 0, TAU, 40, color, 1.8, true)
			draw_arc(Vector2.ZERO, 3, 0, TAU, 24, color, 1.6, true)
			for i in range(8):
				var direction := Vector2.from_angle(TAU * float(i) / 8)
				draw_line(direction * 9, direction * 13, color, 3, true)
		"home":
			_line([Vector2(-13, -1), Vector2(0, -12), Vector2(13, -1)], color)
			_line([Vector2(-9, -2), Vector2(-9, 11), Vector2(9, 11), Vector2(9, -2)], color)
			_line([Vector2(-3, 11), Vector2(-3, 3), Vector2(3, 3), Vector2(3, 11)], color, 1.5)
		"levels":
			for y in range(2):
				for x in range(2):
					draw_rect(Rect2(Vector2(-11 + x * 13, -11 + y * 13), Vector2(8, 8)), color, false, 1.7, true)
		"rules":
			_line([Vector2.ZERO, Vector2(-5, -4), Vector2(-13, -4), Vector2(-13, 10), Vector2(-5, 10), Vector2(0, 13), Vector2(5, 10), Vector2(13, 10), Vector2(13, -4), Vector2(5, -4), Vector2.ZERO, Vector2(0, 13)], color)
			for side in [-1, 1]:
				draw_line(Vector2(4 * side, 2), Vector2(10 * side, 2), Color(color, 0.65), 1.3, true)
				draw_line(Vector2(4 * side, 6), Vector2(10 * side, 6), Color(color, 0.65), 1.3, true)
		"next":
			draw_line(Vector2(-12, 0), Vector2(11, 0), color, 2, true)
			_line([Vector2(3, -8), Vector2(12, 0), Vector2(3, 8)], color, 2)
			draw_line(Vector2(15, -9), Vector2(15, 9), Color(color, 0.65), 1.5, true)
		"replay":
			draw_arc(Vector2.ZERO, 11, -PI * 0.75, PI * 0.94, 48, color, 1.8, true)
			_line([Vector2(-8, -13), Vector2(-8, -5), Vector2(0, -6)], color, 1.8)
