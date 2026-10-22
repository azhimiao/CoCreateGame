extends SceneTree

func _initialize() -> void:
	# Isolated mechanism fixtures; these examples are not in the playable campaign.
	LevelCatalog.LEVELS.assign(MechanicFixtures.LEVELS.duplicate(true))
	call_deferred("_run")

func _run() -> void:
	var failures: Array[String] = []
	var controls := IsoControls.new()
	root.add_child(controls)
	controls.size = Vector2(236, 166)
	await process_frame
	if controls.action_at(controls._center("R")) != "R" or controls.action_at(controls._center("U")) != "U":
		failures.append("isometric direction pads did not hit their rendered controls")
	var right := IsoControls.screen_direction("R")
	var up := IsoControls.screen_direction("U")
	if right.x <= 0.0 or right.y <= 0.0 or up.x <= 0.0 or up.y >= 0.0:
		failures.append("direction arrows did not match the isometric board axes")

	var inventory := InventoryBar.new()
	root.add_child(inventory)
	await process_frame
	var items: Array[Dictionary] = []
	for i in range(7):
		items.append({"id": "item_%d" % i, "name": "道具%d" % (i + 1), "icon": "◇", "count": i + 1})
	inventory.set_items(items)
	if inventory.slots.size() != 5 or inventory._next.disabled:
		failures.append("inventory did not show five slots with forward paging for additional items")
	inventory.change_page(1)
	if inventory.page_start != 5 or String(inventory.slots[0].get_meta("item_id")) != "item_5":
		failures.append("inventory next arrow did not advance to the next five items")
	inventory.change_page(1)
	if inventory.page_start != 5:
		failures.append("inventory paging advanced past its final item")
	inventory.change_page(-1)
	if inventory.page_start != 0 or String(inventory.slots[0].get_meta("item_id")) != "item_0":
		failures.append("inventory previous arrow did not return to the first five items")

	if failures.is_empty():
		print("PASS: isometric input directions and five-slot inventory paging")
		quit(0)
	else:
		for failure in failures:
			push_error(failure)
		quit(1)
