extends RefCounted
class_name ScoreRules

# Each star is earned independently in the current run, including runs using a hint.
static func evaluate(level: Dictionary, state: Dictionary, seconds: float) -> Dictionary:
	var cleared: bool = state.get("status", "playing") == "won"
	var timed: bool = cleared and seconds <= float(level.time_limit)
	var efficient: bool = cleared and int(state.used) <= int(level.par)
	return {"cleared": cleared, "timed": timed, "efficient": efficient,
		"stars": int(cleared) + int(timed) + int(efficient)}

static func clock_text(seconds: float) -> String:
	var value := maxi(0, ceili(seconds))
	return "%02d:%02d" % [value / 60, value % 60]
