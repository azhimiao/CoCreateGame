extends Control
class_name PauseScreen

signal resume_requested
signal home_requested
signal levels_requested
signal rules_requested

var resume_rect := Rect2()
var resume_button: GlyphButton
var _content: VBoxContainer
var _key_label: Label

func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	var shade := ColorRect.new()
	shade.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	shade.color = Color("050d19", 0.85)
	add_child(shade)
	resume_button = GlyphButton.new()
	resume_button.name = "ResumeButton"
	resume_button.glyph = "resume"
	resume_button.position = resume_rect.position
	resume_button.size = resume_rect.size
	resume_button.focus_mode = Control.FOCUS_NONE
	resume_button.tooltip_text = "恢复游戏 · Enter"
	resume_button.pressed.connect(func() -> void: resume_requested.emit())
	add_child(resume_button)
	var key := _label("Enter", 11, Color("aec5ce"))
	_key_label = key
	key.position = resume_rect.position + Vector2(0, resume_rect.size.y + 4)
	key.size.x = resume_rect.size.x
	add_child(key)
	_content = VBoxContainer.new()
	_content.add_theme_constant_override("separation", 18)
	_content.custom_minimum_size = Vector2(600, 240)
	_content.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_content)
	_content.add_child(_label("空 间 已 暂 停", 30, Color("edfff9")))
	_content.add_child(_label("计时与机关动画已冻结 · 点击右上角或按 Enter 继续", 14, Color("9db8c6")))
	var row := HBoxContainer.new()
	row.alignment = BoxContainer.ALIGNMENT_CENTER
	row.add_theme_constant_override("separation", 60)
	_content.add_child(row)
	for entry in [["home", "主页", home_requested], ["levels", "选择关卡", levels_requested], ["rules", "游戏规则", rules_requested]]:
		var column := VBoxContainer.new()
		column.alignment = BoxContainer.ALIGNMENT_CENTER
		row.add_child(column)
		var icon := GlyphButton.new()
		icon.glyph = entry[0]
		icon.custom_minimum_size = Vector2(76, 76)
		icon.focus_mode = Control.FOCUS_NONE
		icon.pressed.connect(func() -> void: entry[2].emit())
		column.add_child(icon)
		column.add_child(_label(entry[1], 15, Color("c5d9e6")))
	resized.connect(_layout)
	_layout()

func _layout() -> void:
	_content.position = (size - _content.size) * 0.5
	resume_button.position = Vector2(size.x - 82, 24)
	_key_label.position = resume_button.position + Vector2(0, resume_button.size.y + 4)

func _label(value: String, font_size: int, color: Color) -> Label:
	var label := Label.new()
	label.text = value
	label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	label.add_theme_font_size_override("font_size", font_size)
	label.add_theme_color_override("font_color", color)
	return label
