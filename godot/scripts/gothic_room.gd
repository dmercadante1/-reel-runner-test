extends Node2D
## Courtyard room: authored geometry, independent art, one readable encounter.
var player: CharacterBody2D
var visual: Node2D
var stock = preload("res://scripts/film_inventory.gd").new()
var guardian = preload("res://scripts/guardian_encounter.gd").new()
var _font: Font
var _bridge: JavaScriptObject
var _callback: JavaScriptObject
var _world: Node2D
var _gate_body: StaticBody2D
var _phase := "ready"
var _record := false
var _reload_requested := false
var _drop_requested := false
var _drop_left := 0.0
var _time := 0.0
var _report_clock := 0.0
var _pose_time := 0.0
var _pose := "idle"
var _turn_left := 0.0
var _land_left := 0.0
var _hurt_left := 0.0
var _invincible := 0.0
var _last_facing := 1
var _health := 3
var _checkpoint := Vector2(65, 230)
var _checkpoint_active := false
var _reels: Array[Vector2] = []
var _pickups := 0
var _jumps := 0
var _hits := 0
var _completed := false
var _sound := true
var _tone: AudioStreamPlayer
var _ambient: AudioStreamPlayer
var _textures: Dictionary = {}
var _keyed: Node2D
var _samples: Array[float] = []
var _review := false
var _review_clock := 0.0
const REVIEW_POSES := ["idle", "turn", "run", "jump", "fall", "land", "film", "film_run", "reload", "hurt"]
const SURFACES := [Rect2(0,230,260,24),Rect2(340,230,300,24),Rect2(0,342,640,18),Rect2(275,310,45,10),Rect2(268,276,40,10),Rect2(302,246,36,10)]

func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	_font = ThemeDB.fallback_font
	texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	for name in ["sky", "architecture", "guardian"]:
		var path := "res://assets/gothic/%s.png" % name
		if ResourceLoader.exists(path): _textures[name] = load(path)
	_world = Node2D.new()
	_world.process_mode = Node.PROCESS_MODE_PAUSABLE
	add_child(_world)
	for box in SURFACES:
		_floor(box)
	_gate_body = _floor(Rect2(598,125,10,105))
	_floor(Rect2(-20,0,20,360))
	_floor(Rect2(640,0,20,360))
	player = preload("res://scenes/player.tscn").instantiate()
	player.get_node("InternalOnlyMarker").hide()
	player.collision_mask = 3
	var character_shape := RectangleShape2D.new()
	character_shape.size = Vector2(20,68)
	player.get_node("Collision").shape = character_shape
	player.get_node("Collision").position = Vector2(0,-34)
	_world.add_child(player)
	visual = preload("res://scripts/character_visual.gd").new()
	player.add_child(visual)
	player.jumped.connect(func(): _jumps += 1; _land_left = 0.0; _chirp(1.3))
	player.landed.connect(func(): _land_left = 0.18)
	_keyed = Node2D.new()
	var shader := ShaderMaterial.new()
	shader.shader = preload("res://shaders/clean_sprite.gdshader")
	_keyed.material = shader
	add_child(_keyed)
	_keyed.draw.connect(_draw_props)
	_tone = AudioStreamPlayer.new()
	_tone.stream = load("res://assets/calibration-tone.wav")
	_tone.volume_db = -22
	add_child(_tone)
	if ResourceLoader.exists("res://assets/gothic/ambience.wav"):
		_ambient = AudioStreamPlayer.new()
		_ambient.stream = load("res://assets/gothic/ambience.wav")
		_ambient.stream.loop_mode = AudioStreamWAV.LOOP_FORWARD
		_ambient.stream.loop_end = 352800
		_ambient.volume_db = -12
		add_child(_ambient)
	Controls.command.connect(_command)
	_reset()
	_phase = "ready"
	get_tree().paused = true
	if OS.has_feature("web"):
		_bridge = JavaScriptBridge.get_interface("M1Bridge")
		_callback = JavaScriptBridge.create_callback(_web_command)
		_bridge.attach(_callback)
	_report()

func _floor(rect: Rect2) -> StaticBody2D:
	var body := StaticBody2D.new()
	body.position = rect.get_center()
	var collision := CollisionShape2D.new()
	var shape := RectangleShape2D.new()
	shape.size = rect.size
	collision.shape = shape
	collision.one_way_collision = rect.size.y == 10
	body.collision_layer = 2 if collision.one_way_collision else 1
	body.add_child(collision)
	_world.add_child(body)
	return body

func _reset() -> void:
	Controls.release_all()
	stock.reset()
	guardian.reset()
	_gate_body.collision_layer = 1
	player.reset_at(_checkpoint)
	player.facing = 1
	_reels = [Vector2(210,218),Vector2(178,329),Vector2(558,329)]
	_health = 3
	_invincible = 0.0
	_hurt_left = 0.0
	_completed = false
	_record = false
	_reload_requested = false
	_drop_left = 0.0
	_drop_requested = false
	player.collision_mask = 3
	_pickups = 0
	_jumps = 0
	_hits = 0

func _input(event: InputEvent) -> void:
	if _phase == "running" and event.is_action_pressed("reload") and not event.is_echo():
		_reload_requested = true

	if _phase == "running" and event.is_action_pressed("drop") and not event.is_echo():
		_drop_requested = true

func _web_command(args: Array) -> void:
	if args.size() < 2: return
	var name := str(args[0])
	var value := bool(args[1])
	if name in ["move_left", "move_right", "jump", "record", "reload", "drop"]:
		if _phase == "running" or not value:
			var event := InputEventAction.new()
			event.action = name
			event.pressed = value
			Input.parse_input_event(event)
	else: _command(name,value)

func _command(name: String, value: bool = true) -> void:
	match name:
		"start", "resume":
			if _completed or _health <= 0: _reset()
			_review = false
			_phase = "running"
			player.clear_buffered_input()
			Controls.release_all()
			get_tree().paused = false
			if _ambient != null:
				_ambient.stream_paused = false
				if _sound and not _ambient.playing: _ambient.play()
		"pause", "focus_lost", "portrait":
			_phase = "paused"
			if _ambient != null: _ambient.stream_paused = true
			Controls.release_all()
			player.clear_buffered_input()
			player.velocity = Vector2.ZERO
			_record = false
			_reload_requested = false
			_drop_requested = false
			get_tree().paused = true
		"pause_game": _command("pause" if _phase == "running" else "resume")
		"reset":
			_review = false
			_reset()
			_command("resume")
		"sound":
			_sound = value
			if _ambient != null:
				if value: _ambient.play()
				else: _ambient.stop()
		"review":
			_reset()
			_command("pause")
			_review = true
			_review_clock = 0.0
			_phase = "review"
			player.reset_at(Vector2(180,230))
			player.facing = 1
	_report()

func _physics_process(delta: float) -> void:
	if _phase == "running":
		_time += delta
		_drop_left = maxf(0.0,_drop_left-delta)
		if (_drop_requested or Input.is_action_just_pressed("drop")) and player.is_on_floor() and player.position.y>240 and player.position.y<320:
			_drop_left = 0.25
			player.position.y += 2
		_drop_requested = false
		player.collision_mask = 1 if _drop_left>0 else 3
		_invincible = maxf(0.0, _invincible - delta)
		_hurt_left = maxf(0.0, _hurt_left - delta)
		_land_left = maxf(0.0, _land_left - delta)
		_turn_left = maxf(0.0, _turn_left - delta)
		if player.facing != _last_facing:
			_turn_left = 0.16
		_last_facing = player.facing
		if _reload_requested and stock.start_reload(): _chirp(0.8)
		_reload_requested = false
		_record = stock.advance(delta, Input.is_action_pressed("record") and _hurt_left == 0.0)
		for i in range(_reels.size()-1,-1,-1):
			if absf(player.position.x - _reels[i].x) < 18 and absf(player.position.y - 18 - _reels[i].y) < 25 and stock.collect_reel():
				_reels.remove_at(i)
				_pickups += 1
				_chirp(1.7)
		if not _checkpoint_active and player.position.x > 352 and player.position.y < 239:
			_checkpoint_active = true
			_checkpoint = Vector2(365,230)
		var old_phase: String = guardian.phase
		var result: Dictionary = guardian.advance(delta,player.position,_record,player.facing)
		if guardian.phase == "windup" and old_phase != "windup": _chirp(0.5)
		if result.hit and _invincible == 0.0:
			_health -= 1
			_hits += 1
			_hurt_left = 0.36
			_invincible = 1.3
			_record = false
			_chirp(0.45)
		if result.captured:
			_gate_body.collision_layer = 0
			_chirp(2.0)
		if _health <= 0:
			_phase = "defeated"
			Controls.release_all()
			get_tree().paused = true
		if guardian.phase == "captured" and player.position.x > 600 and player.position.y < 240:
			_completed = true
			_phase = "complete"
			Controls.release_all()
			get_tree().paused = true
		var next := "idle"
		if _hurt_left > 0: next = "hurt"
		elif stock.reload_left > 0: next = "reload"
		elif not player.is_on_floor(): next = "jump" if player.velocity.y < -15 else "fall"
		elif _land_left > 0: next = "land"
		elif _turn_left > 0: next = "turn"
		elif absf(player.velocity.x) > 5: next = "film_run" if _record else "run"
		elif _record: next = "film"
		if next != _pose: _pose_time = 0.0
		else: _pose_time += delta
		_pose = next
		visual.set_pose(_pose,0.65-stock.reload_left if _pose == "reload" else _pose_time,player.facing)
		visual.modulate.a = 0.45 if _invincible > 0 and int(_time*12)%2 == 0 else 1.0
	elif _phase == "review":
		_review_clock += delta
		var durations := [1.2,0.18,1.2,0.33,0.33,0.18,1.2,1.2,0.65,0.36]
		var phase_time := fmod(_review_clock,6.83)
		var index := 0
		while index < durations.size()-1 and phase_time >= durations[index]:
			phase_time -= durations[index]
			index += 1
		_pose = REVIEW_POSES[index]
		visual.set_pose(_pose,phase_time,1)
		if _pose == "jump": player.position.y = 230.0 - 330.0*phase_time + 500.0*phase_time*phase_time
		elif _pose == "fall": player.position.y = 175.55 + 500.0*phase_time*phase_time
		else: player.position.y = 230

	_report_clock += delta
	if _report_clock > 0.1:
		_report_clock = 0.0
		_report()
	queue_redraw()
	if _keyed != null: _keyed.queue_redraw()

func _process(delta: float) -> void:
	if _phase == "running" and delta < 0.3:
		_samples.append(delta*1000)
		if _samples.size() > 600: _samples.pop_front()

func _chirp(pitch: float) -> void:
	if _sound:
		_tone.pitch_scale = pitch
		_tone.play()

func _report() -> void:
	if not is_instance_valid(player): return
	var sorted := _samples.duplicate()
	sorted.sort()
	var state := {"phase":_phase,"x":player.position.x,"feet":player.position.y,"vx":player.velocity.x,"vy":player.velocity.y,"grounded":player.is_on_floor(),"pose":_pose,"film":stock.film,"film_capacity":stock.CAPACITY,"spares":stock.spares,"reload_left":stock.reload_left,"reloads":stock.reloads,"recording":_record,"health":_health,"hits":_hits,"jumps":_jumps,"pickups":_pickups,"checkpoint":_checkpoint_active,"guardian":guardian.phase,"guardian_x":guardian.x,"guardian_clock":guardian.clock,"exposure":guardian.exposure,"attacks":guardian.attacks,"complete":_completed,"viewport":[640,360],"fps":Engine.get_frames_per_second(),"frame_p95_ms":sorted[int((sorted.size()-1)*0.95)] if not sorted.is_empty() else 0.0,"engine":Engine.get_version_info().string,"build":"courtyard-01","audio_enabled":_sound,"actions":{"move_left":Input.is_action_pressed("move_left"),"move_right":Input.is_action_pressed("move_right"),"jump":Input.is_action_pressed("jump"),"record":Input.is_action_pressed("record")}}
	if _bridge != null: _bridge.report(JSON.stringify(state))

func _draw() -> void:
	if _font == null: return
	if _textures.has("sky"): draw_texture_rect(_textures.sky,Rect2(0,0,640,360),false)
	else: draw_rect(Rect2(0,0,640,360),Color("101c30"))
	if _textures.has("architecture"):
		var texture: Texture2D = _textures.architecture
		var cell := texture.get_size() / Vector2(3,2)
		for x in range(0,640,64):
			draw_texture_rect_region(texture,Rect2(x,251,64,92),Rect2(Vector2(cell.x,0),cell))
		for rect in SURFACES:
			for x in range(int(rect.position.x),int(rect.end.x),32):
				var width := minf(32,rect.end.x-x)
				draw_texture_rect_region(texture,Rect2(x,rect.position.y,width,rect.size.y),Rect2(Vector2(0,cell.y+cell.y*0.063),Vector2(cell.x*width/32,cell.y*0.5)))
			draw_line(rect.position,Vector2(rect.end.x,rect.position.y),Color("9b9d95"))
	# Soft drifting mist is a separate engine layer, not painted into collisions.
	for i in range(3):
		draw_rect(Rect2(fmod(_time*3+i*250,850)-180,285+i*13,210,7),Color(0.25,0.35,0.44,0.035))
	for reel in _reels:
		var p := reel + Vector2(0,sin(_time*3+reel.x)*2)
		draw_circle(p,5,Color("c7b680"))
		draw_circle(p,1,Color("272b30"))
		for angle in [0.0,2.1,4.2]: draw_circle(p+Vector2(cos(angle),sin(angle))*3,1,Color("343843"))
	if _record:
		var lens := player.position + Vector2(12*player.facing,-43)
		draw_colored_polygon(PackedVector2Array([lens,lens+Vector2(158*player.facing,-17),lens+Vector2(158*player.facing,22)]),Color(0.85,0.81,0.59,0.13))
	if _checkpoint_active:
		draw_line(Vector2(354,230),Vector2(354,202),Color("89958c"))
		draw_colored_polygon(PackedVector2Array([Vector2(354,202),Vector2(367,206),Vector2(354,212)]),Color("89c2b6"))
	var message := "Cross the bridge. Film the guardian after its sweep."
	if guardian.phase == "windup": message = "JUMP OR STEP BACK — sweep incoming"
	elif guardian.phase == "exposed": message = "FILM NOW — the guardian is exposed"
	elif guardian.phase == "captured": message = "Captured. The gate is open — continue right."
	elif stock.reload_left > 0: message = "Loading a fresh reel…"
	elif stock.film == 0 and stock.spares == 0: message = "Out of film. Search the crypt or retry the checkpoint."
	if _review: message = "ACTION REVIEW / " + _pose.to_upper().replace("_"," + ")
	draw_rect(Rect2(0,0,640,45),Color(0.025,0.04,0.065,0.93))
	draw_string(_font,Vector2(56,14),"MAN WITH A MOVIE CAMERA",HORIZONTAL_ALIGNMENT_LEFT,-1,10,Color("dad4c0"))
	draw_string(_font,Vector2(485,14),"THE GATEKEEPER",HORIZONTAL_ALIGNMENT_LEFT,-1,10,Color("c3bda7"))
	draw_rect(Rect2(56,21,100,7),Color("333b42"))
	draw_rect(Rect2(56,21,100*stock.film/stock.CAPACITY,7),Color("c9b17b"))
	draw_string(_font,Vector2(165,28),"REELS %d / 3" % stock.spares,HORIZONTAL_ALIGNMENT_LEFT,-1,10,Color("c9b17b"))
	for i in range(3): draw_circle(Vector2(272+i*12,24),4,Color("aa5f56") if i<_health else Color("343b44"))
	draw_string(_font,Vector2(56,40),message,HORIZONTAL_ALIGNMENT_LEFT,-1,9,Color("9aaea9"))
	if guardian.phase == "exposed":
		draw_rect(Rect2(guardian.x-22,148,44,3),Color("253841"))
		draw_rect(Rect2(guardian.x-22,148,44*guardian.exposure/guardian.CAPTURE_SECONDS,3),Color("83bfc4"))
	if _completed or _health <= 0:
		draw_rect(Rect2(150,102,340,94),Color(0.03,0.05,0.075,0.94))
		draw_string(_font,Vector2(181,130),"SCENE CAPTURED" if _completed else "THE TAKE WAS LOST",HORIZONTAL_ALIGNMENT_LEFT,-1,18,Color("dcc58f"))
		draw_string(_font,Vector2(180,156),"Retry to play from your checkpoint.",HORIZONTAL_ALIGNMENT_LEFT,-1,12,Color("b8c3c1"))

func _draw_props() -> void:
	if _textures.has("architecture"):
		var texture: Texture2D = _textures.architecture
		var c := texture.get_size()/Vector2(3,2)
		for x in [12,176,352,520]:
			_keyed.draw_colored_polygon(PackedVector2Array([Vector2(x+15,341),Vector2(x+15,292),Vector2(x+40,268),Vector2(x+65,292),Vector2(x+65,341)]),Color("090f19"))
			_keyed.draw_texture_rect_region(texture,Rect2(x,255,80,86),Rect2(Vector2(c.x*2,0),c))
		_keyed.draw_texture_rect_region(texture,Rect2(575,129,65,101),Rect2(Vector2(c.x,c.y) if guardian.phase != "captured" else Vector2(c.x*2,0),c))
		for x in [8,565]:
			_keyed.draw_texture_rect_region(texture,Rect2(x,180,24,50),Rect2(Vector2(c.x*2,c.y),c))
	if _textures.has("guardian") and (guardian.phase != "captured" or guardian.clock < 0.5):
		var texture: Texture2D = _textures.guardian
		var c := texture.get_size()/Vector2(4,2)
		var frame := 0
		match guardian.phase:
			"windup": frame = 2 if guardian.clock < 0.45 else 3
			"attack": frame = 4
			"exposed": frame = 5 if guardian.clock < 0.3 else 6
			"captured": frame = 7
		var boxes := [Rect2(80,0,230,492),Rect2(430,0,316,492),Rect2(787,0,330,492),Rect2(1200,0,336,492),Rect2(0,630,444,320),Rect2(450,512,300,440),Rect2(850,512,302,440),Rect2(1200,512,336,440)]
		var anchors := [Vector2(195,488),Vector2(570,488),Vector2(960,488),Vector2(1335,488),Vector2(245,944),Vector2(605,944),Vector2(970,944),Vector2(1340,944)]
		var rect: Rect2 = boxes[frame]
		var factor := 64.0/380.0
		var origin: Vector2 = Vector2(guardian.x,230)+(rect.position-anchors[frame])*factor
		_keyed.draw_texture_rect_region(texture,Rect2(origin,rect.size*factor),rect)
		if guardian.phase == "windup":
			_keyed.draw_string(_font,Vector2(guardian.x-3,147),"!",HORIZONTAL_ALIGNMENT_LEFT,-1,19,Color("e7b977"))
	if ResourceLoader.exists("res://assets/private-character/model.png"):
		var portrait: Texture2D = load("res://assets/private-character/model.png")
		_keyed.draw_texture_rect_region(portrait,Rect2(12,3,36,39),Rect2(665,318,548,570))
