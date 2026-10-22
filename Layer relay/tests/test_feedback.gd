extends SceneTree

var failures: Array[String] = []
var game: Variant
var test_path := "user://feedback_test_%d.cfg" % OS.get_process_id()

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
	game.set_process(false)
	game.unlocked = 3
	game._select_level(0)
	game._process(10.0)
	_check(game.elapsed_seconds == 0.0, "level generation counted against the time star")
	_settle()
	var view: BoardView = game.board_view
	game._act("R")
	_check(game.state.bits == 1 and view.state.bits == 0 and game.bit_line.text.begins_with("当前  ○=0"), "switch or HUD flipped before the jump")
	view._process(0.41)
	_check(view.state.bits == 0 and not view._switch_goal_matched(1), "switch flipped before the landing rebound finished")
	view._process(0.20)
	_check(view._mode == "environment" and view.state.bits == 1 and view._switch_goal_matched(1) and game.bit_line.text.begins_with("当前  ○=1"), "switch and HUD did not commit together after landing")
	_settle()
	# Freeze a portal between its two boards. Neither clock nor any animation may advance.
	game._act("X")
	view._process(0.24)
	game.elapsed_seconds = 12.0
	await _key(KEY_ENTER)
	var animation_time := view._elapsed
	game._process(8.0)
	view._process(8.0)
	game._act("L")
	game._restart()
	_check(game.paused and view.paused and view._elapsed == animation_time and game.elapsed_seconds == 12.0 and game.state.used == 2, "pause failed to freeze clock, portal or gameplay actions")
	game._show_legend()
	await process_frame
	_check(game.rules_screen.card_count == 13, "rules lacked the actual tile samples")
	await _key(KEY_ESCAPE)
	_check(game.rules_screen == null and game.paused, "closing rules resumed gameplay without returning to pause")
	await _key(KEY_ENTER)
	_check(not game.paused and not view.paused, "Enter failed to resume the paused portal")
	_settle()
	game._process(2.0)
	game._undo()
	_settle()
	_check(game.elapsed_seconds == 14.0, "undo rolled back the elapsed time")
	game._restart()
	_check(game.elapsed_seconds == 0.0 and view.state.pos == game.level.start, "restart failed to reset timer and player")
	_settle()

	game._select_level(1)
	_settle()
	game._act("R")
	_settle()
	game._act("R")
	view = game.board_view
	_check(game.state.key_owned and not view.state.key_owned and view.state.collected.is_empty() and game.inventory_bar.items.is_empty(), "key or inventory appeared before pickup landing")
	view._process(0.41)
	_check(not view.state.key_owned and view.state.bits == 0, "pickup tile changed during landing rebound")
	_settle()
	_check(view.state.key_owned and view.state.bits == 1 and game.inventory_bar.items.size() == 1, "key and switch did not settle together")
	for action in ["L", "L", "X"]:
		game._act(action)
		_settle()
	game._act("R")
	_check(view.state.beacon_index == 0 and view.state.pending == 0 and game.beacon_line.text == "信标  0 / 2", "beacon or pending bit changed before the jump")
	view._process(0.41)
	_check(view.state.beacon_index == 0, "beacon lit before landing rebound")
	_settle()
	_check(view.state.beacon_index == 1 and view.state.pending == 2 and view.state.bits == 1, "beacon and delayed bit did not queue after landing")
	game._act("R")
	view._process(0.41)
	_check(view.state.beacon_index == 1 and view.state.pending == 2 and view.state.bits == 1, "second beacon or delayed switch advanced during flight")
	_settle()
	_check(view.state.beacon_index == 2 and view.state.pending == 0 and view.state.bits == 3, "next landing did not apply delayed bit and second beacon")

	# A synthetic lift onto a switch ensures the portal handoff cannot reveal environment early.
	var portal_level := LevelCatalog.get_level(0)
	portal_level.switches = [{"at": [1, 1, 1], "mask": 1}]
	portal_level.gates = []
	var before := GameRules.create_state(portal_level)
	before.pos = [0, 1, 1]
	var after: Dictionary = GameRules.try_action(portal_level, before, "X").state
	var standalone := BoardView.new()
	root.add_child(standalone)
	standalone.set_process(false)
	standalone.set_context(portal_level, before, 0, "")
	standalone._process(standalone._generation_duration + BoardView.PLAYER_SPAWN_DURATION + 0.01)
	standalone.play_action(portal_level, before, after, "X", "")
	standalone._process(0.53)
	standalone._process(0.27)
	_check(standalone.selected_layer == 1 and standalone.state.bits == 0, "portal board swap revealed the destination switch too soon")
	standalone._process(0.26)
	standalone._process(0.40)
	_check(standalone.state.bits == 0, "portal destination switch changed before descent ended")
	standalone._process(0.33)
	_check(standalone.state.bits == 1, "portal destination switch did not apply after descent")
	standalone._process(BoardView.STATUS_FADE_DURATION + 0.01)
	var ride_level := LevelCatalog.get_level(3)
	ride_level.items = [{"id": "ride_key", "at": [0, 1, 1], "type": "key"}]
	before = GameRules.create_state(ride_level)
	after = GameRules.try_action(ride_level, before, "D").state
	standalone.set_context(ride_level, before, 0, "")
	standalone._process(standalone._generation_duration + BoardView.PLAYER_SPAWN_DURATION + 0.01)
	standalone.play_action(ride_level, before, after, "D", "")
	standalone._process(0.61)
	_check(standalone._mode == "rows" and not standalone.state.key_owned, "platform pickup appeared when the hop ended before the ride")
	standalone._process(0.24)
	_check(not standalone.state.key_owned, "platform pickup appeared during the ride")
	standalone._process(0.25)
	_check(standalone.state.key_owned and standalone.state.pos == after.pos, "platform pickup did not wait until the player finished riding")
	standalone.queue_free()

	game._select_level(3)
	_settle()
	view = game.board_view
	view._configure_board(0, view._main_grid_area(), 1.0, false, false)
	var capsule := view._wrapped_screen_polygon(0, 1.0, 1.0, view._capsule_outline())
	var bounds := Rect2(capsule[0], Vector2.ZERO)
	for point in capsule:
		bounds = bounds.expand(point)
	_check(is_equal_approx(bounds.size.x, 20) and is_equal_approx(bounds.size.y, 50), "riding capsule did not retain the normal 20 by 50 pixel proportions")
	var clipped := view._wrapped_screen_polygon(0, -0.5, 1.0, view._capsule_outline())
	var seam_bounds := Rect2(clipped[0], Vector2.ZERO)
	for point in clipped:
		seam_bounds = seam_bounds.expand(point)
	_check(is_equal_approx(seam_bounds.size.x, 10) and is_equal_approx(seam_bounds.size.y, 50), "seam clipping flattened the riding capsule")
	view.state.bits = 0
	_check(view._switch_goal_matched(1), "goal-zero switch was not recognized as matching")
	view.state.bits = 1
	_check(not view._switch_goal_matched(1), "goal-zero switch incorrectly highlighted bit one")
	_test_scores()
	# Older ratings carry no time evidence, but must preserve cleared levels and unlocks.
	var legacy := ConfigFile.new()
	legacy.set_value("progress", "unlocked", 3)
	legacy.set_value("progress", "stars", [3, 2, 0, 1])
	legacy.set_value("progress", "campaign_version", LevelCatalog.CAMPAIGN_VERSION)
	legacy.save(test_path)
	var migrated: Variant = load("res://main.tscn").instantiate()
	migrated.tutorials_enabled = false
	migrated.progress_path = test_path
	root.add_child(migrated)
	_check(migrated.unlocked == 3 and migrated.best_stars == [1, 1, 0, 1], "old scoring migration lost unlocks or awarded unmeasured time stars")
	migrated.queue_free()
	game.queue_free()
	await process_frame
	DirAccess.remove_absolute(ProjectSettings.globalize_path(test_path))
	if failures.is_empty():
		print("PASS: delayed environment/HUD/item/beacon/portal, pause clock/input/resume, upright seam capsule, independent stars and best-step targets")
		quit(0)
	else:
		for failure in failures:
			push_error(failure)
		quit(1)

func _test_scores() -> void:
	var level := LevelCatalog.get_level(0)
	var state := GameRules.create_state(level)
	_check(ScoreRules.evaluate(level, state, 0).stars == 0, "uncompleted level earned a star")
	state.status = "won"
	state.assisted = true
	for case in [[3, 45.0, 3], [4, 45.0, 2], [3, 45.001, 2], [4, 45.001, 1]]:
		state.used = case[0]
		_check(ScoreRules.evaluate(level, state, case[1]).stars == case[2], "independent clear/time/steps stars or inclusive time boundary failed")
	for index in range(LevelCatalog.LEVELS.size()):
		level = LevelCatalog.get_level(index)
		state = GameRules.create_state(level)
		var route: Array[String] = []
		for i in range(int(level.move_limit)):
			if state.status == "won":
				break
			var action := GameRules.find_hint(level, state)
			if action.is_empty():
				break
			route.append(action)
			state = GameRules.try_action(level, state, action).state
		_check(state.status == "won" and int(state.used) == int(level.par), "level %d best-step target %d was not its shortest route %d (%s)" % [index + 1, level.par, state.used, str(route)])

func _settle() -> void:
	game.board_view.set_process(false)
	if game.board_view._generation_active:
		game.board_view._process(game.board_view._generation_duration + BoardView.PLAYER_SPAWN_DURATION + 0.01)
	for i in range(16):
		if not game.board_view.busy and not game.board_view._player_spawn_active and not game.board_view._status_fade_active:
			break
		game.board_view._process(0.5)

func _key(code: Key) -> void:
	var event := InputEventKey.new()
	event.keycode = code
	event.pressed = true
	Input.parse_input_event(event)
	await process_frame

func _check(condition: bool, message: String) -> void:
	if not condition:
		failures.append(message)
