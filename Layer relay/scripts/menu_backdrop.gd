extends Control
class_name MenuBackdrop

var page := "home"
var _time := 0.0

func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)

func _process(delta: float) -> void:
	_time += delta
	queue_redraw()

func _draw() -> void:
	draw_rect(Rect2(Vector2.ZERO, size), Color("080e1c"))
	var focus := Vector2(size.x * 0.61, size.y * 0.43)
	for i in range(18, 0, -1):
		var radius := float(i) * 34.0
		draw_circle(focus, radius, Color(0.12, 0.25, 0.39, 0.008))
	for i in range(66):
		var seed_x := fmod(float(i * 173 + 41), 997.0) / 997.0
		var seed_y := fmod(float(i * 269 + 113), 911.0) / 911.0
		var point := Vector2(seed_x * size.x, fposmod(seed_y * size.y - _time * float(2 + i % 3), size.y))
		var alpha := 0.12 + (sin(_time * 0.8 + float(i)) + 1.0) * 0.12
		draw_rect(Rect2(point, Vector2(2, 2) if i % 4 != 0 else Vector2(3, 3)), Color(0.55, 0.81, 0.92, alpha))
	var orbit := Vector2(size.x * 0.67, size.y * 0.50)
	_ellipse(orbit, Vector2(size.x * 0.47, size.y * 0.33), -0.32, Color(0.40, 0.64, 0.76, 0.10))
	_ellipse(orbit, Vector2(size.x * 0.55, size.y * 0.37), -0.32, Color(0.40, 0.64, 0.76, 0.055))
	_trace(Vector2(0, size.y * 0.17), 1, Color(0.42, 0.86, 0.87, 0.30))
	_trace(Vector2(size.x, size.y * 0.78), -1, Color(0.61, 0.59, 0.92, 0.30))
	var edge_opacity := 0.70 if page == "home" else 0.38
	_cluster(Vector2(size.x * 0.07, size.y * 0.34), 68, -0.12, edge_opacity, false)
	_cluster(Vector2(size.x * 0.92, size.y * 0.74), 70, 0.12, edge_opacity, true)
	_cluster(Vector2(size.x * 0.16, size.y * 0.84), 36, 0.16, edge_opacity * 0.7, false)
	_item(Vector2(size.x * 0.13, size.y * 0.61 + sin(_time * 0.7) * 9.0), 0.8, -0.28, false, edge_opacity)
	_item(Vector2(size.x * 0.88, size.y * 0.15 + cos(_time * 0.55) * 8.0), 0.75, 0.24, true, edge_opacity)
	if page == "home":
		_relay(Vector2(size.x * 0.79, size.y * 0.42 + sin(_time * 0.6) * 8.0))
	_small_cross(Vector2(size.x * 0.21, size.y * 0.16), Color(0.54, 0.93, 0.89, 0.5))
	_small_cross(Vector2(size.x * 0.83, size.y * 0.88), Color(0.69, 0.66, 1.0, 0.5))
	for y in range(0, int(size.y), 4):
		draw_line(Vector2(0, y), Vector2(size.x, y), Color(0, 0, 0, 0.035), 1)

func _ellipse(center: Vector2, radius: Vector2, angle: float, color: Color) -> void:
	var points := PackedVector2Array()
	for i in range(97):
		var t := TAU * float(i) / 96.0
		points.append(center + Vector2(cos(t) * radius.x, sin(t) * radius.y).rotated(angle))
	draw_polyline(points, color, 1.0, true)

func _trace(origin: Vector2, direction: int, color: Color) -> void:
	var d := float(direction)
	var points := PackedVector2Array([origin, origin + Vector2(130 * d, 0), origin + Vector2(184 * d, -35), origin + Vector2(275 * d, -35)])
	draw_polyline(points, color, 1.0, true)
	draw_circle(points[points.size() - 1], 3.0, color)
	draw_line(origin + Vector2(20 * d, 9), origin + Vector2(110 * d, 9), Color(color, 0.12), 1.0)

func _cluster(center: Vector2, width: float, angle: float, opacity: float, portal: bool) -> void:
	draw_set_transform(center, angle)
	var layout := [Vector2(-1, 0), Vector2(0, 0), Vector2(1, 0), Vector2(0, 1)]
	for cell in layout:
		var point := Vector2((cell.x - cell.y) * width * 0.5, (cell.x + cell.y) * width * 0.265)
		_tile(point, width, Color("203e50", opacity), Color("72c4ce", opacity * 0.6))
		if cell == Vector2.ZERO:
			if portal:
				_portal(point - Vector2(0, 3), width * 0.31, opacity)
			else:
				var points := PackedVector2Array([point + Vector2(-9, -5), point + Vector2(2, 1), point + Vector2(12, -5)])
				draw_polyline(points, Color("a0f0de", opacity), 2.0, true)
	draw_set_transform(Vector2.ZERO)

func _tile(center: Vector2, width: float, fill: Color, edge: Color) -> void:
	var h := width * 0.53
	var points := PackedVector2Array([center + Vector2(0, -h * 0.5), center + Vector2(width * 0.5, 0), center + Vector2(0, h * 0.5), center + Vector2(-width * 0.5, 0)])
	draw_colored_polygon(PackedVector2Array([points[1], points[2], points[3], points[3] + Vector2(0, 9), points[2] + Vector2(0, 9), points[1] + Vector2(0, 9)]), fill.darkened(0.42))
	draw_colored_polygon(points, fill)
	draw_polyline(PackedVector2Array([points[0], points[1], points[2], points[3], points[0]]), edge, 1.0, true)

func _portal(center: Vector2, radius: float, opacity: float) -> void:
	for i in range(3):
		_ellipse(center, Vector2(radius + i * 4.0, radius * 0.36 + i * 2.0), 0, Color(0.37, 0.94, 0.87, opacity * (0.7 if i == 0 else 0.16)))
	for i in range(5):
		var t := fposmod(_time * 0.22 + float(i) / 5.0, 1.0)
		var point := center + Vector2(sin(float(i) * 2.2) * radius * 0.5, -t * 38)
		draw_rect(Rect2(point, Vector2(2, 4)), Color(0.55, 1, 0.91, opacity * (1.0 - t) * 0.4))

func _relay(center: Vector2) -> void:
	var w := 115.0
	for i in range(3):
		var offset := Vector2(-float(i) * 5, float(i) * 43)
		_tile(center + offset, w, Color("183345", 0.75 - i * 0.12), Color("82b2d6", 0.7 - i * 0.15))
	var upper := center - Vector2(0, 102)
	_portal(upper, 40, 0.85)
	_portal(center, 40, 0.9)
	draw_line(upper, center, Color(0.42, 0.96, 0.87, 0.15), 1.0)
	var capsule := center + Vector2(0, -41)
	for i in range(4, 0, -1):
		draw_circle(capsule, 15 + float(i) * 5.0, Color(0.33, 0.93, 0.83, 0.012))
	draw_rect(Rect2(capsule + Vector2(-10, -14), Vector2(20, 28)), Color("82efdb"))
	draw_circle(capsule + Vector2(0, -14), 10, Color("82efdb"))
	draw_circle(capsule + Vector2(0, 14), 10, Color("82efdb"))
	draw_circle(capsule + Vector2(-3, -17), 3, Color("effffb"))
	_ellipse(center + Vector2(0, 17), Vector2(106, 48), -0.16, Color(0.45, 0.64, 0.88, 0.17))

func _item(center: Vector2, scale_value: float, angle: float, anchor: bool, opacity: float) -> void:
	draw_set_transform(center, angle, Vector2.ONE * scale_value)
	var color := Color("b3abf5", opacity) if anchor else Color("f0d59d", opacity)
	var points := PackedVector2Array([Vector2(0, -23), Vector2(17, 0), Vector2(0, 23), Vector2(-17, 0), Vector2(0, -23)])
	draw_colored_polygon(points, Color(color, opacity * 0.08))
	draw_polyline(points, color, 1.4, true)
	if anchor:
		draw_circle(Vector2.ZERO, 7, Color(color, opacity * 0.3))
		draw_arc(Vector2.ZERO, 9, 0, TAU, 28, color, 1.5, true)
		draw_line(Vector2(0, -14), Vector2(0, 14), color, 1.5)
		draw_line(Vector2(-14, 0), Vector2(14, 0), color, 1.5)
	else:
		draw_arc(Vector2(0, -6), 5, 0, TAU, 20, color, 1.5, true)
		draw_line(Vector2(0, 0), Vector2(0, 12), color, 2)
		draw_line(Vector2(0, 10), Vector2(6, 10), color, 2)
	draw_set_transform(Vector2.ZERO)

func _small_cross(center: Vector2, color: Color) -> void:
	draw_line(center - Vector2(6, 0), center + Vector2(6, 0), color, 1)
	draw_line(center - Vector2(0, 6), center + Vector2(0, 6), color, 1)
