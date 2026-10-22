extends SceneTree

var failures: Array[String] = []
var game: Variant
var test_path := "user://campaign_test_%d.cfg" % OS.get_process_id()

func _initialize() -> void:
	call_deferred("_run")

func _run() -> void:
	_check(LevelCatalog.LEVELS.size() == 50 and LevelCatalog.available_count() == 50, "campaign count/numbering is incorrect")
	for index in range(LevelCatalog.LEVELS.size()):
		if not LevelCatalog.is_available(index):
			_check(false, "unexpected missing level")
			continue
		var level := LevelCatalog.get_level(index)
		var state := GameRules.create_state(level)
		var original := state.duplicate(true)
		for action in level.solution:
			var before := state.duplicate(true)
			var result := GameRules.try_action(level,state,action)
			_check(state == before, "rule mutated its input in level %d" % (index+1))
			if not result.accepted:
				_check(false,"level %d rejected authored solution: %s" % [index+1,action])
				break
			state = result.state
		_check(state.status == "won" and int(state.used) == int(level.par),"level %d solution/par failed" % (index+1))
		_check(index >= 31 or _shortest(level) == int(level.par),"level %d par is not the shortest Godot route" % (index+1))
		_check(not GameRules.find_hint(level,original).is_empty(),"level %d has no runtime hint" % (index+1))
		_check(ScoreRules.evaluate(level,state,0).stars == 3,"level %d optimal route did not earn three stars" % (index+1))
		if index < 6:
			_check(level.bit_count == 0 and level.items.is_empty() and level.switches.is_empty() and level.gates.is_empty() and level.currents.is_empty() and level.moving_rows.is_empty(),"early tutorial introduced a later mechanism")
		if index in range(6,12):
			_check(level.bit_count > 0 and not level.switches.is_empty() and level.items.is_empty() and level.currents.is_empty() and level.moving_rows.is_empty(),"switch course has wrong mechanisms")
		if index in range(12,18):
			_check(state.opened_gates.size() == level.sealed_gates.size() and state.opened_gates.size() > 0,"key route bypassed a required door")
			_check(level.switches.is_empty() and level.currents.is_empty() and level.moving_rows.is_empty(),"key course was not independent")
		if index in range(18,24):
			_check(not level.currents.is_empty() and state.anchor_charges == 0 and not state.collected.is_empty(),"current course did not require spending its anchors")
		if index in range(24,30):
			_check(not level.moving_rows.is_empty() and level.currents.is_empty() and level.items.is_empty() and level.switches.is_empty(),"platform course contains currents or another primary mechanism")
		if index >= 30:
			_check(not level.switches.is_empty() and not level.sealed_gates.is_empty() and not level.currents.is_empty() and not level.moving_rows.is_empty(),"combined course omitted a mechanism")
			_check(state.opened_gates.size() == level.sealed_gates.size() and state.anchor_charges == 0,"late route bypassed a required lock/current")
			for item in level.get("required_items",[]):
				_check(item in state.collected,"late route bypassed a required resource")
		_check(not level.has("hazards") and not bool(level.get("verification",false)),"removed hazard/trial mode remains")
		_check(bool(level.get("challenge",false)) == (index >= 40),"challenge classification is incorrect")
		if index >= 40:
			_check(level.width >= 9 and level.height >= 9 and level.branch_count >= 3 and level.par >= 80,"challenge lacks size/branches/planning")
		print("VERIFIED L%02d · shortest %d / budget %d" % [index+1,level.par,level.move_limit])
	_test_budget()
	await _test_ui()
	await _test_layout()
	await _test_save_migration()
	if failures.is_empty():
		print("PASS: 50 engine routes, early shortest paths, required late resources, staged mechanisms, hints, undo/layer sync, budget failure/retry, sequential unlock and save migration")
		quit(0)
	else:
		for failure in failures:
			push_error(failure)
		quit(1)

func _shortest(level: Dictionary) -> int:
	var queue: Array[Dictionary] = [GameRules.create_state(level)]
	var seen := {}
	var head := 0
	while head < queue.size():
		var state := queue[head]
		head += 1
		if state.status == "won":
			return int(state.used)
		for action in ["U","R","D","L","X"]:
			var result := GameRules.try_action(level,state,action)
			if not result.accepted or result.state.status == "failed":
				continue
			var key := GameRules._state_key(result.state)
			if not seen.has(key):
				seen[key] = true
				queue.append(result.state)
	return -1

func _test_budget() -> void:
	var state: Dictionary
	var last_step := LevelCatalog.get_level(0)
	last_step.move_limit = last_step.par
	state = GameRules.create_state(last_step)
	for action in last_step.solution:
		state = GameRules.try_action(last_step,state,action).state
	_check(state.status == "won","winning on the final allowed step was treated as failure")
	# Re-entering an already opened lock must not consume a newly collected key.
	var key_level := LevelCatalog.get_level(12)
	state = GameRules.create_state(key_level)
	state.pos = [0,3,1]
	state.opened_gates = ["lock_0"]
	state.key_owned = true
	GameRules._open_key_gate(key_level,state)
	_check(state.key_owned,"open lock consumed a second key")

func _test_ui() -> void:
	root.size = Vector2i(1360,860)
	game = load("res://main.tscn").instantiate()
	game.tutorials_enabled = false
	game.progress_path = test_path
	root.add_child(game)
	await process_frame
	game.set_process(false)
	game._show_menu("levels")
	_check(game.menu_screen.level_cards[30].disabled and game.menu_screen.level_cards[40].disabled and game.menu_screen.level_cards[49].disabled,"late levels bypassed sequential locks")
	game._select_level(0)
	_settle()
	game._act("R")
	_settle()
	game._act("X")
	_settle()
	game._undo()
	_check(game.state.pos[0] == 0 and game.selected_layer == 0 and game.board_view.selected_layer == 0 and game.board_view.state.pos == game.state.pos,"undo after ascent left player in thumbnail")
	_settle()
	game._on_preview_pressed(1)
	_settle()
	game._undo()
	_check(game.selected_layer == int(game.state.pos[0]) and game.board_view.selected_layer == int(game.state.pos[0]),"undo did not follow player after manual preview")
	game.unlocked = 49
	game._select_level(2)
	_settle()
	for action in ["R","X","R","R","X"]:
		game._act(action)
		_settle()
	game._undo()
	_check(game.state.pos[0] == 1 and game.selected_layer == 1 and game.board_view.selected_layer == 1,"undo after descent left player in lower main view")
	game._select_level(0)
	_settle()
	for i in range(int(game.level.move_limit)-1):
		game._act("R" if i % 2 == 0 else "L")
		_settle()
	game._act("R")
	var board: BoardView = game.board_view
	_check(game.failure_stage == "waiting" and game.failure_screen == null,"failure choices appeared before final movement")
	board._process(0.41)
	_check(game.failure_stage == "waiting","failure effect interrupted landing")
	board._process(0.21)
	_check(game.failure_stage == "animating" and board._failure_active and game.failure_screen == null,"failure animation did not start after action")
	board._process(0.55)
	_check(game.failure_screen == null,"failure choices skipped animation")
	board._process(0.61)
	_check(game.failure_stage == "choices" and game.failure_screen != null,"failed round did not show retry/selector")
	await _click(game.failure_screen.replay_button)
	_settle()
	_check(game.state.used == 0 and game.state.status == "playing" and game.selected_layer == int(game.level.start[0]),"failure retry retained position, moves or overlay")
	# Budget failure keeps both retry and selector routes available.
	game.level.move_limit = 1
	game._act("R")
	_settle()
	await _click(game.failure_screen.levels_button)
	_check(game.current_screen == "menu" and game.menu_screen.page == "levels","failure selector button failed")
	game._select_level(0)
	_settle()
	game.level.move_limit = 1
	game._act("R")
	_settle()
	var retry := InputEventKey.new()
	retry.keycode = KEY_R
	retry.pressed = true
	Input.parse_input_event(retry)
	await process_frame
	_settle()
	_check(game.state.used == 0 and game.failure_stage == "","failure keyboard retry did not reset the round")
	game.best_stars.fill(0)
	for index in [30,39,49]:
		game.unlocked = index
		game._select_level(index)
		_settle()
		for action in game.level.solution:
			game._act(action)
			_settle()
		_check(game.state.status == "won","late level did not complete through animated UI")
		_check(game.unlocked == mini(index+1,49),"late campaign unlock skipped a level")
		_check(game.completion_screen.next_available == (index < 49),"final/next choice is wrong")
		if index < 49:
			game.completion_screen.next_requested.emit()
			_settle()
			_check(game.level_index == index+1,"Next did not enter the following contiguous level")
	game.queue_free()
	await process_frame
	DirAccess.remove_absolute(ProjectSettings.globalize_path(test_path))

func _test_layout() -> void:
	game = load("res://main.tscn").instantiate()
	game.tutorials_enabled = false
	game.progress_path = test_path
	root.add_child(game)
	game.set_process(false)
	game.unlocked = 49
	for window_size in [Vector2i(1360,860),Vector2i(1080,720)]:
		root.content_scale_size = window_size
		root.size = window_size
		for index in range(LevelCatalog.LEVELS.size()):
			if not LevelCatalog.is_available(index):
				continue
			game._select_level(index)
			_settle()
			await process_frame
			var view: BoardView = game.board_view
			var objective := Rect2(game.objective_panel.position,game.objective_panel.size)
			for layer in range(2):
				view._configure_board(layer,view._main_grid_area(),1,false,false)
				for y in range(int(game.level.height)):
					for x in range(int(game.level.width)):
						var pos := [layer,x,y]
						if String(game.level.floors[layer][y]).substr(x,1) != "." and GameRules._moving_row_at_position(game.level,pos,0).is_empty():
							continue
						var center := view._cell_center(pos)
						var tile := Rect2(center-Vector2(view._tile_w/2,view._tile_h/2),Vector2(view._tile_w,view._tile_h+10))
						var actor := Rect2(center-Vector2(12,52),Vector2(24,54))
						_check(not objective.intersects(tile) and not objective.intersects(actor),"L%d objective covers tile/player at %s" % [index+1,str(window_size)])
						_check(not view._preview_bounds().intersects(actor),"L%d preview covers player at %s" % [index+1,str(window_size)])
						_check(tile.end.y <= game.inventory_bar.position.y,"L%d inventory covers board at %s" % [index+1,str(window_size)])
	game.queue_free()
	await process_frame
	DirAccess.remove_absolute(ProjectSettings.globalize_path(test_path))

func _test_save_migration() -> void:
	var old := ConfigFile.new()
	old.set_value("progress","stars",[3,3,3,3])
	old.set_value("progress","unlocked",3)
	old.save(test_path)
	game = load("res://main.tscn").instantiate()
	game.tutorials_enabled = false
	game.progress_path = test_path
	root.add_child(game)
	_check(game.unlocked == 0 and game.best_stars.size() == 50 and game.best_stars.max() == 0,"old example progress leaked into the new campaign")
	var backup := test_path.get_basename()+"_before_campaign.cfg"
	_check(FileAccess.file_exists(backup),"old example save was not backed up")
	game._select_level(0)
	_settle()
	game.queue_free()
	await process_frame
	game = load("res://main.tscn").instantiate()
	game.tutorials_enabled = false
	game.progress_path = test_path
	root.add_child(game)
	_check(game.has_play_history and game.best_stars.size() == 50,"new campaign save did not survive restart")
	game.queue_free()
	await process_frame
	# Version 3 had unchanged 1-31 plus a different trial at 41.
	old = ConfigFile.new()
	old.set_value("progress","campaign_version",3)
	old.set_value("progress","scoring_version",2)
	old.set_value("progress","unlocked",40)
	var old_stars: Array = []
	old_stars.resize(41)
	old_stars.fill(3)
	old.set_value("progress","stars",old_stars)
	old.set_value("progress","last_played",40)
	old.save(test_path)
	game = load("res://main.tscn").instantiate()
	game.tutorials_enabled = false
	game.progress_path = test_path
	root.add_child(game)
	_check(game.unlocked == 31 and game.best_stars[30] == 3 and game.best_stars[40] == 0 and game.saved_run.is_empty(),"version 3 migration lost early stars or reused changed trial progress")
	_check(game.best_stars.slice(31).max() == 0,"new maps inherited obsolete stars")
	game._save_progress()
	game.queue_free()
	await process_frame
	DirAccess.remove_absolute(ProjectSettings.globalize_path(test_path.get_basename()+"_before_expansion.cfg"))
	DirAccess.remove_absolute(ProjectSettings.globalize_path(test_path))
	DirAccess.remove_absolute(ProjectSettings.globalize_path(backup))

func _settle() -> void:
	game.board_view.set_process(false)
	for i in range(64):
		if not game.board_view.is_animating():
			break
		game.board_view._process(0.25)

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

func _check(condition: bool, message: String) -> void:
	if not condition:
		failures.append(message)
