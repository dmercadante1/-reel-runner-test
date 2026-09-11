extends Node2D
## Fixed, authored pose anchors. Physics never depends on source image dimensions.
var aiming_up := false
var crouch_sheet:Texture2D
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
	if pose in ["crouch","crouch_walk","crouch_film"] or (aiming_up and pose in ["film","film_run"]):
		if crouch_sheet==null:crouch_sheet=load("res://assets/courtyard-scroll/crouch.png")
		var index:=0
		if pose=="crouch_walk":index=[1,2,3,4][int(pose_time*8)%4]
		elif pose=="crouch_film":index=5
		elif aiming_up:index=6
		var cell:=crouch_sheet.get_size()/Vector2(4,2)
		var scale_factor:=0.14 if index==6 else 0.105
		var source:=Rect2(Vector2(index%4,int(index/4))*cell,cell)
		var anchor:=Vector2(cell.x*0.48,cell.y*0.94)
		if index==6:
			source=Rect2(768,470,384,540)
			anchor=Vector2(184,517)
		draw_set_transform(Vector2.ZERO,0,Vector2(direction,1))
		draw_texture_rect_region(crouch_sheet,Rect2(-anchor*scale_factor,source.size*scale_factor),source)
		return
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

func lens_offset()->Vector2:
	# Measured front-glass locations, in the same source coordinates/anchors as the art.
	var point:=Vector2(13.3,-45.6)
	if pose in ["crouch","crouch_walk","crouch_film"]:
		var index:=0
		if pose=="crouch_walk":index=[1,2,3,4][int(pose_time*8)%4]
		elif pose=="crouch_film":index=5
		var lenses:=[Vector2(365,227),Vector2(321,226),Vector2(357,226),Vector2(356,227),Vector2(370,221),Vector2(357,198)]
		point=(lenses[index]-Vector2(184.32,481.28))*0.105
	elif aiming_up and pose in ["film","film_run"]:
		point=(Vector2(310,56)-Vector2(184,517))*0.14
	elif pose in ["run","film_run"]:
		var index:=int(pose_time*stride_rate)%8
		if reverse_stride:index=7-index
		var lenses:=[Vector2(359,140),Vector2(803,138),Vector2(1230,140),Vector2(1707,135),Vector2(386,574),Vector2(815,568),Vector2(1235,571),Vector2(1707,573)]
		var frame:Dictionary=_atlas.run[index]
		point=(lenses[index]-Vector2(frame.anchor[0],frame.anchor[1]))*float(frame.scale)
	elif pose in ["jump","fall","land","hurt"]:
		var index:=3
		if pose=="jump":index=0 if pose_time<0.045 else (1 if pose_time<0.20 else 2)
		elif pose=="land":index=4+mini(1,int(pose_time*10))
		elif pose=="hurt":index=6+mini(1,int(pose_time*5))
		var frame:Dictionary=_atlas.air[index]
		var box:Array=frame.rect
		var lenses:=[Vector2(300,257),Vector2(670,166),Vector2(1052,167),Vector2(1430,165),Vector2(305,794),Vector2(671,725),Vector2(1036,689),Vector2(1445,682)]
		point=(lenses[index]-Vector2(frame.anchor[0],frame.anchor[1]))*float(frame.scale)
	return point*Vector2(direction,1)
