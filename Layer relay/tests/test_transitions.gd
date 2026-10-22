extends SceneTree

var failures: Array[String] = []
var test_path := "user://transition_test_%d.cfg" % OS.get_process_id()

func _initialize() -> void:
	# Isolated mechanism fixtures; these examples are not in the playable campaign.
	LevelCatalog.LEVELS.assign(MechanicFixtures.LEVELS.duplicate(true))
	call_deferred("_run")

func _run() -> void:
	var level := LevelCatalog.get_level(0)
	var initial := GameRules.create_state(level)
	var view := BoardView.new()
	root.add_child(view)
	view.set_process(false)
	view.set_context(level, initial, 0, "")
	view._process(view._generation_duration - 0.10)
	_check(view._generation_active and view._player_spawn_amount() == 0 and not view._player_spawn_active, "player was visible before the final tile formed")
	view.play_action(level, initial, GameRules.try_action(level, initial, "R").state, "R", "")
	_check(not view.busy and view.state.pos == initial.pos, "movement bypassed tile generation")
	view._process(0.10 + 0.00001)
	_check(not view._generation_active and view._player_spawn_active and view._player_spawn_amount() < 0.001, "tile generation did not lead into a separate invisible-to-visible player entrance")
	view._process(BoardView.PLAYER_SPAWN_DURATION * 0.5)
	_check(_between(view._player_spawn_amount()) and view.is_animating() and view._action_highlights(0).is_empty(), "player entrance was abrupt or allowed movement hints")
	view.paused = true
	var paused_spawn := view._player_spawn_amount()
	view._process(5.0)
	_check(view._player_spawn_amount() == paused_spawn, "pause did not freeze player entrance")
	view.paused = false
	view._process(BoardView.PLAYER_SPAWN_DURATION * 0.5 + 0.01)
	_check(not view.is_animating() and view._player_spawn_amount() == 1.0, "player entrance did not end at normal opacity and unlock movement")

	var at_switch: Dictionary = GameRules.try_action(level, initial, "R").state
	view.play_action(level, initial, at_switch, "R", "")
	view._process(0.41)
	_check(view._switch_match_amount(1) == 0, "switch faded before landing rebound")
	view._process(0.20)
	_check(view.state.bits == 1 and view._switch_match_amount(1) == 0, "switch jumped directly to its matched appearance")
	var unlit_fill := view._tile_fill(0, 1, 1, {})
	view._process(BoardView.STATUS_FADE_DURATION * 0.5)
	var intermediate_fill := view._tile_fill(0, 1, 1, {})
	_check(_between(view._switch_match_amount(1)) and not intermediate_fill.is_equal_approx(unlit_fill) and not intermediate_fill.is_equal_approx(Color("a6e6cf")), "switch floor lacked an intermediate blended color")
	view.paused = true
	var paused_match := view._switch_match_amount(1)
	view._process(3.0)
	_check(view._switch_match_amount(1) == paused_match, "pause did not freeze switch fading")
	view.paused = false
	view._process(BoardView.STATUS_FADE_DURATION * 0.5 + 0.01)
	_check(not view.busy and view._switch_match_amount(1) == 1.0, "switch did not finish its fade to matched")

	# Repeat the switch through real moves so losing the goal match fades in reverse.
	var away: Dictionary = GameRules.try_action(level, at_switch, "L").state
	view.play_action(level, at_switch, away, "L", "")
	view._process(0.61)
	var unmatched: Dictionary = GameRules.try_action(level, away, "R").state
	view.play_action(level, away, unmatched, "R", "")
	view._process(0.61)
	_check(view.state.bits == 0 and view._switch_match_amount(1) == 1, "switch became unmatched without preserving its first fade frame")
	view._process(BoardView.STATUS_FADE_DURATION * 0.5)
	_check(_between(view._switch_match_amount(1)), "losing the goal match did not fade")
	view._process(BoardView.STATUS_FADE_DURATION * 0.5 + 0.01)
	_check(view._switch_match_amount(1) == 0 and not view.is_animating(), "unmatched switch retained a check or animation lock")

	# Context changes from undo/restart use the same fade and can reverse continuously.
	view.set_context(level, at_switch, 0, "")
	view._process(BoardView.STATUS_FADE_DURATION * 0.5)
	var partial := view._switch_match_amount(1)
	view.set_context(level, at_switch, 0, "")
	_check(view._switch_match_amount(1) == partial, "HUD refresh restarted the fade")
	view.set_context(level, initial, 0, "")
	_check(is_equal_approx(view._switch_match_amount(1), partial), "reversing a state update caused a visual jump")
	view._process(BoardView.STATUS_FADE_DURATION + 0.01)
	_check(view._switch_match_amount(1) == 0, "reverse fade did not settle to the restored state")

	level = LevelCatalog.get_level(1)
	var before := GameRules.create_state(level)
	before.pos = [1, 0, 1]
	before.bits = 1
	before.key_owned = true
	before.used = 5
	view.set_context(level, before, 1, "")
	view._process(view._generation_duration + BoardView.PLAYER_SPAWN_DURATION + 0.01)
	var lit: Dictionary = GameRules.try_action(level, before, "R").state
	view.play_action(level, before, lit, "R", "")
	view._process(0.41)
	_check(view._beacon_light_amount(0) == 0, "beacon lit while landing")
	view._process(0.20)
	_check(view.state.beacon_index == 1 and view._beacon_light_amount(0) == 0, "beacon switched color instead of fading")
	view._process(BoardView.STATUS_FADE_DURATION * 0.5)
	_check(_between(view._beacon_light_amount(0)), "beacon had no partially lit frame")
	view._process(BoardView.STATUS_FADE_DURATION * 0.5 + 0.01)
	_check(view._beacon_light_amount(0) == 1 and not view.busy, "beacon never reached full brightness")

	# Exceeding the step limit after a lit beacon extinguishes it only after travel.
	before = lit.duplicate(true)
	before.used = int(level.move_limit) - 1
	view.set_context(level, before, 1, "")
	var failure: Dictionary = GameRules.try_action(level, before, "R").state
	_check(failure.status == "failed" and failure.beacon_index == 0, "failed action did not reset the lit beacons")
	view.play_action(level, before, failure, "R", "")
	view._process(0.41)
	_check(view._beacon_light_amount(0) == 1, "failed-action beacon extinguished before landing")
	view._process(0.20)
	_check(view._beacon_light_amount(0) == 1, "failed-action beacon did not preserve its initial brightness")
	view._process(BoardView.STATUS_FADE_DURATION * 0.5)
	_check(_between(view._beacon_light_amount(0)), "failed-action beacon did not fade out gradually")
	view._process(BoardView.STATUS_FADE_DURATION * 0.5 + 0.01)
	_check(view._beacon_light_amount(0) == 0 and not view.busy, "failed-action beacon did not become fully unlit")
	view.set_context(level, before, 1, "")
	view._process(BoardView.STATUS_FADE_DURATION * 0.5)
	_check(_between(view._beacon_light_amount(0)), "undo did not smoothly relight the beacon")
	view._process(BoardView.STATUS_FADE_DURATION * 0.5 + 0.01)
	_check(view._beacon_light_amount(0) == 1, "undo failed to restore the lit beacon")
	# Order failure after a previous beacon also resets its illumination.
	level.beacons = [[1, 1, 1], [1, 0, 1], [1, 2, 1]]
	before.used = 6
	failure = GameRules.try_action(level, before, "R").state
	_check(failure.status == "failed" and failure.beacon_index == 0, "wrong beacon order left earlier beacons lit")
	view.queue_free()
	await _test_game_entrance()
	if failures.is_empty():
		print("PASS: tiles-before-player entrance, paused intro and clock, delayed two-way switch/beacon fades, failure extinction and smooth undo/reversal")
		quit(0)
	else:
		for failure_message in failures:
			push_error(failure_message)
		quit(1)

func _test_game_entrance() -> void:
	var game: Variant = load("res://main.tscn").instantiate()
	game.tutorials_enabled = false
	game.progress_path = test_path
	root.add_child(game)
	await process_frame
	game.set_process(false)
	game._select_level(0)
	game.board_view.set_process(false)
	game.board_view._process(game.board_view._generation_duration)
	game._process(10.0)
	game._act("R")
	_check(game.elapsed_seconds == 0 and game.state.used == 0, "entrance allowed movement or counted against the time star")
	game.board_view._process(BoardView.PLAYER_SPAWN_DURATION + 0.01)
	game._process(2.0)
	_check(game.elapsed_seconds == 2.0, "clock did not start after the entrance")
	game._act("R")
	game.board_view._process(0.61)
	game.board_view._process(BoardView.STATUS_FADE_DURATION + 0.01)
	game._restart()
	_check(game.board_view._player_spawn_active and game.board_view._player_spawn_amount() == 0 and game.state.pos == game.level.start, "restart did not reset the player entrance and position")
	game._process(5.0)
	_check(game.elapsed_seconds == 0, "restart entrance counted against the clock")
	game.queue_free()
	await process_frame
	DirAccess.remove_absolute(ProjectSettings.globalize_path(test_path))

func _between(value: float) -> bool:
	return value > 0.0 and value < 1.0

func _check(condition: bool, message: String) -> void:
	if not condition:
		failures.append(message)
