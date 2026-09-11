extends "res://scripts/capture_effect.gd"
## Twelve drawn frames: three authored aim directions, four phases each.
var artwork:Texture2D
var aim_row:=0
var drawn_tip:=Vector2.ZERO
func _ready()->void:
 super._ready()
 artwork=load("res://assets/courtyard-v3/capture.png")
 texture_filter=CanvasItem.TEXTURE_FILTER_LINEAR
 var light:=ShaderMaterial.new();light.shader=load("res://shaders/illustrated_light.gdshader");material=light
func _draw()->void:
 if not active or artwork==null:return
 var target:=endpoint if locked else lens+Vector2(direction*155,0)
 var axis:=target-lens
 var angle:=absf(atan2(axis.y,absf(axis.x)))
 aim_row=2 if angle>deg_to_rad(38) else (1 if angle>deg_to_rad(12) else 0)
 var frame:=0 if reduced_motion else int(clock*14)%4
 # Anchors measured on the authored sheet. Draw only translate/reflect/uniform-scale.
 var starts:=[Vector2(40,170),Vector2(50,198),Vector2(80,268)]
 var spans:=[Vector2(305,0),Vector2(280,-133),Vector2(220,-243)]
 var source:=Rect2(frame*384,[0,335,650][aim_row],384,[300,300,350][aim_row])
 var scale_factor:=clampf(axis.length()/spans[aim_row].length(),0.09,0.85)
 var flip:=Vector2(direction,-1 if axis.y>0 and aim_row>0 else 1)
 draw_set_transform(lens,0,flip*scale_factor)
 draw_texture_rect_region(artwork,Rect2(-starts[aim_row],source.size),source,Color(0.8,0.94,1,1.0 if locked else 0.65))
 if powered:draw_texture_rect_region(artwork,Rect2(-starts[aim_row],source.size),source,Color(0.5,0.8,1,0.65))
 draw_set_transform(Vector2.ZERO)
 drawn_tip=lens+spans[aim_row]*flip*scale_factor
