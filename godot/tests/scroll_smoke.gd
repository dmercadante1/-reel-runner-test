extends SceneTree
var game:Node
var checks:Array=[]
func _initialize()->void:run.call_deferred()
func tick(n:int=1)->void:
 for i in range(n):await physics_frame
func check(name:String,passed:bool)->void:
 checks.append({"name":name,"passed":passed})
 print(("PASS " if passed else "FAIL ")+name+" state="+str([game._phase,game.player.position,game._health,game.stock.spares,game.death_left]))
func run()->void:
 game=load("res://scenes/courtyard_stage.tscn").instantiate()
 root.add_child(game)
 game._command("resume")
 await tick(10)
 check("12-screen stage and 21 enemies",game.WIDTH==7680 and game.enemies.size()==21)
 var e=game.enemies[0]
 var start:float=e.position.x
 await tick(30)
 check("Distant enemy patrols",absf(e.position.x-start)>5)
 Input.action_press("record");Input.action_press("move_left");await tick(12)
 check("Film retreat preserves facing and drains film",game.player.facing==1 and game.player.velocity.x<0 and game.stock.film<12)
 Input.action_release("record");await tick(5)
 check("Release film restores normal turning",game.player.facing==-1)
 Input.action_release("move_left")
 e.phase="windup";e.clock=0;e.exposure=0;e.advance(0.1,e.position-Vector2(80,0),true,1,e.position-Vector2(70,43))
 var defended:float=e.exposure
 e.phase="exposed";e.clock=0;e.exposure=0;e.advance(0.1,e.position-Vector2(80,0),true,1,e.position-Vector2(70,43))
 check("Vulnerable film drains five times faster",is_equal_approx(e.exposure,defended*5))
 game._reset();game._command("resume");await tick(5)
 for i in range(11):game.enemies[i].phase="captured"
 await tick(3);check("11 captures do not unlock key",not game.key_unlocked)
 game.enemies[11].phase="captured";await tick(3)
 check("Quota awakens distant key, not exit",game.key_unlocked and not game.gate_open and game.enemies[12].phase!="captured")
 game.player.position=game.KEY+Vector2(0,16);await tick(3)
 check("Collecting key opens exit",game.key_collected and game.gate_open)
 game.player.position=Vector2(6280,270);await tick(8)
 game._drop_requested=true;await tick(100)
 check("Service passage returns to midpoint",absf(game.player.position.x-3730)<15 and game._phase=="running")
 game.player.position=Vector2(7610,270);await tick(3)
 check("Stage completes with uncaptured enemies",game._completed and game.enemies[12].phase!="captured")
 game._command("new_game");await tick(5)
 game._health=1;game.damage();await tick(110)
 check("Death restarts whole stage with restored supplies",game._phase=="running" and game.player.position.x<100 and game._health==4 and game.stock.spares==2 and not game.key_unlocked)
 # Input-only traversal isolates all main route gaps and camera boundaries.
 game.enemies.clear();Input.action_press("move_right")
 var frames:=0
 var jumped_at:=-100
 while game.player.position.x<7520 and frames<4000:
  if game.player.is_on_floor():
   for rect in game.surfaces:
    if rect.size.y==38 and absf(game.player.position.y-rect.position.y)<3 and rect.end.x-game.player.position.x>0 and rect.end.x-game.player.position.x<23:
     Input.action_press("jump");jumped_at=frames;break
  if game.player.is_on_floor() and game.player.position.y>275 and frames-jumped_at>35:
   Input.action_press("jump");jumped_at=frames
  if frames-jumped_at>24:Input.action_release("jump")
  await tick();frames+=1
 Input.action_release("move_right");Input.action_release("jump");await tick(10)
 check("Entire stage traversable using controller input",game.player.position.x>7500)
 check("Camera follows and clamps at stage edge",game.camera_x>6900 and game.camera_x<=7040)
 var failed:=checks.filter(func(c):return not c.passed).size()
 var f=FileAccess.open("res://tests/scroll-results.json",FileAccess.WRITE)
 f.store_string(JSON.stringify({"checks":checks,"failed":failed,"note":"Native gameplay rules and input-only traversal; quota states arranged to isolate progression. Not a physical Safari/iPhone test."},"  "));f.close()
 quit(1 if failed else 0)
