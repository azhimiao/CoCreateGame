extends Control
class_name FrontendScreen

signal play_requested
signal level_selected(index: int)
signal reset_requested

const INK := Color("eaf5ff")
const MUTED := Color("869db5")
const CYAN := Color("80f1dc")
const LILAC := Color("b8a5f7")
const PLANNED_LEVELS := 66
const DESIGN_SIZE := Vector2(1360, 860)

var page := "home"
var has_history := false
var unlocked := 0
var stars: Array[int] = [0, 0, 0, 0]
var next_level := 0
var backdrop: MenuBackdrop
var content: Control
var primary_button: Button
var select_button: Button
var level_grid: GridContainer
var level_scroll: ScrollContainer
var level_cards: Array[Button] = []
var reset_overlay: Control
var reset_confirm: Button
var reset_cancel: Button
var _page_tween: Tween

func _ready() -> void:
	stars.resize(LevelCatalog.LEVELS.size())
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	backdrop = MenuBackdrop.new()
	add_child(backdrop)
	resized.connect(_layout)
	show_page(page, false)

func show_page(destination: String, animate := true) -> void:
	if _page_tween != null:
		_page_tween.kill()
	if is_instance_valid(content):
		remove_child(content)
		content.queue_free()
	page = destination
	backdrop.page = destination
	primary_button = null
	select_button = null
	level_grid = null
	level_scroll = null
	reset_overlay = null
	level_cards.clear()
	content = Control.new()
	content.mouse_filter = Control.MOUSE_FILTER_IGNORE
	content.size = DESIGN_SIZE
	add_child(content)
	_label_at("LR  /  双层空间", Vector2(58, 32), 12, MUTED)
	_label_at("LOGIC IN ORBIT     /     LAYER RELAY", Vector2(1006, 34), 10, MUTED)
	match destination:
		"levels": _build_levels()
		"settings": _build_settings()
		"about": _build_about()
		_: _build_home()
	_layout()
	if animate:
		content.modulate.a = 0.0
		_page_tween = create_tween()
		_page_tween.tween_property(content, "modulate:a", 1.0, 0.24)

func _layout() -> void:
	if not is_instance_valid(content):
		return
	var factor := minf(size.x / DESIGN_SIZE.x, size.y / DESIGN_SIZE.y)
	content.scale = Vector2.ONE * factor
	content.position = (size - DESIGN_SIZE * factor) * 0.5

func _build_home() -> void:
	_label_at("01  —  连接另一个维度", Vector2(300, 146), 13, CYAN)
	_label_at("LAYER RELAY", Vector2(286, 176), 70, INK)
	_label_at("折 光 机 关", Vector2(306, 266), 25, INK)
	_label_at("翻转光位，穿过层间，找到你的下一步。", Vector2(309, 316), 15, MUTED)
	var progress_text := "首次连接  /  从第一束光开始"
	if has_history:
		var completed := 0
		for value in stars:
			if value > 0:
				completed += 1
		progress_text = "已点亮 %02d / %02d  ·  下一站 %02d" % [completed, LevelCatalog.available_count(), next_level + 1] if next_level >= 0 else "当前空间已全部点亮  ·  更多旅程正在构建"
	_label_at(progress_text, Vector2(333, 370), 12, CYAN)
	primary_button = _button_at("从新关卡开始" if has_history else "开始游戏", Rect2(326, 404, 410, 66), true)
	primary_button.rotation = deg_to_rad(-1.2)
	primary_button.disabled = next_level < 0
	if next_level < 0:
		primary_button.tooltip_text = "当前开放关卡已全部通关，可从选择关卡重玩。"
	primary_button.pressed.connect(func() -> void: play_requested.emit())
	_button_code(primary_button, "01   ↗", Color("173d43"))
	select_button = _button_at("选择关卡", Rect2(345, 493, 410, 66))
	select_button.rotation = deg_to_rad(0.7)
	select_button.pressed.connect(show_page.bind("levels"))
	_button_code(select_button, "02   ≡", MUTED)
	_label_at("跨越层间的微小冒险", Vector2(980, 503), 14, Color("93b4c8"))
	_label_at("HOP  /  FLIP  /  RELAY", Vector2(980, 530), 10, Color("607d98"))
	var about := _round_button("about", "关于我们", Vector2(94, 718))
	about.pressed.connect(show_page.bind("about"))
	var settings := _round_button("settings", "设置", Vector2(1190, 709))
	settings.pressed.connect(show_page.bind("settings"))
	_label_at("一束光，两重空间。", Vector2(574, 790), 11, MUTED)

func _round_button(glyph: String, title: String, point: Vector2) -> GlyphButton:
	var button := GlyphButton.new()
	button.glyph = glyph
	button.tooltip_text = title
	button.position = point
	button.size = Vector2(66, 66)
	content.add_child(button)
	var caption := _label_at(title, point + Vector2(-13, 73), 12, MUTED)
	caption.size.x = 92
	caption.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	return button

func _build_levels() -> void:
	_label_at("02  /  空间坐标", Vector2(177, 107), 12, CYAN)
	_label_at("选择关卡", Vector2(173, 135), 38, INK)
	_label_at("让每一个落点，成为通往下一层的线索。", Vector2(177, 194), 14, MUTED)
	var back := _button_at("←  返回主页", Rect2(1003, 138, 178, 44), false, true)
	back.pressed.connect(show_page.bind("home"))
	var plate := Panel.new()
	plate.position = Vector2(163, 241)
	plate.size = Vector2(1034, 464)
	plate.mouse_filter = Control.MOUSE_FILTER_IGNORE
	plate.add_theme_stylebox_override("panel", _style(Color("0c1728", 0.88), Color("324b64", 0.6), 14))
	content.add_child(plate)
	level_scroll = ScrollContainer.new()
	level_scroll.position = Vector2(184, 260)
	level_scroll.size = Vector2(994, 426)
	level_scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	level_scroll.vertical_scroll_mode = ScrollContainer.SCROLL_MODE_AUTO
	level_scroll.follow_focus = true
	level_scroll.add_theme_stylebox_override("panel", StyleBoxEmpty.new())
	content.add_child(level_scroll)
	var grid_margin := MarginContainer.new()
	grid_margin.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	grid_margin.add_theme_constant_override("margin_right", 14)
	grid_margin.add_theme_constant_override("margin_bottom", 8)
	level_scroll.add_child(grid_margin)
	level_grid = GridContainer.new()
	level_grid.columns = 6
	level_grid.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	level_grid.add_theme_constant_override("h_separation", 13)
	level_grid.add_theme_constant_override("v_separation", 14)
	grid_margin.add_child(level_grid)
	for index in range(PLANNED_LEVELS):
		var card := _level_card(index)
		level_grid.add_child(card)
		level_cards.append(card)
	var available := LevelCatalog.available_count()
	_label_at("当前开放 %02d 关  ·  共 %02d 个空间坐标" % [available, PLANNED_LEVELS], Vector2(179, 725), 12, MUTED)
	_label_at("滚轮或拖动滚动条上下浏览  ·  通关后依次解锁", Vector2(179, 751), 11, Color("607d98"))
	var reset := _button_at("重置关卡", Rect2(1013, 720, 166, 45), false, true)
	reset.add_theme_color_override("font_color", Color("edb5bc"))
	reset.pressed.connect(open_reset_confirmation)

func _level_card(index: int) -> Button:
	var actual := LevelCatalog.is_available(index)
	var challenge := actual and bool(LevelCatalog.LEVELS[index].get("challenge", false))
	var open := actual and (index <= unlocked)
	var completed := actual and stars[index] > 0
	var color := CYAN if open else Color("58718e")
	var card := Button.new()
	card.custom_minimum_size = Vector2(148, 122)
	card.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	card.disabled = not open
	card.tooltip_text = LevelCatalog.LEVELS[index].subtitle if open else ("通关前一关后解锁" if actual else "规划中的关卡，暂未开放")
	card.add_theme_stylebox_override("normal", _style(Color("18363d", 0.94) if completed else Color("14263a", 0.94), Color("5a9d98") if completed else Color("36506a"), 7))
	card.add_theme_stylebox_override("hover", _style(Color("234857"), CYAN, 7))
	card.add_theme_stylebox_override("pressed", _style(Color("2d5860"), CYAN, 7))
	card.add_theme_stylebox_override("focus", _focus_style())
	card.add_theme_stylebox_override("disabled", _style(Color("0e1c2d", 0.86), Color("24394e"), 7))
	card.pressed.connect(func() -> void: level_selected.emit(index))
	var number := _label("%02d" % (index + 1), 31, INK if open else Color("58718b"))
	number.position = Vector2(14, 10)
	card.add_child(number)
	var marker := _label("↗" if open else "·", 18, color)
	marker.set_anchors_and_offsets_preset(Control.PRESET_TOP_RIGHT)
	marker.position = Vector2(-32, 14)
	card.add_child(marker)
	var name_label := _label(String(LevelCatalog.LEVELS[index].name) if actual else "未开放", 13, INK if open else Color("58718b"))
	name_label.position = Vector2(15, 62)
	card.add_child(name_label)
	var detail := "待解锁" if actual else "建设中"
	if open:
		detail = "★".repeat(stars[index]) + "☆".repeat(3 - stars[index]) if completed else "首次探索"
		if challenge:
			detail = "挑战 · " + ("★".repeat(stars[index]) if completed else "首次探索")
	var record := _label(detail, 12, CYAN if completed else color)
	record.position = Vector2(15, 90)
	card.add_child(record)
	return card

func _build_settings() -> void:
	_label_at("03  /  系统空间", Vector2(429, 260), 12, CYAN)
	_label_at("设置", Vector2(422, 296), 48, INK)
	_label_at("正在开发中……", Vector2(438, 374), 23, MUTED)
	var back := _button_at("←  返回", Rect2(439, 454, 400, 64))
	back.rotation = deg_to_rad(-1)
	back.pressed.connect(show_page.bind("home"))

func _build_about() -> void:
	_label_at("04  /  关于这段旅程", Vector2(386, 210), 12, LILAC)
	_label_at("关于我们", Vector2(379, 245), 44, INK)
	_label_at("我们在搭建一个关于光、机关与空间的小世界。", Vector2(388, 333), 18, INK)
	_label_at("Layer Relay · 折光机关\n在两层棋盘间传递光位，用每一次跳跃解开回路。\n\n50 关双层旅程，最后十关为高难挑战。\n谢谢你参与这场探索。", Vector2(389, 382), 16, MUTED)
	var back := _button_at("←  返回", Rect2(402, 565, 376, 60))
	back.rotation = deg_to_rad(-1.2)
	back.pressed.connect(show_page.bind("home"))

func open_reset_confirmation() -> void:
	if is_instance_valid(reset_overlay):
		return
	reset_overlay = Control.new()
	reset_overlay.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	content.add_child(reset_overlay)
	var shade := ColorRect.new()
	shade.color = Color("030713", 0.86)
	shade.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	reset_overlay.add_child(shade)
	var panel := Panel.new()
	panel.position = Vector2(420, 270)
	panel.size = Vector2(520, 322)
	panel.add_theme_stylebox_override("panel", _style(Color("142236"), Color("7180a6"), 12))
	reset_overlay.add_child(panel)
	var tag := _label("RESET  /  重新连接", 12, LILAC)
	tag.position = Vector2(32, 25)
	panel.add_child(tag)
	var title := _label("确认重置", 30, INK)
	title.position = Vector2(31, 59)
	panel.add_child(title)
	var body := _label("将清空所有关卡的星级、解锁进度及当前局面。\n重置后，将从第 1 关重新开始。", 15, MUTED)
	body.position = Vector2(33, 122)
	panel.add_child(body)
	reset_cancel = _button("取消")
	reset_cancel.position = Vector2(32, 228)
	reset_cancel.size = Vector2(215, 56)
	panel.add_child(reset_cancel)
	reset_cancel.pressed.connect(close_reset_confirmation)
	reset_confirm = _button("确认重置", true)
	reset_confirm.position = Vector2(263, 228)
	reset_confirm.size = Vector2(225, 56)
	panel.add_child(reset_confirm)
	reset_confirm.pressed.connect(func() -> void: reset_requested.emit())
	reset_cancel.focus_next = reset_cancel.get_path_to(reset_confirm)
	reset_cancel.focus_previous = reset_cancel.get_path_to(reset_confirm)
	reset_confirm.focus_next = reset_confirm.get_path_to(reset_cancel)
	reset_confirm.focus_previous = reset_confirm.get_path_to(reset_cancel)
	for direction in ["focus_neighbor_left", "focus_neighbor_right", "focus_neighbor_top", "focus_neighbor_bottom"]:
		reset_cancel.set(direction, reset_cancel.get_path_to(reset_confirm))
		reset_confirm.set(direction, reset_confirm.get_path_to(reset_cancel))
	reset_cancel.grab_focus()

func close_reset_confirmation() -> void:
	if is_instance_valid(reset_overlay):
		content.remove_child(reset_overlay)
		reset_overlay.queue_free()
	reset_overlay = null
	reset_confirm = null
	reset_cancel = null

func go_back() -> void:
	if is_instance_valid(reset_overlay):
		close_reset_confirmation()
	elif page != "home":
		show_page("home")

func _button_at(text_value: String, rect: Rect2, primary := false, small := false) -> Button:
	var button := _button(text_value, primary, small)
	button.position = rect.position
	button.size = rect.size
	content.add_child(button)
	return button

func _button(text_value: String, primary := false, small := false) -> Button:
	var button := Button.new()
	button.text = text_value
	button.alignment = HORIZONTAL_ALIGNMENT_LEFT
	button.add_theme_font_size_override("font_size", 16 if small else 22)
	button.add_theme_color_override("font_color", Color("102c38") if primary else INK)
	button.add_theme_color_override("font_hover_color", Color("102c38") if primary else Color.WHITE)
	button.add_theme_color_override("font_pressed_color", Color("102c38") if primary else CYAN)
	button.add_theme_color_override("font_disabled_color", Color("536a80"))
	button.add_theme_stylebox_override("normal", _style(CYAN if primary else Color("15263c", 0.93), CYAN if primary else Color("476079"), 3))
	button.add_theme_stylebox_override("hover", _style(Color("b2ffee") if primary else Color("254359"), Color("b2ffee") if primary else CYAN, 3))
	button.add_theme_stylebox_override("pressed", _style(Color("5ed1be") if primary else Color("1e384b"), CYAN, 3))
	button.add_theme_stylebox_override("disabled", _style(Color("101d2e", 0.85), Color("293c52"), 3))
	button.add_theme_stylebox_override("focus", _focus_style())
	button.mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
	return button

func _button_code(button: Button, value: String, color: Color) -> void:
	var code := _label(value, 12, color)
	code.set_anchors_and_offsets_preset(Control.PRESET_CENTER_RIGHT)
	code.grow_horizontal = Control.GROW_DIRECTION_BEGIN
	code.offset_left = -112
	code.offset_right = -20
	code.offset_top = -10
	code.offset_bottom = 10
	code.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	button.add_child(code)

func _label_at(value: String, point: Vector2, font_size: int, color: Color) -> Label:
	var label := _label(value, font_size, color)
	label.position = point
	content.add_child(label)
	return label

func _label(value: String, font_size: int, color: Color) -> Label:
	var label := Label.new()
	label.text = value
	label.add_theme_font_size_override("font_size", font_size)
	label.add_theme_color_override("font_color", color)
	label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return label

func _style(fill: Color, edge: Color, radius: int) -> StyleBoxFlat:
	var style := StyleBoxFlat.new()
	style.bg_color = fill
	style.border_color = edge
	style.set_border_width_all(1)
	style.set_corner_radius_all(radius)
	style.content_margin_left = 22
	style.content_margin_right = 22
	style.content_margin_top = 9
	style.content_margin_bottom = 9
	return style

func _focus_style() -> StyleBoxFlat:
	var style := _style(Color.TRANSPARENT, Color("e4e7ff"), 4)
	style.set_border_width_all(2)
	return style
