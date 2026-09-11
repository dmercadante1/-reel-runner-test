extends RefCounted
## One readable attack, a locked attack direction, then a filming opportunity.
const WINDUP := 0.85
const ATTACK := 0.38
const RECOVER := 1.80
const CAPTURE_SECONDS := 1.25
var phase: String = "watch"
var clock: float = 0.0
var exposure: float = 0.0
var x: float = 490.0
var direction: int = -1
var hit_used: bool = false
var attacks: int = 0

func reset() -> void:
	phase = "watch"
	clock = 0.0
	exposure = 0.0
	x = 490.0
	direction = -1
	hit_used = false
	attacks = 0

func advance(delta: float, target: Vector2, filming: bool, facing: int) -> Dictionary:
	var result := {"hit": false, "captured": false}
	clock += delta
	if phase == "captured":
		return result
	var near := absf(target.x - x) < 160.0 and absf(target.y - 230.0) < 75.0
	match phase:
		"watch":
			if near and clock > 0.7:
				direction = -1 if target.x < x else 1
				phase = "windup"
				clock = 0.0
		"windup":
			if clock >= WINDUP:
				phase = "attack"
				clock = 0.0
				hit_used = false
				attacks += 1
		"attack":
			x = clampf(x + direction * 180.0 * delta, 395.0, 560.0)
			if not hit_used and absf(target.x - x) < 48.0 and absf(target.y - 230.0) < 26.0:
				result.hit = true
				hit_used = true
			if clock >= ATTACK:
				phase = "exposed"
				clock = 0.0
		"exposed":
			var in_view := absf(target.x - x) < 160.0 and absf(target.y - 230.0) < 38.0 and (x - target.x) * facing > 0.0
			if clock >= RECOVER:
				phase = "watch"
				clock = 0.0
			elif filming and in_view:
				exposure = minf(CAPTURE_SECONDS, exposure + delta)
				if exposure >= CAPTURE_SECONDS - 0.00001:
					phase = "captured"
					clock = 0.0
					result.captured = true
			elif clock >= RECOVER:
				phase = "watch"
				clock = 0.0
	return result
