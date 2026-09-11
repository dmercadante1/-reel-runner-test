extends CharacterBody2D
## Physics only; the production visual scene is deliberately not supplied by M1.
signal jumped
signal landed
@export var tuning: MovementTuning = preload("res://data/default_movement.tres")
var crouching := false
var knockback_left := 0.0
var film_strafe := false
var facing: int = 1
var _coyote: float = 0.0
var _buffer: float = 0.0
var _was_grounded: bool = false
var _released_jump: bool = false

func _input(event: InputEvent) -> void:
	if event.is_action_pressed("jump") and not event.is_echo():
		_buffer = tuning.jump_buffer_seconds
		_released_jump = false
	if event.is_action_released("jump"):
		_released_jump = true

func _physics_process(delta: float) -> void:
	if is_on_floor():
		_coyote = tuning.coyote_seconds
	else:
		_coyote = maxf(0.0, _coyote - delta)
	_buffer = maxf(0.0, _buffer - delta)
	# action_press in native tests also works; browser/touch edges are buffered in _input.
	if Input.is_action_just_pressed("jump"):
		_buffer = tuning.jump_buffer_seconds
	if film_strafe:
		var want_crouch:=Input.is_action_pressed("drop")
		if crouching and not want_crouch:
			var query:=PhysicsShapeQueryParameters2D.new()
			var standing:=RectangleShape2D.new()
			standing.size=Vector2(19,65)
			query.shape=standing
			query.transform=Transform2D(0,global_position-Vector2(0,34))
			query.collision_mask=1
			query.exclude=[get_rid()]
			want_crouch=not get_world_2d().direct_space_state.intersect_shape(query,1).is_empty()
		crouching=want_crouch
		get_node("Collision").shape.size=Vector2(20,38 if crouching else 68)
		get_node("Collision").position.y=-19 if crouching else -34
	var direction := Input.get_axis("move_left", "move_right")
	var rate: float = tuning.acceleration if direction != 0.0 else tuning.braking
	if knockback_left>0:
		knockback_left=maxf(0,knockback_left-delta)
		velocity.x=move_toward(velocity.x,0,250*delta)
	else:
		velocity.x = move_toward(velocity.x, direction * tuning.run_speed * (0.42 if crouching else 1.0), rate * delta)
	if direction != 0.0 and not (film_strafe and Input.is_action_pressed("record")):
		facing = 1 if direction > 0.0 else -1
	if not is_on_floor():
		velocity.y = minf(velocity.y + tuning.gravity * delta, tuning.terminal_fall_speed)
	if _buffer > 0.0 and _coyote > 0.0:
		velocity.y = tuning.jump_speed
		_buffer = 0.0
		_coyote = 0.0
		jumped.emit()
	if (_released_jump or Input.is_action_just_released("jump")) and velocity.y < 0.0:
		velocity.y *= tuning.release_jump_multiplier
		_released_jump = false
	move_and_slide()
	if is_on_floor() and not _was_grounded:
		landed.emit()
	_was_grounded = is_on_floor()
	if global_position.y > 520.0:
		reset_at(Vector2(90, 240))

func clear_buffered_input() -> void:
	_buffer = 0.0
	_released_jump = false

func reset_at(point: Vector2) -> void:
	knockback_left=0
	crouching=false
	global_position = point
	velocity = Vector2.ZERO
	_coyote = 0.0
	_buffer = 0.0
	_released_jump = false
	_was_grounded = false
