extends SceneTree

var game: Variant
var output := "res://runtime/feedback-review"
var test_path := "user://feedback_capture_%d.cfg" % OS.get_process_id()

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
	_settle()
	game._clear_notice()
	await _frame("01-toolbar-and-switch")
	game._act("R")
	_settle()
	game._clear_notice()
	await _frame("02-matched-switch")
	game._toggle_pause()
	await _frame("03-pause-menu")
	game._show_legend()
	await _frame("04-illustrated-rules")
	var scroll := _scroll(game.rules_screen)
	scroll.scroll_vertical = 440
	await _frame("05-rules-beacons-and-items")
	scroll.scroll_vertical = 940
	await _frame("06-rules-platforms-and-goal")
	game._close_rules()
	game._toggle_pause()
	game._select_level(1)
	_settle()
	for action in ["R", "R", "L", "L", "X"]:
		game._act(action)
		_settle()
	game._clear_notice()
	await _frame("07-floating-beacons")
	game._act("R")
	game.board_view._process(0.41)
	await _frame("08-before-beacon-settlement")
	_settle()
	game._clear_notice()
	await _frame("09-lit-beacon")
	game._select_level(3)
	_settle()
	game._act("D")
	game.board_view._process(0.61)
	game.board_view._process(0.24)
	game._clear_notice()
	await _frame("10-upright-riding-capsule")
	_settle()
	var seam_before := GameRules.create_state(game.level)
	seam_before.phase = 4
	seam_before.pos = [0, 4, 2]
	game.state = seam_before
	game._refresh()
	game._act("U")
	game.board_view._process(0.61)
	game.board_view._process(0.24)
	game._clear_notice()
	await _frame("10b-upright-capsule-across-seam")
	_settle()
	game._select_level(0)
	_settle()
	game.elapsed_seconds = 47.0
	for action in game.level.solution:
		game._act(action)
		_settle()
	game.board_view._process(BoardView.COMPLETION_DURATION + 0.01)
	await create_timer(0.5).timeout
	await _frame("11-independent-two-stars")
	root.content_scale_size = Vector2i(1080, 720)
	root.size = Vector2i(1080, 720)
	await _frame("12-score-1080")
	game._select_level(1)
	_settle()
	game._toggle_pause()
	game._show_legend()
	await _frame("13-rules-1080")
	game._close_rules()
	await _frame("14-pause-1080")
	game._toggle_pause()
	game._clear_notice()
	await _frame("15-game-1080")
	game.queue_free()
	await process_frame
	DirAccess.remove_absolute(ProjectSettings.globalize_path(test_path))
	print("PASS: engine frames saved under runtime/feedback-review")
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

func _scroll(node: Node) -> ScrollContainer:
	if node is ScrollContainer:
		return node
	for child in node.get_children():
		var found := _scroll(child)
		if found != null:
			return found
	return null
