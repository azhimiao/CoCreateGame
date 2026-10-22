extends SceneTree

var game: Variant
var failures: Array[String] = []
var test_path := "user://tutorial_test_%d.cfg" % OS.get_process_id()
var capture := false

func _initialize() -> void:
	capture = "--capture" in OS.get_cmdline_user_args()
	call_deferred("_run")

func _run() -> void:
	root.size = Vector2i(1360,860)
	game = load("res://main.tscn").instantiate()
	game.progress_path = test_path
	root.add_child(game)
	game.set_process(false)
	game.unlocked = 49
	game._select_level(0)
	game.board_view.set_process(false)
	game._process(10)
	_check(game.tutorial_coach == null and game.elapsed_seconds == 0,"guide started before the board formed")
	game.board_view._process(game.board_view._generation_duration)
	game._process(10)
	_check(game.tutorial_coach == null and game.board_view._player_spawn_active,"guide covered the player's entrance")
	_settle()
	game._process(0)
	await _frames()
	_check(game.tutorial_coach != null and game.tutorial_coach.step_count == 7,"level 1 lacks the seven interface cards")
	_check(game.tutorial_coach.previous_button.disabled,"first step has an active previous button")
	var before: Dictionary = game.state.duplicate(true)
	game._process(120)
	game._act("R")
	game._press_cell(0,1,0)
	game._on_preview_pressed(1)
	game._hint()
	game._restart()
	game._undo()
	game._toggle_pause()
	_check(game.state == before and game.elapsed_seconds == 0 and not game.paused,"tutorial allowed gameplay, assistance, preview or clock advancement")
	await _snapshot("01-board")
	await _click(game.tutorial_coach.next_button)
	_check(game.tutorial_step_index == 1,"mouse click did not advance the tutorial")
	await _snapshot("02-objective")
	await _click(game.tutorial_coach.previous_button)
	_check(game.tutorial_step_index == 0,"mouse click did not return to the previous step")
	for index in range(7):
		_check(game.tutorial_step_index == index,"interface steps skipped or advanced automatically")
		await _check_layout()
		await _snapshot("ui-step-%d" % index)
		game.tutorial_coach.next_button.pressed.emit()
	_check(game.tutorial_coach == null and not game.board_view.paused,"finishing the guide did not restore gameplay")
	_check("campaign_ui" in game.tutorial_seen,"completed interface guide was not remembered")
	game._process(2)
	_check(game.elapsed_seconds == 2,"clock did not resume after the tutorial")
	game._select_level(0)
	_settle()
	game._process(0)
	_check(game.tutorial_coach == null,"completed guide repeated on replay")
	_check(not _contains_old_guide(game),"removed sidebar guide is still visible")
	# Every lift must connect supported terrain at the same coordinates on both layers.
	for number in range(LevelCatalog.LEVELS.size()):
		if not LevelCatalog.is_available(number):
			continue
		var level := LevelCatalog.get_level(number)
		for event in level.tutorial_events:
			_check(event.steps.size() >= 2,"L%02d still contains a one-page mechanism tutorial" % (number+1))
		for lift in level.lifts:
			for layer in [0,1]:
				_check(String(level.floors[layer][int(lift[1])]).substr(int(lift[0]),1) == ".","L%02d has a lift without support on layer %d" % [number+1,layer])
	# Visit the natural first appearances and verify every highlighted tile/layer.
	for index in [6,7,8,9,10,11,12,18,24,27,30,40]:
		game._select_level(index)
		_settle()
		game._process(0)
		_check(game.tutorial_coach != null,"new mechanism lacks a bubble in L%02d" % (index+1))
		while game.tutorial_coach != null:
			var step: Dictionary = game._current_tutorial_step()
			if step.target == "cell":
				_check(game.selected_layer == int(step.at[0]) and game.board_view.selected_layer == int(step.at[0]),"bubble highlighted the wrong layer")
			await _check_layout()
			await _snapshot("L%02d-%s-%d" % [index+1,game.tutorial_batches[game.tutorial_batch_index].id,game.tutorial_step_index])
			game.tutorial_coach.next_button.pressed.emit()
		_check(game.selected_layer == int(game.state.pos[0]) and game.board_view.selected_layer == int(game.state.pos[0]),"finishing a mechanism guide left the player in the preview")
	# Restarting the app retains completed introductions without losing normal progress.
	var expected: Array = game.tutorial_seen.duplicate()
	game.queue_free()
	await process_frame
	game = load("res://main.tscn").instantiate()
	game.progress_path = test_path
	root.add_child(game)
	game.set_process(false)
	_check(game.tutorial_seen == expected,"seen guides were lost on reload")
	game._reset_progress()
	_check(game.tutorial_seen.is_empty(),"reset did not restore first-time introductions")
	game.unlocked = 49
	# Direct trial entry must introduce the four unfamiliar mechanisms too.
	game._select_level(30)
	_settle()
	game._process(0)
	var ids: Array = game.tutorial_batches.map(func(batch: Dictionary) -> String: return String(batch.id))
	_check(ids.has("switch_goal") and ids.has("key_lock") and ids.has("current_anchor") and ids.has("moving_platform"),"direct trial omitted unfamiliar mechanisms")
	var total := 0
	for batch in game.tutorial_batches:
		total += batch.steps.size()
	_check(game.tutorial_coach.step_count == total,"page count does not include the full level walkthrough")
	await _click(game.tutorial_coach.next_button)
	_check(game.tutorial_coach.step_index == 1 and not game.tutorial_coach.previous_button.disabled,"second bubble has no working Back button")
	await _click(game.tutorial_coach.next_button)
	_check(game.tutorial_batch_index == 1 and game.tutorial_coach.step_index == 2,"page number reset at the next mechanism")
	await _snapshot("continuous-mechanisms-before-back")
	await _click(game.tutorial_coach.previous_button)
	_check(game.tutorial_batch_index == 0 and game.tutorial_step_index == 1 and game.tutorial_coach.step_index == 1,"Back did not cross the mechanism boundary")
	_check(game.tutorial_seen.is_empty(),"partial navigation marked a mechanism completed before finishing the walkthrough")
	# A long first message must stay inside the screen even after text reflows.
	var first: Dictionary = game.tutorial_batches[0].steps[0]
	var original_copy: String = first.text
	first.text = original_copy.repeat(18)
	game._previous_tutorial_step()
	await _check_layout()
	await _snapshot("long-first-bubble")
	_check(game.tutorial_coach._body_label.get_content_height() > game.tutorial_coach._body_label.size.y,"long guidance did not use the bounded scroll area")
	first.text = original_copy
	game._show_tutorial_step()
	await _frames()
	# Reproduce a parent larger than the visible viewport and inspect the first box.
	game._show_menu("levels")
	game._select_level(0)
	_settle()
	game._process(0)
	root.content_scale_size = Vector2i(1080,720)
	root.size = Vector2i(1080,720)
	game.custom_minimum_size = Vector2(1360,1000)
	await _frames()
	var visible_area: Rect2 = game.tutorial_coach._visible_area()
	_check(visible_area.encloses(game.tutorial_coach.bubble.get_rect()),"first bubble escaped a viewport smaller than its parent")
	_check(visible_area.grow(4).encloses(game.tutorial_coach._focus_bounds()),"first highlight extended below the visible screen")
	await _snapshot("first-bubble-visible-viewport")
	game.custom_minimum_size = Vector2(1080,720)
	game.size = Vector2(1080,720)
	await _frames()
	# Updating the guide reopens its new version while retaining campaign progress.
	var config := ConfigFile.new()
	config.load(test_path)
	config.set_value("progress","unlocked",12)
	config.set_value("progress","tutorial_version",game.TUTORIAL_VERSION-1)
	config.set_value("progress","tutorial_seen",["campaign_ui","switch_goal"])
	config.save(test_path)
	game.queue_free()
	await process_frame
	game = load("res://main.tscn").instantiate()
	game.progress_path = test_path
	root.add_child(game)
	game.set_process(false)
	_check(game.unlocked == 12 and game.tutorial_seen.is_empty(),"guide update lost campaign progress or retained old single-page completion")
	game.queue_free()
	await process_frame
	DirAccess.remove_absolute(ProjectSettings.globalize_path(test_path))
	if failures.is_empty():
		print("PASS: continuous page numbering and mouse Back across mechanisms, paired introductions, first bubble/long text/viewport bounds, tutorial version migration, L5 lifts and previous tutorial regressions")
		quit(0)
	else:
		for failure in failures:
			push_error(failure)
		quit(1)

func _settle() -> void:
	game.board_view.set_process(false)
	for i in range(64):
		if not game.board_view.is_animating():
			break
		game.board_view._process(0.25)

func _frames() -> void:
	await process_frame
	await process_frame
	game._process(0)
	await process_frame

func _check_layout() -> void:
	for viewport_size in [Vector2i(1360,860),Vector2i(1080,720)]:
		root.content_scale_size = viewport_size
		root.size = viewport_size
		await _frames()
		var coach: TutorialCoach = game.tutorial_coach
		var window := Rect2(Vector2.ZERO,Vector2(viewport_size))
		_check(window.encloses(coach.bubble.get_rect()) and window.encloses(coach.focus_rect),"tutorial frame or bubble escaped the viewport")
		_check(not coach.bubble.get_rect().intersects(coach.focus_rect),"bubble obscured its highlighted target")
		_check(coach.focus_rect.size.x > 0 and coach.focus_rect.size.y > 0,"tutorial has an empty focus frame")
		_check(coach.bubble.get_rect().encloses(Rect2(coach.next_button.global_position,coach.next_button.size)),"next button escaped the bubble")
		_check(coach.bubble.get_rect().encloses(Rect2(coach.previous_button.global_position,coach.previous_button.size)),"Back button escaped the bubble")
		if viewport_size.x == 1080:
			await _snapshot("1080-L%02d-%s-%d" % [game.level_index+1,game.tutorial_batches[game.tutorial_batch_index].id,game.tutorial_step_index])
	root.content_scale_size = Vector2i(1360,860)
	root.size = Vector2i(1360,860)
	await _frames()

func _click(button: Button) -> void:
	await _frames()
	var click := InputEventMouseButton.new()
	click.button_index = MOUSE_BUTTON_LEFT
	click.position = button.get_global_rect().get_center()
	click.pressed = true
	Input.parse_input_event(click)
	await process_frame
	click = click.duplicate()
	click.pressed = false
	Input.parse_input_event(click)
	await _frames()

func _snapshot(name: String) -> void:
	if not capture:
		return
	await _frames()
	await RenderingServer.frame_post_draw
	var folder := "res://runtime/tutorial-review"
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(folder))
	_check(root.get_texture().get_image().save_png(folder+"/"+name+".png") == OK,"could not save review frame")

func _contains_old_guide(node: Node) -> bool:
	if node is Label and "本关引导" in node.text:
		return true
	for child in node.get_children():
		if _contains_old_guide(child):
			return true
	return false

func _check(condition: bool, message: String) -> void:
	if not condition:
		failures.append(message)
