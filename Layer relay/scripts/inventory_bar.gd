extends PanelContainer
class_name InventoryBar

const VISIBLE_SLOTS := 5
var items: Array[Dictionary] = []
var page_start := 0
var slots: Array[PanelContainer] = []
var _icons: Array[Label] = []
var _names: Array[Label] = []
var _counts: Array[Label] = []
var _previous: Button
var _next: Button
var _page_label: Label

func _ready() -> void:
	custom_minimum_size = Vector2(460, 96)
	var style := _style(Color("14272e", 0.86), Color("597d80", 0.65))
	style.content_margin_left = 10
	style.content_margin_right = 10
	style.content_margin_top = 6
	style.content_margin_bottom = 8
	add_theme_stylebox_override("panel", style)
	var layout := VBoxContainer.new()
	layout.add_theme_constant_override("separation", 4)
	add_child(layout)
	var heading := HBoxContainer.new()
	layout.add_child(heading)
	var title := _label("随身道具", 11, Color("d4e4df"))
	title.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	heading.add_child(title)
	_page_label = _label("", 10, Color("9ab3b6"))
	heading.add_child(_page_label)
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 6)
	layout.add_child(row)
	_previous = _page_button("‹", -1)
	row.add_child(_previous)
	for i in range(VISIBLE_SLOTS):
		var slot := PanelContainer.new()
		slot.name = "Slot%d" % (i + 1)
		slot.custom_minimum_size = Vector2(66, 62)
		slot.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		slot.add_theme_stylebox_override("panel", _style(Color("21363e", 0.88), Color("47636b", 0.55)))
		row.add_child(slot)
		slots.append(slot)
		var content := VBoxContainer.new()
		content.add_theme_constant_override("separation", 0)
		slot.add_child(content)
		var icon := _label("·", 20, Color("6a858b"))
		var item_name := _label("空槽", 10, Color("728d93"))
		var count := _label("", 10, Color("f1c86b"))
		for label in [icon, item_name, count]:
			label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
			label.mouse_filter = Control.MOUSE_FILTER_IGNORE
			content.add_child(label)
		item_name.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS
		_icons.append(icon)
		_names.append(item_name)
		_counts.append(count)
	_next = _page_button("›", 1)
	row.add_child(_next)
	_refresh_slots()

func set_items(entries: Array[Dictionary]) -> void:
	items = entries.duplicate(true)
	var last_page := maxi(0, ceili(float(items.size()) / VISIBLE_SLOTS) - 1) * VISIBLE_SLOTS
	page_start = clampi(page_start, 0, last_page)
	if is_node_ready():
		_refresh_slots()

func change_page(direction: int) -> void:
	var last_page := maxi(0, ceili(float(items.size()) / VISIBLE_SLOTS) - 1) * VISIBLE_SLOTS
	page_start = clampi(page_start + direction * VISIBLE_SLOTS, 0, last_page)
	_refresh_slots()

func _refresh_slots() -> void:
	if _previous == null:
		return
	_previous.disabled = page_start == 0
	_next.disabled = page_start + VISIBLE_SLOTS >= items.size()
	_page_label.text = "%d 件 · %d / %d" % [items.size(), page_start / VISIBLE_SLOTS + 1, maxi(1, ceili(float(items.size()) / VISIBLE_SLOTS))]
	for i in range(VISIBLE_SLOTS):
		var index := page_start + i
		var present := index < items.size()
		var item: Dictionary = items[index] if present else {}
		_icons[i].text = String(item.get("icon", "·"))
		_icons[i].add_theme_color_override("font_color", Color("8ce4d7") if present else Color("6a858b"))
		_names[i].text = String(item.get("name", "空槽"))
		_names[i].add_theme_color_override("font_color", Color("edf3ee") if present else Color("728d93"))
		_counts[i].text = "×%d" % int(item.get("count", 1)) if present else ""
		slots[i].tooltip_text = String(item.get("description", item.get("name", "尚未持有道具")))
		slots[i].set_meta("item_id", String(item.get("id", "")))

func _page_button(text: String, direction: int) -> Button:
	var button := Button.new()
	button.text = text
	button.custom_minimum_size = Vector2(26, 62)
	button.focus_mode = Control.FOCUS_NONE
	button.add_theme_font_size_override("font_size", 23)
	button.add_theme_stylebox_override("normal", _style(Color("223b43", 0.9), Color("47636b", 0.6)))
	button.add_theme_stylebox_override("hover", _style(Color("35545c"), Color("62d6c3")))
	button.tooltip_text = "上一页道具" if direction < 0 else "下一页道具"
	button.pressed.connect(change_page.bind(direction))
	return button

func _label(text: String, font_size: int, color: Color) -> Label:
	var label := Label.new()
	label.text = text
	label.add_theme_font_size_override("font_size", font_size)
	label.add_theme_color_override("font_color", color)
	return label

func _style(fill: Color, border: Color) -> StyleBoxFlat:
	var style := StyleBoxFlat.new()
	style.bg_color = fill
	style.border_color = border
	style.set_border_width_all(1)
	style.set_corner_radius_all(6)
	return style
