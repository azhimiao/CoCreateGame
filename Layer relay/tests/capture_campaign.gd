extends SceneTree

var game: Variant
var output := "res://runtime/campaign-review"
var test_path := "user://campaign_capture_%d.cfg" % OS.get_process_id()

func _initialize() -> void:
	call_deferred("_capture")

func _capture() -> void:
	root.size = Vector2i(1360,860)
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(output))
	game = load("res://main.tscn").instantiate()
	game.tutorials_enabled = false
	game.progress_path = test_path
	root.add_child(game)
	game.set_process(false)
	game.unlocked = 49
	for index in range(LevelCatalog.LEVELS.size()):
		if not LevelCatalog.is_available(index):
			continue
		game._select_level(index)
		_settle()
		game._clear_notice()
		await _frame("L%02d-start" % (index+1))
		game._on_preview_pressed(1)
		_settle()
		await _frame("L%02d-upper" % (index+1))
	game._show_menu("levels")
	await create_timer(0.3).timeout
	await _frame("selector-top")
	game.menu_screen.level_scroll.scroll_vertical = 520
	await _frame("selector-platforms")
	game.menu_screen.level_scroll.scroll_vertical = 790
	await _frame("selector-challenges")
	game._select_level(0)
	_settle()
	game._act("R")
	_settle()
	game._act("X")
	_settle()
	game._undo()
	_settle()
	game._clear_notice()
	await _frame("undo-main-layer-restored")
	game._select_level(0)
	_settle()
	game.level.move_limit = 1
	game._act("R")
	game.board_view._process(0.61)
	game.board_view._process(0.29)
	game.board_view._process(0.45)
	await _frame("budget-failure-animation")
	_settle()
	await create_timer(0.4).timeout
	await _frame("budget-failure-choices")
	root.content_scale_size = Vector2i(1080,720)
	root.size = Vector2i(1080,720)
	await _frame("failure-1080")
	game._select_level(29)
	_settle()
	game._clear_notice()
	await _frame("platforms-1080")
	for index in [31,39,40,44,49]:
		game._select_level(index)
		_settle()
		game._clear_notice()
		await _frame("L%02d-start-1080" % (index+1))
		game._on_preview_pressed(1)
		_settle()
		await _frame("L%02d-upper-1080" % (index+1))
	game.queue_free()
	await process_frame
	DirAccess.remove_absolute(ProjectSettings.globalize_path(test_path))
	print("PASS: campaign engine frames saved under runtime/campaign-review")
	quit()

func _settle() -> void:
	game.board_view.set_process(false)
	for i in range(64):
		if not game.board_view.is_animating():
			break
		game.board_view._process(0.25)

func _frame(filename: String) -> void:
	await process_frame
	await process_frame
	await RenderingServer.frame_post_draw
	var error := root.get_texture().get_image().save_png(output+"/"+filename+".png")
	assert(error == OK)
