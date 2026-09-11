extends SceneTree
var game:Node
var checks:Array=[]
func _initialize()->void:run.call_deferred()
func tick(n:int=1)->void:
 for i in range(n):await physics_frame
func check(name:String,passed:bool)->void:
 checks.append({"name":name,"passed":passed})
 print(("PASS " if passed else "FAIL ")+name+" "+str(game.player.position))
func fresh()->void:
 game._command("new_game")
 await tick(5)
func run()->void:
 game=load("res://scenes/courtyard_stage.tscn").instantiate();root.add_child(game)
 await fresh()
 check("Eight screens and four reel pickups",game.WIDTH==5120 and game._reels.size()==4)
 Input.action_press("drop");Input.action_press("move_right");await tick(15)
 check("Crouch changes collision and slows walking",game.player.crouching and game.player.get_node("Collision").shape.size.y==38 and game.player.velocity.x<=81)
 Input.action_release("move_right")
 game.player.position=Vector2(1430,350);await tick(8);Input.action_release("drop");await tick(5)
 check("Cannot stand inside low tunnel",game.player.crouching)
 game.player.position=Vector2(2070,350);await tick(5)
 check("Stands once clear of tunnel",not game.player.crouching)
 await fresh();game._health=3;var h:Vector2=game.hearts[0];game.player.position=h+Vector2(0,16);await tick(3)
 check("Food pickup restores half a heart",game._health==4 and game.half_heart and game.hearts.size()==4)
 game.player.position=game.hearts[0]+Vector2(0,16);await tick(3)
 check("Two food pickups restore one heart",game._health==4 and not game.half_heart)
 await fresh();game._health=1;game.half_heart=true;game._command("pause");game._command("resume");await tick(2)
 check("Half-heart survivor resumes without reset",game._health==1 and game.half_heart and game._phase=="running")
 game.damage();check("Hit at half a heart defeats player",game._phase=="defeated")
 await fresh();game.enemies.clear();game.player.position=Vector2(1430,350);Input.action_press("drop");Input.action_press("move_right");await tick(70);Input.action_release("move_right");Input.action_release("drop")
 check("Crouch passage rewards a silver reel",game.super_charges==1 and game.rare_pickups.size()==1)
 game.visual.set_pose("film",0,1);var lens=game.visual.lens_offset();game.visual.set_pose("film",0,-1)
 check("Lens reflects with facing at fixed camera anchor",absf(lens.x+game.visual.lens_offset().x)<0.001 and lens.y==game.visual.lens_offset().y)
 await fresh();game.player.position=Vector2(250,270);game.damage(300);Input.action_press("move_right");await tick(4)
 check("Hit rebound resists movement input",game.player.velocity.x<0 and game.player.knockback_left>0)
 Input.action_release("move_right")
 await fresh();var e=game.enemies[0];e.position=Vector2(300,270);e.origin=e.position;e.bounds=Vector2(300,300);e.spec.windup=10;game.enemies=[e];game.player.position=Vector2(245,270)
 Input.action_press("move_right");await tick(25);Input.action_release("move_right")
 check("Cannot walk through enemy body",game.player.position.x<275)
 var foe=load("res://scripts/courtyard_enemy.gd").new();foe.setup("skeleton",Vector2(400,178),Vector2(370,480));foe.phase="exposed"
 foe.advance(0.1,Vector2(300,218),true,1,Vector2(315,175));var first:float=foe.exposure
 foe.advance(0.1,Vector2(300,280),true,1,Vector2(315,237))
 check("Jump-acquired film lock follows vertical separation",foe.target_locked and foe.exposure>first)
 foe.phase="watch";foe.advance(0.01,Vector2(300,280),true,1,Vector2(315,237))
 check("Lock ends when vulnerability ends",not foe.target_locked)
 foe.phase="exposed";foe.clock=0;foe.exposure=0;foe.advance(0.43,Vector2(300,178),true,1,Vector2(315,135))
 check("Skeleton captures in under half a second exposed",foe.phase=="capturing")
 await fresh()
 for i in range(7):game.enemies[i].phase="captured"
 await tick(3);check("Seven captures keep key asleep",not game.key_unlocked)
 game.enemies[7].phase="captured";await tick(3);check("Eight captures unlock key",game.key_unlocked and not game.gate_open)
 game.player.position=game.KEY+Vector2(0,16);await tick(3);check("Key opens stage exit",game.gate_open)
 game.player.position=Vector2(4530,270);await tick(5);game._drop_requested=true;await tick(100)
 check("Shortened-stage service passage works",absf(game.player.position.x-2590)<15)
 game.player.position=Vector2(5050,270);await tick(3);check("Can finish without capturing every enemy",game._completed)
 await fresh();game._health=1;game.damage();await tick(110);check("Death resets stage and supplies",game._health==4 and game.player.position.x<100 and game.stock.spares==2)
 game.enemies.clear();Input.action_press("move_right");var frames:=0;var jumped_at:=-100
 while game.player.position.x<4930 and frames<2400:
  if game.player.is_on_floor():
   for rect in game.surfaces:
    if rect.size.y==38 and absf(game.player.position.y-rect.position.y)<3 and rect.end.x-game.player.position.x>0 and rect.end.x-game.player.position.x<23:
     Input.action_press("jump");jumped_at=frames;break
  if game.player.is_on_floor() and game.player.position.y>275 and frames-jumped_at>35:
   Input.action_press("jump");jumped_at=frames
  if frames-jumped_at>24:Input.action_release("jump")
  await tick();frames+=1
 Input.action_release("move_right");Input.action_release("jump")
 check("Eight-screen route traversable with actual controller",game.player.position.x>4900)
 check("Action Foley emitted during traversal",game.sfx_index>10)
 var failed:=checks.filter(func(c):return not c.passed).size()
 var f=FileAccess.open("res://tests/scroll03-results.json",FileAccess.WRITE)
 f.store_string(JSON.stringify({"checks":checks,"failed":failed,"method":"Native gameplay checks with arranged states for individual mechanics; input-only route traversal isolates geometry. Physical Safari and audio listening not certified."},"  "));f.close()
 game.queue_free();await process_frame;await process_frame
 quit(1 if failed else 0)
