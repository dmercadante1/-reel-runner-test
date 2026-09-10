"""Verify the public root and exact approved HTML after Pages publishes. No writes."""
import hashlib,json,pathlib,time,urllib.request
from playwright.sync_api import sync_playwright
BASE='https://dmercadante1.github.io/-reel-runner-test/'
TARGET=BASE+'game/releases/gothic-hud-r2/'
EXPECTED='99676e652482b652eadfcb87bf7411ebbfe11bcefffa87b7aa60fdfc98962839'
OUT=pathlib.Path('live-evidence');OUT.mkdir(exist_ok=True);results=[];errors=[]
for attempt in range(40):
 try:
  with urllib.request.urlopen(TARGET+'?verify='+str(int(time.time())),timeout=20) as r:body=r.read()
  if hashlib.sha256(body).hexdigest()==EXPECTED:break
 except Exception:pass
 time.sleep(8)
else:raise RuntimeError('Pages is not serving the approved bytes; no live success claim.')
results.append({'name':'Deployed HTML exact SHA-256','passed':True,'sha256':EXPECTED,'bytes':len(body)})
with sync_playwright() as pw:
 for engine in ('chromium','webkit'):
  b=getattr(pw,engine).launch(headless=True)
  for mobile in (False,True):
   label=engine+('-phone' if mobile else '-desktop');ctx=b.new_context(viewport={'width':844,'height':390} if mobile else {'width':1280,'height':816},is_mobile=mobile,has_touch=mobile,device_scale_factor=2 if mobile else 1)
   p=ctx.new_page();p.set_default_timeout(15000);p.on('pageerror',lambda e:errors.append(str(e)));p.goto(BASE+'?build=gothic-hud-r2');p.wait_for_function('window.GOTHIC&&GOTHIC.phase==="ready"');assert p.url.rstrip('/')==TARGET.rstrip('/'),p.url
   assert p.locator('#build').inner_text()=='BUILD R2';assert p.locator('#life-value').inner_text()=='5/5';assert p.locator('#capture-value').inner_text()=='0/6'
   p.locator('#start').tap() if mobile else p.locator('#start').click();p.wait_for_function('GOTHIC.phase==="running"');p.wait_for_timeout(600)
   assert p.evaluate('GOTHIC.scene.tick>10&&GOTHIC.scene.player.visible&&GOTHIC.scene.player.alpha>0')
   dims=p.locator('canvas').bounding_box();assert abs(dims['width']/dims['height']-16/9)<.001
   hud=p.locator('footer').bounding_box();assert hud['y']>=dims['y']+dims['height']-1
   p.screenshot(path=str(OUT/(label+'.png')))
   if not mobile:
    x=p.evaluate('GOTHIC.scene.player.x');p.keyboard.down('ArrowRight');p.wait_for_timeout(450);p.keyboard.up('ArrowRight');assert p.evaluate('GOTHIC.scene.player.x')>x+35
    p.keyboard.down('ArrowUp');p.wait_for_timeout(140);p.keyboard.up('ArrowUp');assert p.evaluate('GOTHIC.scene.player.body.velocity.y')<0
    p.wait_for_timeout(800);p.keyboard.down('Space');p.wait_for_timeout(400);p.keyboard.up('Space');assert p.evaluate('GOTHIC.scene.film')<100
    p.keyboard.press('r');p.wait_for_function('GOTHIC.phase==="ready"');p.locator('#start').click();p.wait_for_function('GOTHIC.phase==="running"');p.wait_for_timeout(350);assert p.evaluate('GOTHIC.scene.tick>5')
   p.locator('#pause').tap() if mobile else p.locator('#pause').click();p.wait_for_function('GOTHIC.phase==="paused"');p.locator('#pause').tap() if mobile else p.locator('#pause').click();p.wait_for_function('GOTHIC.phase==="running"')
   results.append({'name':label+' actual root start, visible player, HUD, aspect ratio, pause/resume'+('' if mobile else ', movement, jump, film and replay'),'passed':True,'url':p.url});ctx.close()
  b.close()
assert not errors,errors
report={'success':True,'checks':results,'uncaughtErrors':errors,'physicalPhoneTested':False,'recordedAt':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())};(OUT/'live-checks.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
