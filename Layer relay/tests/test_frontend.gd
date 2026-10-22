extends SceneTree

var failures: Array[String] = []
var test_path := "user://frontend_test_%d.cfg" % OS.get_process_id()

func _initialize() -> void:
	# Isolated mechanism fixtures; these examples are not in the playable campaign.
	LevelCatalog.LEVELS.assign(MechanicFixtures.LEVELS.duplicate(true))
	call_deferred("_run")

func _run() -> void:
	root.size = Vector2i(1360, 860)
	var game: Variant = load("res://main.tscn").instantiate()
	game.tutorials_enabled = false
	game.progress_path = test_path
	root.add_child(game)
	await process_frame
	await process_frame
	_check(game.current_screen == "menu" and game.menu_screen.page == "home", "boot did not open the home screen")
	_check(game.menu_screen.primary_button.text == "开始游戏", "fresh profile did not show a first-play action")
	_check(_buttons(game.menu_screen.content).size() == 4 and game.menu_screen.select_button.text == "选择关卡", "home did not have exactly two main actions plus About and Settings")
	var untouched: Dictionary = game.state.duplicate(true)
	var key := InputEventKey.new()
	key.keycode = KEY_R
	key.pressed = true
	game._unhandled_input(key)
	_check(game.state == untouched and not FileAccess.file_exists(test_path), "gameplay shortcuts changed progress while in a menu")
	game.menu_screen.show_page("settings", false)
	_check(_buttons(game.menu_screen.content).size() == 1 and _buttons(game.menu_screen.content)[0].text == "←  返回", "settings had controls beyond Return")
	await _click(_buttons(game.menu_screen.content)[0])
	await _click(game.menu_screen.primary_button)
	await process_frame
	_finish_animation(game)
	_check(game.current_screen == "game" and game.level_index == 0, "start button did not enter level 1")
	game._act("R")
	_finish_animation(game)
	game._act("X")
	_finish_animation(game)
	var checkpoint: Dictionary = game.state.duplicate(true)
	_check(int(checkpoint.pos[0]) == 1 and int(checkpoint.used) == 2, "could not prepare an upper-layer checkpoint")
	game._show_menu("home")
	_check(game.menu_screen.primary_button.text == "从新关卡开始" and _buttons(game.menu_screen.content).size() == 4, "home did not keep two main actions after playing")
	game.queue_free()
	await process_frame
	# Recreate the entire scene to check disk persistence, not just in-memory navigation.
	game = load("res://main.tscn").instantiate()
	game.tutorials_enabled = false
	game.progress_path = test_path
	root.add_child(game)
	await process_frame
	_check(game.menu_screen.primary_button.text == "从新关卡开始", "play history did not persist across application restarts")
	await _click(game.menu_screen.primary_button)
	await process_frame
	_finish_animation(game)
	_check(game.level_index == 0 and game.state.used == 0 and game.state.pos == game.level.start and game.history.is_empty(), "start from new level did not reset the first unfinished level")
	_check(game.selected_layer == 0 and game.board_view.selected_layer == 0, "new level retained the previous upper-layer view")
	game._act("R")
	_finish_animation(game)
	game._act("X")
	_finish_animation(game)
	game._undo()
	_check(game.state.used == 1 and game.state.pos[0] == 0, "new run did not support Undo")
	game._act("X")
	_finish_animation(game)
	game._act("R")
	_finish_animation(game)
	_check(game.state.status == "won" and game.unlocked == 1 and game.best_stars[0] == 3, "winning did not unlock level 2")
	game._show_menu("home")
	await _click(game.menu_screen.select_button)
	_check(game.menu_screen.page == "levels", "second home action did not open level selection")
	game.menu_screen.go_back()
	await _click(game.menu_screen.primary_button)
	await process_frame
	_finish_animation(game)
	_check(game.level_index == 1, "New level did not choose the first unfinished available level")
	game._show_menu("levels")
	await process_frame
	await process_frame
	var menu: FrontendScreen = game.menu_screen
	_check(menu.level_grid.columns == 6 and menu.level_cards.size() == 66, "selector did not arrange 66 coordinates in six columns")
	_check(not menu.level_cards[1].disabled and menu.level_cards[2].disabled and menu.level_cards[65].disabled, "selector ignored progress locks or future-level locks")
	var wheel := InputEventMouseButton.new()
	wheel.position = menu.level_scroll.get_global_rect().get_center()
	wheel.global_position = wheel.position
	wheel.button_index = MOUSE_BUTTON_WHEEL_DOWN
	wheel.pressed = true
	Input.parse_input_event(wheel)
	await process_frame
	wheel = wheel.duplicate()
	wheel.pressed = false
	Input.parse_input_event(wheel)
	await process_frame
	_check(menu.level_scroll.scroll_vertical > 0, "mouse wheel did not scroll over a locked level card")
	menu.level_scroll.scroll_vertical = 9999
	await process_frame
	_check(menu.level_scroll.scroll_vertical > 0, "selector could not scroll to later rows")
	menu.open_reset_confirmation()
	_check(game.unlocked == 1 and game.best_stars[0] == 3, "opening reset confirmation destroyed progress")
	await _click(menu.reset_cancel)
	_check(menu.reset_overlay == null and game.unlocked == 1, "cancel did not preserve progress")
	menu.open_reset_confirmation()
	key.keycode = KEY_ESCAPE
	game._unhandled_input(key)
	_check(menu.reset_overlay == null and menu.page == "levels", "Escape did not dismiss reset confirmation before leaving the selector")
	menu.open_reset_confirmation()
	await _click(menu.reset_confirm)
	await process_frame
	_check(game.unlocked == 0 and game.best_stars == [0, 0, 0, 0] and not game.has_play_history and game.saved_run.is_empty(), "confirmed reset did not clear all progression and the checkpoint")
	_check(game.menu_screen.page == "levels" and game.menu_screen.level_cards[1].disabled, "selector was not refreshed after reset")
	game.queue_free()
	await process_frame
	game = load("res://main.tscn").instantiate()
	game.tutorials_enabled = false
	game.progress_path = test_path
	root.add_child(game)
	await process_frame
	_check(not game.has_play_history and game.unlocked == 0 and game.menu_screen.primary_button.text == "开始游戏", "reset did not persist across application restarts")
	game.best_stars.assign([3, 3, 3, 3])
	game.unlocked = 3
	game.has_play_history = true
	game._show_menu("home")
	_check(game.menu_screen.primary_button.disabled and game.menu_screen.next_level == -1, "all-completed profile incorrectly offered an existing level as new")
	game.queue_free()
	await process_frame
	DirAccess.remove_absolute(ProjectSettings.globalize_path(test_path))
	if failures.is_empty():
		print("PASS: two-action home/navigation, history labels, fresh new-level start/undo/unlock, six-column scrolling, confirmed reset and persistence")
		quit(0)
	else:
		for failure in failures:
			push_error(failure)
		quit(1)

func _finish_animation(game: Variant) -> void:
	game.board_view.set_process(false)
	for i in range(12):
		game.board_view._process(0.5)

func _click(button: Button) -> void:
	await process_frame
	var point := button.get_global_transform_with_canvas() * (button.size * 0.5)
	var motion := InputEventMouseMotion.new()
	motion.position = point
	motion.global_position = point
	Input.parse_input_event(motion)
	await process_frame
	var press := InputEventMouseButton.new()
	press.position = point
	press.global_position = point
	press.button_index = MOUSE_BUTTON_LEFT
	press.pressed = true
	Input.parse_input_event(press)
	await process_frame
	press = press.duplicate()
	press.pressed = false
	Input.parse_input_event(press)
	await process_frame

func _buttons(node: Node) -> Array[Button]:
	var result: Array[Button] = []
	for child in node.get_children():
		if child is Button:
			result.append(child)
		result.append_array(_buttons(child))
	return result

func _check(condition: bool, message: String) -> void:
	if not condition:
		failures.append(message)
