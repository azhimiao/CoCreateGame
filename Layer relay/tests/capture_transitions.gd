extends SceneTree

var game: Variant
var output := "res://runtime/transition-review"
var test_path := "user://transition_capture_%d.cfg" % OS.get_process_id()

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
	await process_frame
	game.set_process(false)
	game.unlocked = 3
	game._select_level(0)
	game.board_view.set_process(false)
	game._clear_notice()
	game.board_view._process(0.65)
	await _frame("01-tiles-only")
	game.board_view._process(game.board_view._generation_duration - game.board_view._generation_elapsed)
	await _frame("02-board-complete-player-hidden")
	game.board_view._process(BoardView.PLAYER_SPAWN_DURATION * 0.5)
	await _frame("03-player-fading-in")
	game.board_view._process(BoardView.PLAYER_SPAWN_DURATION * 0.5 + 0.01)
	await _frame("04-player-ready")
	game._act("R")
	game.board_view._process(0.61)
	await _frame("05-switch-fade-start")
	game.board_view._process(BoardView.STATUS_FADE_DURATION * 0.5)
	await _frame("06-switch-fade-middle")
	_settle()
	game._act("L")
	_settle()
	game._clear_notice()
	await _frame("07-switch-center-check")
	game._act("R")
	game.board_view._process(0.61)
	game.board_view._process(BoardView.STATUS_FADE_DURATION * 0.5)
	await _frame("08-switch-unmatch-middle")
	_settle()
	game._select_level(1)
	_settle()
	for action in ["R", "R", "L", "L", "X"]:
		game._act(action)
		_settle()
	game._act("R")
	game.board_view._process(0.61)
	game._clear_notice()
	await _frame("09-beacon-fade-start")
	game.board_view._process(BoardView.STATUS_FADE_DURATION * 0.5)
	await _frame("10-beacon-fade-middle")
	_settle()
	game._act("R")
	_settle()
	game._clear_notice()
	await _frame("11-beacon-center-check-and-diamond-number")
	# Force a real step-limit failure after both beacons, by moving back off beacon 2.
	game.state.used = int(game.level.move_limit) - 1
	game._refresh()
	game._act("L")
	game.board_view._process(0.61)
	await _frame("12-beacon-extinction-start")
	game.board_view._process(BoardView.STATUS_FADE_DURATION * 0.5)
	await _frame("13-beacon-extinction-middle")
	_settle()
	game._clear_notice()
	await _frame("14-beacon-extinction-end")
	game._show_legend()
	await _frame("15-rules-center-checks")
	game._close_rules()
	game._toggle_pause()
	root.content_scale_size = Vector2i(1080, 720)
	root.size = Vector2i(1080, 720)
	game._select_level(0)
	game.board_view.set_process(false)
	game._clear_notice()
	game.board_view._process(game.board_view._generation_duration)
	game.board_view._process(BoardView.PLAYER_SPAWN_DURATION * 0.5)
	await _frame("16-entrance-1080")
	_settle()
	game._act("R")
	_settle()
	game._act("L")
	_settle()
	game._clear_notice()
	await _frame("17-center-check-1080")
	game.queue_free()
	await process_frame
	DirAccess.remove_absolute(ProjectSettings.globalize_path(test_path))
	print("PASS: engine entrance, status fade and centered-check frames saved under runtime/transition-review")
	quit()

func _settle() -> void:
	game.board_view.set_process(false)
	if game.board_view._generation_active:
		game.board_view._process(game.board_view._generation_duration + BoardView.PLAYER_SPAWN_DURATION + 0.01)
	for i in range(16):
		if not game.board_view.busy and not game.board_view._player_spawn_active and not game.board_view._status_fade_active:
			break
		game.board_view._process(0.5)

func _frame(filename: String) -> void:
	await process_frame
	await process_frame
	await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_png(output + "/" + filename + ".png")
