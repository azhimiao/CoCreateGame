extends SceneTree

var test_path := "user://layer_relay_visual_%d.cfg" % OS.get_process_id()

# Generates engine-rendered review frames without changing the local progress save.
func _initialize() -> void:
	LevelCatalog.LEVELS.assign(MechanicFixtures.LEVELS.duplicate(true))
	call_deferred("_capture")

func _capture() -> void:
	root.size = Vector2i(1360, 860)
	var game: Variant = load("res://main.tscn").instantiate()
	game.tutorials_enabled = false
	game.progress_path = test_path
	root.add_child(game)
	await process_frame
	game.unlocked = 3
	game._select_level(3)
	await process_frame
	game.board_view._process(game.board_view._generation_duration + BoardView.PLAYER_SPAWN_DURATION + 0.01)
	game.board_view.set_process(false)
	game._clear_notice()
	await process_frame
	await RenderingServer.frame_post_draw
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path("res://runtime/visual-review"))
	root.get_texture().get_image().save_png("res://runtime/visual-review/level-4-layout.png")
	var before: Dictionary = game.state.duplicate(true)
	before.phase = 4
	var result := GameRules.try_action(game.level, before, "D")
	game.state = result.state
	game.board_view.play_action(game.level, before, game.state, "D", "")
	game.board_view._process(0.61)
	game.board_view._process(0.24)
	game._clear_notice()
	await process_frame
	await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_png("res://runtime/visual-review/level-4-wrap-midpoint.png")
	game.board_view._process(0.49)
	game._select_level(1)
	await process_frame
	game.board_view._process(game.board_view._generation_duration + BoardView.PLAYER_SPAWN_DURATION + 0.01)
	game.board_view.set_process(false)
	game.state.key_owned = true
	game.state.anchor_charges = 2
	game._refresh()
	game._clear_notice()
	await process_frame
	await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_png("res://runtime/visual-review/inventory-and-highlights.png")
	DirAccess.remove_absolute(ProjectSettings.globalize_path(test_path))
	print("PASS: engine-rendered review frames saved under runtime/visual-review")
	quit()
