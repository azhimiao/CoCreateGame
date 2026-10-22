extends Control
class_name TutorialCoach

signal next_requested
signal previous_requested

var focus_rect := Rect2()
var title := ""
var body := ""
var step_index := 0
var step_count := 1
var previous_button: Button
var next_button: Button
var bubble: PanelContainer
var _body_label: RichTextLabel
var _step_label: Label
var _pointer_side := "top"

func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	focus_mode = Control.FOCUS_ALL
	_build_bubble()
	resized.connect(_layout)
	set_process(true)
	_layout()

func configure(heading: String, copy: String, index: int, count: int, target: Rect2) -> void:
	title = heading
	body = copy
	step_index = index
	step_count = count
	focus_rect = target
	if not is_node_ready():
		return
	_step_label.text = "%s  ·  %d / %d" % [title, step_index + 1, step_count]
	_body_label.text = body
	previous_button.disabled = step_index == 0
	next_button.text = "开始操作" if step_index == step_count - 1 and title == "界面导览" else ("完成" if step_index == step_count - 1 else "下一步")
	_layout()
	queue_redraw()
	next_button.grab_focus()

func set_target(target: Rect2) -> void:
	if focus_rect != target:
		focus_rect = target
		_layout()
		queue_redraw()

func _process(_delta: float) -> void:
	# Containers settle after text wrapping; re-clamp using the actual final height.
	_layout()
	queue_redraw()

func _visible_area() -> Rect2:
	var viewport := get_viewport_rect()
	return Rect2(Vector2.ZERO,size).intersection(Rect2(viewport.position-global_position,viewport.size)).grow(-12)

func _focus_bounds() -> Rect2:
	return focus_rect.grow(10).intersection(_visible_area().grow(4))

func _draw() -> void:
	var focus := _focus_bounds()
	var shade := Color(0.015,0.035,0.06,0.76)
	draw_rect(Rect2(0,0,size.x,focus.position.y),shade)
	draw_rect(Rect2(0,focus.position.y+focus.size.y,size.x,size.y-focus.position.y-focus.size.y),shade)
	draw_rect(Rect2(0,focus.position.y,focus.position.x,focus.size.y),shade)
	draw_rect(Rect2(focus.position.x+focus.size.x,focus.position.y,size.x-focus.position.x-focus.size.x,focus.size.y),shade)
	var pulse := 0.65 + 0.25 * sin(float(Time.get_ticks_msec()) / 270.0)
	draw_rect(focus,Color(0.31,0.95,0.83,pulse*0.82),false,2.2,true)
	var corner := 12.0
	var color := Color(0.68,1.0,0.91,pulse)
	for point in [focus.position,Vector2(focus.end.x,focus.position.y),focus.end,Vector2(focus.position.x,focus.end.y)]:
		var sx := 1.0 if point.x == focus.position.x else -1.0
		var sy := 1.0 if point.y == focus.position.y else -1.0
		draw_line(point,point+Vector2(sx*corner,0),color,3.0,true)
		draw_line(point,point+Vector2(0,sy*corner),color,3.0,true)
	# A short speech pointer links the bubble to the highlighted card or tile.
	if bubble != null:
		var horizontal := _pointer_side in ["left","right"]
		var base := Vector2.ZERO
		var tip := Vector2.ZERO
		if horizontal:
			var y := clampf(focus.get_center().y,bubble.position.y+20,bubble.position.y+bubble.size.y-20)
			base = Vector2(bubble.position.x if _pointer_side == "left" else bubble.get_rect().end.x,y)
			tip = Vector2(focus.end.x+5 if _pointer_side == "left" else focus.position.x-5,y)
		else:
			var x := clampf(focus.get_center().x,bubble.position.x+24,bubble.get_rect().end.x-24)
			base = Vector2(x,bubble.position.y if _pointer_side == "top" else bubble.get_rect().end.y)
			tip = Vector2(x,focus.end.y+5 if _pointer_side == "top" else focus.position.y-5)
		var span := Vector2(0,8) if horizontal else Vector2(8,0)
		var points := PackedVector2Array([base-span,tip,base+span])
		draw_colored_polygon(points,Color("10232f"))
		draw_polyline(points,Color("65dfca"),1.0,true)

func _build_bubble() -> void:
	bubble = PanelContainer.new()
	bubble.custom_minimum_size = Vector2(300,0)
	var style := StyleBoxFlat.new()
	style.bg_color = Color("10232f",0.98)
	style.border_color = Color("65dfca")
	style.set_border_width_all(1)
	style.set_corner_radius_all(8)
	style.content_margin_left = 18
	style.content_margin_right = 18
	style.content_margin_top = 15
	style.content_margin_bottom = 13
	bubble.add_theme_stylebox_override("panel",style)
	add_child(bubble)
	var column := VBoxContainer.new()
	column.add_theme_constant_override("separation",10)
	bubble.add_child(column)
	_step_label = Label.new()
	_step_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_step_label.add_theme_font_size_override("font_size",13)
	_step_label.add_theme_color_override("font_color",Color("80f1dc"))
	column.add_child(_step_label)
	_body_label = RichTextLabel.new()
	_body_label.custom_minimum_size = Vector2(0,48)
	_body_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_body_label.fit_content = false
	_body_label.scroll_active = true
	_body_label.add_theme_stylebox_override("normal",StyleBoxEmpty.new())
	_body_label.add_theme_constant_override("line_separation",4)
	_body_label.add_theme_font_size_override("font_size",16)
	_body_label.add_theme_color_override("default_color",Color("ecf5fa"))
	column.add_child(_body_label)
	var buttons := HBoxContainer.new()
	buttons.alignment = BoxContainer.ALIGNMENT_END
	buttons.add_theme_constant_override("separation",8)
	column.add_child(buttons)
	previous_button = Button.new()
	previous_button.text = "上一步"
	previous_button.custom_minimum_size = Vector2(92,38)
	previous_button.pressed.connect(func() -> void: previous_requested.emit())
	buttons.add_child(previous_button)
	next_button = Button.new()
	next_button.text = "下一步"
	next_button.custom_minimum_size = Vector2(118,38)
	next_button.pressed.connect(func() -> void: next_requested.emit())
	buttons.add_child(next_button)

func _layout() -> void:
	if bubble == null:
		return
	var area := _visible_area()
	if area.size.x < 100 or area.size.y < 100:
		return
	var body_height := clampf(float(_body_label.get_content_height()),48.0,minf(164.0,area.size.y*0.30))
	_body_label.custom_minimum_size.y = body_height
	bubble.size = Vector2(minf(430,area.size.x-8),bubble.get_combined_minimum_size().y)
	var focus := _focus_bounds()
	var centered_x := clampf(focus.get_center().x-bubble.size.x*0.5,area.position.x,area.end.x-bubble.size.x)
	var centered_y := clampf(focus.get_center().y-bubble.size.y*0.5,area.position.y,area.end.y-bubble.size.y)
	var gap := 16.0
	var candidates := [
		{"position":Vector2(centered_x,focus.position.y-gap-bubble.size.y),"side":"bottom"},
		{"position":Vector2(centered_x,focus.end.y+gap),"side":"top"},
		{"position":Vector2(focus.end.x+gap,centered_y),"side":"left"},
		{"position":Vector2(focus.position.x-gap-bubble.size.x,centered_y),"side":"right"}
	]
	for candidate in candidates:
		if area.encloses(Rect2(candidate.position,bubble.size)):
			bubble.position = candidate.position
			_pointer_side = candidate.side
			return
	# Tight layouts keep the text and both controls visible inside the viewport.
	bubble.position = Vector2(centered_x,clampf(focus.position.y-gap-bubble.size.y,area.position.y,area.end.y-bubble.size.y))
	_pointer_side = "bottom" if bubble.get_rect().get_center().y < focus.get_center().y else "top"

func _gui_input(event: InputEvent) -> void:
	if event is InputEventMouseButton or event is InputEventMouseMotion:
		accept_event()
