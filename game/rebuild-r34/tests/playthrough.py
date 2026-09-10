"""Real-keyboard progression test. No health/position/AI overrides in the full traversal."""
from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image,ImageChops
from io import BytesIO
import json,time,traceback,os,sys
R=Path(__file__).resolve().parents[1];edition=int(sys.argv[1])if len(sys.argv)>1 else 3;engine=os.getenv('BROWSER','chromium');checks=[];errors=[];keys=set()
def ck(n,v,d=None):
 checks.append({'name':n,'passed':bool(v),'detail':d});save();print(('PASS'if v else'FAIL'),n,flush=True)
 if not v:raise AssertionError((n,d))
def save():
 (R/f'evidence/r{edition}-{engine}-progress.json').write_text(json.dumps({'checks':checks,'errors':errors},indent=2))
def info(p):return p.evaluate('''(()=>{let s=GOTHIC.scene;return {phase:GOTHIC.phase,stage:s.stageIndex,x:s.player.x,y:s.player.y,bottom:s.player.body.bottom,vx:s.player.body.velocity.x,vy:s.player.body.velocity.y,hp:s.health,film:s.film,cap:s.captured,total:s.total,tick:s.tick,exit:s.stage.exit.x,top:s.exitTop,flash:s.flashUntil-s.clock,enemies:s.enemies.filter(e=>e.active&&e.getData('state')!=='capturing').map(e=>({x:e.x,type:e.getData('type'),state:e.getData('state')})),stats:s.stats};})()''')
def setkeys(p,desired):
 global keys
 for k in keys-desired:p.keyboard.up(k)
 for k in desired-keys:p.keyboard.down(k)
 keys=desired

def walk_to(p,x,limit=8):
 end=time.time()+limit
 while time.time()<end:
  a=info(p)
  if abs(a['x']-x)<7:break
  setkeys(p,{'ArrowRight'if a['x']<x else'ArrowLeft'});p.wait_for_timeout(40)
 setkeys(p,set());p.wait_for_timeout(140)
def jump_to(p,x):
 setkeys(p,{'ArrowUp','ArrowRight'});p.wait_for_timeout(150);setkeys(p,{'ArrowRight'})
 end=time.time()+2
 while time.time()<end and info(p)['x']<x:p.wait_for_timeout(35)
 setkeys(p,set());p.wait_for_timeout(500)
try:
 with sync_playwright()as pw:
  kwargs={'executable_path':'/usr/bin/chromium','args':['--no-sandbox']}if engine=='chromium'and not os.getenv('GITHUB_ACTIONS')else{}
  b=getattr(pw,engine).launch(**kwargs);p=b.new_page(viewport={'width':1280,'height':720});p.on('pageerror',lambda e:errors.append(str(e)));p.set_default_timeout(10000);p.set_content((R/f'releases/gothic-r{edition}/index.html').read_text(),wait_until='load');p.wait_for_function('GOTHIC.phase==="ready"');ck('Boot validates all 24 textures',p.evaluate('GOTHIC_ASSETS.length===24'))
  before=p.screenshot();p.evaluate('GOTHIC.scene.player.setVisible(false)');p.wait_for_timeout(65);after=p.screenshot();p.evaluate('GOTHIC.scene.player.setVisible(true)');ck('Player contributes visible rendered pixels',ImageChops.difference(Image.open(BytesIO(before)).convert('RGB'),Image.open(BytesIO(after)).convert('RGB')).getbbox()is not None)
  ck('HUD rendered in canvas, fixed over world',p.evaluate('GOTHIC.scene.hudHearts.length===5&&GOTHIC.scene.hudGraphics.scrollFactorX===0&&GOTHIC.scene.hudGraphics.depth===1000'))
  # Screenshot comparison is performed before Start, with the world paused, not while enemies can attack an unattended player.
  p.locator('#start').click();p.wait_for_timeout(650);ck('Start and floor landing',info(p)['phase']=='running'and abs(info(p)['bottom']-316)<2)
  setkeys(p,{'ArrowRight'});p.wait_for_timeout(400);ck('Moving hero uses 12 articulated frames',p.evaluate('GOTHIC.scene.player.anims.currentAnim.key==="hero-stride"&&GOTHIC.scene.player.anims.currentAnim.frames.length===12'));setkeys(p,{'ArrowUp'});p.wait_for_timeout(190);ck('Jump rises',info(p)['bottom']<285,info(p));setkeys(p,set());p.wait_for_timeout(700)
  setkeys(p,{'Space'});p.wait_for_function('GOTHIC.scene.light.visible && GOTHIC.scene.beaming');p.wait_for_timeout(40);ck('Camera optical spill illuminates scene',p.evaluate('GOTHIC.scene.light.visible&&GOTHIC.scene.light.alpha>.7'));p.screenshot(path=str(R/f'evidence/r{edition}-light-active.png'));setkeys(p,set())
  seen=set();nav=set();deadline=time.time()+165;last=time.time()
  while time.time()<deadline:
   s=info(p)
   if s['phase']=='complete':break
   if s['phase']=='transition':setkeys(p,set());p.wait_for_timeout(400);continue
   if s['phase']!='running':raise AssertionError(s)
   if s['stage']not in seen:
    seen.add(s['stage']);p.screenshot(path=str(R/f'evidence/r{edition}-{engine}-stage-{s["stage"]}.png'));ck('Game enters stage '+str(s['stage']+1),True,s['x'])
   if time.time()-last>5:print('PLAY',s,flush=True);last=time.time()
   if edition==4 and s['stage']==2 and 600<s['x']<890 and 'pit'not in nav:
    setkeys(p,set());walk_to(p,651);jump_to(p,736);ck('Catacomb near ledge reached by keyboard',any(abs(info(p)['bottom']-top)<8 for top in [264,286,292]),info(p));jump_to(p,897);ck('Chasm crossed with jump',info(p)['x']>878,info(p));nav.add('pit');continue
   if edition==4 and s['stage']==1 and not s['enemies']and s['x']>1220 and 'balcony'not in nav:
    setkeys(p,set());walk_to(p,1279);jump_to(p,1380);ck('Cathedral lower stair landed',abs(info(p)['bottom']-270)<6,info(p));jump_to(p,1480);ck('Cathedral balcony landed',abs(info(p)['bottom']-222)<6,info(p));nav.add('balcony');continue
   target=min(s['enemies'],key=lambda e:abs(e['x']-s['x']))if s['enemies']else None
   if target and abs(target['x']-s['x'])<263:
    desired={'Space'}
    if abs(target['x']-s['x'])>145:desired.add('ArrowLeft'if target['x']<s['x']else'ArrowRight')
    else:
     flip=p.evaluate('GOTHIC.scene.player.flipX')
     if flip!=(target['x']<s['x']):desired.add('ArrowLeft'if target['x']<s['x']else'ArrowRight')
    if edition==4 and abs(target['x']-s['x'])<186 and s['flash']<=0 and s['film']>=18 and target['state']in ['attack','windup']:desired.add('KeyX')
   else:desired={'ArrowRight'}
   if 'KeyX'in desired:desired.remove('KeyX');desired.add('x')
   setkeys(p,desired);p.wait_for_timeout(100)
  setkeys(p,set());ck('Keyboard-only complete four-stage traversal',info(p)['phase']=='complete',info(p));ck('All twelve encounters captured',info(p)['total']==12);ck('All four stages visited',len(seen)==4);p.screenshot(path=str(R/f'evidence/r{edition}-{engine}-complete.png'))
  p.locator('#start').click();p.wait_for_timeout(700);ck('Replay resets stage and captures',info(p)['stage']==0 and info(p)['total']==0);setkeys(p,{'ArrowRight'});p.wait_for_timeout(400);setkeys(p,set());ck('Replay moves',info(p)['x']>140)
  ck('No uncaught JavaScript exceptions',not errors,errors);b.close()
except Exception as e:
 traceback.print_exc();checks.append({'name':'fatal','passed':False,'detail':str(e)})
finally:
 result={'edition':edition,'engine':engine,'passed':sum(c['passed']for c in checks),'failed':sum(not c['passed']for c in checks),'checks':checks,'errors':errors};(R/f'evidence/r{edition}-{engine}-playthrough.json').write_text(json.dumps(result,indent=2));print('RESULT',result['passed'],result['failed']);
 if result['failed']:raise SystemExit(1)
