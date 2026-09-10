extends Node
## All devices will feed these actions. This first pass binds keyboard only.

func _ready() -> void:
	_bind("move_left", KEY_LEFT, false)
	_bind("move_left", KEY_A, true)
	_bind("move_right", KEY_RIGHT, false)
	_bind("move_right", KEY_D, true)
	_bind("jump", KEY_UP, false)
	_bind("jump", KEY_W, true)
	_bind("record", KEY_SPACE, false)
	_bind("record", KEY_C, true)
	_bind("defend", KEY_X, true)
	_bind("pause_game", KEY_ESCAPE, false)

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

func _notification(what: int) -> void:
	if what == NOTIFICATION_APPLICATION_FOCUS_OUT:
		for action in ["move_left", "move_right", "jump", "record", "defend"]:
			Input.action_release(action)
