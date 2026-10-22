extends RefCounted
class_name LevelCatalog

const CAMPAIGN_VERSION := 4
static var LEVELS: Array[Dictionary] = _load_campaign()

static func _load_campaign() -> Array[Dictionary]:
	var result: Array[Dictionary] = []
	var data: Variant = JSON.parse_string(FileAccess.get_file_as_string("res://data/campaign.json"))
	if data is Array:
		for entry in data:
			result.append(_normalize(entry))
	return result

static func _normalize(value: Variant) -> Variant:
	if value is float and value == floor(value):
		return int(value)
	if value is Array:
		var array: Array = []
		for entry in value:
			array.append(_normalize(entry))
		return array
	if value is Dictionary:
		var dictionary: Dictionary = {}
		for key in value:
			dictionary[key] = _normalize(value[key])
		return dictionary
	return value

static func is_available(index: int) -> bool:
	return index >= 0 and index < LEVELS.size() and bool(LEVELS[index].get("available", true))

static func next_available(index: int) -> int:
	for candidate in range(index + 1, LEVELS.size()):
		if is_available(candidate):
			return candidate
	return -1

static func available_count() -> int:
	var count := 0
	for index in range(LEVELS.size()):
		count += int(is_available(index))
	return count

static func get_level(index: int) -> Dictionary:
	assert(is_available(index), "此关尚未开放")
	return LEVELS[index].duplicate(true)

static func position_key(position: Array) -> String:
	return "%d,%d,%d" % [int(position[0]), int(position[1]), int(position[2])]
