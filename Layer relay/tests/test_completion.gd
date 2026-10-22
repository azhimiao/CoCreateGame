extends SceneTree

var failures: Array[String] = []
var game: Variant
var test_path := "user://completion_test_%d.cfg" % OS.get_process_id()

func _initialize() -> void:
	# Isolated mechanism fixtures; these examples are not in the playable campaign.
	LevelCatalog.LEVELS.assign(MechanicFixtures.LEVELS.duplicate(true))
	call_deferred("_run")

func _run() -> void:
	root.size = Vector2i(1360, 860)
	game = load("res://main.tscn").instantiate()
	game.tutorials_enabled = false
	game.progress_path = test_path
	root.add_child(game)
	await process_frame
	var home_icons := _icons(game.menu_screen)
	_check(home_icons.size() == 2 and home_icons[0].glyph == "about" and home_icons[1].glyph == "settings", "home did not use round About and Settings icons")
	_check(not home_icons[0]._has_point(Vector2.ZERO) and home_icons[0]._has_point(home_icons[0].size * 0.5), "round icon hit area did not match its circle")
	game._select_level(0)
	await process_frame
	_settle_motion()
	_check(game.header_title.text == game.level.name and game.header_subtitle.text == game.level.subtitle, "header contained content beyond the level title and subtitle")
	_check(game.move_counter.get_parent().get_parent() == game.objective_panel and game.move_counter.get_theme_font_size("font_size") >= 20, "move count was not enlarged below the objective")
	_check(game.toast_panel.get_theme_stylebox("panel") is StyleBoxEmpty, "notice still had a panel background or border")
	var icons := _icons(game)
	_check(icons.size() == 3 and icons[0].glyph == "replay" and icons[1].glyph == "hint" and icons[2].glyph == "pause", "in-game toolbar did not provide Restart, Hint, Pause")
	await _click(icons[2])
	_check(game.paused and game.pause_screen != null, "pause icon did not freeze gameplay and open the menu")
	var menu_icons := _icons(game.pause_screen)
	await _click(menu_icons[3])
	_check(game.rules_screen != null and game.rules_screen.card_count == 13, "pause Rules icon did not open the illustrated rule explanation")
	game._close_rules()
	await _click(game.pause_screen.resume_button)
	_check(not game.paused and game.pause_screen == null, "same top-right icon did not resume gameplay")
	game._act("R")
	_settle_motion()
	game._act("X")
	_settle_motion()
	game._act("R")
	_check(game.completion_stage == "waiting" and game.completion_screen == null, "completion overlay appeared before the final jump landed")
	game.board_view._process(0.41)
	_check(game.completion_stage == "waiting", "celebration began before landing rebound finished")
	game.board_view._process(0.21)
	_check(game.completion_stage == "celebrating" and game.board_view._completion_active and game.board_view.state.pos == game.level.goal, "goal celebration did not start at the settled player position")
	game.board_view._process(0.80)
	_check(game.completion_screen == null and game.board_view.is_animating(), "dimmed choices interrupted the visible goal celebration")
	game.board_view._process(0.81)
	await process_frame
	_check(game.completion_stage == "choices" and game.completion_screen != null, "celebration did not lead to the dimmed completion choices")
	_check(not game.completion_screen.next_button.disabled, "next level was unavailable after a normal win")
	var restart_key := InputEventKey.new()
	restart_key.keycode = KEY_R
	restart_key.pressed = true
	game._unhandled_input(restart_key)
	_check(game.state.status == "won", "gameplay restart shortcut bypassed the completion choices")
	await _click(game.completion_screen.next_button)
	_settle_motion()
	_check(game.level_index == 1 and game.state.status == "playing" and game.completion_screen == null, "Next did not enter the unlocked next level with a clean overlay state")
	_win_current_level()
	await process_frame
	await _click(game.completion_screen.replay_button)
	_settle_motion()
	_check(game.level_index == 1 and game.state.used == 0 and game.selected_layer == int(game.level.start[0]), "Replay did not reset the same level and start layer")
	_win_current_level()
	await process_frame
	await _click(game.completion_screen.levels_button)
	_check(game.current_screen == "menu" and game.menu_screen.page == "levels", "Back to level selection did not open the selector")
	game.unlocked = 3
	game._select_level(3)
	_settle_motion()
	_win_current_level()
	await process_frame
	_check(game.completion_screen.next_button.disabled, "final available level offered a nonexistent next level")
	await _click(game.completion_screen.replay_button)
	_settle_motion()
	_check(game.level_index == 3 and not game.board_view._completion_active, "Replay retained the previous goal particles")
	game._toggle_pause()
	await _click(_icons(game.pause_screen)[2])
	_check(game.current_screen == "menu" and game.menu_screen.page == "levels", "pause Levels icon did not open the selector")
	game._select_level(2)
	_settle_motion()
	game._toggle_pause()
	await _click(_icons(game.pause_screen)[1])
	_check(game.current_screen == "menu" and game.menu_screen.page == "home", "pause Home icon did not open the home page")
	root.content_scale_size = Vector2i(1080, 720)
	root.size = Vector2i(1080, 720)
	await process_frame
	await process_frame
	game._select_level(2)
	_settle_motion()
	await process_frame
	var view: BoardView = game.board_view
	view._configure_board(1, view._main_grid_area(), 1, false, false)
	var goal_point := view._cell_center(game.level.goal)
	var objective_rect := Rect2(game.objective_panel.position, game.objective_panel.size)
	_check(not objective_rect.has_point(goal_point), "minimum window objective covered the exit")
	game.queue_free()
	await process_frame
	DirAccess.remove_absolute(ProjectSettings.globalize_path(test_path))
	if failures.is_empty():
		print("PASS: circular icon input, clean HUD/text notice, landing-before-celebration, next/replay/selector choices, last-level guard")
		quit(0)
	else:
		for failure in failures:
			push_error(failure)
		quit(1)

func _settle_motion() -> void:
	game.board_view.set_process(false)
	if game.board_view._generation_active:
		game.board_view._process(game.board_view._generation_duration + BoardView.PLAYER_SPAWN_DURATION + 0.01)
	for i in range(12):
		if not game.board_view.busy and not game.board_view._player_spawn_active and not game.board_view._status_fade_active:
			break
		game.board_view._process(0.5)

func _win_current_level() -> void:
	for action in game.level.solution:
		game._act(action)
		_settle_motion()
	_check(game.state.status == "won", "solution did not win the current level")
	game.board_view._process(BoardView.COMPLETION_DURATION + 0.01)

func _icons(node: Node) -> Array[GlyphButton]:
	var found: Array[GlyphButton] = []
	for child in node.get_children():
		if child is GlyphButton:
			found.append(child)
		found.append_array(_icons(child))
	return found

func _click(button: Button) -> void:
	await process_frame
	var point := button.get_global_transform_with_canvas() * (button.size * 0.5)
	var motion := InputEventMouseMotion.new()
	motion.position = point
	motion.global_position = point
	Input.parse_input_event(motion)
	await process_frame
	for pressed_value in [true, false]:
		var click := InputEventMouseButton.new()
		click.position = point
		click.global_position = point
		click.button_index = MOUSE_BUTTON_LEFT
		click.pressed = pressed_value
		Input.parse_input_event(click)
		await process_frame

func _check(condition: bool, message: String) -> void:
	if not condition:
		failures.append(message)
