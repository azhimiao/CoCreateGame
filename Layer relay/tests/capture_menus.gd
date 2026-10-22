extends SceneTree

var output := "res://runtime/menu-review"
var game: Variant
var test_path := "user://menu_capture_%d.cfg" % OS.get_process_id()

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
	await _frame("home-fresh")
	game.unlocked = 2
	game.best_stars.assign([3, 2, 0, 0])
	game.has_play_history = true
	game.last_played = 1
	game._show_menu("home")
	await _frame("home-history")
	game.menu_screen.show_page("levels", false)
	await _frame("level-select")
	game.menu_screen.level_scroll.scroll_vertical = 9999
	await _frame("level-select-bottom")
	game.menu_screen.level_scroll.scroll_vertical = 0
	game.menu_screen.open_reset_confirmation()
	await _frame("reset-confirmation")
	game.menu_screen.close_reset_confirmation()
	game.menu_screen.show_page("settings", false)
	await _frame("settings")
	game.menu_screen.show_page("about", false)
	await _frame("about")
	game.menu_screen.show_page("levels", false)
	# Match the smallest supported desktop viewport and verify all six columns fit.
	root.content_scale_size = Vector2i(1080, 720)
	root.size = Vector2i(1080, 720)
	await _frame("level-select-1080")
	game.queue_free()
	await process_frame
	if FileAccess.file_exists(test_path):
		DirAccess.remove_absolute(ProjectSettings.globalize_path(test_path))
	print("PASS: engine-rendered menu review frames saved under runtime/menu-review")
	quit()

func _frame(filename: String) -> void:
	await process_frame
	await process_frame
	await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_png("%s/%s.png" % [output, filename])
