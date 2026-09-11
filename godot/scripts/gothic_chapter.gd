extends "res://scripts/gothic_room.gd"
## Connected first-pass chapter. Original single-room previews remain independent.
var rooms: Array = preload("res://scripts/chapter_rooms.gd").all()
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
 for name in ["catacombs","cathedral","castle","dracula_chamber","werewolf","ghoul","monster","phantom","vampire","dracula"]:
  var path:="res://assets/chapter/%s.png"%name
  if ResourceLoader.exists(path): _textures[name]=load(path)
 if FileAccess.file_exists("res://assets/chapter/atlas.json"):
  enemy_atlas=JSON.parse_string(FileAccess.get_file_as_string("res://assets/chapter/atlas.json"))
 _enemy_canvas=Node2D.new()
 _enemy_canvas.z_index=3
 var mat:=ShaderMaterial.new()
 mat.shader=load("res://shaders/chapter_sprite.gdshader")
 _enemy_canvas.material=mat
 add_child(_enemy_canvas)
 _enemy_canvas.draw.connect(_draw_enemies)
 effect=preload("res://scripts/capture_effect.gd").new()
 add_child(effect)
 _hud=Node2D.new()
 _hud.z_index=10
 add_child(_hud)
 _hud.draw.connect(_draw_hud)
 player.z_index=2
 _keyed.z_index=1
 var portrait:=Node2D.new()
 portrait.z_index=11
 portrait.material=_keyed.material
 add_child(portrait)
 portrait.draw.connect(func():
  var texture:Texture2D=load("res://assets/private-character/model.png")
  portrait.draw_texture_rect_region(texture,Rect2(10,3,37,40),Rect2(665,318,548,570)))
 _chapter_ready=true
 var saved:=0
 if OS.has_feature("web"):
  var value=JavaScriptBridge.eval("(()=>{try{return Number(localStorage.getItem('mwmc-gothic-room-v1')||0)}catch(e){return -1}})()")
  if value!=null:
   saved=clampi(int(value),0,rooms.size()-1)
   _save_available=int(value)>=0
 load_room(saved)
 _phase="ready"
 get_tree().paused=true
 _report()

func _reset() -> void:
 if not _chapter_ready:
  super._reset()
  return
 super_charges=room_entry_super
 load_room(room_index)

func load_room(index: int) -> void:
 Controls.release_all()
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
 _floor(Rect2(640,0,20,360))
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
  var enemy=preload("res://scripts/chapter_enemy.gd").new()
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
  JavaScriptBridge.eval("try{localStorage.setItem('mwmc-gothic-room-v1','%d')}catch(e){}"%room_index)
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
    effect.pulse(e.capture_origin)
    if _sound:_capture_audio.play()
   if result.projectile!="":_spawn_projectiles(e,result.projectile)
   if e.phase=="captured":captured+=1
  for i in range(projectiles.size()-1,-1,-1):
   var p:Dictionary=projectiles[i]
   p.position+=p.velocity*delta
   p.life-=delta
   if p.life<=0 or p.position.x<0 or p.position.x>640:
    projectiles.remove_at(i)
   elif p.position.distance_to(player.position-Vector2(0,25 if p.kind=="orb" else 8))<17:
    damage()
    projectiles.remove_at(i)
  gate_open=captured>=int(room.required)
  _gate_body.collision_layer=0 if gate_open else 1
  if gate_open and player.position.x>600 and absf(player.position.y-float(room.exit[1]))<22:
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
 _bridge.report(JSON.stringify({"build":"gothic-chapter-01","phase":_phase,"stage":room.get("stage",""),"room":room_index,"room_name":room.get("name",""),"room_count":rooms.size(),"x":player.position.x,"feet":player.position.y,"vx":player.velocity.x,"vy":player.velocity.y,"grounded":player.is_on_floor(),"pose":_pose,"facing":player.facing,"projectiles":shots,"film":stock.film,"film_capacity":stock.CAPACITY,"spares":stock.spares,"reload_left":stock.reload_left,"reloads":stock.reloads,"recording":_record,"super_charges":super_charges,"super_left":super_left,"health":_health,"hits":_hits,"jumps":_jumps,"pickups":_pickups,"gate_open":gate_open,"enemies":foe_states,"captures":total_captures,"chapter_seconds":chapter_time,"viewport":[get_window().size.x,get_window().size.y],"design_viewport":[640,360],"fps":Engine.get_frames_per_second(),"frame_p95_ms":sorted[int((sorted.size()-1)*0.95)] if not sorted.is_empty() else 0.0,"engine":Engine.get_version_info().string,"audio_enabled":_sound,"save_available":_save_available,"actions":{"move_left":Input.is_action_pressed("move_left"),"move_right":Input.is_action_pressed("move_right"),"jump":Input.is_action_pressed("jump"),"record":Input.is_action_pressed("record")}}))

func _draw() -> void:
 if _font==null or room.is_empty():return
 var bg:String=room.bg
 if _textures.has(bg):draw_texture_rect(_textures[bg],Rect2(0,0,640,360),false)
 else:draw_rect(Rect2(0,0,640,360),Color("0b1420"))
 if _textures.has("architecture"):
  var texture:Texture2D=_textures.architecture
  var cell:=texture.get_size()/Vector2(3,2)
  for rect in surfaces:
   if rect.size.y>10:
    for x in range(int(rect.position.x),int(rect.end.x),32):
     var width:=minf(32,rect.end.x-x)
     draw_texture_rect_region(texture,Rect2(x,rect.position.y,width,rect.size.y),Rect2(Vector2(0,cell.y+cell.y*0.063),Vector2(cell.x*width/32,cell.y*0.5)))
   else:
    draw_texture_rect_region(texture,rect,Rect2(Vector2(0,cell.y+cell.y*0.08),Vector2(cell.x,cell.y*0.22)))
    draw_line(rect.position+Vector2(2,10),rect.end-Vector2(2,0),Color("35434f"),2)
   draw_line(rect.position,Vector2(rect.end.x,rect.position.y),Color("a1adae"),1)
 for i in range(3):
  draw_rect(Rect2(fmod(_time*3+i*250,850)-180,278+i*19,210,5),Color(0.3,0.5,0.6,0.04))
 for reel in _reels:_draw_reel(reel+Vector2(0,sin(_time*3+reel.x)*2),false)
 for reel in rare_pickups:_draw_reel(reel+Vector2(0,sin(_time*2+reel.x)*3),true)
 for p in projectiles:
  var color:=Color("90b889") if p.kind=="poison" else Color("cd635e")
  if p.kind=="wave":
   draw_arc(p.position,10,PI,TAU,14,Color(0.95,0.45,0.27,0.5),5,true)
   draw_arc(p.position,8,PI,TAU,14,Color("f8c785"),2,true)
  else:
   draw_circle(p.position,8,Color(color,0.13))
   draw_circle(p.position,4,color)
   draw_circle(p.position-Vector2(1,1),1.6,Color("f0eac9"))

func _draw_reel(point: Vector2,rare: bool) -> void:
 if rare:
  draw_circle(point,11,Color(0.3,0.7,1,0.10))
  draw_arc(point,8,0,TAU,24,Color("94d7ff"),0.8,true)
 draw_circle(point,5,Color("d6e8ef") if rare else Color("c7b680"))
 draw_circle(point,1,Color("272b30"))
 for angle in [0.0,2.1,4.2]:draw_circle(point+Vector2(cos(angle),sin(angle))*3,1,Color("343843"))

func _draw_props() -> void:
 if room.is_empty() or not _textures.has("architecture"):return
 var texture:Texture2D=_textures.architecture
 var c:=texture.get_size()/Vector2(3,2)
 var point:=Vector2(room.exit[0],room.exit[1])
 _keyed.draw_texture_rect_region(texture,Rect2(point-Vector2(36,101),Vector2(62,101)),Rect2(Vector2(c.x*2,0) if gate_open else Vector2(c.x,c.y),c))
 for x in [12,566]:
  _keyed.draw_texture_rect_region(texture,Rect2(x,float(room.floor)-48,22,48),Rect2(Vector2(c.x*2,c.y),c))
 if gate_open:
  _keyed.draw_string(_font,point-Vector2(22,110),"EXIT >",HORIZONTAL_ALIGNMENT_LEFT,-1,8,Color("a5d8cf"))

func _draw_enemies() -> void:
 for e in enemies:
  if e.phase=="captured":continue
  var frame:=0
  if e.phase=="windup":frame=1
  elif e.phase=="attack":frame=2
  elif e.phase=="exposed":frame=3 if e.clock<0.4 else 4
  elif e.phase=="capturing":frame=5
  var rect:Rect2
  var anchor:Vector2
  var factor:float
  var texture:Texture2D
  if e.kind=="skeleton":
   texture=_textures.guardian
   var boxes:=[Rect2(80,0,230,492),Rect2(1200,0,336,492),Rect2(0,630,444,320),Rect2(450,512,300,440),Rect2(850,512,302,440),Rect2(1200,512,336,440)]
   var anchors:=[Vector2(195,488),Vector2(1335,488),Vector2(245,944),Vector2(605,944),Vector2(970,944),Vector2(1340,944)]
   rect=boxes[frame]
   anchor=anchors[frame]
   factor=float(e.spec.height)/488.0
  elif _textures.has(e.kind) and enemy_atlas.has(e.kind):
   texture=_textures[e.kind]
   var data:Dictionary=enemy_atlas[e.kind][frame]
   rect=Rect2(data.rect[0],data.rect[1],data.rect[2],data.rect[3])
   anchor=Vector2(data.anchor[0],data.anchor[1])
   factor=float(e.spec.height)/float(enemy_atlas[e.kind][0].standing_height)
  else:continue
  var shrink:=1.0
  var angle:=0.0
  var color:=Color.WHITE
  if e.kind=="phantom" and e.phase=="watch":color.a=0.28
  if e.phase=="capturing":
   var t:float=clampf(e.clock/0.85,0,1)
   shrink=maxf(0.04,1.0-t)
   angle=sin(t*TAU)*0.5 if not reduced_motion else 0.0
   color=Color(0.55,0.82,1,1.0-t*0.4)
  var side:float=-1 if e.direction>0 else 1
  _enemy_canvas.draw_set_transform(e.position,angle,Vector2(side,1)*factor*shrink)
  _enemy_canvas.draw_texture_rect_region(texture,Rect2(rect.position-anchor,rect.size),rect,color)
  _enemy_canvas.draw_set_transform(Vector2.ZERO)
  if e.phase=="windup":
   _enemy_canvas.draw_string(_font,e.position+Vector2(-3,-float(e.spec.height)-7),"!",HORIZONTAL_ALIGNMENT_LEFT,-1,17,Color("f5c279"))
  if e.phase=="exposed":
   _enemy_canvas.draw_rect(Rect2(e.position+Vector2(-22,-float(e.spec.height)-5),Vector2(44,3)),Color("1e3548"))
   _enemy_canvas.draw_rect(Rect2(e.position+Vector2(-22,-float(e.spec.height)-5),Vector2(44*e.exposure/float(e.spec.capture),3)),Color("9addf2"))

func _draw_hud() -> void:
 if room.is_empty():return
 _hud.draw_rect(Rect2(0,0,640,46),Color(0.025,0.04,0.065,0.94))
 _hud.draw_string(_font,Vector2(55,14),"MAN WITH A MOVIE CAMERA",HORIZONTAL_ALIGNMENT_LEFT,-1,10,Color("dad4c0"))
 _hud.draw_string(_font,Vector2(405,14),str(room.stage).to_upper(),HORIZONTAL_ALIGNMENT_LEFT,-1,10,Color("c3bda7"))
 _hud.draw_rect(Rect2(55,22,98,6),Color("333b42"))
 _hud.draw_rect(Rect2(55,22,98*stock.film/stock.CAPACITY,6),Color("a3cddd"))
 _hud.draw_string(_font,Vector2(161,28),"REELS %d/3"%stock.spares,HORIZONTAL_ALIGNMENT_LEFT,-1,9,Color("c9b17b"))
 for i in range(4):_hud.draw_circle(Vector2(231+i*10,24),3.2,Color("bc7166") if i<_health else Color("343b44"))
 _hud.draw_string(_font,Vector2(280,28),"SUPER ×%d"%super_charges,HORIZONTAL_ALIGNMENT_LEFT,-1,9,Color("a6e3ff") if super_charges>0 else Color("617784"))
 _hud.draw_string(_font,Vector2(527,28),"ROOM %d / %d"%[room_index+1,rooms.size()],HORIZONTAL_ALIGNMENT_LEFT,-1,8,Color("8caaa9"))
 var message:String=room.hint
 if gate_open:message="The way is open. Continue through the arch >"
 if stock.reload_left>0:message="Reloading a fresh reel…"
 elif stock.film<=0:message="Film empty — Reload (R), find a reel, or retry this room."
 if toast_left>0:message=toast
 _hud.draw_string(_font,Vector2(55,40),message,HORIZONTAL_ALIGNMENT_LEFT,575,8,Color("b0c2c5"))
 if banner_left>0 and _phase=="running":
  _hud.draw_rect(Rect2(185,55,270,34),Color(0.015,0.025,0.04,minf(0.82,banner_left)))
  _hud.draw_string(_font,Vector2(200,77),str(room.name),HORIZONTAL_ALIGNMENT_CENTER,240,13,Color("dccba5"))
 if room_index==rooms.size()-1 and not enemies.is_empty() and enemies[0].phase!="captured":
  var boss=enemies[0]
  _hud.draw_rect(Rect2(170,337,300,7),Color("302633"))
  _hud.draw_rect(Rect2(170,337,300*(1-boss.exposure/float(boss.spec.capture)),7),Color("a34d64"))
  _hud.draw_string(_font,Vector2(260,331),"DRACULA · PHASE %d"%boss.boss_phase,HORIZONTAL_ALIGNMENT_LEFT,-1,9,Color("dec7c9"))
 if _phase in ["transition","chapter_complete","defeated"]:
  _hud.draw_rect(Rect2(140,105,360,105),Color(0.02,0.035,0.055,0.96))
  var title:="THE TAKE WAS LOST"
  var detail:="Retry this room. Your chapter progress is saved."
  if _phase=="transition":
   title="SCENE CAPTURED"
   detail="Entering "+str(rooms[mini(room_index+1,rooms.size()-1)].name)
  elif _phase=="chapter_complete":
   title="DRACULA — CAPTURED"
   detail="Gothic Horror chapter complete. The night is on film."
  _hud.draw_string(_font,Vector2(158,142),title,HORIZONTAL_ALIGNMENT_CENTER,324,18,Color("e2d1a9"))
  _hud.draw_string(_font,Vector2(157,170),detail,HORIZONTAL_ALIGNMENT_CENTER,326,10,Color("b9d1d8"))
  if _phase=="chapter_complete":_hud.draw_string(_font,Vector2(190,193),"%d captures · %.1f minutes"%[total_captures,chapter_time/60],HORIZONTAL_ALIGNMENT_CENTER,260,10,Color("8ca5b5"))
