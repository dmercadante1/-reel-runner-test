extends Node2D
## Authored world placements: five depths, no moving collision geometry.
var camera_x:=0.0
var clock:=0.0
var reduced_motion:=false
var art:Dictionary={}
var lights:Node2D
var haze:Node2D
const KIT_REGIONS=[Rect2(24,180,472,320),Rect2(529,16,472,486),Rect2(1037,230,475,273),Rect2(45,553,448,444),Rect2(548,514,462,486),Rect2(1050,648,453,350)]
const TORCHES=[140.0,940.0,1700.0,2560.0,3110.0,3980.0,4780.0]
func _ready()->void:
 texture_filter=CanvasItem.TEXTURE_FILTER_LINEAR
 var key:=ShaderMaterial.new();key.shader=load("res://shaders/scenery_depth.gdshader");material=key
 for name in ["sky","castle","forest","kit","ambient"]:art[name]=load("res://assets/courtyard-v3/%s.png"%name)
 lights=Node2D.new();add_child(lights)
 var light:=ShaderMaterial.new();light.shader=load("res://shaders/illustrated_light.gdshader");lights.material=light
 lights.draw.connect(_draw_lights)
 haze=Node2D.new();add_child(haze);haze.material=light;haze.draw.connect(_draw_haze)
func advance(x:float,t:float,still:bool)->void:
 camera_x=x;clock=t;reduced_motion=still;queue_redraw();lights.queue_redraw();haze.queue_redraw()
func piece(canvas:Node2D,index:int,dest:Rect2,tint:Color=Color.WHITE)->void:
 canvas.draw_texture_rect_region(art.kit,dest,KIT_REGIONS[index],tint)
func _draw()->void:
 if art.is_empty():return
 # Natural image proportions; only a small crop of sky moves over the whole stage.
 draw_texture_rect(art.sky,Rect2(-camera_x*0.012,-8,708,398),false)
 # Castle starts beyond the right edge, progressively revealed rather than tiled.
 draw_texture_rect(art.castle,Rect2(300-camera_x*0.07,32,760,428),false,Color(0.9,0.95,1,0.72))
 # Continuous wooded ground sits behind the walkway; repeat edges remain under masonry.
 for i in range(-1,5):
  var x:=i*510-camera_x*0.24
  if x>650 or x+610<0:continue
  draw_texture_rect(art.forest,Rect2(x,0,520,293),false,Color(0.67,0.73,0.82,0.88))
 # Estate boundary has its own slower motion and visibly supported piers.
 for i in range(-1,45):
  var x:=i*122-camera_x*0.57
  if x>680 or x+230<0:continue
  piece(self,2,Rect2(x,200,124,71),Color(0.60,0.65,0.73))
 # Near landmarks are fixed in world space at the same speed as the player platforms.
 for entry in [[80,205,64],[1160,180,90],[2690,153,115],[4110,170,100],[4980,142,128]]:
  var x:float=entry[0]-camera_x
  if x>690 or x+150<0:continue
  piece(self,1,Rect2(x,entry[1],124,entry[2]))
 for x0 in [40,780,1860,2900,3680,4630]:
  var x:float=x0-camera_x
  if x>680 or x+150<0:continue
  piece(self,4,Rect2(x,110,150,160),Color(0.57,0.61,0.68))
 for x0 in [2460,4360]:
  var x:float=x0-camera_x
  if x>680 or x+115<0:continue
  piece(self,3,Rect2(x,156,115,114))
func ambient_frame(canvas:Node2D,row:int,frame:int,dest:Rect2,color:Color=Color.WHITE)->void:
 var cell:=Vector2(384,1024.0/3.0)
 canvas.draw_texture_rect_region(art.ambient,dest,Rect2(Vector2(frame,row)*cell,cell),color)
func _draw_lights()->void:
 if art.is_empty():return
 var frame:=0 if reduced_motion else int(clock*9)%4
 for x0 in TORCHES:
  var x:float=x0-camera_x
  if x< -70 or x>710:continue
  for j in range(6,0,-1):lights.draw_circle(Vector2(x,242),j*9,Color(0.72,0.25,0.035,0.012))
  ambient_frame(lights,0,frame,Rect2(x-19,228,38,42))
 for x0 in [2460,4360]:
  var x:float=x0-camera_x
  if x< -150 or x>700:continue
  ambient_frame(lights,1,frame,Rect2(x+61,185,27,49),Color(0.65,0.82,1,0.8))
func _draw_haze()->void:
 if art.is_empty():return
 for i in range(-1,13):
  var drift:=0.0 if reduced_motion else sin(clock*0.09+i)*15
  var x:=i*290-camera_x*0.34+drift
  if x< -340 or x>700:continue
  ambient_frame(haze,2,i%4 if i>=0 else 0,Rect2(x,215,340,110),Color(0.48,0.66,0.92,0.18))
