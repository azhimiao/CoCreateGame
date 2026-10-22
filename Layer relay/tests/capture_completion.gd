extends SceneTree

var output := "res://runtime/completion-review"
var game: Variant
var test_path := "user://completion_capture_%d.cfg" % OS.get_process_id()

func _initialize() -> void:
	LevelCatalog.LEVELS.assign(MechanicFixtures.LEVELS.duplicate(true))
	call_deferred("_capture")

func _capture() -> void:
	root.size = Vector2i(1360, 860)
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(output))
	game = load("res://main.tscn").instantiate()
	game.tutorials_enabled = false
	game.progress_path = test_path
	root.add_child(game)
	await _frame("home-icons")
	game.unlocked = 3
	game._select_level(0)
	await process_frame
	game.board_view.set_process(false)
	game._clear_notice()
	game.board_view._process(0.65)
	await _frame("reveal-white-wave")
	game.board_view._process(game.board_view._generation_duration + BoardView.PLAYER_SPAWN_DURATION + 0.01)
	await _frame("level-1-clean-hud")
	game._set_notice("向下一束光出发。", Color("b0ebdf"))
	await create_timer(0.30).timeout
	await _frame("text-only-notice")
	game._clear_notice()
	for action in game.level.solution:
		game._act(action)
		_settle_motion()
	game.board_view._process(0.36)
	await _frame("goal-confetti")
	game.board_view._process(1.25)
	await create_timer(0.50).timeout
	await _frame("completion-choices")
	game._select_level(1)
	await process_frame
	_settle_motion()
	game._clear_notice()
	await _frame("key-and-switch")
	game.state.pos = [1, 0, 1]
	game.state.bits = 1
	game.state.key_owned = true
	game.selected_layer = 1
	game.board_view.reset_view(1)
	game._refresh()
	await _frame("beacons-and-gate")
	game._select_level(2)
	await process_frame
	_settle_motion()
	game._clear_notice()
	await _frame("anchor-and-circuit")
	game.state.pos = [1, 3, 1]
	game.state.bits = 3
	game.state.anchor_charges = 1
	game.selected_layer = 1
	game.board_view.reset_view(1)
	game._refresh()
	await _frame("flow-and-exit")
	root.content_scale_size = Vector2i(1080, 720)
	root.size = Vector2i(1080, 720)
	await _frame("hud-1080")
	game._select_level(3)
	await process_frame
	_settle_motion()
	game._clear_notice()
	await _frame("moving-rows-1080")
	for action in game.level.solution:
		game._act(action)
		_settle_motion()
	game.board_view._process(BoardView.COMPLETION_DURATION + 0.01)
	await create_timer(0.50).timeout
	await _frame("completion-1080")
	game.queue_free()
	await process_frame
	DirAccess.remove_absolute(ProjectSettings.globalize_path(test_path))
	print("PASS: engine-rendered HUD, special cells, white reveal, celebration and completion frames saved")
	quit()

func _settle_motion() -> void:
	game.board_view.set_process(false)
	if game.board_view._generation_active:
		game.board_view._process(game.board_view._generation_duration + BoardView.PLAYER_SPAWN_DURATION + 0.01)
	for i in range(12):
		if not game.board_view.busy and not game.board_view._player_spawn_active and not game.board_view._status_fade_active:
			break
		game.board_view._process(0.5)

func _frame(filename: String) -> void:
	await process_frame
	await process_frame
	await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_png("%s/%s.png" % [output, filename])
