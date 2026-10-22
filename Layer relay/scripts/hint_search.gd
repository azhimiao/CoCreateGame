extends RefCounted
class_name HintSearch

static var _models := {}
static var _routes := {}

class Request extends RefCounted:
	var action := ""
	func compute(level: Dictionary,state: Dictionary) -> void:
		action = HintSearch.find_action(level,state)

static func find_action(level: Dictionary, start: Dictionary) -> String:
	var id := String(level.id)
	if not _routes.has(id):
		var route := {}
		var state := GameRules.create_state(level)
		var solution: Array = level.get("solution", [])
		for index in range(solution.size()):
			var action := String(solution[index])
			route[GameRules._state_key(state)] = {"action":action,"remaining":solution.size()-index}
			var result := GameRules.try_action(level,state,String(action))
			if not result.accepted or result.state.status == "failed":
				break
			state = result.state
		_routes[id] = route
	var key := GameRules._state_key(start)
	if _routes[id].has(key):
		var known: Dictionary = _routes[id][key]
		if int(start.used)+int(known.remaining) <= int(level.move_limit):
			return known.action
	if not _models.has(id):
		_models[id] = _build_model(level)
	var model: Dictionary = _models[id]
	var heap: Array[Dictionary] = []
	var visited := {key:int(start.used)}
	var parents := {}
	_push(heap,{"state":start.duplicate(true),"first":"","f":int(start.used)+_estimate(level,start,model),"g":int(start.used)})
	var expanded := 0
	while not heap.is_empty() and expanded < 180000:
		var entry := _pop(heap)
		var state: Dictionary = entry.state
		if int(state.used) != int(visited.get(GameRules._state_key(state),-1)):
			continue
		if GameRules._is_goal(level,state):
			_cache_path(id,GameRules._state_key(state),parents)
			return entry.first
		expanded += 1
		for action in ["U","R","D","L","X"]:
			var result := GameRules.try_action(level,state,action)
			if not result.accepted or result.state.status == "failed":
				continue
			var next: Dictionary = result.state
			var next_key := GameRules._state_key(next)
			if int(visited.get(next_key,2147483647)) <= int(next.used):
				continue
			visited[next_key] = int(next.used)
			parents[next_key] = {"from":GameRules._state_key(state),"action":action}
			_push(heap,{"state":next,"first":action if String(entry.first).is_empty() else entry.first,"f":int(next.used)+_estimate(level,next,model),"g":int(next.used)})
	return ""

static func _cache_path(id: String, goal: String, parents: Dictionary) -> void:
	var cursor := goal
	var remaining := 0
	while parents.has(cursor):
		var edge: Dictionary = parents[cursor]
		remaining += 1
		_routes[id][String(edge.from)] = {"action":String(edge.action),"remaining":remaining}
		cursor = edge.from

static func _build_model(level: Dictionary) -> Dictionary:
	# Optimistic graph: doors are open and moving tracks occupy all phases.
	# Add both ordinary and carried landings; reverse links only lower the bound.
	var graph := {}
	for layer in range(2):
		for y in range(int(level.height)):
			for x in range(int(level.width)):
				var supported := String(level.floors[layer][y]).substr(x,1) == "."
				for row in level.moving_rows:
					if int(row.layer) == layer and int(row.y) == y:
						supported = true
				if supported:
					graph[LevelCatalog.position_key([layer,x,y])] = []
	for key in graph:
		var coords := String(key).split(",")
		var at := [int(coords[0]),int(coords[1]),int(coords[2])]
		var destinations: Array = []
		for delta in GameRules.DIRECTIONS.values():
			destinations.append([at[0],int(at[1])+delta.x,int(at[2])+delta.y])
		if [at[1],at[2]] in level.lifts:
			destinations.append([1-int(at[0]),at[1],at[2]])
		var carried: Array = []
		for destination in destinations:
			if not graph.has(LevelCatalog.position_key(destination)):
				continue
			for row in level.moving_rows:
				if int(row.layer) == int(destination[0]) and int(row.y) == int(destination[2]):
					carried.append([destination[0],posmod(int(destination[1])+int(row.direction),int(level.width)),destination[2]])
		destinations.append_array(carried)
		for destination in destinations:
			var other := LevelCatalog.position_key(destination)
			if graph.has(other) and other not in graph[key]:
				graph[key].append(other)
				graph[other].append(key)
	var targets := [LevelCatalog.position_key(level.goal)]
	for item in level.items:
		if String(item.id) in level.get("required_items",[]):
			targets.append(LevelCatalog.position_key(item.at))
	for switch in level.switches:
		targets.append(LevelCatalog.position_key(switch.at))
	var distances := {}
	for target in targets:
		if distances.has(target):
			continue
		var distance := {target:0}
		var queue := [target]
		var head := 0
		while head < queue.size():
			var current: String = queue[head]
			head += 1
			for neighbor in graph.get(current,[]):
				if not distance.has(neighbor):
					distance[neighbor] = int(distance[current])+1
					queue.append(neighbor)
		distances[target] = distance
	return {"distances":distances,"trees":{}}

static func _estimate(level: Dictionary, state: Dictionary, model: Dictionary) -> int:
	var at := LevelCatalog.position_key(state.pos)
	var goal := LevelCatalog.position_key(level.goal)
	var remaining := [goal]
	var signature := ""
	for item in level.items:
		if String(item.id) in level.get("required_items",[]) and String(item.id) not in state.collected:
			remaining.append(LevelCatalog.position_key(item.at))
			signature += String(item.id)+";"
	if not model.trees.has(signature):
		var connected := [remaining[0]]
		var todo := remaining.slice(1)
		var cost := 0
		while not todo.is_empty():
			var best := 100000
			var best_index := 0
			for index in range(todo.size()):
				for point in connected:
					var distance := int(model.distances[point].get(todo[index],100000))
					if distance < best:
						best = distance
						best_index = index
			cost += best
			connected.append(todo.pop_at(best_index))
		model.trees[signature] = cost
	var nearest := 100000
	for point in remaining:
		nearest = mini(nearest,int(model.distances[point].get(at,100000)))
	var estimate := int(model.trees[signature])+nearest
	var mismatch := (int(state.bits)^int(level.goal_bits)) & ~int(state.pending)
	for bit in range(int(level.bit_count)):
		if mismatch & (1 << bit):
			var flip_bound := 100000
			for switch in level.switches:
				if int(switch.mask) & (1 << bit):
					var point := LevelCatalog.position_key(switch.at)
					flip_bound = mini(flip_bound,int(model.distances[point].get(at,100000))+int(model.distances[goal].get(point,100000)))
			estimate = maxi(estimate,flip_bound)
	return estimate

static func _less(a: Dictionary,b: Dictionary) -> bool:
	return int(a.f) < int(b.f) or (int(a.f) == int(b.f) and int(a.g) > int(b.g))

static func _push(heap: Array[Dictionary],entry: Dictionary) -> void:
	heap.append(entry)
	var index := heap.size()-1
	while index > 0:
		var parent: int = (index-1)/2
		if not _less(heap[index],heap[parent]):
			break
		var swap := heap[parent]
		heap[parent] = heap[index]
		heap[index] = swap
		index = parent

static func _pop(heap: Array[Dictionary]) -> Dictionary:
	var first := heap[0]
	var last: Dictionary = heap.pop_back()
	if heap.is_empty():
		return first
	heap[0] = last
	var index := 0
	while index*2+1 < heap.size():
		var child := index*2+1
		if child+1 < heap.size() and _less(heap[child+1],heap[child]):
			child += 1
		if not _less(heap[child],heap[index]):
			break
		var swap := heap[index]
		heap[index] = heap[child]
		heap[child] = swap
		index = child
	return first
