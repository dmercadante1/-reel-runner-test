extends "res://scripts/capture_effect.gd"
## Narrow luminous exposure beam and amber-edged photographic ribbon.
func _draw() -> void:
 if not active:return
 var tip:=endpoint if locked else lens+Vector2(direction*(245 if powered else 185),0)
 var normal:Vector2=(tip-lens).normalized().orthogonal()
 var spread:=20.0 if powered else 10.0
 for layer in range(5,0,-1):
  var width:=spread*layer*0.65
  draw_colored_polygon(PackedVector2Array([lens-normal,lens+normal,tip+normal*width,tip-normal*width]),Color(0.25,0.56,0.82,0.018))
 # Fine uneven shafts make the light feel projected through air.
 for i in range(9):
  var n:=sin(i*1.72+clock*0.8)
  draw_line(lens+normal*n,tip+normal*n*spread,Color(0.63,0.82,0.91,0.075),0.4,true)
 draw_circle(lens,4,Color(0.58,0.8,1,0.15))
 draw_circle(lens,1.3,Color("d8edf1"))
 if not locked and not powered:return
 for ribbon in range(2 if powered else 1):
  var pts:=PackedVector2Array()
  for j in range(49):
   var t:=j/48.0
   var bend:=sin(t*9-clock*5+ribbon*PI)*sin(t*PI)*13
   pts.append(lens.lerp(tip,t)+normal*bend)
  draw_polyline(pts,Color(0.36,0.69,0.87,0.12),10,true)
  draw_polyline(pts,Color("8d9683"),5.0,true)
  draw_polyline(pts,Color("263a47"),3.5,true)
  for j in range(25):
   var t:=fposmod(j/25.0-clock*0.48,1)
   var bend:=sin(t*9-clock*5+ribbon*PI)*sin(t*PI)*13
   var point:=lens.lerp(tip,t)+normal*bend
   for side in [-1,1]:draw_circle(point+normal*side*2,0.48,Color("d7d8bd"))
   if j%3==0:draw_line(point-normal*1.3,point+normal*1.3,Color("7f9aa0"),0.6,true)
