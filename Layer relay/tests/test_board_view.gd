extends SceneTree

func _initialize() -> void:
	# Isolated mechanism fixtures; these examples are not in the playable campaign.
	LevelCatalog.LEVELS.assign(MechanicFixtures.LEVELS.duplicate(true))
	call_deferred("_run")

func _run() -> void:
	var failures: Array[String] = []
	var level: Dictionary = LevelCatalog.get_level(0)
	var start := GameRules.create_state(level)
	var step_to_lift: Dictionary = GameRules.try_action(level, start, "R")
	if not step_to_lift.accepted:
		push_error("failed to reach the lift for animation test")
		quit(1)
		return
	var at_lift: Dictionary = step_to_lift.state
	var layer_step: Dictionary = GameRules.try_action(level, at_lift, "X")
	if not layer_step.accepted:
		push_error("lift action was rejected in animation test")
		quit(1)
		return

	var view := BoardView.new()
	root.add_child(view)
	view.size = Vector2(1100, 700)
	view.set_context(level, at_lift, 0, "")
	var final_fill := Color("ecd7a4")
	if view._generation_fill(BoardView.GENERATION_EDGE_DURATION + BoardView.GENERATION_WAVE_DELAY * 3.0, final_fill) != Color.WHITE:
		failures.append("tile did not stay white while three more tile waves spread outward")
	if view._generation_fill(BoardView.GENERATION_EDGE_DURATION + BoardView.GENERATION_WAVE_DELAY * 4.0, final_fill) != Color("a9ddf2"):
		failures.append("white hold did not switch directly to blue by the fourth outward wave")
	if view._generation_fill(BoardView.GENERATION_CELL_DURATION, final_fill) != final_fill:
		failures.append("tile did not finish on its special-cell color")
	if not view.is_animating():
		failures.append("level reveal did not lock input while tiles are forming")
	view._process(view._generation_duration + BoardView.PLAYER_SPAWN_DURATION + 0.01)
	if view.is_animating():
		failures.append("level reveal did not finish after its final tile wave")
	if view._roll_sign("R") != 1.0 or view._roll_sign("D") != 1.0 or view._roll_sign("L") != -1.0 or view._roll_sign("U") != -1.0:
		failures.append("directional roll did not map to the four movement directions")
	view.selected_layer = 1
	view.set_context(level, start, 0, "")
	if view.selected_layer != 0 or view.state.pos != start.pos:
		failures.append("reset context did not synchronize the main layer and player position")
	view.set_context(level, at_lift, 0, "")
	view._hover = Vector2i(2, 1)
	if not view._hover_is_movable(0):
		failures.append("legal jump destination was not recognized for hover feedback")
	view._hover = Vector2i(0, 0)
	if view._hover_is_movable(0):
		failures.append("invalid floor did not reject hover feedback")
	view._hover = Vector2i(2, 1)
	if view._highlight_fill(Color("b9d4e5"), "hover") == view._highlight_fill(Color("b9d4e5"), "jump"):
		failures.append("legal hover did not brighten the tile fill beyond the base move hint")
	var main_rect := view._main_grid_area()
	var mini_rect := view._preview_mini_area()
	var outgoing_mid := view._lerp_rect(main_rect, mini_rect, 0.5)
	var incoming_mid := view._lerp_rect(mini_rect, main_rect, 0.5)
	if outgoing_mid.size.x >= main_rect.size.x or incoming_mid.size.x <= mini_rect.size.x:
		failures.append("layer view transition did not shrink and grow both boards")
	if view._highlight_fill(Color("b9d4e5"), "jump").is_equal_approx(Color("b9d4e5")):
		failures.append("legal destination highlight did not brighten the existing tile fill")
	if view._highlight_fill(Color("b9d4e5"), "jump") == view._highlight_fill(Color("b9d4e5"), "lift"):
		failures.append("jump and lift highlights did not retain different intensities")

	view.play_action(level, at_lift, layer_step.state, "X", "")
	view._process(0.53)
	if not view.busy or view._stage != 1 or view.selected_layer != 0:
		failures.append("layer transition did not enter its cross-layer handoff")
	view._process(0.27)
	if not view.busy or view.selected_layer != 1 or view.state.pos != [1, 1, 1]:
		failures.append("layer transition did not switch the main view during the handoff")
	view._process(0.26)
	if not view.busy or view._stage != 2:
		failures.append("layer transition skipped the destination portal descent")
	view._process(0.73)
	if view.busy or view.selected_layer != 1 or view.state.pos != layer_step.state.pos:
		failures.append("layer transition did not finish on the destination layer")

	var move: Dictionary = GameRules.try_action(level, layer_step.state, "R")
	if not move.accepted:
		failures.append("post-transition movement was rejected")
	else:
		view.play_action(level, layer_step.state, move.state, "R", "")
		view._process(0.41)
		if not view.busy:
			failures.append("landing rebound was skipped at the end of the jump")
		view._process(0.21)
		if view.busy or view.state.pos != move.state.pos:
			failures.append("movement animation did not settle on the rules state")

	view.animate_layer_view(0)
	if not view.is_animating():
		failures.append("manual preview selection did not start a view transition")
	view._process(0.27)
	if view.selected_layer != 0:
		failures.append("manual preview transition did not promote the selected thumbnail")
	view._process(0.27)
	if view.is_animating():
		failures.append("manual preview transition did not finish")
	view.selected_layer = 1
	view.set_context(level, at_lift, 1, "")
	view.animate_layer_view(0)
	view.set_context(level, start, 0, "")
	view.reset_view(0)
	view._process(BoardView.STATUS_FADE_DURATION + 0.01)
	if view.is_animating() or view.state.pos != start.pos or view.selected_layer != 0:
		failures.append("restart while on the other layer left the player or view out of sync")

	var moving_level: Dictionary = LevelCatalog.get_level(3)
	var moving_start := GameRules.create_state(moving_level)
	view.set_context(moving_level, moving_start, 0, "")
	var right_wrap := view._wrapped_row_centers(float(moving_level.width - 1), 1, 0.5)
	var left_wrap := view._wrapped_row_centers(0.0, -1, 0.5)
	if not right_wrap.has(-0.5) or not right_wrap.has(4.5):
		failures.append("right-edge platform wrap did not show matching clipped pieces at both edges")
	if not left_wrap.has(-0.5) or not left_wrap.has(4.5):
		failures.append("left-edge platform wrap did not show matching clipped pieces at both edges")
	var seam_piece := view._clip_row_polygon(PackedVector3Array([
		Vector3(-0.75, 1.0, 0), Vector3(-0.25, 1.0, 0), Vector3(-0.25, 1.0, 12), Vector3(-0.75, 1.0, 12)
	]))
	if seam_piece.is_empty() or not is_equal_approx(seam_piece[0].x, -0.5):
		failures.append("wrapped front face was not clipped to the board boundary")
	var moving_step: Dictionary = GameRules.try_action(moving_level, moving_start, "D")
	if not moving_step.accepted:
		failures.append("moving-platform ride action was rejected")
	else:
		view.set_context(moving_level, moving_start, 0, "")
		view._process(view._generation_duration + BoardView.PLAYER_SPAWN_DURATION + 0.01)
		view._hover = Vector2i(0, 1)
		if not view._hover_is_movable(0):
			failures.append("moving platform landing tile was not recognized as a jump destination")
		view._hover = Vector2i(1, 1)
		if view._hover_is_movable(0):
			failures.append("platform carried position was confused with the clickable jump destination")
		view.play_action(moving_level, moving_start, moving_step.state, "D", "")
		view._process(0.61)
		if view._mode != "rows" or not view._row_transition_active or view._board_phase() != 0:
			failures.append("moving platforms advanced before the hop animation completed")
		if view._carry_from != [0, 0, 1] or view._carry_to != moving_step.state.pos:
			failures.append("moving platform ride did not capture the intermediate and carried positions")
		if not (view._entry_depth(2.0, 2.0, true) > view._entry_depth(2.0, 2.0, false)):
			failures.append("moving platform surface was not ordered over the covered floor")
		view._process(0.24)
		if view._mode != "rows" or view._board_phase() != 0:
			failures.append("moving platform phase changed before the slide finished")
		view._process(0.25)
		if view.busy or view.state.phase != moving_step.state.phase or view.state.pos != moving_step.state.pos:
			failures.append("platform slide did not settle to the rules phase and carried position")

	var lift_state: Dictionary = GameRules.create_state(moving_level)
	lift_state.pos = [0, 2, 2]
	var lift_move: Dictionary = GameRules.try_action(moving_level, lift_state, "X")
	view.set_context(moving_level, lift_state, 0, "")
	view.play_action(moving_level, lift_state, lift_move.state, "X", "")
	view._process(0.53)
	view._process(0.53)
	if not view.busy or view._stage != 2 or view.display_phase() != 0:
		failures.append("moving platforms advanced before the portal destination descent completed")
	view._process(0.73)
	if view._mode != "rows" or view.display_phase() != 0:
		failures.append("lift transition did not wait for the layer animation before platform motion")
	view._process(0.49)
	if view.busy or view.state.phase != lift_move.state.phase:
		failures.append("platform motion after a layer transfer did not settle")

	if failures.is_empty():
		print("PASS: tile reveal, directional roll, animated layer views, portal descent, delayed moving rows, and carried player")
		quit(0)
	else:
		for failure in failures:
			push_error(failure)
		quit(1)
