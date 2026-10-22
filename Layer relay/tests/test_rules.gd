extends SceneTree

func _initialize() -> void:
	# Isolated mechanism fixtures; these examples are not in the playable campaign.
	LevelCatalog.LEVELS.assign(MechanicFixtures.LEVELS.duplicate(true))
	var failures: Array[String] = []
	for index in range(LevelCatalog.LEVELS.size()):
		var level: Dictionary = LevelCatalog.get_level(index)
		var state := GameRules.create_state(level)
		for action in level.solution:
			var result := GameRules.try_action(level, state, action)
			if not result.accepted:
				failures.append("%s rejected %s: %s" % [level.id, action, result.message])
				break
			state = result.state
		if state.status != "won":
			failures.append("%s solution ended at %s after %d moves" % [level.id, state.status, state.used])
		if index == 1 and (bool(state.key_owned) or not state.opened_gates.has("opal")):
			failures.append("L02 did not consume the key and open the gate")
		if index == 2 and (int(state.anchor_charges) != 0 or not state.collected.has("anchor_shard")):
			failures.append("L03 did not collect and spend the phase anchor")
		var hint := GameRules.find_hint(level, GameRules.create_state(level))
		if hint.is_empty():
			failures.append("%s has no solver hint" % level.id)

	var level_one := LevelCatalog.get_level(0)
	var initial := GameRules.create_state(level_one)
	var invalid := GameRules.try_action(level_one, initial, "L")
	if invalid.accepted or int(initial.used) != 0:
		failures.append("invalid movement changed state")

	var level_two := LevelCatalog.get_level(1)
	var wrong_order := GameRules.create_state(level_two)
	wrong_order.pos = [1, 2, 1]
	if GameRules._advance_beacon(level_two, wrong_order).ok:
		failures.append("out-of-order beacon was not rejected")
	var delayed := GameRules.create_state(level_two)
	for action in ["R", "R", "L", "L", "X", "R"]:
		var step: Dictionary = GameRules.try_action(level_two, delayed, action)
		if not step.accepted:
			failures.append("delayed switch setup rejected %s: %s" % [action, step.message])
			break
		delayed = step.state
	if int(delayed.pending) != 2 or int(delayed.bits) != 1:
		failures.append("ion-layer switch did not defer its bit")
	var apply_pending: Dictionary = GameRules.try_action(level_two, delayed, "R")
	if not apply_pending.accepted:
		failures.append("delayed switch landing rejected: %s" % apply_pending.message)
	else:
		delayed = apply_pending.state
	if int(delayed.pending) != 0 or int(delayed.bits) != 3:
		failures.append("queued bit was not applied on the following landing")

	var level_three := LevelCatalog.get_level(2)
	var against_flow := GameRules.create_state(level_three)
	against_flow.pos = [1, 2, 1]
	var blocked := GameRules.try_action(level_three, against_flow, "L")
	if blocked.accepted:
		failures.append("flow allowed reverse movement without an anchor")
	against_flow.anchor_charges = 1
	var anchored_reverse := GameRules.try_action(level_three, against_flow, "L")
	if not anchored_reverse.accepted or int(anchored_reverse.state.anchor_charges) != 0:
		failures.append("phase anchor did not authorize one reverse move")

	var level_four := LevelCatalog.get_level(3)
	var rail_state := GameRules.create_state(level_four)
	var ride := GameRules.try_action(level_four, rail_state, "D")
	if not ride.accepted or ride.state.pos != [0, 1, 1] or int(ride.state.phase) != 1:
		failures.append("upper moving row did not carry the player and advance phase")
	else:
		var invalid_rail_move := GameRules.try_action(level_four, ride.state, "U")
		if invalid_rail_move.accepted or int(ride.state.phase) != 1:
			failures.append("invalid move changed moving-row phase")

	if failures.is_empty():
		print("PASS: 4 level routes, BFS hints, invalid move, beacon order, delayed switch, current lock, and moving rows")
		quit(0)
	else:
		for failure in failures:
			push_error(failure)
		quit(1)
