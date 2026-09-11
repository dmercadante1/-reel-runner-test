extends "res://scripts/gothic_room.gd"
## Connected first-pass chapter. Original single-room previews remain independent.
var rooms: Array = preload("res://scripts/courtyard_stage_data.gd").all()
var passage_left := 0.0
var passage_from := Vector2.ZERO
var passage_to := Vector2.ZERO
var death_left := 0.0
var sfx_pool:Array[AudioStreamPlayer]=[]
var sfx_index:=0
var step_clock:=0.0
var film_clock:=0.0
var scenery:Node2D
var half_heart:=false # True means the top heart is half full; _health stores the ceiling.
var heart_icons:Node2D
var _items:Node2D
var world_canvas:CanvasLayer
var _foreground:Node2D
var hearts: Array[Vector2]=[]
var camera_x := 0.0
var key_unlocked := false
var key_collected := false
const WIDTH := 5120.0
const KEY := Vector2(2540,246)
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
 scenery=preload("res://scripts/courtyard_scenery.gd").new()
 add_child(scenery)
 texture_filter=CanvasItem.TEXTURE_FILTER_LINEAR
 _ambient.stream=load("res://assets/chapter/audio/night.wav")
 _ambient.stream.loop_mode=AudioStreamWAV.LOOP_FORWARD
 _ambient.stream.loop_end=705600
 _ambient.volume_db=-80
 for i in range(10):
  var voice:=AudioStreamPlayer.new()
  add_child(voice)
  sfx_pool.append(voice)
 player.jumped.connect(func():_sfx("jump",1.0,-13))
 player.landed.connect(func():_sfx("land",1.0,-11))
 _capture_audio=AudioStreamPlayer.new()
 _capture_audio.stream=load("res://assets/courtyard-scroll/audio/metalLatch.ogg")
 _capture_audio.volume_db=-6
 add_child(_capture_audio)
 _super_audio=AudioStreamPlayer.new()
 _super_audio.stream=load("res://assets/courtyard-scroll/audio/impactBell_heavy_000.ogg")
 _super_audio.volume_db=-6
 add_child(_super_audio)
 _enemy_canvas=Node2D.new()
 _enemy_canvas.z_index=3
 var mat:=ShaderMaterial.new()
 mat.shader=load("res://shaders/courtyard_enemy.gdshader")
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
 _foreground=foreground
 foreground.z_index=6
 add_child(foreground)
 foreground.draw.connect(_draw_foreground)
 _hud.draw.connect(func():foreground.queue_redraw())
 player.z_index=2
 _keyed.z_index=1
 var opaque:=ShaderMaterial.new()
 opaque.shader=load("res://shaders/courtyard_key.gdshader")
 _hud.material=opaque
 _keyed.material=opaque
 material=opaque
 foreground.material=opaque
 world_canvas=CanvasLayer.new()
 world_canvas.layer=1
 add_child(world_canvas)
 for node in [_world,_keyed,_enemy_canvas,effect]:node.reparent(world_canvas)
 _items=Node2D.new()
 _items.z_index=4
 _items.material=opaque
 world_canvas.add_child(_items)
 _items.draw.connect(_draw_items)
 var foreground_canvas:=CanvasLayer.new()
 foreground_canvas.layer=2
 add_child(foreground_canvas)
 foreground.reparent(foreground_canvas)
 var hud_canvas:=CanvasLayer.new()
 hud_canvas.layer=3
 add_child(hud_canvas)
 _hud.reparent(hud_canvas)
 heart_icons=Node2D.new();_hud.add_child(heart_icons)
 var heart_mat:=ShaderMaterial.new();heart_mat.shader=load("res://shaders/hud_heart.gdshader");heart_icons.material=heart_mat
 heart_icons.draw.connect(_draw_hearts)
 _chapter_ready=true
 player.tuning=player.tuning.duplicate()
 player.tuning.run_speed=190.0
 player.tuning.acceleration=2300.0
 player.tuning.braking=2700.0
 player.tuning.jump_speed=-355.0
 player.film_strafe=true
 visual.stride_rate=15.0
 for name in ["trees","enemies","objects","panorama","masonry","portraits"]:
  var path:="res://assets/courtyard-scroll/%s.png"%name
  if ResourceLoader.exists(path):_textures[name]=load(path)
 for name in ["kit","pickups","hud","vulnerable"]:_textures[name]=load("res://assets/courtyard-v3/%s.png"%name)
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
 half_heart=false
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
 hearts.clear()
 for h in room.get("hearts",[]):hearts.append(Vector2(h[0],h[1]))
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
 for voice in sfx_pool:
  if name=="sound" and not value:voice.stop()
  if name in ["pause","focus_lost","pause_game","resume"]:voice.stream_paused=name!="resume"
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
 return player.position+visual.lens_offset()

func damage(source_x:float=INF) -> void:
 if _invincible>0 or _phase!="running":return
 var away:float=-player.facing if is_inf(source_x) else (1.0 if player.position.x>=source_x else -1.0)
 player.velocity=Vector2(away*230,-145)
 player.knockback_left=0.32
 _health-=1
 _hits+=1
 _invincible=1.3
 _hurt_left=0.36
 _record=false
 _sfx("hurt",0.9,-6)
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
  if _drop_requested and player.is_on_floor() and key_unlocked and (absf(player.position.x-4530)<38 or absf(player.position.x-2590)<30):
   passage_from=player.position
   passage_to=Vector2(2590 if player.position.x>3500 else 4530,270)
   passage_left=1.4
   _phase="passage"
   Controls.release_all()
   player.velocity=Vector2.ZERO
   get_tree().paused=true
  if _drop_requested and Input.is_action_pressed("jump") and player.is_on_floor():
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
  if _reload_requested and stock.start_reload():_sfx("reload",0.85,-8)
  _reload_requested=false
  super_left=maxf(0,super_left-delta)
  if super_requested:fire_super()
  super_requested=false
  _record=stock.advance(delta,Input.is_action_pressed("record") and _hurt_left<=0)
  step_clock-=delta
  if player.is_on_floor() and absf(player.velocity.x)>20 and step_clock<=0:
   _sfx("step",0.95,-18 if player.crouching else -12)
   step_clock=0.48 if player.crouching else 0.27
  film_clock-=delta
  if _record and film_clock<=0:
   _sfx("film",1.15,-31)
   film_clock=0.105
  for i in range(hearts.size()-1,-1,-1):
   if (_health<4 or half_heart) and player.position.distance_to(hearts[i]+Vector2(0,16))<27:
    hearts.remove_at(i)
    if not half_heart:_health=mini(4,_health+1)
    half_heart=not half_heart
    _sfx("heart")
  for i in range(_reels.size()-1,-1,-1):
   if player.position.distance_to(_reels[i]+Vector2(0,16))<28 and stock.collect_reel():
    _reels.remove_at(i)
    _pickups+=1
    _sfx("reel",1.0,-10)
  for i in range(rare_pickups.size()-1,-1,-1):
   if player.position.distance_to(rare_pickups[i]+Vector2(0,16))<28 and super_charges<2:
    rare_pickups.remove_at(i)
    super_charges+=1
    effect.pulse(player.position-Vector2(0,30),true)
    _sfx("heart",1.5,-17)
    toast="SILVER REEL — Super Shot ready (X)"
    toast_left=3
  var captured:=0
  for e in enemies:
   var old:String=e.phase
   var result:Dictionary=e.advance(delta,player.position,_record,player.facing,lens_point())
   if e.phase=="windup" and old!="windup" and absf(e.position.x-player.position.x)<280:_sfx("enemy",0.60 if e.kind=="werewolf" else 1.15,-12)
   if e.phase=="attack" and old!="attack" and absf(e.position.x-player.position.x)<280:_sfx("attack",0.8,-10)
   if result.hit and not (player.crouching and e.kind=="skeleton"):damage(e.position.x)
   # Solid enemy contact is resolved even during invulnerability; no walking through.
   if e.phase not in ["capturing","captured"] and absf(player.position.y-e.position.y)<(35 if player.crouching else 55) and absf(player.position.x-e.position.x)<29:
    var side:float=-1 if player.position.x<e.position.x else 1
    player.position.x=e.position.x+side*29
    if player.velocity.x*side<0:player.velocity.x=0
    if e.phase=="attack" and not (player.crouching and e.kind=="skeleton"):damage(e.position.x)
   if result.captured:
    total_captures+=1
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
   toast="FILM SLATE FOUND — the next scene is ready."
   toast_left=4
   _sfx("reel",1.4,-8)
  gate_open=key_collected
  _gate_body.collision_layer=0 if gate_open else 1
  if gate_open and player.position.x>5020 and absf(player.position.y-float(room.exit[1]))<22:
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
  elif player.crouching:next="crouch_walk" if absf(player.velocity.x)>5 else ("crouch_film" if _record else "crouch")
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
   if e.phase=="capturing" or ((e.in_view(player.position,player.facing) or e.target_locked) and e.vulnerable()):
    var distance:float=player.position.distance_to(e.position)
    if distance<nearest:
     nearest=distance
     effect.endpoint=e.position-Vector2(0,float(e.spec.height)*0.8*(maxf(0,1-e.clock/0.85) if e.phase=="capturing" else 1.0))
     effect.locked=true
     if e.phase=="capturing":effect.active=true
  visual.aiming_up=effect.locked and effect.endpoint.y<effect.lens.y-20
  effect.lens=lens_point()
  effect.advance(delta)
 _report_clock+=delta
 if _phase in ["running","passage"]:
  camera_x=lerpf(camera_x,clampf(player.position.x-290,0,WIDTH-640),1-exp(-delta*9))
 world_canvas.transform=Transform2D(0,Vector2(-camera_x,0))
 if _report_clock>0.1:
  _report_clock=0
  _report()
 scenery.advance(camera_x,_time,reduced_motion)
 queue_redraw()
 _keyed.queue_redraw()
 _enemy_canvas.queue_redraw()
 _hud.queue_redraw()
 _items.queue_redraw()

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
 _bridge.report(JSON.stringify({"build":"courtyard-scroll-03","crouching":player.crouching,"knockback":player.knockback_left,"hearts_remaining":hearts.size(),"camera_x":camera_x,"world_width":WIDTH,"key_unlocked":key_unlocked,"key_collected":key_collected,"phase":_phase,"stage":room.get("stage",""),"room":room_index,"room_name":room.get("name",""),"room_count":rooms.size(),"x":player.position.x,"feet":player.position.y,"vx":player.velocity.x,"vy":player.velocity.y,"grounded":player.is_on_floor(),"pose":_pose,"facing":player.facing,"projectiles":shots,"film":stock.film,"film_capacity":stock.CAPACITY,"spares":stock.spares,"reload_left":stock.reload_left,"reloads":stock.reloads,"recording":_record,"super_charges":super_charges,"super_left":super_left,"health":_health-(0.5 if half_heart else 0.0),"lens_x":lens_point().x,"lens_y":lens_point().y,"hits":_hits,"jumps":_jumps,"pickups":_pickups,"gate_open":gate_open,"enemies":foe_states,"captures":total_captures,"chapter_seconds":chapter_time,"viewport":[get_window().size.x,get_window().size.y],"design_viewport":[640,360],"fps":Engine.get_frames_per_second(),"frame_p95_ms":sorted[int((sorted.size()-1)*0.95)] if not sorted.is_empty() else 0.0,"engine":Engine.get_version_info().string,"audio_enabled":_sound,"save_available":_save_available,"actions":{"move_left":Input.is_action_pressed("move_left"),"move_right":Input.is_action_pressed("move_right"),"jump":Input.is_action_pressed("jump"),"record":Input.is_action_pressed("record")}}))


func _draw() -> void:
 pass # Scenery owns five independent render depths.

func _object(canvas: Node2D,index: int,dest: Rect2,color: Color=Color.WHITE) -> void:
 if not _textures.has("objects"):return
 var texture:Texture2D=_textures.objects
 var regions:=[Rect2(25,24,471,435),Rect2(542,25,480,430),Rect2(1170,110,320,280),Rect2(12,624,512,240),Rect2(537,452,560,560),Rect2(1138,393,360,631)]
 canvas.draw_texture_rect_region(texture,dest,regions[index],color)

func _draw_surfaces() -> void:
 if scenery==null:return
 for rect in surfaces:
  if rect.end.x<camera_x-120 or rect.position.x>camera_x+760:continue
  if rect.size.y==38:
   for x in range(int(rect.position.x),int(rect.end.x),110):
    var width:=minf(110,rect.end.x-x)
    scenery.piece(_keyed,0,Rect2(x,rect.position.y,width,350-rect.position.y))
  elif rect.position.y<270:
   for x in [rect.position.x+7,rect.end.x-18]:
    _keyed.draw_texture_rect_region(_textures.kit,Rect2(x,rect.position.y+6,12,270-rect.position.y-6),Rect2(44,300,86,198))
   _keyed.draw_texture_rect_region(_textures.kit,Rect2(rect.position,Vector2(rect.size.x,12)),Rect2(1060,793,426,91))
  else:
   # Cut blocks from the same bridge coping; the structural surface matches collision.
   for x in range(int(rect.position.x),int(rect.end.x),48):
    var width:=minf(48,rect.end.x-x)
    _keyed.draw_texture_rect_region(_textures.kit,Rect2(x,rect.position.y,width,rect.size.y),Rect2(26,181,width*6,rect.size.y*5))
  _keyed.draw_line(rect.position,Vector2(rect.end.x,rect.position.y),Color("8b969f"),0.7)

func _draw_reel(point: Vector2,rare: bool) -> void:
 _object(self,1 if rare else 0,Rect2(point-Vector2(11,11),Vector2(22,22)))

func _draw_props() -> void:
 if room.is_empty():return
 _draw_surfaces()


 if not gate_open:
  for x in range(5000,5070,9):_keyed.draw_line(Vector2(x,207),Vector2(x,270),Color("28313a"),2)

 if key_unlocked:
  for x in [2590,4530]:
   _keyed.draw_string(_font,Vector2(x-70,225),"↓ SERVICE PASSAGE",HORIZONTAL_ALIGNMENT_CENTER,140,8,Color("d6cca4"))
 if absf(player.position.x-1475)<160 and player.position.y>300:
  _keyed.draw_string(_font,Vector2(1360,276),"HOLD DOWN · CROUCH THROUGH",HORIZONTAL_ALIGNMENT_LEFT,-1,8,Color("d6cca4"))

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
  var tex:Texture2D=texture
  var draw_cell:Vector2=cell
  var source:=Rect2(Vector2(frame,row)*cell,cell)
  if e.phase in ["exposed","capturing"]:
   tex=_textures.vulnerable
   draw_cell=Vector2(384,512)
   var recovery_frame:=mini(3,int(e.clock*7)) if e.phase=="exposed" else 0
   source=Rect2(Vector2(recovery_frame,row)*draw_cell+Vector2(12,8),draw_cell-Vector2(24,16))
   draw_cell=source.size
  var factor:=float(e.spec.height)/(draw_cell.y*0.90)
  var shrink:=1.0
  var angle:=0.0
  var color:=Color.WHITE
  var anchor:=Vector2(draw_cell.x*0.5,draw_cell.y*0.96)
  var bob:=sin(e.animation_clock*11)*0.65 if e.phase=="watch" else 0.0
  if e.phase=="capturing":
   var t:float=clampf(e.clock/0.85,0,1)
   shrink=maxf(0.03,1-t)
   angle=sin(t*PI)*0.4
   color=Color(0.63,0.85,1,1-t*0.3)
  _enemy_canvas.draw_set_transform(e.position+Vector2(0,bob),angle,Vector2(-e.direction,1)*factor*shrink)
  if _record and (e.in_view(player.position,player.facing) or e.target_locked) or e.phase=="capturing":
   for offset in [Vector2(-3,0),Vector2(3,0),Vector2(0,-3),Vector2(0,3)]:
    _enemy_canvas.draw_texture_rect_region(tex,Rect2(-anchor+offset,draw_cell),source,Color(-1,1,1,0.7))
  _enemy_canvas.draw_texture_rect_region(tex,Rect2(-anchor,draw_cell),source,color)
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
 var hud:Texture2D=_textures.hud
 var health_value:=_health-(0.5 if half_heart else 0.0)
 var portrait:=clampi(4-_health,0,3)
 _hud.draw_texture_rect_region(hud,Rect2(9,7,42,54),Rect2(28+portrait*376,58,361,460))
 heart_icons.queue_redraw()
 var fill:float=stock.film/stock.CAPACITY
 _hud.draw_texture_rect_region(hud,Rect2(60,34,112,31),Rect2(1100,765,294,128))
 if fill>0:_hud.draw_texture_rect_region(hud,Rect2(60,34,112*fill,31),Rect2(251,765,294*fill,128))
 for i in range(3):_pickup_art(_hud,7,Rect2(180+i*20,35,19,24),Color.WHITE if i<stock.spares else Color(0.2,0.25,0.3,0.5))
 if super_charges>0:
  _pickup_art(_hud,5,Rect2(246,35,20,24))
  _label(Vector2(268,52),"×%d"%super_charges)
 var zone:=clampi(int(player.position.x/1024),0,4)
 var names:=["THE OUTER WALL","THE BROKEN WALK","THE IVY GARDEN","THE FOUNTAIN COURT","THE MOON TERRACES","THE CATACOMBS GATE"]
 _label(Vector2(410,20),names[zone],10,Color("d4cfb7"))
 _label(Vector2(410,35),"CAPTURES %d / 8"%mini(total_captures,8),9)
 if key_collected:
  _pickup_art(_hud,6,Rect2(573,23,28,28))
  _label(Vector2(410,48),"Slate found · reach the eastern gate",8)
 elif key_unlocked:
  _label(Vector2(410,48),"FILM SLATE %s  %dm"%["←" if player.position.x>KEY.x else "→",int(absf(player.position.x-KEY.x)/10)],8,Color("e2c583"))
 else:_label(Vector2(410,48),"Capture creatures to awaken the slate",8)
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
 pass # Keep the player silhouette clear; atmospheric fog is behind the walking plane.

func _sfx(name:String,pitch:float=1.0,level:float=-10.0) -> void:
 if not _sound or sfx_pool.is_empty():return
 var choices:Dictionary={"cloth":["cloth1","cloth2"],"step":["footstep_concrete_000","footstep_concrete_001","footstep_concrete_002"],"jump":["cloth1","cloth2"],"land":["impactSoft_heavy_000"],"hurt":["impactPunch_heavy_000"],"reel":["metalLatch","handleCoins"],"heart":["impactBell_heavy_000"],"reload":["metalClick"],"film":["metalClick"],"attack":["knifeSlice"],"enemy":["creak1","creak2"],"capture":["bookFlip1","metalLatch"]}
 if not choices.has(name):return
 var options:Array=choices[name]
 var clip:String=options[sfx_index%options.size()]
 var voice:AudioStreamPlayer=sfx_pool[sfx_index%sfx_pool.size()]
 sfx_index+=1
 voice.stream=load("res://assets/courtyard-scroll/audio/%s.ogg"%clip)
 voice.pitch_scale=pitch*(0.96+float(sfx_index%5)*0.02)
 voice.volume_db=level
 voice.play()
 if name=="step":_sfx("cloth",1.1,-28)

func _chirp(_pitch:float=1.0) -> void:
 pass # Replaced by action-specific Foley in this stage.

func _masonry(canvas:Node2D,index:int,dest:Rect2,color:Color=Color.WHITE)->void:
 if not _textures.has("masonry"):return
 var regions:=[Rect2(6,105,551,382),Rect2(570,38,454,446),Rect2(1050,80,471,414),Rect2(8,545,535,405),Rect2(531,614,505,197),Rect2(1045,512,491,512)]
 canvas.draw_texture_rect_region(_textures.masonry,dest,regions[index],color)

func _draw_midground()->void:
 if not _textures.has("masonry"):return
 var middle:Node2D=self
 for i in range(12):
  var x:=i*215-camera_x*0.30-40
  if x>700 or x+190<0:continue
  var height:=130+(i%3)*22
  _masonry(middle,5,Rect2(x,290-height,190,height),Color("71869c"))


func _pickup_art(canvas:Node2D,index:int,dest:Rect2,color:Color=Color.WHITE)->void:
 var regions:=[Rect2(90,48,280,390),Rect2(530,50,250,390),Rect2(929,41,219,399),Rect2(1260,105,374,330),Rect2(30,525,384,300),Rect2(451,488,360,368),Rect2(868,481,346,363),Rect2(1275,484,374,377)]
 canvas.draw_texture_rect_region(_textures.pickups,dest,regions[index],color)

func _draw_items()->void:
 for reel in _reels:_pickup_art(_items,7,Rect2(reel-Vector2(10,11),Vector2(20,22)))
 for reel in rare_pickups:_pickup_art(_items,5,Rect2(reel-Vector2(10,11),Vector2(20,22)))
 for h in hearts:
  var kind:=int(h.x)%5
  _pickup_art(_items,kind,Rect2(h-Vector2(9,11),Vector2(18,22)))
 if key_unlocked and not key_collected:
  for j in range(4,0,-1):_items.draw_circle(KEY,j*7,Color(0.15,0.7,1.0,0.06))
  _pickup_art(_items,6,Rect2(KEY-Vector2(16,17),Vector2(32,34)))

func _draw_hearts()->void:
 var hud:Texture2D=_textures.hud
 var health_value:=_health-(0.5 if half_heart else 0.0)
 for i in range(4):
  var rect:=Rect2(60+i*20,10,18,18)
  heart_icons.draw_texture_rect_region(hud,rect,Rect2(270,630,85,84),Color.WHITE if health_value>=i+1 else Color(0.20,0.22,0.27))
  if health_value>i and health_value<i+1:heart_icons.draw_texture_rect_region(hud,Rect2(rect.position,Vector2(9,18)),Rect2(270,630,42.5,84))
