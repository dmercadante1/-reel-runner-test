"""Isolated R4 physics/combat fixtures plus real mobile-emulated input. Not a full-playthrough claim."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import os,json,traceback,time
from platform_probe import check_platform_carry
from shockwave_probe import check_shockwave_dodge
R=Path(__file__).resolve().parents[1];engine=os.getenv('BROWSER','chromium');checks=[];errors=[]
def ck(name,ok,detail=None):
 checks.append({'name':name,'passed':bool(ok),'detail':detail});(R/f'evidence/r4-{engine}-mechanics-progress.json').write_text(json.dumps({'checks':checks,'errors':errors},indent=2));print(('PASS'if ok else'FAIL'),name,flush=True)
 if not ok:raise AssertionError((name,detail))
def fixture(p,i=0):
 p.evaluate('(i)=>{window.__fixtureStats=GOTHIC.scene.stats;GOTHIC.scene.scene.restart({stage:i,auto:true});}',i)
 p.wait_for_function('(i)=>GOTHIC.phase==="running"&&GOTHIC.scene.stageIndex===i&&GOTHIC.scene.stats!==window.__fixtureStats&&GOTHIC.scene.player?.body?.enable',arg=i)
 p.evaluate('GOTHIC.scene.enemies.forEach(e=>{e.setData("stunUntil",1e9);e.setVelocity(0)})')
 p.wait_for_function('GOTHIC.scene.tick>=2&&(GOTHIC.scene.player.body.blocked.down||GOTHIC.scene.player.body.touching.down)')
 assert p.evaluate('GOTHIC.scene.stats.damage===0&&GOTHIC.scene.stats.attacks===0&&GOTHIC.scene.enemies.every(e=>e.getData("stunUntil")>GOTHIC.scene.clock)'), 'Fixture is not isolated from previous scene/AI'
def snapshot(p):return p.evaluate('({x:GOTHIC.scene.player.x,bottom:GOTHIC.scene.player.body.bottom,health:GOTHIC.scene.health,film:GOTHIC.scene.film,stats:GOTHIC.scene.stats,phase:GOTHIC.phase})')
try:
 with sync_playwright()as pw:
  kw={'executable_path':'/usr/bin/chromium','args':['--no-sandbox']}if engine=='chromium'and not os.getenv('GITHUB_ACTIONS')else{}
  b=getattr(pw,engine).launch(**kw);p=b.new_page(viewport={'width':1280,'height':720});p.on('pageerror',lambda e:errors.append(str(e)));H=(R/'releases/gothic-r4/index.html').read_text();p.set_content(H,wait_until='load');p.wait_for_function('GOTHIC.phase==="ready"');p.locator('#start').click();p.wait_for_timeout(400)
  ck('R4 edition enabled',p.evaluate('GOTHIC_CONFIG.edition===4'))
  fixture(p);p.evaluate('GOTHIC.scene.player.body.reset(590,322)');p.keyboard.down('ArrowUp');p.wait_for_timeout(210);p.keyboard.up('ArrowUp');ck('Jump passes upward through one-way ledge',snapshot(p)['bottom']<264,snapshot(p));p.wait_for_timeout(720);ck('Lands on ledge top',abs(snapshot(p)['bottom']-264)<2,snapshot(p));ck('Visible artwork matches collision surface',p.evaluate('GOTHIC.scene.platforms.every(p=>Math.abs(p.art.y-p.zone.body.top)<1&&Math.abs(p.art.x-(p.zone.x-p.def.width/2))<1)'))
  fixture(p,1);check_platform_carry(p,ck)
  fixture(p,2);p.evaluate('(()=>{let s=GOTHIC.scene,a=s.platforms.find(p=>p.def.crumble);s.player.body.reset(a.zone.x,a.zone.body.top-18);s.player.setVelocity(0);})()');p.wait_for_timeout(1300);ck('Crumbling ledge gives way after landing',p.evaluate('!GOTHIC.scene.platforms.find(p=>p.def.crumble).zone.body.enable'));p.wait_for_timeout(3400);ck('Crumbling ledge restores safely',p.evaluate('GOTHIC.scene.platforms.find(p=>p.def.crumble).zone.body.enable'))
  # Each ability exercised without capture input suppressing the tell.
  for kind in ['skeleton','ghoul','vampire','ghost','monster','werewolf']:
   fixture(p);p.evaluate('''kind=>{let s=GOTHIC.scene;s.enemies.forEach(e=>e.destroy());s.enemies=[];let c=GOTHIC_CONFIG.enemies[kind];s.spawn(kind,110+c.range-15);s.enemies[0].setData('nextAttack',s.clock); }''',kind);p.wait_for_timeout(240);ck(kind+' readable windup',p.evaluate('GOTHIC.scene.enemies[0].getData("state")==="windup"'));p.wait_for_timeout(1000);ck(kind+' executes its attack',p.evaluate('GOTHIC.scene.stats.attacks>=1'));p.screenshot(path=str(R/f'evidence/r4-{engine}-{kind}-attack.png'))
  fixture(p);p.evaluate('''()=>{let s=GOTHIC.scene;s.enemies.forEach(e=>e.destroy());s.enemies=[];s.spawn('monster',230);s.enemies[0].setData({state:'windup',attackAt:s.clock,nextAttack:s.clock+3000});}''');p.keyboard.press('x');p.wait_for_timeout(90);s=snapshot(p);ck('Flash costs film and triggers defense',s['film']<88 and s['stats']['flashes']==1,s);ck('Flash interrupts monster armor/attack',p.evaluate('GOTHIC.scene.enemies[0].getData("stunUntil")>GOTHIC.scene.clock'));p.keyboard.press('x');p.wait_for_timeout(90);ck('Flash cooldown prevents spamming',snapshot(p)['stats']['flashes']==1);p.screenshot(path=str(R/f'evidence/r4-{engine}-flash.png'))
  p.evaluate('GOTHIC.scene.film=0;GOTHIC.scene.flashUntil=0');p.keyboard.press('x');p.wait_for_timeout(70);ck('Insufficient film refuses flash',snapshot(p)['stats']['flashes']==1)
  fixture(p);p.evaluate('''()=>{let s=GOTHIC.scene,e=s.enemies[0];e.body.reset(280,322);e.setData('stunUntil',1e9);s.player.setFlipX(false);GOTHIC_COMBAT.shoot(s,e,'bone',-1);}''');p.keyboard.down('Space');p.wait_for_timeout(300);p.keyboard.up('Space');ck('Camera light destroys incoming bone projectile',snapshot(p)['stats']['blocked']>=1,snapshot(p))
  check_shockwave_dodge(p,fixture,ck,snapshot)
  fixture(p);p.evaluate('''()=>{let s=GOTHIC.scene,e=s.enemies[0];e.body.reset(260,322);GOTHIC_COMBAT.shoot(s,e,'wave',-1);}''');p.wait_for_timeout(1100);ck('Same ground shockwave damages grounded player',snapshot(p)['health']==4,snapshot(p));p.evaluate('GOTHIC.scene.damage({x:300});GOTHIC.scene.damage({x:300})');ck('Invulnerability prevents stacked damage',snapshot(p)['health']==4)
  fixture(p);p.evaluate('GOTHIC.scene.checkpoint=850;GOTHIC.scene.health=1;GOTHIC.scene.damage({x:400})');p.wait_for_timeout(250);ck('Lethal damage restores checkpoint',abs(snapshot(p)['x']-850)<2 and snapshot(p)['health']==5,snapshot(p))
  p.evaluate('GOTHIC.pause("manual",true)');a=p.evaluate('GOTHIC.scene.clock');p.wait_for_timeout(400);ck('Pause freezes combat clock',p.evaluate('GOTHIC.scene.clock')==a);p.locator('#start').click();ck('Resume restores running state',snapshot(p)['phase']=='running')
  for i in range(4):
   p.keyboard.press('r');p.wait_for_timeout(400);p.keyboard.down('ArrowRight');p.wait_for_timeout(220);p.keyboard.up('ArrowRight');ck('Restart cycle '+str(i+1)+' moves',snapshot(p)['x']>122)
  c=b.new_context(viewport={'width':844,'height':390},has_touch=True,is_mobile=True);m=c.new_page();m.on('pageerror',lambda e:errors.append(str(e)));m.set_content(H,wait_until='load');m.wait_for_function('GOTHIC.phase==="ready"');m.locator('#start').tap();m.wait_for_timeout(350);ck('Mobile touch Start works',snapshot(m)['phase']=='running');bb=m.locator('canvas').bounding_box();ck('Mobile canvas retains 16:9',abs(bb['width']/bb['height']-16/9)<.01,bb)
  if engine=='chromium':
   cd=c.new_cdp_session(m);r=m.locator('[data-input="right"]').bounding_box();f=m.locator('[data-input="beam"]').bounding_box();points=[{'x':r['x']+r['width']/2,'y':r['y']+r['height']/2,'id':1},{'x':f['x']+f['width']/2,'y':f['y']+f['height']/2,'id':2}];x=snapshot(m)['x'];cd.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':points});m.wait_for_timeout(420);ck('Simultaneous mobile movement and filming',snapshot(m)['x']>x+10 and m.evaluate('GOTHIC.scene.beaming'));cd.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]});m.wait_for_timeout(130);ck('Touch release clears controls',m.evaluate('Object.values(GOTHIC.inputs).every(v=>!v)'))
  m.screenshot(path=str(R/f'evidence/r4-{engine}-mobile.png'));m.set_viewport_size({'width':390,'height':844});m.wait_for_timeout(300);ck('Portrait pauses play',snapshot(m)['phase']=='paused');m.set_viewport_size({'width':844,'height':390});m.wait_for_timeout(300);ck('Landscape resumes safely',snapshot(m)['phase']=='running');c.close()
  ck('No uncaught browser exceptions',not errors,errors);b.close()
except Exception as e:
 traceback.print_exc();checks.append({'name':'fatal','passed':False,'detail':str(e)})
finally:
 result={'edition':4,'engine':engine,'scope':'Controlled physics/combat fixtures and mobile emulation; not a physical-device test','checks':checks,'errors':errors,'passed':sum(x['passed']for x in checks),'failed':sum(not x['passed']for x in checks)};(R/f'evidence/r4-{engine}-mechanics.json').write_text(json.dumps(result,indent=2));print('RESULT',result['passed'],result['failed']);
 if result['failed']:raise SystemExit(1)
