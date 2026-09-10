extends RefCounted
## Shared film rules. Durations are seconds of active filming, not passive time.
const CAPACITY: float = 12.0
const MAX_SPARES: int = 3
const RELOAD_SECONDS: float = 0.65
var film: float = CAPACITY
var spares: int = 2
var reload_left: float = 0.0
var reloads: int = 0

func reset() -> void:
	film = CAPACITY
	spares = 2
	reload_left = 0.0
	reloads = 0

func collect_reel() -> bool:
	if spares >= MAX_SPARES:
		return false
	spares += 1
	return true

func start_reload() -> bool:
	if reload_left > 0.0 or spares == 0 or film >= CAPACITY:
		return false
	# Commit one reel immediately; repeated input cannot consume another.
	spares -= 1
	reload_left = RELOAD_SECONDS
	return true

func advance(delta: float, filming: bool) -> bool:
	if reload_left > 0.0:
		reload_left = maxf(0.0, reload_left - delta)
		if reload_left < 0.000001:
			reload_left = 0.0
			film = CAPACITY
			reloads += 1
		return false
	if not filming or film <= 0.0:
		return false
	film = maxf(0.0, film - delta)
	return true
