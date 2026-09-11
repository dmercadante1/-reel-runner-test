extends SceneTree
var game:Node
var checks:Array=[]
func _initialize()->void: run.call_deferred()
func tick(n:int=1)->void:
 for i in range(n):await physics_frame
func stop()->void:
 for action in ["move_left","move_right","jump"]:Input.action_release(action)
func walk(x:float)->bool:
 var n:=0
 while absf(game.player.position.x-x)>4 and n<360:
  var right:bool=game.player.position.x<x
  Input.action_press("move_right" if right else "move_left")
  Input.action_release("move_left" if right else "move_right")
  await tick()
  n+=1
 stop()
 await tick(10)
 return n<360
func jump_to(x:float)->bool:
 var n:=0
 while not game.player.is_on_floor() and n<180:
  await tick()
  n+=1
 Input.action_press("move_right")
 Input.action_press("jump")
 await tick(23)
 Input.action_release("jump")
 while game.player.position.x<x-4 and n<360:
  await tick()
  n+=1
 stop()
 await tick(35)
 return n<360
func check(label:String,ok:bool)->void:
 checks.append({"name":label,"passed":ok,"room":game.room_index,"position":[game.player.position.x,game.player.position.y]})
 print(("PASS " if ok else "FAIL ")+label+" "+str(game.player.position))
func run()->void:
 game=load("res://scenes/gothic_chapter.tscn").instantiate()
 root.add_child(game)
 for item in [[1,135,190,234,324],[2,145,205,244,355],[6,175,235,258,375],[7,125,180,214,330]]:
  game.load_room(item[0]);game._command("resume");game.enemies.clear();await tick(20)
  await walk(item[1]);await jump_to(item[2]);await walk(item[3]);await jump_to(item[4])
  check("Optional upper route "+str(item[0]),game.player.position.y<float(game.room.floor)-70)
  if item[0]!=7:check("Silver reel reachable "+str(item[0]),game.super_charges>0)
  game.super_charges=0
 game.load_room(8);game._command("resume");game.enemies.clear();await tick(20)
 await walk(139);await jump_to(188)
 check("Boss supply platform reachable",game.player.position.y<260)
 game.load_room(0);game._command("resume");game.enemies.clear();await tick(20)
 await walk(249);await jump_to(307)
 for i in range(3):
  game._drop_requested=true
  await tick(35)
 await walk(558)
 check("Lower crypt silver reel reachable",game.super_charges>0 and game.player.position.y>330)
 game.load_room(3);game._command("resume");game.enemies.clear();game.player.reset_at(Vector2(260,350));await tick(20)
 game._drop_requested=true;await tick(40)
 check("Crypt bottom cannot be dropped through",game.player.position.y<355)
 stop();game._command("pause");game._ambient.stop();game._ambient.stream=null;await tick(10);game.queue_free();await tick(5)
 var failed:=checks.filter(func(c):return not c.passed).size()
 var result={"checks":checks,"passed":checks.size()-failed,"failed":failed,"method":"Native controller inputs with enemies removed to isolate optional route geometry"}
 var f=FileAccess.open("res://tests/latest-chapter-routes.json",FileAccess.WRITE);f.store_string(JSON.stringify(result,"  "));f.close();quit(1 if failed else 0)
