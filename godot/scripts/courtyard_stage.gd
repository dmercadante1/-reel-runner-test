extends "res://scripts/gothic_room.gd"
## Connected first-pass chapter. Original single-room previews remain independent.
var rooms: Array = preload("res://scripts/courtyard_stage_data.gd").all()
var passage_left := 0.0
var passage_from := Vector2.ZERO
var passage_to := Vector2.ZERO
var death_left := 0.0
var camera_x := 0.0
var key_unlocked := false
var key_collected := false
const WIDTH := 7680.0
const KEY := Vector2(3700,246)
var room_index := 0
var room: Dictionary = {}
var enemies: Array = []
var surfaces: Array[Rect2] = []
var projectiles: Array = []
var rare_pickups: Array[Vector2] = []
var super_charges := 0
var super_left := 0.0
var super_requested := false
var room_entry_super := 0
var total_captures := 0
var chapter_time := 0.0
var transition_left := 0.0
var banner_left := 0.0
var gate_open := false
var reduced_motion := false
var _enemy_canvas: Node2D
var _hud: Node2D
var effect: Node2D
var enemy_atlas: Dictionary = {}
var _chapter_ready := false
var _save_available := true
var _capture_audio: AudioStreamPlayer
var _super_audio: AudioStreamPlayer
var toast := ""
var toast_left := 0.0

func _ready() -> void:
 super._ready()
 _ambient.stream=load("res://assets/chapter/audio/night.wav")
 _ambient.stream.loop_mode=AudioStreamWAV.LOOP_FORWARD
 _ambient.stream.loop_end=705600
 _ambient.volume_db=-7
 _capture_audio=AudioStreamPlayer.new()
 _capture_audio.stream=load("res://assets/chapter/audio/capture.wav")
 _capture_audio.volume_db=-6
 add_child(_capture_audio)
 _super_audio=AudioStreamPlayer.new()
 _super_audio.stream=load("res://assets/chapter/audio/super.wav")
 _super_audio.volume_db=-6
 add_child(_super_audio)
 _enemy_canvas=Node2D.new()
 _enemy_canvas.z_index=3
 var mat:=ShaderMaterial.new()
 mat.shader=load("res://shaders/chapter_sprite.gdshader")
 _enemy_canvas.material=mat
 add_child(_enemy_canvas)
 _enemy_canvas.draw.connect(_draw_enemies)
 effect=preload("res://scripts/courtyard_capture.gd").new()
 add_child(effect)
 _hud=Node2D.new()
 _hud.z_index=10
 add_child(_hud)
 _hud.draw.connect(_draw_hud)
 var foreground:=Node2D.new()
 foreground.z_index=6
 add_child(foreground)
 foreground.draw.connect(_draw_foreground)
 _hud.draw.connect(func():foreground.queue_redraw())
 player.z_index=2
 _keyed.z_index=1
 _chapter_ready=true
 player.tuning=player.tuning.duplicate()
 player.tuning.run_speed=190.0
 player.tuning.acceleration=2300.0
 player.tuning.braking=2700.0
 player.tuning.jump_speed=-355.0
 player.film_strafe=true
 visual.stride_rate=15.0
 for name in ["trees","enemies","objects"]:
  var path:="res://assets/courtyard-scroll/%s.png"%name
  if ResourceLoader.exists(path):_textures[name]=load(path)
 var saved:=0
 load_room(saved)
 _phase="ready"
 get_tree().paused=true
 _report()

func _reset() -> void:
 if not _chapter_ready:
  super._reset()
  return
 super_charges=0
 total_captures=0
 chapter_time=0
 load_room(0)

func load_room(index: int) -> void:
 Controls.release_all()
 camera_x=0
 _world.position=Vector2.ZERO
 key_unlocked=false
 key_collected=false
 room_index=clampi(index,0,rooms.size()-1)
 room=rooms[room_index]
 for child in _world.get_children():
  if child!=player:
   _world.remove_child(child)
   child.queue_free()
 surfaces.clear()
 for box in room.surfaces:
  var rect:=Rect2(box[0],box[1],box[2],box[3])
  surfaces.append(rect)
  _floor(rect)
 _floor(Rect2(-20,0,20,360))
 _floor(Rect2(WIDTH,0,20,360))
 var exit_point:=Vector2(room.exit[0],room.exit[1])
 _gate_body=_floor(Rect2(exit_point.x-16,exit_point.y-110,8,110))
 _checkpoint=Vector2(room.spawn[0],room.spawn[1])
 player.reset_at(_checkpoint)
 player.facing=1
 player.collision_mask=3
 stock.reset()
 _health=4
 _invincible=0
 _hurt_left=0
 _land_left=0
 _turn_left=0
 _record=false
 _reload_requested=false
 _drop_requested=false
 _drop_left=0
 _completed=false
 _review=false
 _pickups=0
 _hits=0
 _jumps=0
 super_left=0
 super_requested=false
 room_entry_super=super_charges
 enemies.clear()
 projectiles.clear()
 for item in room.enemies:
  var enemy=preload("res://scripts/courtyard_enemy.gd").new()
  enemy.setup(item[0],Vector2(item[1],item[2]),Vector2(item[3],item[4]))
  enemies.append(enemy)
 _reels.clear()
 for item in room.reels: _reels.append(Vector2(item[0],item[1]))
 rare_pickups.clear()
 for item in room.rare: rare_pickups.append(Vector2(item[0],item[1]))
 gate_open=false
 banner_left=3
 toast=""
 toast_left=0
 if effect!=null:
  effect.active=false
  effect.bursts.clear()
 if OS.has_feature("web"):
  JavaScriptBridge.eval("try{localStorage.setItem('mwmc-courtyard-scroll-v1','%d')}catch(e){}"%room_index)
 queue_redraw()

func _input(event: InputEvent) -> void:
 super._input(event)
 if _phase=="running" and event.is_action_pressed("super_shot") and not event.is_echo(): super_requested=true

func _web_command(args: Array) -> void:
 if args.size()>=2 and str(args[0])=="super_shot":
  if bool(args[1]) and _phase=="running": super_requested=true
  return
 super._web_command(args)

func _command(name: String,value: bool=true) -> void:
 if _capture_audio!=null:
  if name=="sound" and not value:
   _capture_audio.stop()
   _super_audio.stop()
  elif name in ["pause","focus_lost","pause_game","resume"]:
   _capture_audio.stream_paused=name!="resume"
   _super_audio.stream_paused=name!="resume"
 if name=="new_game":
  total_captures=0
  chapter_time=0
  super_charges=0
  room_entry_super=0
  load_room(0)
  super._command("resume")
 elif name=="reduced_motion":
  reduced_motion=value
  if effect!=null:effect.reduced_motion=value
 elif name=="review":
  # Character review uses the unchanged coherent action cycle, then Retry returns here.
  super._command(name,value)
 elif name=="resume" and _phase=="chapter_complete":
  _command("new_game")
 else:
  if name in ["pause","focus_lost","pause_game"]:super_requested=false
  super._command(name,value)

func lens_point() -> Vector2:
 return player.position+Vector2(15*player.facing,-43)

func damage() -> void:
 if _invincible>0 or _phase!="running":return
 _health-=1
 _hits+=1
 _invincible=1.3
 _hurt_left=0.36
 _record=false
 _chirp(0.45)
 if _health<=0:
  death_left=1.5
  _phase="defeated"
  Controls.release_all()
  player.clear_buffered_input()
  get_tree().paused=true

func fire_super() -> bool:
 if super_charges<=0 or super_left>0 or stock.reload_left>0 or _phase!="running":return false
 super_charges-=1
 super_left=0.95
 var count:=0
 for e in enemies:
  if e.super_hit(player.position,player.facing,lens_point()):
   count+=1
   total_captures+=1
   effect.pulse(e.capture_origin,true)
 effect.pulse(lens_point(),true)
 if _sound:_super_audio.play()
 toast="SUPER SHOT — silver film unleashed"
 toast_left=2
 return true

func _physics_process(delta: float) -> void:
 if not _chapter_ready:return
 if _phase=="passage":
  passage_left-=delta
  player.position=passage_from.lerp(passage_to,smoothstep(0,1,1-passage_left/1.4))
  if passage_left<=0:
   player.position=passage_to
   super._command("resume")
 if _phase=="defeated":
  death_left-=delta
  if death_left<=0:
   _reset()
   super._command("resume")
 if _phase=="review":
  super._physics_process(delta)
  player.position.y+=float(room.floor)-230.0
  if _enemy_canvas!=null:_enemy_canvas.queue_redraw()
  if _hud!=null:_hud.queue_redraw()
  return
 if _phase=="transition":
  transition_left-=delta
  if transition_left<=0:
   load_room(room_index+1)
   super._command("resume")
 elif _phase=="running":
  _time+=delta
  chapter_time+=delta
  banner_left=maxf(0,banner_left-delta)
  toast_left=maxf(0,toast_left-delta)
  _drop_left=maxf(0,_drop_left-delta)
  if _drop_requested and player.is_on_floor() and key_unlocked and (absf(player.position.x-6280)<38 or absf(player.position.x-3730)<30):
   passage_from=player.position
   passage_to=Vector2(3730 if player.position.x>5000 else 6280,270)
   passage_left=1.4
   _phase="passage"
   Controls.release_all()
   player.velocity=Vector2.ZERO
   get_tree().paused=true
  if _drop_requested and player.is_on_floor():
   for rect in surfaces:
    if rect.size.y==10 and absf(player.position.y-rect.position.y)<3 and player.position.x>=rect.position.x-8 and player.position.x<=rect.end.x+8:
     _drop_left=0.25
     player.position.y+=2
     break
  _drop_requested=false
  player.collision_mask=1 if _drop_left>0 else 3
  _invincible=maxf(0,_invincible-delta)
  _hurt_left=maxf(0,_hurt_left-delta)
  _land_left=maxf(0,_land_left-delta)
  _turn_left=maxf(0,_turn_left-delta)
  if player.facing!=_last_facing:_turn_left=0.12
  _last_facing=player.facing
  if _reload_requested and stock.start_reload():_chirp(0.8)
  _reload_requested=false
  super_left=maxf(0,super_left-delta)
  if super_requested:fire_super()
  super_requested=false
  _record=stock.advance(delta,Input.is_action_pressed("record") and _hurt_left<=0)
  for i in range(_reels.size()-1,-1,-1):
   if player.position.distance_to(_reels[i]+Vector2(0,16))<28 and stock.collect_reel():
    _reels.remove_at(i)
    _pickups+=1
    _chirp(1.6)
  for i in range(rare_pickups.size()-1,-1,-1):
   if player.position.distance_to(rare_pickups[i]+Vector2(0,16))<28 and super_charges<2:
    rare_pickups.remove_at(i)
    super_charges+=1
    effect.pulse(player.position-Vector2(0,30),true)
    _chirp(2.0)
    toast="SILVER REEL — Super Shot ready (X)"
    toast_left=3
  var captured:=0
  for e in enemies:
   var old:String=e.phase
   var result:Dictionary=e.advance(delta,player.position,_record,player.facing,lens_point())
   if e.phase=="windup" and old!="windup":_chirp(0.55)
   if result.hit:damage()
   if result.captured:
    total_captures+=1
    if total_captures%4==0:_health=mini(4,_health+1)
    effect.pulse(e.capture_origin)
    if _sound:_capture_audio.play()
   if result.projectile!="":_spawn_projectiles(e,result.projectile)
   if e.phase=="captured":captured+=1
  for i in range(projectiles.size()-1,-1,-1):
   var p:Dictionary=projectiles[i]
   p.position+=p.velocity*delta
   p.life-=delta
   if p.life<=0 or p.position.x<0 or p.position.x>WIDTH:
    projectiles.remove_at(i)
   elif p.position.distance_to(player.position-Vector2(0,25 if p.kind=="orb" else 8))<17:
    damage()
    projectiles.remove_at(i)
  if captured>=int(room.required) and not key_unlocked:
   key_unlocked=true
   toast="The shrine has awakened. Return to the courtyard fountain."
   toast_left=5
  if key_unlocked and not key_collected and player.position.distance_to(KEY+Vector2(0,16))<35:
   key_collected=true
   toast="IRON KEY FOUND — the Catacombs gate is open."
   toast_left=4
   _chirp(1.8)
  gate_open=key_collected
  _gate_body.collision_layer=0 if gate_open else 1
  if gate_open and player.position.x>7580 and absf(player.position.y-float(room.exit[1]))<22:
   Controls.release_all()
   player.clear_buffered_input()
   player.velocity=Vector2.ZERO
   get_tree().paused=true
   if room_index==rooms.size()-1:
    _phase="chapter_complete"
    _completed=true
   else:
    _phase="transition"
    transition_left=1.2
  var next:="idle"
  if _hurt_left>0:next="hurt"
  elif stock.reload_left>0:next="reload"
  elif not player.is_on_floor():next="jump" if player.velocity.y< -15 else "fall"
  elif _land_left>0:next="land"
  elif _turn_left>0:next="turn"
  elif absf(player.velocity.x)>5:next="film_run" if _record or super_left>0 else "run"
  elif _record or super_left>0:next="film"
  visual.reverse_stride=_record and player.velocity.x*player.facing<0
  _pose_time=0 if next!=_pose else _pose_time+delta
  _pose=next
  visual.set_pose(_pose,0.65-stock.reload_left if _pose=="reload" else _pose_time,player.facing)
  visual.modulate.a=0.5 if _invincible>0 and int(_time*8)%2==0 and not reduced_motion else 1
  effect.active=_record or super_left>0
  effect.powered=super_left>0
  effect.direction=player.facing
  effect.lens=lens_point()
  effect.locked=false
  var nearest:=10000.0
  for e in enemies:
   if e.phase=="capturing" or (e.in_view(player.position,player.facing) and e.vulnerable()):
    var distance:float=player.position.distance_to(e.position)
    if distance<nearest:
     nearest=distance
     effect.endpoint=e.position-Vector2(0,30 if e.phase!="capturing" else 0)
     effect.locked=true
     if e.phase=="capturing":effect.active=true
  effect.advance(delta)
 _report_clock+=delta
 if _phase in ["running","passage"]:
  camera_x=lerpf(camera_x,clampf(player.position.x-290,0,WIDTH-640),1-exp(-delta*9))
 _world.position.x=-camera_x
 _keyed.position.x=-camera_x
 _enemy_canvas.position.x=-camera_x
 effect.position.x=-camera_x
 if _report_clock>0.1:
  _report_clock=0
  _report()
 queue_redraw()
 _keyed.queue_redraw()
 _enemy_canvas.queue_redraw()
 _hud.queue_redraw()

func _spawn_projectiles(enemy,kind: String) -> void:
 var wave:=kind in ["monster","wave"]
 var point:Vector2=enemy.position-Vector2(0,8 if wave or kind=="ghoul" else 37)
 var directions:=[enemy.direction]
 if wave:directions=[-1,1]
 for dir in directions:
  projectiles.append({"position":point,"velocity":Vector2(dir*(135 if kind!="dracula" else 160),0),"life":4.0,"kind":"wave" if wave else ("poison" if kind=="ghoul" else "orb")})

func _report() -> void:
 if not _chapter_ready or _bridge==null:return
 var foe_states:=[]
 for e in enemies:foe_states.append({"kind":e.kind,"phase":e.phase,"clock":e.clock,"x":e.position.x,"y":e.position.y,"exposure":e.exposure,"required":e.spec.capture,"boss_phase":e.boss_phase})
 var shots:=[]
 for p in projectiles:shots.append({"x":p.position.x,"y":p.position.y,"vx":p.velocity.x,"kind":p.kind})
 var sorted:=_samples.duplicate()
 sorted.sort()
 _bridge.report(JSON.stringify({"build":"courtyard-scroll-01","camera_x":camera_x,"world_width":WIDTH,"key_unlocked":key_unlocked,"key_collected":key_collected,"phase":_phase,"stage":room.get("stage",""),"room":room_index,"room_name":room.get("name",""),"room_count":rooms.size(),"x":player.position.x,"feet":player.position.y,"vx":player.velocity.x,"vy":player.velocity.y,"grounded":player.is_on_floor(),"pose":_pose,"facing":player.facing,"projectiles":shots,"film":stock.film,"film_capacity":stock.CAPACITY,"spares":stock.spares,"reload_left":stock.reload_left,"reloads":stock.reloads,"recording":_record,"super_charges":super_charges,"super_left":super_left,"health":_health,"hits":_hits,"jumps":_jumps,"pickups":_pickups,"gate_open":gate_open,"enemies":foe_states,"captures":total_captures,"chapter_seconds":chapter_time,"viewport":[get_window().size.x,get_window().size.y],"design_viewport":[640,360],"fps":Engine.get_frames_per_second(),"frame_p95_ms":sorted[int((sorted.size()-1)*0.95)] if not sorted.is_empty() else 0.0,"engine":Engine.get_version_info().string,"audio_enabled":_sound,"save_available":_save_available,"actions":{"move_left":Input.is_action_pressed("move_left"),"move_right":Input.is_action_pressed("move_right"),"jump":Input.is_action_pressed("jump"),"record":Input.is_action_pressed("record")}}))


func _draw() -> void:
 if _font==null or room.is_empty():return
 draw_rect(Rect2(0,0,640,360),Color("101b2c"))
 if _textures.has("sky"):
  # One distant castle panorama; it does not restart with each screen.
  draw_texture_rect(_textures.sky,Rect2(-camera_x*0.055,-15,1120,420),false,Color("b4c5d8"))
 if _textures.has("trees"):
  for i in range(-1,6):
   var x:=i*710-camera_x*0.33
   if x>640 or x+720<0:continue
   draw_texture_rect(_textures.trees,Rect2(x,36,720,320),false,Color(0.52,0.65,0.75,0.77))
 draw_set_transform(Vector2(-camera_x,0))
 # Foundation walls give the lower passage its own enclosed architectural rhythm.
 for rect in surfaces:
  if rect.size.y==38 and rect.end.x>camera_x-60 and rect.position.x<camera_x+700:
   draw_rect(Rect2(rect.position+Vector2(0,13),Vector2(rect.size.x,65)),Color("111b26"))
 for reel in _reels:
  if absf(reel.x-camera_x-320)<370:_draw_reel(reel+Vector2(0,sin(_time*3+reel.x)*2),false)
 for reel in rare_pickups:
  if absf(reel.x-camera_x-320)<370:_draw_reel(reel+Vector2(0,sin(_time*2+reel.x)*3),true)
 if key_unlocked and not key_collected:
  draw_circle(KEY,19,Color(0.9,0.75,0.35,0.07))
  _object(self,3,Rect2(KEY-Vector2(17,10),Vector2(34,20)))
 draw_set_transform(Vector2.ZERO)

func _object(canvas: Node2D,index: int,dest: Rect2,color: Color=Color.WHITE) -> void:
 if not _textures.has("objects"):return
 var texture:Texture2D=_textures.objects
 var regions:=[Rect2(25,24,471,435),Rect2(542,25,480,430),Rect2(1170,110,320,280),Rect2(12,624,512,240),Rect2(537,452,560,560),Rect2(1138,393,360,631)]
 canvas.draw_texture_rect_region(texture,dest,regions[index],color)

func _draw_surfaces() -> void:
 if not _textures.has("architecture"):return
 var texture:Texture2D=_textures.architecture
 var cell:=texture.get_size()/Vector2(3,2)
 for rect in surfaces:
  if rect.end.x<camera_x-40 or rect.position.x>camera_x+680:continue
  for x in range(int(maxf(rect.position.x,floor((camera_x-40)/32)*32)),int(minf(rect.end.x,camera_x+680)),32):
   var width:=minf(32,rect.end.x-x)
   _keyed.draw_texture_rect_region(texture,Rect2(x,rect.position.y,width,rect.size.y),Rect2(Vector2(0,cell.y+cell.y*0.065),Vector2(cell.x*width/32,cell.y*(0.23 if rect.size.y==10 else 0.5))))
  _keyed.draw_line(rect.position,Vector2(rect.end.x,rect.position.y),Color("899a9e"),0.7)

func _draw_reel(point: Vector2,rare: bool) -> void:
 if rare:draw_circle(point,13,Color(0.3,0.7,1,0.13))
 _object(self,1 if rare else 0,Rect2(point-Vector2(11,11),Vector2(22,22)))

func _draw_props() -> void:
 if room.is_empty():return
 if _textures.has("architecture"):
  var masonry:Texture2D=_textures.architecture
  var unit:=masonry.get_size()/Vector2(3,2)
  for rect in surfaces:
   if rect.end.x<camera_x-80 or rect.position.x>camera_x+720:continue
   if rect.size.y==20:
    for x in [rect.position.x+8,rect.end.x-24]:
     _keyed.draw_texture_rect_region(masonry,Rect2(x,rect.position.y+15,16,270-rect.position.y-15),Rect2(0,0,unit.x*0.3,unit.y),Color("829097"))
   elif rect.size.y==38:
    for x in range(int(maxf(rect.position.x,camera_x-70)),int(minf(rect.end.x-45,camera_x+700)),90):
     _keyed.draw_texture_rect_region(masonry,Rect2(x,296,65,54),Rect2(Vector2(unit.x*2,0),unit),Color("52616f"))
 _draw_surfaces()
 # Repeated architectural vocabulary, varied spacing and height; landmarks are unique.
 for x in [35,690,1305,2070,2640,3350,4120,4730,5400,6080,6780,7500]:
  if absf(x-camera_x-320)<430:
   _object(_keyed,5,Rect2(x-34,115,68,155),Color("8295a8"))
 _object(_keyed,4,Rect2(3610,175,170,95))
 if absf(KEY.x-camera_x-320)<410:
  _keyed.draw_string(_font,Vector2(3635,163),"THE KEY SHRINE",HORIZONTAL_ALIGNMENT_CENTER,130,9,Color("d1c5a5"))
  if not key_unlocked:_keyed.draw_string(_font,Vector2(3620,176),"Awakens after 12 captures",HORIZONTAL_ALIGNMENT_CENTER,160,7,Color("a0b3c5"))
 if _textures.has("architecture"):
  var t:Texture2D=_textures.architecture
  var c:=t.get_size()/Vector2(3,2)
  _keyed.draw_texture_rect_region(t,Rect2(7580,160,70,110),Rect2(Vector2(c.x*2,0) if gate_open else Vector2(c.x,c.y),c))
  for x in range(150,7600,420):
   if absf(x-camera_x-320)<370:
    _keyed.draw_texture_rect_region(t,Rect2(x,230,18,40),Rect2(Vector2(c.x*2,c.y),c))
 if key_unlocked:
  for x in [3730,6280]:
   _keyed.draw_string(_font,Vector2(x-66,205),"↓ OLD SERVICE PASSAGE",HORIZONTAL_ALIGNMENT_CENTER,132,8,Color("cec79f"))
   _object(_keyed,5,Rect2(x-26,215,52,55))
 if player.position.y>310:
  _keyed.draw_string(_font,Vector2(player.position.x-78,306),"LOWER PASSAGE · stairs lead back up",HORIZONTAL_ALIGNMENT_CENTER,156,7,Color("9bb9c6"))

func _draw_enemies() -> void:
 if not _textures.has("enemies"):return
 var texture:Texture2D=_textures.enemies
 var cell:=texture.get_size()/Vector2(8,2)
 for e in enemies:
  if e.phase=="captured" or absf(e.position.x-camera_x-320)>410:continue
  var frame:=int(e.animation_clock*7)%4
  if e.phase=="watch" and e.aware and Input.is_action_pressed("record"):frame=4
  elif e.phase=="windup":frame=5
  elif e.phase=="attack":frame=6
  elif e.phase in ["exposed","capturing"]:frame=7
  var row:=0 if e.kind=="skeleton" else 1
  var source:=Rect2(Vector2(frame,row)*cell,cell)
  var factor:=float(e.spec.height)/(cell.y*0.88)
  var shrink:=1.0
  var angle:=0.0
  var color:=Color.WHITE
  var anchor:=Vector2(cell.x*0.5,cell.y*0.94)
  var bob:=sin(e.animation_clock*11)*0.65 if e.phase=="watch" else 0.0
  if e.phase=="capturing":
   var t:float=clampf(e.clock/0.85,0,1)
   shrink=maxf(0.03,1-t)
   angle=sin(t*PI)*0.4
   color=Color(0.63,0.85,1,1-t*0.3)
   # Successive photographic exposures wind into the lens alongside the body.
   for j in range(1,4):
    var at:Vector2=e.position.lerp(e.capture_origin,float(j)*0.15)
    _enemy_canvas.draw_set_transform(at,angle,Vector2(-e.direction,1)*factor*shrink*(1+j*0.12))
    _enemy_canvas.draw_texture_rect_region(texture,Rect2(-anchor,cell),source,Color(0.5,0.78,1,0.18/float(j)))
  _enemy_canvas.draw_set_transform(e.position+Vector2(0,bob),angle,Vector2(-e.direction,1)*factor*shrink)
  _enemy_canvas.draw_texture_rect_region(texture,Rect2(-anchor,cell),source,color)
  _enemy_canvas.draw_set_transform(Vector2.ZERO)
  if e.phase=="windup":
   _enemy_canvas.draw_arc(e.position-Vector2(0,float(e.spec.height)*0.55),22,-PI*0.7,-PI*0.3,12,Color(0.9,0.7,0.45,0.7),1,true)
  if e.exposure>0 and e.phase!="capturing":
   _enemy_canvas.draw_rect(Rect2(e.position+Vector2(-14,-float(e.spec.height)-7),Vector2(28,2)),Color("263845"))
   _enemy_canvas.draw_rect(Rect2(e.position+Vector2(-14,-float(e.spec.height)-7),Vector2(28*(1-e.exposure/float(e.spec.capture)),2)),Color("aecfd9"))

func _label(at: Vector2,text: String,size: int=9,color: Color=Color("dce4df")) -> void:
 _hud.draw_string_outline(_font,at,text,HORIZONTAL_ALIGNMENT_LEFT,-1,size,3,Color(0.025,0.04,0.06,0.8))
 _hud.draw_string(_font,at,text,HORIZONTAL_ALIGNMENT_LEFT,-1,size,color)

func _draw_hud() -> void:
 if room.is_empty():return
 for i in range(4):_object(_hud,2,Rect2(12+i*18,10,18,18),Color.WHITE if i<_health else Color(0.2,0.25,0.3,0.7))
 # Perforated film with individual exposed frames rather than a plain status bar.
 _hud.draw_rect(Rect2(14,34,106,13),Color("17232c"))
 for i in range(10):
  var filled:bool=stock.film/stock.CAPACITY>float(i)/10
  _hud.draw_rect(Rect2(16+i*10,37,8,7),Color("a2c9ce") if filled else Color("344553"))
  for y in [35,45]:_hud.draw_rect(Rect2(18+i*10,y,3,1),Color("d0cfb7"))
 for i in range(3):_object(_hud,0,Rect2(131+i*19,30,19,19),Color.WHITE if i<stock.spares else Color(0.2,0.25,0.3,0.6))
 if super_charges>0:
  _object(_hud,1,Rect2(197,30,19,19))
  _label(Vector2(218,43),"×%d"%super_charges)
 var zone:=clampi(int(player.position.x/1280),0,5)
 var names:=["THE OUTER WALL","THE BROKEN WALK","THE IVY GARDEN","THE FOUNTAIN COURT","THE MOON TERRACES","THE CATACOMBS GATE"]
 _label(Vector2(410,20),names[zone],10,Color("d4cfb7"))
 _label(Vector2(410,35),"CAPTURES %d / 12"%mini(total_captures,12),9)
 if key_collected:
  _object(_hud,3,Rect2(553,25,36,21))
  _label(Vector2(410,48),"Key found · reach the eastern gate",8)
 elif key_unlocked:
  _label(Vector2(410,48),"KEY SHRINE %s  %dm"%["←" if player.position.x>KEY.x else "→",int(absf(player.position.x-KEY.x)/10)],8,Color("e2c583"))
 else:_label(Vector2(410,48),"Capture creatures to awaken the key",8)
 if stock.reload_left>0:_label(Vector2(14,60),"RELOADING…",8)
 elif stock.film<=0:_label(Vector2(14,60),"FILM EMPTY · RELOAD",8,Color("e4bc83"))
 if toast_left>0:_label(Vector2(130,84),toast,9,Color("ddcea7"))
 if _phase=="passage":
  _hud.draw_rect(Rect2(0,0,640,360),Color(0.015,0.025,0.04,0.85))
  _label(Vector2(230,170),"THE OLD SERVICE PASSAGE",11)
 if _phase in ["chapter_complete","defeated"]:
  _hud.draw_rect(Rect2(125,112,390,100),Color(0.02,0.035,0.055,0.92))
  _label(Vector2(165,147),"THE COURTYARD IS CAPTURED" if _completed else "THE TAKE WAS LOST",17)
  _label(Vector2(153,175),"The Catacombs await. Courtyard review complete." if _completed else "Retry stage returns you to the Courtyard entrance.",10)
  _label(Vector2(180,196),"%d captures · %.1f minutes"%[total_captures,chapter_time/60],9)


func _draw_foreground() -> void:
 if not _textures.has("trees"):return
 var layer:Node2D=_hud
 # Foreground is drawn on its own node; only edge foliage overlaps the playfield.
 for child in get_children():
  if child is Node2D and child.z_index==6:layer=child;break
 for i in range(7):
  var x:=i*1450-camera_x*1.12-100
  if x>640 or x+110<0:continue
  layer.draw_texture_rect_region(_textures.trees,Rect2(x,180,110,180),Rect2(0,340,430,684),Color(0.3,0.4,0.5,0.7))
