extends SceneTree

var failures: Array[String] = []
var late_alternative: Dictionary

func _initialize() -> void:
	call_deferred("_run")

func _run() -> void:
	for index in [31,39,40,44,49]:
		var level := LevelCatalog.get_level(index)
		var state := GameRules.create_state(level)
		GameRules.find_hint(level,state)
		# Leave the known optimal route, then require a legal, solvable continuation.
		var route: Dictionary = HintSearch._routes[String(level.id)]
		var alternative := {}
		for action in level.solution:
			for direction in ["U","R","D","L","X"]:
				var result := GameRules.try_action(level,state,direction)
				if result.accepted and result.state.status == "playing" and not route.has(GameRules._state_key(result.state)):
					alternative = result.state
					break
			if not alternative.is_empty():
				break
			state = GameRules.try_action(level,state,action).state
		_check(not alternative.is_empty(),"no off-route case for L%d" % (index+1))
		if alternative.is_empty():
			continue
		if index == 49:
			late_alternative = alternative.duplicate(true)
		var started := Time.get_ticks_msec()
		var hint := GameRules.find_hint(level,alternative)
		var duration := Time.get_ticks_msec()-started
		_check(not hint.is_empty(),"off-route search found no continuation in L%d" % (index+1))
		if not hint.is_empty():
			_check(GameRules.try_action(level,alternative,hint).accepted,"off-route hint is invalid")
		print("OFF-ROUTE L%02d: %s in %d ms" % [index+1,hint,duration])
	# A canonical route match must respect the steps already consumed.
	var level := LevelCatalog.get_level(0)
	var exhausted := GameRules.create_state(level)
	exhausted.used = int(level.move_limit)-1
	_check(GameRules.find_hint(level,exhausted).is_empty(),"cached route ignored remaining budget")
	# Compare uncached A* with exhaustive BFS for the smaller mechanism course.
	for index in [6,9,11,16,21,28,30]:
		level = LevelCatalog.get_level(index)
		HintSearch._routes[String(level.id)] = {}
		var state := GameRules.create_state(level)
		for step in range(int(level.par)):
			var hint := GameRules.find_hint(level,state)
			if hint.is_empty():
				_check(false,"uncached solver stopped in L%d" % (index+1))
				break
			state = GameRules.try_action(level,state,hint).state
		_check(state.status == "won" and state.used == level.par,"uncached route missed verified optimum")
	await _test_background_hint()
	if failures.is_empty():
		print("PASS: off-route late-map search, budget-aware cache and uncached optimal mechanism routes")
		quit(0)
	else:
		for failure in failures:
			push_error(failure)
		quit(1)

func _check(condition: bool,message: String) -> void:
	if not condition:
		failures.append(message)

func _test_background_hint() -> void:
	var path := "user://hint_test_%d.cfg" % OS.get_process_id()
	var game = load("res://main.tscn").instantiate()
	game.tutorials_enabled = false
	game.progress_path = path
	root.add_child(game)
	game.set_process(false)
	game.unlocked = 49
	game._select_level(49)
	_settle(game)
	game.state = late_alternative.duplicate(true)
	game._refresh()
	# Remove the newly cached continuation to exercise a real background search.
	HintSearch._routes[String(game.level.id)].erase(GameRules._state_key(game.state))
	var started := Time.get_ticks_msec()
	game._hint()
	_check(Time.get_ticks_msec()-started < 100,"hint search blocked the interface")
	_check(game._hint_task >= 0,"hint was not dispatched")
	game._toggle_pause()
	_check(game.paused,"pause did not respond while a hint was computing")
	game._toggle_pause()
	game._select_level(0)
	_settle(game)
	while game._hint_task >= 0 and Time.get_ticks_msec()-started < 60000:
		game._poll_hint()
		await process_frame
	_check(game._hint_task < 0 and game.hint_action.is_empty() and not game.state.assisted,"stale background result changed another level")
	game._hint()
	while game._hint_task >= 0:
		game._poll_hint()
		await process_frame
	_check(game.hint_action == "R" and game.state.assisted,"background result failed to highlight the next action")
	game.queue_free()
	await process_frame
	DirAccess.remove_absolute(ProjectSettings.globalize_path(path))

func _settle(game: Control) -> void:
	game.board_view.set_process(false)
	for i in range(64):
		if not game.board_view.is_animating():
			break
		game.board_view._process(0.25)
