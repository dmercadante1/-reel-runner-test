extends Node
## All devices feed the same action map. This does not claim physical-device testing.
signal command(name: String, value: bool)

func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	_bind("move_left", KEY_LEFT, false)
	_bind("move_left", KEY_A, true)
	_bind("move_right", KEY_RIGHT, false)
	_bind("move_right", KEY_D, true)
	_bind("jump", KEY_UP, false)
	_bind("jump", KEY_W, true)
	_bind("record", KEY_SPACE, false)
	_bind("record", KEY_C, true)
	_bind("reload", KEY_R, true)
	_bind("drop", KEY_DOWN, false)
	_bind("drop", KEY_S, true)
	_bind("pause_game", KEY_ESCAPE, false)
	_bind("pause_game", KEY_P, true)
	_bind("reset_trial", KEY_T, true)

func _bind(action: StringName, code: Key, physical: bool) -> void:
	if not InputMap.has_action(action):
		InputMap.add_action(action)
	var event := InputEventKey.new()
	if physical:
		event.physical_keycode = code
	else:
		event.keycode = code
	if not InputMap.action_has_event(action, event):
		InputMap.action_add_event(action, event)

func _input(event: InputEvent) -> void:
	if event.is_action_pressed("pause_game") and not event.is_echo():
		command.emit("pause_game", true)
	elif event.is_action_pressed("reset_trial") and not event.is_echo():
		command.emit("reset", true)

func release_all() -> void:
	for action in ["move_left", "move_right", "jump", "record", "reload", "drop"]:
		Input.action_release(action)

func _notification(what: int) -> void:
	if what == NOTIFICATION_APPLICATION_FOCUS_OUT:
		release_all()
		command.emit("focus_lost", true)
