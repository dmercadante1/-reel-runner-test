extends Node2D
## Blue volumetric cone, perforated moving film ribbons and inward capture sparks.
var active := false
var powered := false
var lens := Vector2.ZERO
var endpoint := Vector2.ZERO
var direction := 1
var locked := false
var clock := 0.0
var reduced_motion := false
var bursts: Array = []

func _ready() -> void:
 z_index=5

func pulse(at: Vector2, strong: bool=false) -> void:
 bursts.append({"point":at,"age":0.0,"strong":strong})

func advance(delta: float) -> void:
 clock+=delta
 for i in range(bursts.size()-1,-1,-1):
  bursts[i].age+=delta
  if bursts[i].age>0.7: bursts.remove_at(i)
 queue_redraw()

func _draw() -> void:
 if active:
  var tip:=endpoint if locked else lens+Vector2(direction*(245 if powered else 185),0)
  var axis:=tip-lens
  var normal:=axis.normalized().orthogonal()
  var breadth:=38.0 if powered else 23.0
  var beat:=1.0 if reduced_motion else 0.93+sin(clock*17)*0.07
  for i in range(5,0,-1):
   var w:=breadth*float(i)/3.0
   draw_colored_polygon(PackedVector2Array([lens+normal*2,lens-normal*2,tip-normal*w,tip+normal*w]),Color(0.08,0.43,1.0,0.035*beat))
  draw_colored_polygon(PackedVector2Array([lens,tip-normal*breadth*0.45,tip+normal*breadth*0.45]),Color(0.42,0.78,1.0,0.15))
  draw_line(lens,tip,Color(0.53,0.84,1.0,0.55),2.2,true)
  draw_circle(lens,10 if powered else 6,Color(0.15,0.6,1,0.15))
  draw_circle(lens,3.5,Color(0.8,0.96,1,0.95))
  if locked or powered:
   for ribbon in range(3 if powered else 2):
    var points:=PackedVector2Array()
    var phase:=float(ribbon)*PI
    for j in range(37):
     var t:=j/36.0
     var wave:=sin(t*12-clock*7+phase)*sin(t*PI)*(12 if powered else 8)
     points.append(lens.lerp(tip,t)+normal*wave)
    draw_polyline(points,Color(0.1,0.4,0.9,0.36),9,true)
    draw_polyline(points,Color(0.65,0.88,1,0.95),4,true)
    draw_polyline(points,Color(0.035,0.095,0.18,0.92),2.0,true)
    for j in range(1,18):
     var t:=fmod(j/18.0-clock*0.6,1.0)
     if t<0: t+=1
     var wave:=sin(t*12-clock*7+phase)*sin(t*PI)*(12 if powered else 8)
     var p:=lens.lerp(tip,t)+normal*wave
     draw_line(p-normal*1.8,p+normal*1.8,Color(0.75,0.94,1,0.96),0.8,true)
  for i in range(16 if not reduced_motion else 5):
   var t:=fmod(i/16.0-clock*0.7,1.0)
   if t<0:t+=1
   var p:=lens.lerp(tip,t)+normal*sin(i*3.7+clock*2)*breadth*t*0.5
   draw_circle(p,0.5+(1-t)*0.6,Color(0.7,0.94,1,0.65))
 for burst in bursts:
  var t:float=burst.age/0.7
  var p:Vector2=burst.point
  draw_arc(p,3+t*(26 if burst.strong else 17),0,TAU,32,Color(0.36,0.79,1,1-t),1.5,true)
  for i in range(12):
   var a:=i*TAU/12
   var q:=p+Vector2(cos(a),sin(a))*t*24
   draw_line(q,q+Vector2(cos(a),sin(a))*3,Color(0.7,0.94,1,1-t),1,true)
