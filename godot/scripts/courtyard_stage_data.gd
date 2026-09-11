extends RefCounted
static func all() -> Array:
 return JSON.parse_string(FileAccess.get_file_as_string("res://assets/courtyard-scroll/layout.json"))
