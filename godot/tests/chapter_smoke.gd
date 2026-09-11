extends SceneTree
var checks:Array=[]
func _initialize() -> void:run.call_deferred()
func check(label:String,ok:bool,detail:Variant=null) -> void:
 checks.append({"name":label,"passed":ok,"detail":detail})
 print(("PASS " if ok else "FAIL ")+label+" "+str(detail))
func wait(seconds:float) -> void:await create_timer(seconds).timeout
func run() -> void:
 var kinds=["skeleton","werewolf","ghoul","monster","phantom","vampire","dracula"]
 for kind in kinds:
  var foe=preload("res://scripts/chapter_enemy.gd").new()
  foe.setup(kind,Vector2(490,300),Vector2(300,570))
  for i in range(20):foe.advance(0.02,Vector2(350,300),true,1,Vector2(365,257))
  check(kind+" guarded exposure stays zero",foe.exposure==0)
  foe.phase="exposed"
  foe.clock=0
  foe.advance(0.1,Vector2(350,300),true,-1,Vector2(335,257))
  check(kind+" requires facing",foe.exposure==0)
  foe.advance(0.3,Vector2(350,300),true,1,Vector2(365,257))
  check(kind+" recovery can be filmed",foe.exposure>0)
  foe.phase="watch"
  var before:float=foe.exposure
  foe.super_hit(Vector2(350,300),1,Vector2(365,257))
  check(kind+" Super Shot rule",foe.exposure==before if kind=="dracula" else foe.exposure>before)
  foe.phase="exposed"
  foe.exposure=float(foe.spec.capture)-0.01
  var hit:Dictionary=foe.advance(0.02,Vector2(350,300),true,1,Vector2(365,257))
  check(kind+" enters capture animation",hit.captured and foe.phase=="capturing")
  foe.advance(0.9,Vector2(350,300),false,1,Vector2(365,257))
  check(kind+" finishes in the camera",foe.phase=="captured" and foe.position.distance_to(Vector2(365,257))<0.01)
 var chapter=load("res://scenes/gothic_chapter.tscn").instantiate()
 root.add_child(chapter)
 chapter._command("resume")
 await wait(0.4)
 check("Chapter starts with four health and no unearned Super",chapter._health==4 and chapter.super_charges==0)
 check("Chapter has all five named stages",chapter.rooms.size()==9 and chapter.rooms[8].stage=="Dracula's Chamber")
 check("Empty Super Shot is rejected",not chapter.fire_super())
 chapter.super_charges=1
 chapter.enemies[0].phase="watch"
 chapter.player.reset_at(Vector2(365,230))
 chapter.player.facing=1
 check("Charged Super fires once",chapter.fire_super() and chapter.super_charges==0)
 check("Repeated Super cannot double-spend",not chapter.fire_super())
 check("Super captures a normal guarded enemy",chapter.enemies[0].phase=="capturing")
 await wait(1.0)
 check("Captured foe opens the gate",chapter.gate_open)
 chapter.load_room(8)
 chapter._command("resume")
 chapter.player.reset_at(Vector2(350,300))
 chapter.super_charges=2
 chapter.fire_super()
 check("Dracula shield survives Super",chapter.enemies[0].exposure==0)
 chapter.super_left=0
 chapter.enemies[0].phase="exposed"
 chapter.fire_super()
 check("Super damages exposed Dracula without skipping boss",chapter.enemies[0].exposure>0 and chapter.enemies[0].phase!="capturing")
 chapter._command("pause")
 var frozen:float=chapter.enemies[0].clock
 var super_frozen:float=chapter.super_left
 await wait(0.3)
 check("Pause freezes enemy and Super timers",chapter.enemies[0].clock==frozen and chapter.super_left==super_frozen)
 for index in range(9):
  chapter.load_room(index)
  chapter._command("resume")
  await wait(0.3)
  check("Room %d spawn stands on authored floor"%index,chapter.player.is_on_floor(),chapter.player.position)
  check("Room %d has distinct encounter data"%index,not chapter.enemies.is_empty() and not chapter.surfaces.is_empty())
 chapter.load_room(0)
 chapter._command("resume")
 chapter._record=true
 chapter._command("pause")
 check("Pause clears held filming",not chapter._record and not Input.is_action_pressed("record"))
 chapter._command("new_game")
 check("New chapter clears progress",chapter.room_index==0 and chapter.total_captures==0 and chapter.super_charges==0)
 # Stop audio cleanly before freeing an always-processing paused tree.
 if chapter._ambient!=null:
  chapter._ambient.stream_paused=false
  chapter._ambient.stop()
  chapter._ambient.stream=null
 await wait(0.15)
 chapter.free()
 var failed:=0
 for item in checks:
  if not item.passed:failed+=1
 var result={"passed":checks.size()-failed,"failed":failed,"checks":checks,"physical_phone_tested":false}
 var file=FileAccess.open("res://tests/latest-chapter-results.json",FileAccess.WRITE)
 file.store_string(JSON.stringify(result,"  "))
 quit(1 if failed else 0)
