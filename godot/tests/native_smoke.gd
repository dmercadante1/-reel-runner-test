extends SceneTree
## Native physics tests; these do not claim browser input or visible-art validation.
var checks: Array = []
var player: CharacterBody2D

func _initialize() -> void:
	_run.call_deferred()

func check_result(label: String, passed: bool) -> void:
	checks.append({"name": label, "passed": passed})
	print(("PASS " if passed else "FAIL ") + label)

func settle(seconds: float) -> void:
	await create_timer(seconds).timeout

func measure_jump(short_hop: bool) -> float:
	player.reset_at(Vector2(90, 240))
	Input.action_release("jump")
	await settle(0.65)
	var start_y: float = player.position.y
	var min_y: float = start_y
	Input.action_press("jump")
	for i in range(55):
		await physics_frame
		if short_hop and i == 4:
			Input.action_release("jump")
		min_y = minf(min_y, player.position.y)
	Input.action_release("jump")
	await settle(0.3)
	return start_y - min_y

func _run() -> void:
	var lab: Node = load("res://scenes/movement_lab.tscn").instantiate()
	root.add_child(lab)
	player = lab.get_node("Player")
	await settle(0.8)
	check_result("Player lands on floor at authored foot height", player.is_on_floor() and absf(player.position.y - 296.0) < 2.0)
	var before: float = player.position.x
	Input.action_press("move_right")
	await settle(0.3)
	Input.action_release("move_right")
	check_result("Right action moves the collision body", player.position.x > before + 20.0)
	await settle(0.3)
	check_result("Releasing input brakes to rest", absf(player.velocity.x) < 0.1)
	before = player.position.x
	Input.action_press("move_left")
	await settle(0.25)
	Input.action_release("move_left")
	check_result("Left action moves the collision body", player.position.x < before - 15.0)
	var full_height: float = await measure_jump(false)
	var short_height: float = await measure_jump(true)
	check_result("Held jump reaches its provisional height", full_height > 45.0 and full_height < 62.0)
	check_result("Early release creates a shorter jump", short_height > 5.0 and full_height > short_height + 10.0)
	check_result("Player returns to floor after jump", player.is_on_floor())
	var has_up := false
	for event in InputMap.action_get_events("jump"):
		if event is InputEventKey and event.keycode == KEY_UP:
			has_up = true
	check_result("Up-arrow binding is present", has_up)
	var stock = preload("res://scripts/film_inventory.gd").new()
	check_result("Full camera does not waste a spare", not stock.start_reload() and stock.spares == 2)
	check_result("Pickups stack only to three", stock.collect_reel() and not stock.collect_reel() and stock.spares == 3)
	stock.advance(3.0, true)
	check_result("Filming consumes film", stock.film == 9.0)
	check_result("Reload commits exactly one spare", stock.start_reload() and stock.spares == 2 and not stock.start_reload())
	check_result("Reload suspends filming", not stock.advance(0.3, true) and stock.film == 9.0)
	stock.advance(0.35, false)
	check_result("Reload restores full film", stock.film == stock.CAPACITY and stock.reloads == 1)
	stock.advance(20.0, true)
	check_result("Empty camera cannot film or go negative", stock.film == 0.0 and not stock.advance(1.0, true))
	stock.spares = 0
	check_result("No free refill without spare reels", not stock.start_reload() and stock.film == 0.0)
	stock.collect_reel()
	stock.start_reload()
	stock.advance(1.0, false)
	check_result("Pickup recovers an empty camera", stock.film == stock.CAPACITY and stock.spares == 0)
	var failed := 0
	for entry in checks:
		if not entry.passed:
			failed += 1
	var report := {"scope": "native physics and source binding only", "engine": Engine.get_version_info().string, "passed": checks.size() - failed, "failed": failed, "checks": checks, "browser_tested": false, "physical_phone_tested": false, "art_approved": false}
	var output := FileAccess.open("res://tests/latest-native-results.json", FileAccess.WRITE)
	if output:
		output.store_string(JSON.stringify(report, "  "))
	print(JSON.stringify(report))
	quit(1 if failed else 0)
