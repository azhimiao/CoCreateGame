extends Control
class_name RulesScreen

signal closed
var card_count := 0

func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	var shade := ColorRect.new()
	shade.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	shade.color = Color("071321", 0.98)
	add_child(shade)
	var margin := MarginContainer.new()
	margin.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	for edge in ["left", "right", "top", "bottom"]:
		margin.add_theme_constant_override("margin_" + edge, 36)
	add_child(margin)
	var column := VBoxContainer.new()
	column.add_theme_constant_override("separation", 14)
	margin.add_child(column)
	var header := HBoxContainer.new()
	column.add_child(header)
	var title := _label("空间手册 / 游戏规则", 28, Color("edfaff"))
	title.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	header.add_child(title)
	var back := Button.new()
	back.text = "返回暂停菜单 · Esc"
	back.custom_minimum_size = Vector2(200, 44)
	back.focus_mode = Control.FOCUS_NONE
	back.pressed.connect(func() -> void: closed.emit())
	header.add_child(back)
	column.add_child(_label("匹配目标位型 → 按序点亮信标 → 抵达出口。所有机关变化都在角色移动完成后播放。", 15, Color("8de2cf")))
	var scroll := ScrollContainer.new()
	scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	column.add_child(scroll)
	var body := VBoxContainer.new()
	body.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	body.add_theme_constant_override("separation", 16)
	scroll.add_child(body)
	var controls := _label("方向键 / WASD：沿斜向格子跳跃    X / 空格：升降    Z / 退格：撤销\nR：重开    H：提示    Enter：暂停 / 恢复    点击缩略图：交换两层视图（不移动角色）", 15, Color("c4d7e6"))
	body.add_child(controls)
	body.add_child(_label("三星 · 三个条件各计一星", 21, Color("f1d28b")))
	body.add_child(_label("★ 完成通关    ★ 在本关时间目标内通关    ★ 在最佳步数内通关\n三个条件独立判断；提示不直接扣星。暂停、规则、生成与角色入场不计时；撤销不倒退计时。", 15, Color("c4d7e6")))
	var grid := GridContainer.new()
	grid.columns = 2
	grid.add_theme_constant_override("h_separation", 16)
	grid.add_theme_constant_override("v_separation", 14)
	body.add_child(grid)
	for entry in [
		["switch", "翻位格 · 未匹配", "落地后翻转标注的共享位，圆、菱形、三角分别表示三个共享通道；0 ↔ 1。两层使用同一组位。琥珀色表示相关位还未匹配目标。", false],
		["switch", "翻位格 · 目标已匹配", "相关位符合目标时，格面与电路渐变为薄荷绿，中央圆形区域淡入勾号。再次翻位失配时，颜色与勾号平滑退回。", true],
		["delayed", "延迟格 · 下一步结算", "带小钟的翻位格只把对应图案的位加入待生效队列；完成下一次有效跳跃或传送后才翻转。左侧面板显示待生效位。", false],
		["lift", "升降台 · 双层同坐标", "站在双环格上按 X / 空格，通过传送门切到另一层同坐标。主图和缩略图交换后，角色才从高处落下。", false],
		["beacon", "悬浮信标 · 按圆点顺序点亮", "菱形标志位于格子上方，圆点数量表示顺序。角色落地后点亮；提前进入后一个信标会失败。", false],
		["beacon", "已点亮信标", "菱形保留顺序圆点，中央圆形区域淡入勾号。复合格圆环左侧为翻位，右侧为信标。错误操作导致本局失败后，信标渐暗，再选择重新开始或选关。", true],
		["gate", "位门 · 先满足门上条件", "门上的图案对应目标卡中的位；实心要求点亮，空心要求熄灭。门打开会收起光栅；无效操作不扣步数。", false],
		["key", "棱镜钥匙 · 自动开锁", "进入钥匙所在格后拾取，存入底部道具栏。进入对应钥匙门时自动消耗并永久打开该门。", false],
		["anchor", "相位锚片 · 一次逆流机会", "拾取后获得一片锚片；逆着折流方向离开时自动消耗。撤销会恢复位置、道具和机关状态。", false],
		["flow", "折流格 · 沿箭头离开", "默认只能沿箭头方向离开，有锚片才能逆流离开。切层不受风向限制。箭头方向与等距棋盘一致。", false],
		["platform", "双轨平台 · 落地后移动", "每次有效动作完成后，两条轨道各平滑移动一格。角色站在平台上会一起平移，到边缘后分段绕回另一侧。", false],
		["goal", "出口 · 检查全部通关条件", "抵达绿色出口时，需同时匹配目标位型并完成所有信标。通关后庆祝，再选择下一关、重玩或回到选关。", true],
		["void", "空格 · 没有支撑", "深色空框不能进入。更亮的格子是当前可达位置；升降与跳跃亮度有区别，鼠标仅在可达位置显示蓝色反馈。", false]
	]:
		_add_card(grid, entry)

func _add_card(grid: GridContainer, entry: Array) -> void:
	var panel := PanelContainer.new()
	panel.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	panel.custom_minimum_size = Vector2(450, 162)
	var style := StyleBoxFlat.new()
	style.bg_color = Color("122635")
	style.border_color = Color("2d4c5d")
	style.set_border_width_all(1)
	style.set_corner_radius_all(10)
	style.content_margin_right = 16
	style.content_margin_top = 10
	style.content_margin_bottom = 10
	panel.add_theme_stylebox_override("panel", style)
	grid.add_child(panel)
	var row := HBoxContainer.new()
	panel.add_child(row)
	var sample := RuleTile.new()
	sample.kind = entry[0]
	sample.fulfilled = entry[3]
	row.add_child(sample)
	var text_column := VBoxContainer.new()
	text_column.alignment = BoxContainer.ALIGNMENT_CENTER
	text_column.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	text_column.add_theme_constant_override("separation", 8)
	row.add_child(text_column)
	text_column.add_child(_label(entry[1], 17, Color("b5f1df")))
	var explanation := _label(entry[2], 14, Color("b8cbd9"))
	explanation.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	text_column.add_child(explanation)
	card_count += 1

func _label(value: String, font_size: int, color: Color) -> Label:
	var label := Label.new()
	label.text = value
	label.add_theme_font_size_override("font_size", font_size)
	label.add_theme_color_override("font_color", color)
	return label
