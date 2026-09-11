extends "res://scripts/capture_effect.gd"
var artwork:Texture2D
func _draw() -> void:
 if not active:return
 if artwork==null:artwork=load("res://assets/courtyard-scroll/film-fx.png")
 var tip:=endpoint if locked else lens+Vector2(direction*(245 if powered else 185),0)
 var axis:=tip-lens
 var normal:=axis.normalized().orthogonal()
 var length:=axis.length()
 draw_set_transform(lens,axis.angle())
 var height:=78.0 if powered else 55.0
 draw_texture_rect_region(artwork,Rect2(0,-height*0.55,length,height),Rect2(50,70,1486,565),Color(0.8,0.92,1,0.6 if locked else 0.42))
 draw_set_transform(Vector2.ZERO)
 if not locked and not powered:return
 var half:=4.2 if powered else 3.0
 for ribbon in range(2 if powered else 1):
  for i in range(32):
   var t:=i/32.0
   var u:=(i+1)/32.0
   var a:Vector2=(lens.lerp(tip,t)+normal*sin(t*9-clock*5+ribbon*PI)*sin(t*PI)*12).snapped(Vector2(0.5,0.5))
   var b:Vector2=(lens.lerp(tip,u)+normal*sin(u*9-clock*5+ribbon*PI)*sin(u*PI)*12).snapped(Vector2(0.5,0.5))
   var x:=36+fposmod(t*2-clock*0.7,1)*1465
   var x2:=minf(x+92,1500)
   var uv:=PackedVector2Array([Vector2(x,720),Vector2(x,894),Vector2(x2,894),Vector2(x2,720)])
   for j in range(4):uv[j]/=artwork.get_size()
   draw_polygon(PackedVector2Array([a-normal*half,a+normal*half,b+normal*half,b-normal*half]),PackedColorArray([Color.WHITE,Color.WHITE,Color.WHITE,Color.WHITE]),uv,artwork)
