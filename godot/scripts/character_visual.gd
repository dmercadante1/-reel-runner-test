extends Node2D
## Fixed, authored pose anchors. Physics never depends on source image dimensions.
var stride_rate := 12.0
var reverse_stride := false
var pose: String = "idle"
var pose_time: float = 0.0
var direction: int = 1
var _images: Dictionary = {}
var _atlas: Dictionary = {}

func _ready() -> void:
	texture_filter = CanvasItem.TEXTURE_FILTER_NEAREST
	var key := ShaderMaterial.new()
	key.shader = preload("res://shaders/clean_sprite.gdshader")
	material = key
	if FileAccess.file_exists("res://assets/private-character/atlas.json"):
		_atlas = JSON.parse_string(FileAccess.get_file_as_string("res://assets/private-character/atlas.json"))
	for name in ["model", "run", "ground", "air"]:
		var path := "res://assets/private-character/%s.png" % name
		if ResourceLoader.exists(path):
			_images[name] = load(path)

func set_pose(value: String, elapsed: float, facing: int) -> void:
	pose = value
	pose_time = elapsed
	direction = facing
	queue_redraw()

func _draw() -> void:
	if _atlas.is_empty():
		return
	var source := "ground"
	var index := 0
	match pose:
		"idle": index = int(pose_time * 2.0) % 2
		"turn": index = 2 + mini(1, int(pose_time * 12.0))
		"reload": index = 4 + mini(3, int(pose_time / 0.65 * 4.0))
		"run", "film_run":
			source = "run"
			index = int(pose_time * stride_rate) % 8
			if reverse_stride: index = 7-index
		"jump":
			source = "air"
			index = 0 if pose_time < 0.045 else (1 if pose_time < 0.20 else 2)
		"fall":
			source = "air"
			index = 3
		"land":
			source = "air"
			index = 4 + mini(1, int(pose_time * 10.0))
		"hurt":
			source = "air"
			index = 6 + mini(1, int(pose_time * 5.0))
		"film":
			source = "ground"
			index = 0
	if not _images.has(source):
		return
	var frame: Dictionary = _atlas[source][index]
	var box: Array = frame.rect
	var anchor: Array = frame.anchor
	var scale_factor: float = frame.scale
	var rect := Rect2(float(box[0]), float(box[1]), float(box[2]), float(box[3]))
	draw_set_transform(Vector2.ZERO, 0.0, Vector2(direction, 1))
	draw_texture_rect_region(_images[source], Rect2(Vector2((rect.position.x - float(anchor[0])) * scale_factor, (rect.position.y - float(anchor[1])) * scale_factor), rect.size * scale_factor), rect)
