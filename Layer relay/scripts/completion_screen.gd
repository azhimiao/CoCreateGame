extends Control
class_name CompletionScreen

signal next_requested
signal replay_requested
signal levels_requested

var next_available := true
var level_name := ""
var stars := 3
var used := 0
var par := 0
var seconds := 0.0
var time_limit := 90.0
var awards: Dictionary = {}
var next_button: GlyphButton
var replay_button: GlyphButton
var levels_button: GlyphButton
var _content: Control

func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	var shade := ColorRect.new()
	shade.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	shade.color = Color("030a14", 0.84)
	add_child(shade)
	_content = Control.new()
	_content.size = Vector2(700, 440)
	_content.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_content)
	_label("回 路 已 点 亮", 17, Color("80f1dc"), 6)
	_label(level_name + " · 通关", 38, Color("effaff"), 42)
	_label("★".repeat(stars) + "☆".repeat(3 - stars), 28, Color("f2d28b"), 105)
	for index in range(3):
		var earned := bool(awards.get(["cleared", "timed", "efficient"][index], false))
		var caption := Label.new()
		caption.text = ("★ " if earned else "☆ ") + ["完成通关", "用时 %s / %s" % [ScoreRules.clock_text(seconds), ScoreRules.clock_text(time_limit)], "步数 %d / 最佳 %d" % [used, par]][index]
		caption.position = Vector2(10 + index * 230, 157)
		caption.size = Vector2(220, 48)
		caption.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		caption.add_theme_font_size_override("font_size", 15)
		caption.add_theme_color_override("font_color", Color("f1d28b") if earned else Color("70889b"))
		_content.add_child(caption)
	next_button = _choice("next", "下一关", 133)
	next_button.disabled = not next_available
	next_button.tooltip_text = "进入下一开放关卡" if next_available else "当前开放关卡已全部完成"
	next_button.pressed.connect(func() -> void: next_requested.emit())
	replay_button = _choice("replay", "重玩此关卡", 309)
	replay_button.pressed.connect(func() -> void: replay_requested.emit())
	levels_button = _choice("levels", "回到选关", 485)
	levels_button.pressed.connect(func() -> void: levels_requested.emit())
	if not next_available:
		_label("当前空间已全部点亮，更多旅程正在构建。", 13, Color("8ba0b6"), 412)
	var focus_buttons: Array[GlyphButton] = []
	focus_buttons.assign([next_button, replay_button, levels_button] if next_available else [replay_button, levels_button])
	for i in range(focus_buttons.size()):
		var button := focus_buttons[i]
		var forward := button.get_path_to(focus_buttons[(i + 1) % focus_buttons.size()])
		var backward := button.get_path_to(focus_buttons[posmod(i - 1, focus_buttons.size())])
		button.focus_next = forward
		button.focus_previous = backward
		button.focus_neighbor_left = backward
		button.focus_neighbor_right = forward
		button.focus_neighbor_top = forward
		button.focus_neighbor_bottom = backward
	focus_buttons[0].grab_focus()
	resized.connect(_layout)
	_layout()
	modulate.a = 0.0
	create_tween().tween_property(self, "modulate:a", 1.0, 0.42)

func _choice(glyph: String, title: String, x: float) -> GlyphButton:
	var button := GlyphButton.new()
	button.glyph = glyph
	button.position = Vector2(x, 265)
	button.size = Vector2(82, 82)
	button.tooltip_text = title
	_content.add_child(button)
	var caption := Label.new()
	caption.text = title
	caption.position = Vector2(x - 33, 358)
	caption.size = Vector2(148, 28)
	caption.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	caption.add_theme_font_size_override("font_size", 16)
	caption.add_theme_color_override("font_color", Color("c3d3e2") if glyph != "next" or next_available else Color("5e7386"))
	caption.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_content.add_child(caption)
	return button

func _label(value: String, font_size: int, color: Color, y: float) -> void:
	var label := Label.new()
	label.text = value
	label.position = Vector2(0, y)
	label.size.x = 700
	label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	label.add_theme_font_size_override("font_size", font_size)
	label.add_theme_color_override("font_color", color)
	label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_content.add_child(label)

func _layout() -> void:
	var factor := minf(1.0, minf(size.x / 760, size.y / 520))
	_content.scale = Vector2.ONE * factor
	_content.position = (size - _content.size * factor) * 0.5
