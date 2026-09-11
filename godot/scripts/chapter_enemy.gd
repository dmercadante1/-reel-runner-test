extends RefCounted
## Deterministic enemy encounter state. Rendering and collision remain in the room.
const SPECS := {
 "skeleton":{"wait":0.7,"windup":0.85,"attack":0.38,"recover":2.0,"speed":175.0,"capture":1.2,"height":66.0},
 "werewolf":{"wait":0.6,"windup":0.85,"attack":0.55,"recover":2.2,"speed":200.0,"capture":1.6,"height":75.0},
 "ghoul":{"wait":0.85,"windup":0.9,"attack":0.55,"recover":2.4,"speed":75.0,"capture":1.3,"height":63.0},
 "monster":{"wait":1.0,"windup":1.2,"attack":0.35,"recover":2.8,"speed":30.0,"capture":2.4,"height":88.0},
 "phantom":{"wait":0.9,"windup":0.85,"attack":0.55,"recover":2.2,"speed":90.0,"capture":1.5,"height":70.0},
 "vampire":{"wait":0.65,"windup":0.7,"attack":0.42,"recover":1.9,"speed":245.0,"capture":1.9,"height":72.0},
 "dracula":{"wait":0.7,"windup":1.0,"attack":0.65,"recover":2.6,"speed":150.0,"capture":7.5,"height":92.0}}
var kind := "skeleton"
var position := Vector2(490,230)
var origin := Vector2(490,230)
var bounds := Vector2(350,570)
var phase := "watch"
var clock := 0.0
var exposure := 0.0
var direction := -1
var hit_used := false
var attacks := 0
var shot_emitted := false
var capture_origin := Vector2.ZERO
var capture_to := Vector2.ZERO
var boss_phase := 1
var spec: Dictionary

func setup(name: String, point: Vector2, limits: Vector2) -> void:
 kind=name
 spec=SPECS[name]
 position=point
 origin=point
 bounds=limits

func vulnerable() -> bool:
 return phase=="exposed"

func in_view(target: Vector2, facing: int, distance: float=185.0) -> bool:
 return absf(position.x-target.x)<distance and absf(position.y-target.y)<47 and (position.x-target.x)*facing>0

func expose(amount: float, lens: Vector2) -> bool:
 if phase in ["capturing","captured"]: return false
 exposure=minf(float(spec.capture),exposure+amount)
 if exposure>=float(spec.capture)-0.00001:
  phase="capturing"
  clock=0.0
  capture_origin=position
  capture_to=lens
  return true
 return false

func super_hit(target: Vector2, facing: int, lens: Vector2) -> bool:
 if not in_view(target,facing,245.0) or phase in ["capturing","captured"]: return false
 if kind=="dracula" and not vulnerable(): return false
 if kind!="dracula": phase="exposed"
 return expose(1.65 if kind=="dracula" else 2.8,lens)

func advance(delta: float,target: Vector2,filming: bool,facing: int,lens: Vector2) -> Dictionary:
 var result := {"hit":false,"captured":false,"projectile":""}
 clock+=delta
 if phase=="captured": return result
 if phase=="capturing":
  capture_to=lens
  var t:=clampf(clock/0.85,0,1)
  position=capture_origin.lerp(lens,1.0-pow(1.0-t,2.0))+Vector2(0,-sin(t*PI)*24)
  if t>=1: phase="captured"
  return result
 boss_phase=1+mini(2,int(exposure/2.5)) if kind=="dracula" else 1
 var near:=absf(target.x-position.x)<220 and absf(target.y-origin.y)<100
 match phase:
  "watch":
   position.y=origin.y
   if kind=="phantom": position.y-=sin(clock*3)*7
   if near and clock>=float(spec.wait):
    direction=-1 if target.x<position.x else 1
    phase="windup"
    clock=0
  "windup":
   if clock>=float(spec.windup)/(1.0+(boss_phase-1)*0.12):
    phase="attack"
    clock=0
    attacks+=1
    hit_used=false
    shot_emitted=false
  "attack":
   var duration:float=spec.attack
   position.x=clampf(position.x+direction*float(spec.speed)*delta,bounds.x,bounds.y)
   if kind=="werewolf": position.y=origin.y-sin(clampf(clock/duration,0,1)*PI)*48
   if not shot_emitted:
    shot_emitted=true
    if kind in ["ghoul","phantom","monster"]: result.projectile=kind
    elif kind=="dracula": result.projectile="wave" if attacks%2==0 else "orb"
   if not hit_used and absf(target.x-position.x)<(48 if kind!="monster" else 62) and absf(target.y-position.y)<29:
    result.hit=true
    hit_used=true
   if clock>=duration:
    position.y=origin.y
    phase="exposed"
    clock=0
  "exposed":
   if clock>=float(spec.recover):
    phase="watch"
    clock=0
    if kind in ["phantom","dracula"]:
     position.x=clampf(target.x+(-140 if target.x>320 else 140),bounds.x,bounds.y)
   elif filming and in_view(target,facing):
    result.captured=expose(delta,lens)
 return result
