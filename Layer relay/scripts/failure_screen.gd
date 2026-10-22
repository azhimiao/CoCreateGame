extends Control
class_name FailureScreen

signal replay_requested
signal levels_requested

var reason := "步数耗尽"
var replay_button: GlyphButton
var levels_button: GlyphButton
var _content: Control

func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	var shade := ColorRect.new()
	shade.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	shade.color = Color("110b1c", 0.86)
	add_child(shade)
	_content = Control.new()
	_content.size = Vector2(660,360)
	add_child(_content)
	_label("连 接 中 断", 16, Color("ff94ae"), 0)
	_label("再规划一次航线", 34, Color("f2ecf5"), 40)
	_label(reason, 18, Color("cda9bc"), 103)
	replay_button = _choice("replay", "重新开始 · R / Enter", 175)
	levels_button = _choice("levels", "重新选择关卡 · Esc", 403)
	replay_button.pressed.connect(func() -> void: replay_requested.emit())
	levels_button.pressed.connect(func() -> void: levels_requested.emit())
	for pair in [[replay_button,levels_button],[levels_button,replay_button]]:
		var path: NodePath = pair[0].get_path_to(pair[1])
		for property in ["focus_next","focus_previous","focus_neighbor_left","focus_neighbor_right"]:
			pair[0].set(property,path)
	replay_button.grab_focus()
	resized.connect(_layout)
	_layout()
	modulate.a = 0.0
	create_tween().tween_property(self,"modulate:a",1.0,0.35)

func _choice(glyph: String, caption: String, x: float) -> GlyphButton:
	var button := GlyphButton.new()
	button.glyph = glyph
	button.position = Vector2(x,186)
	button.size = Vector2(82,82)
	button.tooltip_text = caption
	_content.add_child(button)
	var label := Label.new()
	label.text = caption
	label.position = Vector2(x-72,286)
	label.size.x = 226
	label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	label.add_theme_font_size_override("font_size",16)
	label.add_theme_color_override("font_color",Color("d0bdcf"))
	_content.add_child(label)
	return button

func _label(text_value: String, font_size: int, color: Color, y: float) -> void:
	var label := Label.new()
	label.text = text_value
	label.position.y = y
	label.size.x = 660
	label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	label.add_theme_font_size_override("font_size",font_size)
	label.add_theme_color_override("font_color",color)
	_content.add_child(label)

func _layout() -> void:
	var factor := minf(1.0,minf(size.x / 720,size.y / 440))
	_content.scale = Vector2.ONE * factor
	_content.position = (size - _content.size * factor) * 0.5
