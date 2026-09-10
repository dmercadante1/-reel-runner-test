"""Rendered-browser acceptance suite. It never marks unexecuted checks as passed."""
from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image,ImageChops
from io import BytesIO
import json,time,traceback,base64
R=Path(__file__).resolve().parents[1];H=(R/'Gothic-Horror-Playable.html').read_text();results=[];errors=[];fatal=None

def check(n,c,d=None):
 results.append({'name':n,'passed':bool(c),'detail':d});print(('PASS 'if c else'FAIL ')+n,flush=True)
 (R/'evidence/acceptance-progress.json').write_text(json.dumps({'checks':results,'uncaughtErrors':errors,'partial':True},indent=2))
 if not c:raise AssertionError((n,d))
def state(p):return p.evaluate('({phase:GOTHIC.phase,x:GOTHIC.scene.player.x,y:GOTHIC.scene.player.y,vy:GOTHIC.scene.player.body.velocity.y,film:GOTHIC.scene.film,health:GOTHIC.scene.health,captured:GOTHIC.scene.captured,ticks:GOTHIC.scene.tick,checkpoint:GOTHIC.scene.checkpoint})')
def hold(p,k,ms):p.keyboard.down(k);p.wait_for_timeout(ms);p.keyboard.up(k)
def load(b,mobile=False,canvas=False):
 c=b.new_context(viewport={'width':844,'height':390}if mobile else{'width':1280,'height':816},is_mobile=mobile,has_touch=mobile,device_scale_factor=1)
 p=c.new_page();p.set_default_timeout(10000);p.on('pageerror',lambda e:errors.append(str(e)));p.set_content(H.replace('type:Phaser.AUTO','type:Phaser.CANVAS')if canvas else H,wait_until='load');p.wait_for_function('GOTHIC.phase==="ready"');return c,p
def start(p):p.locator('#start').click();p.wait_for_timeout(750)
try:
 with sync_playwright()as pw:
  b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
  c,p=load(b);check('Ready state after asset validation',p.evaluate('GOTHIC.phase')=='ready')
  check('14 textures have exact expected dimensions',p.evaluate('GOTHIC_ASSETS.length===14&&GOTHIC_ASSETS.every(a=>{const t=GOTHIC.game.textures.get(a.key);return t.source[0].width===a.width&&t.source[0].height===a.height})'))
  p.screenshot(path=str(R/'evidence/verified-title.png'));start(p);check('Game loop advances',state(p)['ticks']>20)
  rect=p.locator('canvas').bounding_box();check('Desktop 16:9 canvas',abs(rect['width']/rect['height']-16/9)<.001,rect);check('Player lands on floor',abs(state(p)['y']-322)<1,state(p))
  p.evaluate('GOTHIC.scene.physics.pause();GOTHIC.phase="pixel-test"');p.wait_for_timeout(80);before=Image.open(BytesIO(p.screenshot())).convert('RGB');p.evaluate('GOTHIC.scene.player.setVisible(false)');p.wait_for_timeout(80);after=Image.open(BytesIO(p.screenshot())).convert('RGB');diff=ImageChops.difference(before,after);count=sum(1 for rgb in diff.getdata()if sum(rgb)>30);check('Player contributes actual visible raster pixels',count>1200,{'changedPixels':count,'bounds':diff.getbbox()});p.evaluate('GOTHIC.scene.player.setVisible(true);GOTHIC.phase="running";GOTHIC.scene.physics.resume()')
  x=state(p)['x'];hold(p,'ArrowRight',600);check('Move right',state(p)['x']>x+55);x=state(p)['x'];hold(p,'ArrowLeft',500);check('Move left',state(p)['x']<x-20);p.wait_for_timeout(160);y=state(p)['y'];hold(p,'ArrowUp',180);check('Jump moves upward',state(p)['y']<y-20);p.wait_for_timeout(800);check('Jump lands',abs(state(p)['y']-322)<1)
  p.evaluate('window.dispatchEvent(new Event("blur"))');check('Blur pauses',state(p)['phase']=='paused');x=state(p)['x'];p.wait_for_timeout(180);check('Paused player stays still',abs(state(p)['x']-x)<.01);p.evaluate('window.dispatchEvent(new Event("focus"))');check('Focus resumes',state(p)['phase']=='running')
  # Actual keyboard-only playthrough. No teleporting or changing game values here.
  for i in range(6):
   typ=p.evaluate(f'GOTHIC_CONFIG.spawns[{i}][0]');p.keyboard.down('ArrowRight');p.wait_for_function('i=>GOTHIC.scene.enemies[i].x-GOTHIC.scene.player.x<210',arg=i,timeout=15000);p.keyboard.up('ArrowRight');p.wait_for_timeout(120);p.keyboard.down('Space')
   if i==0:p.wait_for_timeout(350);p.screenshot(path=str(R/'evidence/verified-capture.png'));check('Camera consumes film',state(p)['film']<100)
   p.wait_for_function('n=>GOTHIC.scene.captured>=n',arg=i+1,timeout=8000);p.keyboard.up('Space');check('Capture '+typ,state(p)['captured']==i+1,state(p))
  p.keyboard.down('ArrowRight');p.wait_for_function('GOTHIC.phase==="complete"',timeout=15000);p.keyboard.up('ArrowRight');check('Full level clears via keyboard',state(p)['captured']==6 and state(p)['phase']=='complete',state(p));check('Checkpoint reached in playthrough',state(p)['checkpoint']==1440);p.screenshot(path=str(R/'evidence/verified-level-complete.png'))
  p.locator('#start').click();p.wait_for_function('GOTHIC.phase==="ready"');check('Restart resets encounters',state(p)['captured']==0 and state(p)['film']==100);start(p)
  # Controlled setup to exercise ledges/attacks, then ordinary simulation.
  p.evaluate('(()=>{const s=GOTHIC.scene;s.player.body.reset(620,322);s.player.setVelocity(0);})()');p.wait_for_timeout(60);p.keyboard.down('ArrowRight');hold(p,'ArrowUp',240);p.wait_for_timeout(140);p.keyboard.up('ArrowRight');p.wait_for_timeout(350);check('Lower raster ledge is reachable',abs(state(p)['y']-269)<2,state(p))
  p.evaluate('(()=>{const s=GOTHIC.scene;s.player.body.reset(400,322);s.player.setVelocity(0);s.enemies[0].body.reset(445,322);s.enemies[0].setData({nextAttack:0,state:"walk"});s.invUntil=0;})()');p.wait_for_function('GOTHIC.scene.health===4',timeout=4000);check('Enemy attack causes damage',state(p)['health']==4);p.wait_for_timeout(250);check('Invulnerability blocks immediate repeat damage',state(p)['health']==4)
  p.evaluate('(()=>{const s=GOTHIC.scene;s.checkpoint=1440;s.health=1;s.invUntil=0;s.hurtUntil=0;s.player.body.reset(400,322);s.enemies[0].body.reset(439,322);s.enemies[0].setData({state:"walk",nextAttack:0});})()');p.wait_for_function('GOTHIC.scene.player.x>1300',timeout=4000);check('Death respawns at checkpoint',state(p)['health']==5 and abs(state(p)['x']-1440)<25,state(p));p.wait_for_timeout(250)
  p.evaluate('GOTHIC.scene.film=.01');p.keyboard.down('Space');p.wait_for_timeout(80);check('Empty film enforces cooldown',p.evaluate('GOTHIC.scene.emptyUntil>GOTHIC.scene.time.now'));p.keyboard.up('Space');p.wait_for_timeout(700);check('Film recharges',state(p)['film']>5);check('Desktop no uncaught JS exceptions',not errors,errors[:]);c.close()
  c,p=load(b,canvas=True);start(p);check('Canvas renderer fallback starts',p.evaluate('GOTHIC.game.renderer.type')==1);x=state(p)['x'];hold(p,'ArrowRight',250);check('Canvas movement works',state(p)['x']>x+20);c.close()
  c,p=load(b,mobile=True);start(p);check('Touch controls visible',p.locator('#touch').is_visible());rect=p.locator('canvas').bounding_box();check('Mobile 16:9 canvas',abs(rect['width']/rect['height']-16/9)<.001,rect)
  right=p.locator('[data-input="right"]').bounding_box();beam=p.locator('[data-input="beam"]').bounding_box();jump=p.locator('[data-input="jump"]').bounding_box();cdp=c.new_cdp_session(p)
  def pt(q,i):return{'x':q['x']+q['width']/2,'y':q['y']+q['height']/2,'id':i}
  x=state(p)['x'];cdp.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[pt(right,1),pt(beam,2)]});p.wait_for_timeout(500);s=state(p);check('Real simultaneous move/camera touches',s['x']>x+20 and s['film']<98,s);cdp.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]});p.wait_for_timeout(120);check('Touch release clears inputs',p.evaluate('Object.values(GOTHIC.inputs).every(v=>!v)'))
  cdp.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[pt(jump,3)]});p.wait_for_timeout(160);check('Mobile touch jump',state(p)['vy']<0);cdp.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]});p.wait_for_timeout(700);p.screenshot(path=str(R/'evidence/verified-mobile.png'));p.set_viewport_size({'width':390,'height':844});p.wait_for_timeout(200);check('Portrait pauses',state(p)['phase']=='paused');check('Rotation instruction shown','ROTATE'in p.locator('#overlay-title').inner_text());p.set_viewport_size({'width':844,'height':390});p.wait_for_timeout(200);check('Landscape resumes',state(p)['phase']=='running');c.close();check('Suite has no uncaught JS errors',not errors,errors[:])
  c=b.new_context();p=c.new_page();a=json.loads((R/'assets/manifest.json').read_text())['assets'][0];encoded=base64.b64encode((R/a['file']).read_bytes()).decode();bad=H.replace(encoded,'AAAAAAAA'+encoded[8:],1);p.set_content(bad);p.wait_for_function('GOTHIC.phase==="error"',timeout=5000);check('Corrupt asset fails visibly without fake character',p.locator('#overlay').is_visible()and p.locator('#start').is_hidden());c.close();b.close()
except Exception as e:
 fatal=str(e);traceback.print_exc()
finally:
 data={'build':json.loads((R/'build.json').read_text()),'scope':'Chromium real renders, WebGL default/Canvas; mobile emulation with CDP multitouch. NOT Safari or physical phone.','passed':sum(r['passed']for r in results),'failed':sum(not r['passed']for r in results),'fatal':fatal,'checks':results,'uncaughtErrors':errors,'recordedAt':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())};(R/'evidence/acceptance-results.json').write_text(json.dumps(data,indent=2));print('TOTAL',data['passed'],'passed',data['failed'],'failed','fatal',fatal,flush=True)
