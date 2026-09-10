extends Node2D
## Engine/delivery calibration only; nothing here is production character or level art.
var player: CharacterBody2D
var _world: Node2D
var _font: Font
var _tone: AudioStreamPlayer
var _tick: int = 0
var _elapsed: float = 0.0
var _report_timer: float = 0.0
var _phase: String = "ready"
var _audio_enabled: bool = true
var _audio_events: int = 0
var _jumps: int = 0
var _lands: int = 0
var _respawns: int = 0
var _frame_ms: Array[float] = []
var _bridge: JavaScriptObject
var _command_callback: JavaScriptObject
var _record: bool = false
var _reload_requested: bool = false
var film_stock = preload("res://scripts/film_inventory.gd").new()
var _reels: Array[Vector2] = [Vector2(145, 284), Vector2(220, 251), Vector2(420, 253)]
var _calibration: Texture2D
const SPAWN := Vector2(85, 220)

func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	_font = ThemeDB.fallback_font
	_calibration = load("res://assets/calibration.png")
	_world = Node2D.new()
	_world.name = "World"
	_world.process_mode = Node.PROCESS_MODE_PAUSABLE
	add_child(_world)
	_floor(Vector2(130, 307), Vector2(260, 22), false)
	_floor(Vector2(490, 307), Vector2(300, 22), false)
	_floor(Vector2(216, 268), Vector2(62, 10), true)
	_floor(Vector2(307, 239), Vector2(55, 10), true)
	_floor(Vector2(402, 270), Vector2(72, 10), true)
	_floor(Vector2(-12, 180), Vector2(24, 360), false)
	_floor(Vector2(652, 180), Vector2(24, 360), false)
	player = preload("res://scenes/player.tscn").instantiate()
	player.name = "Player"
	_world.add_child(player)
	player.reset_at(SPAWN)
	player.jumped.connect(_jumped)
	player.landed.connect(_landed)
	_tone = AudioStreamPlayer.new()
	_tone.stream = load("res://assets/calibration-tone.wav")
	_tone.volume_db = -16.0
	add_child(_tone)
	Controls.command.connect(_command)
	if OS.has_feature("web"):
		_bridge = JavaScriptBridge.get_interface("M1Bridge")
		_command_callback = JavaScriptBridge.create_callback(_web_command)
		_bridge.attach(_command_callback)
	get_tree().paused = true
	_report()

func _floor(point: Vector2, size: Vector2, one_way: bool) -> void:
	var body := StaticBody2D.new()
	body.position = point
	var shape := RectangleShape2D.new()
	shape.size = size
	var collision := CollisionShape2D.new()
	collision.shape = shape
	collision.one_way_collision = one_way
	body.add_child(collision)
	_world.add_child(body)

func _web_command(args: Array) -> void:
	if args.size() < 2:
		return
	var name: String = str(args[0])
	var pressed: bool = bool(args[1])
	if name in ["move_left", "move_right", "jump", "record", "reload"]:
		if _phase == "running" or not pressed:
			var event := InputEventAction.new()
			event.action = name
			event.pressed = pressed
			Input.parse_input_event(event)
	else:
		_command(name, pressed)

func _input(event: InputEvent) -> void:
	if _phase == "running" and event.is_action_pressed("reload") and not event.is_echo():
		_reload_requested = true

func _command(name: String, value: bool = true) -> void:
	_reload_requested = false
	match name:
		"start", "resume":
			player.clear_buffered_input()
			_phase = "running"
			Controls.release_all()
			get_tree().paused = false
			_chirp()
		"pause", "focus_lost", "portrait":
			player.clear_buffered_input()
			Controls.release_all()
			player.velocity = Vector2.ZERO
			_record = false
			get_tree().paused = true
			_phase = "paused"
		"pause_game":
			_command("resume" if _phase == "paused" else "pause")
		"reset":
			Controls.release_all()
			player.reset_at(SPAWN)
			_record = false
			film_stock.reset()
			_reels = [Vector2(145, 284), Vector2(220, 251), Vector2(420, 253)]
			_jumps = 0
			_lands = 0
			_respawns = 0
			_tick = 0
			_elapsed = 0.0
			_phase = "running"
			get_tree().paused = false
		"sound":
			_audio_enabled = value
			if value:
				_chirp()
	_report()

func _physics_process(delta: float) -> void:
	if _phase == "running":
		_tick += 1
		_elapsed += delta
		if _reload_requested and film_stock.start_reload():
			_chirp()
		_reload_requested = false
		_record = film_stock.advance(delta, Input.is_action_pressed("record"))
		for i in range(_reels.size() - 1, -1, -1):
			if absf(player.position.x - _reels[i].x) < 18.0 and absf(player.position.y - 20.0 - _reels[i].y) < 25.0:
				if film_stock.collect_reel():
					_reels.remove_at(i)
					_chirp()
		if player.position.y > 450.0:
			_respawns += 1
			Controls.release_all()
			player.reset_at(SPAWN)
	_report_timer += delta
	if _report_timer >= 0.10:
		_report_timer = 0.0
		_report()
	queue_redraw()

func _process(delta: float) -> void:
	if _phase == "running" and delta < 0.3:
		_frame_ms.append(delta * 1000.0)
		if _frame_ms.size() > 600:
			_frame_ms.pop_front()

func _jumped() -> void:
	_jumps += 1
	_chirp()

func _landed() -> void:
	_lands += 1

func _chirp() -> void:
	if _audio_enabled:
		_tone.play()
		_audio_events += 1

func _report() -> void:
	if not is_instance_valid(player):
		return
	var samples := _frame_ms.duplicate()
	samples.sort()
	var p95: float = samples[int((samples.size() - 1) * 0.95)] if not samples.is_empty() else 0.0
	var state := {"phase": _phase, "x": player.position.x, "feet": player.position.y,
		"vx": player.velocity.x, "vy": player.velocity.y, "grounded": player.is_on_floor() and player._was_grounded,
		"tick": _tick, "jumps": _jumps, "landings": _lands, "respawns": _respawns,
		"recording": _record, "audio_events": _audio_events, "audio_enabled": _audio_enabled,
		"fps": Engine.get_frames_per_second(), "frame_p95_ms": p95, "frame_samples": samples.size(),
		"viewport": [get_viewport_rect().size.x, get_viewport_rect().size.y],
		"actions": {"move_left": Input.is_action_pressed("move_left"), "move_right": Input.is_action_pressed("move_right"), "jump": Input.is_action_pressed("jump"), "record": Input.is_action_pressed("record")},
		"film": film_stock.film, "film_capacity": film_stock.CAPACITY, "spares": film_stock.spares, "max_spares": film_stock.MAX_SPARES, "reload_left": film_stock.reload_left, "reloads": film_stock.reloads, "pickups": _reels.size(),
		"engine": Engine.get_version_info().string, "build": "m1-02", "production_art": false}
	if _bridge != null:
		_bridge.report(JSON.stringify(state))

func _draw() -> void:
	if _font == null:
		return
	draw_rect(Rect2(0, 0, 640, 360), Color("0a101a"))
	for x in range(0, 641, 20):
		draw_line(Vector2(x, 62), Vector2(x, 337), Color("182330"))
	for y in range(76, 338, 20):
		draw_line(Vector2(0, y), Vector2(640, y), Color("182330"))
	draw_rect(Rect2(12, 10, 616, 42), Color("142536"))
	draw_string(_font, Vector2(23, 27), "M1 / ENGINE & INPUT LAB", HORIZONTAL_ALIGNMENT_LEFT, -1, 13, Color("dbe4df"))
	draw_string(_font, Vector2(23, 44), "640 x 360   |   Calibration art only. Cameraman artwork comes next.", HORIZONTAL_ALIGNMENT_LEFT, -1, 10, Color("94a6b6"))
	for box in [Rect2(0, 296, 260, 22), Rect2(340, 296, 300, 22), Rect2(185, 263, 62, 10), Rect2(279.5, 234, 55, 10), Rect2(366, 265, 72, 10)]:
		draw_rect(box, Color("2b3947"))
		draw_line(box.position, box.position + Vector2(box.size.x, 0), Color("c3ac7a"), 1)
	draw_string(_font, Vector2(257, 321), "80 PX GAP", HORIZONTAL_ALIGNMENT_LEFT, -1, 10, Color("dd846d"))
	draw_line(Vector2(260, 294), Vector2(260, 334), Color("dd846d"))
	draw_line(Vector2(340, 294), Vector2(340, 334), Color("dd846d"))
	if _calibration != null:
		draw_texture(_calibration, Vector2(512, 160))
		draw_string(_font, Vector2(488, 235), "PIXEL / ALPHA TEST", HORIZONTAL_ALIGNMENT_LEFT, -1, 9, Color("94a6b6"))
	if is_instance_valid(player):
		var p := player.position
		draw_line(p, p + Vector2(0, -68), Color("76b8ca"))
		draw_line(p + Vector2(-17, 0), p + Vector2(17, 0), Color("76b8ca"))
		if _record:
			var lens := p + Vector2(10 * player.facing, -39)
			draw_colored_polygon(PackedVector2Array([lens, lens + Vector2(110 * player.facing, -20), lens + Vector2(110 * player.facing, 22)]), Color(0.9, 0.78, 0.45, 0.22))
		if film_stock.reload_left > 0.0:
			draw_string(_font, p + Vector2(-23, -77), "RELOADING", HORIZONTAL_ALIGNMENT_LEFT, -1, 9, Color("e5d291"))
	for reel in _reels:
		draw_circle(reel, 7, Color("c3ac7a"))
		draw_circle(reel, 2, Color("142536"))
	draw_rect(Rect2(15, 65, 100, 7), Color("2b3947"))
	draw_rect(Rect2(15, 65, 100 * film_stock.film / film_stock.CAPACITY, 7), Color("c3ac7a"))
	draw_string(_font, Vector2(123, 73), "FILM %d%%   SPARE REELS %d / %d" % [roundi(film_stock.film / film_stock.CAPACITY * 100), film_stock.spares, film_stock.MAX_SPARES], HORIZONTAL_ALIGNMENT_LEFT, -1, 11, Color("dbe4df"))
	draw_string(_font, Vector2(14, 352), "ARROWS / WASD  |  UP = JUMP  |  SPACE = FILM  |  R = RELOAD  |  GOLD REELS = PICKUPS", HORIZONTAL_ALIGNMENT_LEFT, -1, 9, Color("aab7bd"))
