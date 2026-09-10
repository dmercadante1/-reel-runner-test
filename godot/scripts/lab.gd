extends Node2D
## No production graphics: this is explicitly a movement/engine laboratory.
func _ready() -> void:
	var file := FileAccess.open("res://data/game_definition.json", FileAccess.READ)
	if file == null:
		push_error("Missing game definition")
		return
	var definition: Variant = JSON.parse_string(file.get_as_text())
	if typeof(definition) != TYPE_DICTIONARY:
		push_error("Invalid game definition")
		return
	get_window().title = str(definition.get("display_title", "Movie Camera")) + " — INTERNAL LAB"
