extends "res://scripts/chapter_enemy.gd"
var animation_clock := 0.0
var aware := false
func setup(name: String, point: Vector2, limits: Vector2) -> void:
 super.setup(name,point,limits)
 spec=spec.duplicate()
 spec.capture=0.95 if kind=="skeleton" else 1.35
 spec.recover=0.8 if kind=="skeleton" else 1.0
 spec.windup=0.55 if kind=="skeleton" else 0.65
 spec.speed=170.0 if kind=="skeleton" else 260.0
 spec.wait=0.7
func advance(delta: float,target: Vector2,filming: bool,facing: int,lens: Vector2) -> Dictionary:
 animation_clock+=delta
 aware=absf(target.x-position.x)<245 and absf(target.y-origin.y)<65
 if phase=="watch":
  if aware:
   direction=-1 if target.x<position.x else 1
   if absf(target.x-position.x)>100:position.x=clampf(position.x+direction*58*delta,bounds.x,bounds.y)
  else:
   position.x+=direction*26*delta
   if position.x<=bounds.x:direction=1
   elif position.x>=bounds.y:direction=-1
   position.x=clampf(position.x,bounds.x,bounds.y)
 var result=super.advance(delta,target,filming,facing,lens)
 if filming and in_view(target,facing) and phase in ["watch","windup","attack"]:
  result.captured=expose(delta*0.20,lens)
 return result
