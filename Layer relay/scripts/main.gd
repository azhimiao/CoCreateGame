extends Control

const BG := Color("10191f")
const SURFACE := Color("18262d")
const SURFACE_ALT := Color("203139")
const TEXT := Color("edf3ee")
const MUTED := Color("9eafb1")
const TEAL := Color("62d6c3")
const CORAL := Color("ff8979")
const GOLD := Color("f1c86b")
const BLUE := Color("76aee8")
const EMPTY := Color("263940")
const TUTORIAL_VERSION := 3

var level_index := 0
var level: Dictionary
var state: Dictionary
var history: Array[Dictionary] = []
var unlocked := 0
var best_stars: Array[int] = []
var selected_layer := 0
var tutorial_coach: TutorialCoach
var tutorials_enabled := true
var tutorial_seen: Array[String] = []
var tutorial_batches: Array[Dictionary] = []
var tutorial_batch_index := 0
var tutorial_step_index := 0
var toolbar_panel: Control
var controls_panel: Control
var hint_action := ""
var _hint_task := -1
var _hint_request: HintSearch.Request
var _hint_snapshot := ""
var notice_text := ""
var notice_color := MUTED
var screen_root: VBoxContainer
var header_title: Label
var header_subtitle: Label
var bit_line: Label
var pending_line: Label
var beacon_line: Label
var inventory_bar: InventoryBar
var objective_panel: PanelContainer
var iso_controls: IsoControls
var phase_line: Label
var rules_screen: RulesScreen
var pause_screen: PauseScreen
var paused := false
var pause_button: GlyphButton
var elapsed_seconds := 0.0
var timer_label: Label
var completion_awards: Dictionary = {}
var _queued_notice := ""
var _queued_notice_color := MUTED
var board_view: BoardView
var move_counter: Label
var feedback_label: Label
var toast_panel: PanelContainer
var _notice_tween: Tween
var completion_screen: CompletionScreen
var completion_stage := ""
var completion_stars := 0
var failure_stage := ""
var failure_screen: FailureScreen
var current_screen := "home"
var menu_screen: FrontendScreen
var has_play_history := false
var last_played := 0
var saved_run: Dictionary = {}
var saved_history: Array[Dictionary] = []
var progress_path := "user://layer_relay.cfg"

func _ready() -> void:
	custom_minimum_size = Vector2(1080, 720)
	_load_progress()
	level = LevelCatalog.get_level(level_index)
	state = GameRules.create_state(level)
	_show_menu("home")

func _process(delta: float) -> void:
	_poll_hint()
	if current_screen != "game" or paused or board_view == null or board_view.is_revealing():
		return
	if tutorial_coach != null:
		tutorial_coach.set_target(_tutorial_target(_current_tutorial_step()))
		return
	if _tutorial_pending():
		if not board_view.is_animating():
			_show_tutorial_step()
		return
	if state.status == "playing" or completion_stage == "waiting":
		elapsed_seconds += delta
		_refresh_clock()

func _refresh_clock() -> void:
	if timer_label != null and is_instance_valid(timer_label):
		timer_label.text = "用时 %s / %s" % [ScoreRules.clock_text(elapsed_seconds), ScoreRules.clock_text(float(level.time_limit))]
		timer_label.add_theme_color_override("font_color", GOLD if elapsed_seconds <= float(level.time_limit) else CORAL)

func _input(event: InputEvent) -> void:
	if current_screen != "game" or not event is InputEventKey or not event.pressed or event.echo:
		return
	if _tutorial_pending():
		if event.keycode not in [KEY_TAB, KEY_ENTER, KEY_KP_ENTER] or tutorial_coach == null:
			get_viewport().set_input_as_handled()
		return
	if failure_stage != "":
		if failure_stage == "choices":
			if event.keycode in [KEY_R, KEY_ENTER, KEY_KP_ENTER]:
				_select_level(level_index)
			elif event.keycode == KEY_ESCAPE:
				_show_menu("levels")
			else:
				return
		get_viewport().set_input_as_handled()
		return
	if event.keycode in [KEY_ENTER, KEY_KP_ENTER]:
		if rules_screen == null and completion_stage not in ["celebrating", "choices"]:
			_toggle_pause()
		get_viewport().set_input_as_handled()
	elif event.keycode == KEY_ESCAPE and paused:
		if rules_screen != null:
			_close_rules()
		else:
			_toggle_pause()
		get_viewport().set_input_as_handled()

func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo:
		var key := event as InputEventKey
		if current_screen != "game":
			if key.keycode == KEY_ESCAPE and menu_screen != null:
				menu_screen.go_back()
			return
		if paused or _tutorial_pending():
			return
		if completion_stage != "":
			if key.keycode == KEY_ESCAPE:
				_show_menu("levels")
			return
		match key.keycode:
			KEY_UP, KEY_W: _act("U")
			KEY_RIGHT, KEY_D: _act("R")
			KEY_DOWN, KEY_S: _act("D")
			KEY_LEFT, KEY_A: _act("L")
			KEY_X, KEY_SPACE: _act("X")
			KEY_Z, KEY_BACKSPACE: _undo()
			KEY_R: _restart()
			KEY_H: _hint()
			KEY_ESCAPE: _toggle_pause()

func _clear_ui() -> void:
	if _notice_tween != null:
		_notice_tween.kill()
	_notice_tween = null
	for child in get_children():
		remove_child(child)
		child.queue_free()
	completion_screen = null
	completion_stage = ""
	failure_stage = ""
	failure_screen = null
	board_view = null
	screen_root = null
	menu_screen = null
	toast_panel = null
	feedback_label = null
	rules_screen = null
	pause_screen = null
	paused = false
	pause_button = null
	timer_label = null
	tutorial_coach = null
	tutorial_batches.clear()
	tutorial_batch_index = 0
	tutorial_step_index = 0
	_queued_notice = ""

func _show_menu(destination := "home") -> void:
	_clear_ui()
	current_screen = "menu"
	menu_screen = FrontendScreen.new()
	menu_screen.page = destination
	menu_screen.has_history = has_play_history
	menu_screen.unlocked = unlocked
	menu_screen.stars = best_stars.duplicate()
	menu_screen.next_level = _next_level()
	menu_screen.play_requested.connect(_start_from_menu)
	menu_screen.level_selected.connect(_select_level)
	menu_screen.reset_requested.connect(_reset_progress)
	add_child(menu_screen)

func _next_level() -> int:
	for index in range(LevelCatalog.LEVELS.size()):
		if LevelCatalog.is_available(index) and best_stars[index] == 0 and index <= unlocked:
			return index
	return -1

func _start_from_menu() -> void:
	_select_level(_next_level())

func _build_ui() -> void:
	_clear_ui()
	current_screen = "game"

	var background := ColorRect.new()
	background.color = BG
	background.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(background)
	background.mouse_filter = Control.MOUSE_FILTER_IGNORE

	var margin := MarginContainer.new()
	margin.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	margin.add_theme_constant_override("margin_left", 34)
	margin.add_theme_constant_override("margin_right", 34)
	margin.add_theme_constant_override("margin_top", 24)
	margin.add_theme_constant_override("margin_bottom", 22)
	add_child(margin)
	var page := VBoxContainer.new()
	page.add_theme_constant_override("separation", 18)
	margin.add_child(page)
	screen_root = page

	var top := HBoxContainer.new()
	top.add_theme_constant_override("separation", 20)
	page.add_child(top)
	var brand := VBoxContainer.new()
	brand.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	top.add_child(brand)
	header_title = _label("Layer Relay", 30, TEXT)
	brand.add_child(header_title)
	header_subtitle = _label("在双层机关之间传递光位，规划每一步的状态。", 14, MUTED)
	brand.add_child(header_subtitle)
	var navigation := HBoxContainer.new()
	toolbar_panel = navigation
	navigation.add_theme_constant_override("separation", 10)
	top.add_child(navigation)
	for entry in [["replay", "重开", "R", _restart], ["hint", "提示", "H", _hint], ["pause", "暂停", "Enter", _toggle_pause]]:
		var column := VBoxContainer.new()
		column.add_theme_constant_override("separation", 3)
		navigation.add_child(column)
		var button := GlyphButton.new()
		button.glyph = entry[0]
		button.tooltip_text = entry[1] + " · " + entry[2]
		button.name = String(entry[0]).capitalize() + "Button"
		button.custom_minimum_size = Vector2(48, 48)
		button.focus_mode = Control.FOCUS_NONE
		button.pressed.connect(entry[3])
		column.add_child(button)
		var key_label := _label(entry[2], 11, MUTED)
		key_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		column.add_child(key_label)
		if entry[0] == "pause":
			pause_button = button

	var divider := HSeparator.new()
	divider.add_theme_color_override("separator", Color("34464c"))
	page.add_child(divider)

	var work_area := HBoxContainer.new()
	work_area.add_theme_constant_override("separation", 18)
	work_area.size_flags_vertical = Control.SIZE_EXPAND_FILL
	page.add_child(work_area)
	board_view = BoardView.new()
	board_view.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	board_view.size_flags_vertical = Control.SIZE_EXPAND_FILL
	board_view.custom_minimum_size = Vector2(680, 520)
	board_view.cell_pressed.connect(_on_board_cell_pressed)
	board_view.preview_pressed.connect(_on_preview_pressed)
	board_view.layer_changed.connect(_on_board_layer_changed)
	board_view.animation_finished.connect(_on_board_animation_finished)
	board_view.completion_finished.connect(_on_completion_finished)
	board_view.failure_finished.connect(_on_failure_finished)
	board_view.environment_changed.connect(_refresh)
	work_area.add_child(board_view)

	var sidebar := VBoxContainer.new()
	sidebar.custom_minimum_size = Vector2(258, 0)
	sidebar.add_theme_constant_override("separation", 12)
	work_area.add_child(sidebar)
	objective_panel = _panel()
	objective_panel.name = "ObjectivePanel"
	var objective_style := _box(Color("182c33", 0.74), Color("5e8185", 0.48), 8, 1)
	objective_style.content_margin_left = 12
	objective_style.content_margin_right = 12
	objective_style.content_margin_top = 10
	objective_style.content_margin_bottom = 10
	objective_panel.add_theme_stylebox_override("panel", objective_style)
	objective_panel.position = Vector2(20, 82)
	objective_panel.size = Vector2(224, 220)
	board_view.add_child(objective_panel)
	var objective := VBoxContainer.new()
	objective.add_theme_constant_override("separation", 7)
	objective_panel.add_child(objective)
	objective.add_child(_label("本关目标", 15, TEXT))
	objective.add_child(_label("抵达出口 · 匹配目标位型" if int(level.bit_count) > 0 else "规划路线 · 抵达出口", 11, MUTED))
	bit_line = _label("当前位型", 12, TEAL)
	objective.add_child(bit_line)
	pending_line = _label("待生效", 12, MUTED)
	objective.add_child(pending_line)
	beacon_line = _label("信标", 12, MUTED)
	objective.add_child(beacon_line)
	phase_line = _label("轨道相位", 12, BLUE)
	phase_line.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	objective.add_child(phase_line)
	objective.add_child(HSeparator.new())
	move_counter = _label("步数 0 / 0", 22, TEXT)
	move_counter.name = "MoveCounter"
	objective.add_child(move_counter)
	objective.add_child(_label("最佳步数  %d" % int(level.par), 13, GOLD))
	timer_label = _label("", 13, GOLD)
	timer_label.name = "TimerLabel"
	objective.add_child(timer_label)
	_refresh_clock()
	inventory_bar = InventoryBar.new()
	inventory_bar.name = "InventoryBar"
	inventory_bar.anchor_left = 0.5
	inventory_bar.anchor_right = 0.5
	inventory_bar.anchor_top = 1.0
	inventory_bar.anchor_bottom = 1.0
	inventory_bar.offset_left = -230
	inventory_bar.offset_right = 230
	inventory_bar.offset_top = -112
	inventory_bar.offset_bottom = -16
	board_view.add_child(inventory_bar)

	controls_panel = _panel()
	sidebar.add_child(controls_panel)
	var controls := VBoxContainer.new()
	controls.add_theme_constant_override("separation", 9)
	controls_panel.add_child(controls)
	controls.add_child(_label("等距操作", 15, TEXT))
	iso_controls = IsoControls.new()
	iso_controls.name = "IsoControls"
	iso_controls.action_pressed.connect(_act)
	controls.add_child(iso_controls)
	var actions := HBoxContainer.new()
	actions.add_theme_constant_override("separation", 5)
	controls.add_child(actions)
	for item in [["撤销 · Z", _undo]]:
		var button := _small_button(item[0])
		button.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		button.pressed.connect(item[1])
		actions.add_child(button)
	var key_help := _label("方向键移动   X 升降\nEnter 暂停 / 恢复", 11, MUTED)
	controls.add_child(key_help)

	var footer := HBoxContainer.new()
	page.add_child(footer)
	footer.add_child(_label("点击相邻地块移动 · 右上角暂停菜单内查看图文规则", 11, MUTED))

	toast_panel = PanelContainer.new()
	toast_panel.anchor_left = 0.5
	toast_panel.anchor_right = 0.5
	toast_panel.anchor_top = 0.19
	toast_panel.anchor_bottom = 0.19
	toast_panel.offset_left = -330
	toast_panel.offset_right = 330
	toast_panel.offset_top = 0
	toast_panel.offset_bottom = 62
	toast_panel.mouse_filter = Control.MOUSE_FILTER_IGNORE
	toast_panel.add_theme_stylebox_override("panel", StyleBoxEmpty.new())
	feedback_label = _label("", 18, TEXT)
	feedback_label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	feedback_label.add_theme_color_override("font_shadow_color", Color("030b13", 0.85))
	feedback_label.add_theme_constant_override("shadow_offset_y", 2)
	feedback_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	feedback_label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	feedback_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	toast_panel.add_child(feedback_label)
	add_child(toast_panel)
	toast_panel.visible = false


func _refresh() -> void:
	if screen_root == null:
		return
	_refresh_clock()
	if board_view != null:
		board_view.set_context(level, state, selected_layer, hint_action)
	var visible_state: Dictionary = board_view.state if board_view != null else state
	header_title.text = level.name
	header_subtitle.text = level.subtitle
	move_counter.text = "步数  %d / %d" % [state.used, level.move_limit]
	bit_line.text = "当前  %s\n目标  %s" % [_bits_text(int(visible_state.bits)), _bits_text(int(level.goal_bits))]
	if int(level.bit_count) == 0:
		bit_line.text = "目标  抵达出口"
	pending_line.text = "下一步结算  %s" % _bits_text(int(visible_state.pending)) if int(visible_state.pending) != 0 else "待生效  无"
	pending_line.visible = "delayed" in level.switch_mode_by_layer
	beacon_line.text = "信标  %d / %d" % [visible_state.beacon_index, level.beacons.size()]
	beacon_line.visible = not level.beacons.is_empty()
	inventory_bar.set_items(_inventory_items(visible_state))
	phase_line.visible = not level.get("moving_rows", []).is_empty()
	if phase_line.visible:
		var tracks: Array[String] = []
		for row in level.moving_rows:
			var columns: Array[String] = []
			for start_x in row.tiles:
				var visible_phase := board_view.display_phase() if board_view != null else int(state.phase)
				columns.append(String.chr(65 + posmod(int(start_x) + int(row.direction) * visible_phase, int(level.width))))
			columns.sort()
			tracks.append("%s %s" % [String(row.name), ",".join(columns)])
		phase_line.text = "轨道相位  " + "  ·  ".join(tracks)

func _act(action: String) -> void:
	if current_screen != "game" or paused or _tutorial_pending() or state.status != "playing" or (board_view != null and board_view.is_animating()):
		return
	var before: Dictionary = state.duplicate(true)
	var result := GameRules.try_action(level, state, action)
	if not result.accepted:
		_set_notice(result.message, CORAL)
		return
	history.append(before)
	state = result.state
	hint_action = ""
	if state.status == "won":
		completion_stage = "waiting"
		_clear_notice()
	elif state.status == "failed":
		failure_stage = "waiting"
		_clear_notice()
	else:
		_queued_notice = result.message
		_queued_notice_color = TEAL if action == "X" else MUTED
	if board_view != null:
		board_view.play_action(level, before, state, action, hint_action)
	_remember_run()
	_refresh()

func _press_cell(layer: int, x: int, y: int) -> void:
	if paused or _tutorial_pending():
		return
	selected_layer = layer
	var current: Array = state.pos
	if int(current[0]) != layer:
		_refresh()
		return
	var delta := Vector2i(x - int(current[1]), y - int(current[2]))
	if delta == Vector2i.ZERO and GameRules.try_action(level, state, "X").accepted:
		_act("X")
		return
	for action in GameRules.DIRECTIONS:
		if GameRules.DIRECTIONS[action] == delta:
			_act(String(action))
			return
	_refresh()

func _on_board_cell_pressed(layer: int, x: int, y: int) -> void:
	_press_cell(layer, x, y)

func _on_preview_pressed(layer: int) -> void:
	if paused or _tutorial_pending() or board_view == null or completion_stage != "" or failure_stage != "":
		return
	board_view.animate_layer_view(layer)
	if layer != selected_layer:
		_set_notice("正在切换至%s。" % ("下层" if layer == 0 else "上层"), MUTED)

func _on_board_layer_changed(layer: int) -> void:
	selected_layer = layer
	_refresh()

func _on_board_animation_finished() -> void:
	_refresh()
	if failure_stage == "waiting" and state.status == "failed":
		failure_stage = "animating"
		board_view.start_failure()
		return
	if not _queued_notice.is_empty():
		_set_notice(_queued_notice, _queued_notice_color)
		_queued_notice = ""
	if completion_stage == "waiting" and state.status == "won":
		completion_awards = ScoreRules.evaluate(level, state, elapsed_seconds)
		completion_stars = int(completion_awards.stars)
		best_stars[level_index] = maxi(best_stars[level_index], completion_stars)
		var following := LevelCatalog.next_available(level_index)
		if level_index == unlocked and following >= 0:
			unlocked = following
			# Retain completed early levels when migrating an existing profile.
			while best_stars[unlocked] > 0:
				var next_unplayed := LevelCatalog.next_available(unlocked)
				if next_unplayed < 0:
					break
				unlocked = next_unplayed
		_save_progress()
		completion_stage = "celebrating"
		board_view.start_completion()

func _on_completion_finished() -> void:
	if current_screen != "game" or completion_stage != "celebrating":
		return
	completion_stage = "choices"
	completion_screen = CompletionScreen.new()
	completion_screen.level_name = level.name
	completion_screen.stars = completion_stars
	completion_screen.used = int(state.used)
	completion_screen.par = int(level.par)
	completion_screen.awards = completion_awards.duplicate()
	completion_screen.seconds = elapsed_seconds
	completion_screen.time_limit = float(level.time_limit)
	var following := LevelCatalog.next_available(level_index)
	completion_screen.next_available = following >= 0
	completion_screen.next_requested.connect(func() -> void: _select_level(following))
	completion_screen.replay_requested.connect(func() -> void: _select_level(level_index))
	completion_screen.levels_requested.connect(_show_menu.bind("levels"))
	add_child(completion_screen)

func _on_failure_finished() -> void:
	if current_screen != "game" or failure_stage != "animating":
		return
	failure_stage = "choices"
	failure_screen = FailureScreen.new()
	failure_screen.reason = String(state.failure)
	failure_screen.replay_requested.connect(func() -> void: _select_level(level_index))
	failure_screen.levels_requested.connect(_show_menu.bind("levels"))
	add_child(failure_screen)

func _select_level(index: int) -> void:
	if not LevelCatalog.is_available(index):
		return
	if index > unlocked or (board_view != null and board_view.is_animating()):
		return
	level_index = index
	level = LevelCatalog.get_level(index)
	state = GameRules.create_state(level)
	elapsed_seconds = 0.0
	completion_awards.clear()
	_queued_notice = ""
	history.clear()
	selected_layer = int(state.pos[0])
	hint_action = ""
	_remember_run()
	_build_ui()
	_refresh()
	_queue_level_tutorials()
	if not _tutorial_pending():
		_set_notice("点击相邻地块移动；右上角缩略图可切换层视图。", MUTED)

func _undo() -> void:
	if current_screen != "game" or paused or _tutorial_pending() or failure_stage != "":
		return
	if board_view != null and board_view.is_animating():
		return
	if history.is_empty() or state.status == "won":
		_set_notice("没有可撤销的有效步。", MUTED)
		return
	var was_assisted := bool(state.assisted)
	state = history.pop_back()
	state.assisted = was_assisted or bool(state.assisted)
	state.status = "playing"
	state.failure = ""
	hint_action = ""
	selected_layer = int(state.pos[0])
	if board_view != null:
		board_view.reset_view(selected_layer)
	_remember_run()
	_refresh()
	_set_notice("已撤销一步。", MUTED)

func _restart() -> void:
	if current_screen != "game" or paused or _tutorial_pending() or completion_stage != "" or failure_stage != "":
		return
	if board_view != null and board_view.is_animating():
		return
	state = GameRules.create_state(level)
	elapsed_seconds = 0.0
	completion_awards.clear()
	_queued_notice = ""
	history.clear()
	hint_action = ""
	var start_layer := int(state.pos[0])
	selected_layer = start_layer
	if board_view != null:
		board_view.reset_view(start_layer, true)
	_remember_run()
	_set_notice("本关已重开。", MUTED)
	_refresh()

func _hint() -> void:
	if current_screen != "game" or paused or _tutorial_pending() or state.status != "playing" or (board_view != null and board_view.is_animating()):
		return
	if _hint_task >= 0:
		_set_notice("正在规划路线…", GOLD)
		return
	_hint_snapshot = _hint_state_key()
	_hint_request = HintSearch.Request.new()
	_hint_task = WorkerThreadPool.add_task(_hint_request.compute.bind(level.duplicate(true),state.duplicate(true)))
	_set_notice("正在规划路线…", GOLD)

func _hint_state_key() -> String:
	return "%s|%s|%d" % [level.id,GameRules._state_key(state),int(state.used)]

func _poll_hint() -> void:
	if _hint_task < 0 or not WorkerThreadPool.is_task_completed(_hint_task) or paused:
		return
	WorkerThreadPool.wait_for_task_completion(_hint_task)
	_hint_task = -1
	var action := _hint_request.action
	_hint_request = null
	if current_screen != "game" or state.status != "playing" or _hint_state_key() != _hint_snapshot:
		return
	state.assisted = true
	_remember_run()
	if action.is_empty():
		_set_notice("当前局面无可用提示；试试撤销或重开。", GOLD)
		return
	hint_action = action
	_set_notice("下一步建议：" + _action_name(action), GOLD)
	_refresh()

func _exit_tree() -> void:
	if _hint_task >= 0:
		WorkerThreadPool.wait_for_task_completion(_hint_task)

func _bits_text(bits: int) -> String:
	var labels := []
	for bit in range(int(level.bit_count)):
		labels.append("%s=%d" % [["○", "◇", "△"][bit], (bits >> bit) & 1])
	return "  ".join(labels)

func _inventory_items(visible_state: Dictionary = {}) -> Array[Dictionary]:
	if visible_state.is_empty():
		visible_state = state
	var entries: Array[Dictionary] = []
	if visible_state.key_owned:
		entries.append({"id": "key", "icon": "◇", "name": "棱镜钥匙", "count": 1, "description": "进入钥匙门时自动使用，开启对应的锁。"})
	if int(visible_state.anchor_charges) > 0:
		entries.append({"id": "anchor", "icon": "⌖", "name": "相位锚片", "count": int(visible_state.anchor_charges), "description": "逆着折流方向离开时自动消耗一片。"})
	return entries

func _action_name(action: String) -> String:
	return {"U":"上", "R":"右", "D":"下", "L":"左", "X":"切换层"}.get(action, action)

func _tutorial_pending() -> bool:
	return tutorial_batch_index < tutorial_batches.size()

func _queue_level_tutorials() -> void:
	if not tutorials_enabled:
		return
	if level_index == 0 and "campaign_ui" not in tutorial_seen:
		tutorial_batches.append({"id":"campaign_ui", "title":"界面导览", "steps":[
			{"target":"board", "text":"这里是当前层的主棋盘。胶囊是你；浅色格可以落脚，空缺处无法通行。发光的出口格是本关终点。"},
			{"target":"objective", "text":"目标卡显示过关条件、已用步数、最佳步数与计时。通关、限时内通关、达到最佳步数各得一星；步数耗尽会失败。"},
			{"target":"preview", "text":"这张卡展示另一层的地形。点击可交换主视图和缩略图，方便规划路线；查看地图不会移动主角，也不消耗步数。"},
			{"target":"controls", "text":"方向按钮与棋盘方向一致；也可用方向键或 WASD 移动。走到升降格后按 X 或空格切层。点“撤销”或按 Z 可退回上一步。"},
			{"target":"cell", "at":level.lifts[0].duplicate(), "lift":true, "text":"有同心圆标记的是升降格。站在这里后点击脚下或按 X，可传送到另一层的对应位置。每次有效移动或升降都消耗一步。"},
			{"target":"inventory", "text":"底部是道具卡栏，显示已收集的钥匙和锚片等物品；左右箭头可以翻看更多。后续遇到新道具时，会单独介绍它的用途。"},
			{"target":"toolbar", "text":"右上角依次是重开 R、提示 H、暂停 Enter。暂停菜单可回主页、选关或查看图文规则；阅读这些引导时不会计时。点击“开始操作”试一试！"}
		]})
	for event in level.get("tutorial_events", []):
		if String(event.id) not in tutorial_seen:
			tutorial_batches.append(event.duplicate(true))

func _current_tutorial_step() -> Dictionary:
	return tutorial_batches[tutorial_batch_index].steps[tutorial_step_index]

func _tutorial_target(step: Dictionary) -> Rect2:
	var target := Rect2()
	match String(step.target):
		"objective": target = objective_panel.get_global_rect()
		"preview": target = board_view.preview_global_rect()
		"controls": target = controls_panel.get_global_rect()
		"toolbar": target = toolbar_panel.get_global_rect()
		"inventory": target = inventory_bar.get_global_rect()
		"board": target = board_view.board_global_rect()
		"cell":
			var position: Array = step.at.duplicate()
			if bool(step.get("lift",false)):
				position.push_front(int(state.pos[0]))
			selected_layer = int(position[0])
			board_view.selected_layer = selected_layer
			board_view.queue_redraw()
			target = board_view.cell_global_rect(position)
	return Rect2(target.position-global_position,target.size)

func _show_tutorial_step() -> void:
	if not _tutorial_pending():
		return
	if tutorial_coach == null:
		_clear_notice()
		board_view.paused = true
		tutorial_coach = TutorialCoach.new()
		tutorial_coach.name = "TutorialCoach"
		tutorial_coach.next_requested.connect(_next_tutorial_step)
		tutorial_coach.previous_requested.connect(_previous_tutorial_step)
		add_child(tutorial_coach)
	var batch := tutorial_batches[tutorial_batch_index]
	var step := _current_tutorial_step()
	var total := 0
	var current := tutorial_step_index
	for index in range(tutorial_batches.size()):
		var count: int = tutorial_batches[index].steps.size()
		total += count
		if index < tutorial_batch_index:
			current += count
	tutorial_coach.configure(String(batch.title),String(step.text),current,total,_tutorial_target(step))

func _next_tutorial_step() -> void:
	if tutorial_coach == null:
		return
	tutorial_step_index += 1
	if tutorial_step_index < tutorial_batches[tutorial_batch_index].steps.size():
		_show_tutorial_step()
		return
	tutorial_batch_index += 1
	tutorial_step_index = 0
	if _tutorial_pending():
		_show_tutorial_step()
		return
	# Keep the whole sequence available to Back; remember it only on final completion.
	for batch in tutorial_batches:
		var id := String(batch.id)
		if id not in tutorial_seen:
			tutorial_seen.append(id)
	_save_progress()
	remove_child(tutorial_coach)
	tutorial_coach.queue_free()
	tutorial_coach = null
	board_view.paused = false
	selected_layer = int(state.pos[0])
	board_view.reset_view(selected_layer)
	_refresh()

func _previous_tutorial_step() -> void:
	if tutorial_coach == null:
		return
	if tutorial_step_index > 0:
		tutorial_step_index -= 1
	elif tutorial_batch_index > 0:
		tutorial_batch_index -= 1
		tutorial_step_index = tutorial_batches[tutorial_batch_index].steps.size() - 1
	_show_tutorial_step()

func _toggle_pause() -> void:
	if current_screen != "game" or _tutorial_pending() or rules_screen != null or completion_stage in ["celebrating", "choices"] or failure_stage != "":
		return
	paused = not paused
	board_view.paused = paused
	pause_button.glyph = "resume" if paused else "pause"
	pause_button.queue_redraw()
	if paused:
		if _notice_tween != null and _notice_tween.is_valid():
			_notice_tween.pause()
		pause_screen = PauseScreen.new()
		pause_screen.resume_rect = Rect2(pause_button.global_position - global_position, pause_button.size)
		pause_screen.resume_requested.connect(_toggle_pause)
		pause_screen.home_requested.connect(_show_menu.bind("home"))
		pause_screen.levels_requested.connect(_show_menu.bind("levels"))
		pause_screen.rules_requested.connect(_show_legend)
		add_child(pause_screen)
	else:
		if pause_screen != null:
			remove_child(pause_screen)
			pause_screen.queue_free()
			pause_screen = null
		if _notice_tween != null and _notice_tween.is_valid():
			_notice_tween.play()

func _show_legend() -> void:
	if rules_screen != null:
		return
	if not paused:
		_toggle_pause()
	rules_screen = RulesScreen.new()
	rules_screen.closed.connect(_close_rules)
	add_child(rules_screen)

func _close_rules() -> void:
	if rules_screen != null:
		remove_child(rules_screen)
		rules_screen.queue_free()
		rules_screen = null

func _set_notice(message: String, color: Color) -> void:
	notice_text = message
	notice_color = color
	if toast_panel == null or feedback_label == null:
		return
	if _notice_tween != null and _notice_tween.is_running():
		_notice_tween.kill()
	feedback_label.text = message
	feedback_label.add_theme_color_override("font_color", color)
	toast_panel.visible = true
	toast_panel.modulate.a = 0.0
	_notice_tween = create_tween()
	_notice_tween.tween_property(toast_panel, "modulate:a", 1.0, 0.25)
	_notice_tween.tween_interval(3.0)
	_notice_tween.tween_property(toast_panel, "modulate:a", 0.0, 0.38)
	_notice_tween.tween_callback(_hide_notice)

func _hide_notice() -> void:
	if toast_panel != null:
		toast_panel.visible = false
	notice_text = ""

func _clear_notice() -> void:
	notice_text = ""
	if _notice_tween != null and _notice_tween.is_running():
		_notice_tween.kill()
	if toast_panel != null:
		toast_panel.visible = false

func _load_progress() -> void:
	best_stars.resize(LevelCatalog.LEVELS.size())
	best_stars.fill(0)
	var config := ConfigFile.new()
	if config.load(progress_path) == OK:
		var saved_version := int(config.get_value("progress", "campaign_version", 0))
		if saved_version not in [3, LevelCatalog.CAMPAIGN_VERSION]:
			# The old four examples have different goals. Preserve their save separately.
			config.save(progress_path.get_basename() + "_before_campaign.cfg")
			return
		unlocked = clampi(int(config.get_value("progress", "unlocked", 0)), 0, LevelCatalog.LEVELS.size() - 1)
		var migrating := saved_version == 3
		if migrating:
			config.save(progress_path.get_basename() + "_before_expansion.cfg")
			unlocked = mini(unlocked, 31)
		var saved_tutorials: Variant = config.get_value("progress", "tutorial_seen", [])
		if saved_tutorials is Array and int(config.get_value("progress", "tutorial_version", 0)) == TUTORIAL_VERSION:
			for entry in saved_tutorials:
				if entry is String and entry not in tutorial_seen:
					tutorial_seen.append(entry)
		var saved_stars: Variant = config.get_value("progress", "stars", [0, 0, 0, 0])
		if saved_stars is Array:
			for i in range(mini(saved_stars.size(), best_stars.size())):
				if migrating and i >= 31:
					continue
				# Old ratings did not record elapsed time; retain their clear star and unlocks.
				best_stars[i] = clampi(int(saved_stars[i]), 0, 3) if int(config.get_value("progress", "scoring_version", 1)) >= 2 else mini(1, int(saved_stars[i]))
		has_play_history = bool(config.get_value("progress", "has_history", unlocked > 0 or best_stars.max() > 0))
		var saved_last := int(config.get_value("progress", "last_played", unlocked))
		last_played = clampi(saved_last, 0, unlocked)
		if not LevelCatalog.is_available(last_played):
			last_played = 0
		if migrating and saved_last >= 31:
			return
		var previous_level := LevelCatalog.get_level(last_played)
		saved_run = _validated_state(config.get_value("run", "state", {}), previous_level)
		var previous_history: Variant = config.get_value("run", "history", [])
		if not saved_run.is_empty() and previous_history is Array:
			for entry in previous_history.slice(0, int(previous_level.move_limit)):
				var valid := _validated_state(entry, previous_level)
				if valid.is_empty():
					saved_history.clear()
					break
				saved_history.append(valid)

func _validated_state(value: Variant, data: Dictionary) -> Dictionary:
	if not value is Dictionary:
		return {}
	var defaults := GameRules.create_state(data)
	for key in defaults:
		if not value.has(key) or typeof(value[key]) != typeof(defaults[key]):
			return {}
	if value.pos.size() != 3:
		return {}
	for coordinate in value.pos:
		if not coordinate is int:
			return {}
	if int(value.pos[0]) < 0 or int(value.pos[0]) > 1 or int(value.pos[1]) < 0 or int(value.pos[1]) >= int(data.width) or int(value.pos[2]) < 0 or int(value.pos[2]) >= int(data.height):
		return {}
	if value.status not in ["playing", "won", "failed"] or int(value.used) < 0 or int(value.used) > int(data.move_limit):
		return {}
	if int(value.phase) < 0 or int(value.phase) >= int(data.get("moving_period", 1)) or int(value.beacon_index) < 0 or int(value.beacon_index) > data.beacons.size():
		return {}
	return value.duplicate(true)

func _remember_run() -> void:
	has_play_history = true
	last_played = level_index
	saved_run = state.duplicate(true)
	saved_history.assign(history.duplicate(true))
	_save_progress()

func _reset_progress() -> void:
	unlocked = 0
	tutorial_seen.clear()
	best_stars.resize(LevelCatalog.LEVELS.size())
	best_stars.fill(0)
	has_play_history = false
	last_played = 0
	saved_run.clear()
	saved_history.clear()
	history.clear()
	level_index = 0
	level = LevelCatalog.get_level(0)
	state = GameRules.create_state(level)
	selected_layer = int(state.pos[0])
	_save_progress()
	_show_menu("levels")

func _save_progress() -> void:
	var config := ConfigFile.new()
	config.set_value("progress", "unlocked", unlocked)
	config.set_value("progress", "stars", best_stars)
	config.set_value("progress", "scoring_version", 2)
	config.set_value("progress", "campaign_version", LevelCatalog.CAMPAIGN_VERSION)
	config.set_value("progress", "has_history", has_play_history)
	config.set_value("progress", "last_played", last_played)
	config.set_value("progress", "tutorial_seen", tutorial_seen)
	config.set_value("progress", "tutorial_version", TUTORIAL_VERSION)
	config.set_value("run", "state", saved_run)
	config.set_value("run", "history", saved_history)
	var error := config.save(progress_path)
	if error != OK:
		push_warning("无法保存本地进度：%s" % error_string(error))

func _label(text_value: String, size: int, color: Color) -> Label:
	var label := Label.new()
	label.text = text_value
	label.add_theme_font_size_override("font_size", size)
	label.add_theme_color_override("font_color", color)
	return label

func _small_button(text_value: String) -> Button:
	var button := Button.new()
	button.text = text_value
	button.custom_minimum_size = Vector2(54, 38)
	button.focus_mode = Control.FOCUS_NONE
	button.add_theme_stylebox_override("normal", _box(SURFACE_ALT, Color("3d535b"), 6, 1))
	button.add_theme_stylebox_override("hover", _box(Color("2b4149"), TEAL, 6, 1))
	button.add_theme_color_override("font_color", TEXT)
	return button

func _panel() -> PanelContainer:
	var panel := PanelContainer.new()
	panel.add_theme_stylebox_override("panel", _box(SURFACE, Color("2a3d44"), 8, 1))
	return panel

func _box(fill: Color, border: Color, radius: int, border_width: int) -> StyleBoxFlat:
	var style := StyleBoxFlat.new()
	style.bg_color = fill
	style.border_color = border
	style.set_border_width_all(border_width)
	style.set_corner_radius_all(radius)
	style.content_margin_left = 8
	style.content_margin_right = 8
	style.content_margin_top = 5
	style.content_margin_bottom = 5
	return style
