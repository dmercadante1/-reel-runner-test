"""Verify public bytes and actual-root input in both engines. No gameplay state overrides."""
import hashlib,json,pathlib,time,urllib.request,traceback
from playwright.sync_api import sync_playwright
BASE='https://dmercadante1.github.io/-reel-runner-test/'
OUT=pathlib.Path('live-evidence');OUT.mkdir(exist_ok=True)
checks=[];errors=[]
def check(name,ok,detail=None):
 checks.append({'name':name,'passed':bool(ok),'detail':detail});print(('PASS ' if ok else 'FAIL ')+name,flush=True)
 if not ok:raise AssertionError((name,detail))
def state(p):
 return p.evaluate('({phase:GOTHIC.phase,x:GOTHIC.scene.player.x,bottom:GOTHIC.scene.player.body.bottom,stage:GOTHIC.scene.stageIndex,edition:GOTHIC_CONFIG.edition,tick:GOTHIC.scene.tick,film:GOTHIC.scene.film,flashes:GOTHIC.scene.stats.flashes})')
def press(p,key,mobile):
 if mobile:
  box=p.locator('[data-input="'+key+'"]').bounding_box();p.mouse.move(box['x']+box['width']/2,box['y']+box['height']/2);p.mouse.down();return p.mouse.up
 name={'right':'ArrowRight','jump':'ArrowUp','beam':'Space','flash':'x'}[key];p.keyboard.down(name);return lambda:p.keyboard.up(name)
def wait_bytes(edition):
 build=json.loads(pathlib.Path(f'game/releases/gothic-r{edition}/build.json').read_text());last=None
 for _ in range(75):
  try:
   req=urllib.request.Request(BASE+f'game/releases/gothic-r{edition}/?verify='+str(time.time_ns()),headers={'Cache-Control':'no-cache'})
   with urllib.request.urlopen(req,timeout=25) as res:data=res.read()
   last=hashlib.sha256(data).hexdigest()
   if last==build['sha256']:
    check(f'R{edition} served SHA-256 matches tested bytes',len(data)==build['bytes'],{'sha256':last,'bytes':len(data)});return build
  except Exception as e:last=type(e).__name__
  time.sleep(4)
 raise AssertionError(('Published content never matched tested build',edition,last))
result={'success':False,'physicalDeviceTested':False,'checks':checks,'errors':errors}
try:
 result['builds']={str(n):wait_bytes(n) for n in [3,4]}
 with sync_playwright() as pw:
  for engine in ['chromium','webkit']:
   browser=getattr(pw,engine).launch()
   for edition in [3,4]:
    for mobile in [False,True]:
     label=f'{engine}-r{edition}-'+('phone-emulated' if mobile else 'desktop');w,h=(844,390) if mobile else (1280,720)
     context=browser.new_context(viewport={'width':w,'height':h},has_touch=mobile,is_mobile=mobile);page=context.new_page();page.on('pageerror',lambda e,l=label:errors.append({'case':l,'error':e.message}));page.set_default_timeout(15000)
     url=BASE if edition==4 else BASE+'game/releases/gothic-r3/'
     page.goto(url+'?verify='+str(time.time_ns()),wait_until='load');page.wait_for_function('window.GOTHIC && GOTHIC.phase==="ready"')
     check(label+' root resolves correct edition',state(page)['edition']==edition and f'gothic-r{edition}/' in page.url,page.url)
     check(label+' all 24 raster textures loaded',page.evaluate('GOTHIC_ASSETS.length===24 && GOTHIC_ASSETS.every(a=>GOTHIC.scene.textures.exists(a.key))'))
     (page.locator('#start').tap() if mobile else page.locator('#start').click());page.wait_for_function('GOTHIC.phase==="running"')
     # Exercise camera before approaching enemies; the full combat runs are separate.
     if edition==4:
      release=press(page,'flash',mobile);page.wait_for_function('GOTHIC.scene.stats.flashes===1',timeout=4000);release();check(label+' flash defense accepts input',True,state(page))
     a=state(page);release=press(page,'beam',mobile)
     page.wait_for_function('(value)=>GOTHIC.scene.film<value-1',arg=a['film'],timeout=4000);b=state(page);release();check(label+' camera consumes film',b['film']<a['film']-1,{'before':a['film'],'after':b['film']})
     a=state(page);release=press(page,'right',mobile);page.wait_for_function('(x)=>GOTHIC.scene.player.x>x+15',arg=a['x'],timeout=4000);b=state(page);release();check(label+' actual input moves hero',b['x']>a['x']+12,{'before':a['x'],'after':b['x']})
     release=press(page,'jump',mobile);page.wait_for_function('GOTHIC.scene.player.body.bottom<285',timeout=4000);air=state(page);release();check(label+' jump lifts physics body',air['bottom']<285,air)
     # Frame scheduling is different under software rendering. Await the collision
     # event within five seconds instead of assuming 750 wall-clock ms is a landing.
     page.wait_for_function('Math.abs(GOTHIC.scene.player.body.bottom-316)<3 && (GOTHIC.scene.player.body.blocked.down || GOTHIC.scene.player.body.touching.down)',timeout=5000)
     check(label+' jump lands on floor',abs(state(page)['bottom']-316)<3,state(page))
     check(label+' HUD inside canvas',page.evaluate('GOTHIC.scene.hudGraphics.scrollFactorX===0 && GOTHIC.scene.hudGraphics.depth===1000 && !document.querySelector("footer")'))
     rect=page.locator('canvas').bounding_box();check(label+' canvas fits without distortion',abs(rect['width']/rect['height']-16/9)<.012 and rect['x']>=-1 and rect['y']>=-1 and rect['x']+rect['width']<=w+1 and rect['y']+rect['height']<=h+1,rect)
     x=rect['x']+603*rect['width']/640;y=rect['y']+22*rect['height']/360
     (page.touchscreen.tap(x,y) if mobile else page.mouse.click(x,y));page.wait_for_function('GOTHIC.phase==="paused"');check(label+' native HUD pause works',True)
     (page.locator('#start').tap() if mobile else page.locator('#start').click());page.wait_for_function('GOTHIC.phase==="running"')
     page.evaluate('window.__previousRunStats=GOTHIC.scene.stats');page.keyboard.press('r');page.wait_for_function('GOTHIC.phase==="running" && GOTHIC.scene.stats!==window.__previousRunStats && GOTHIC.scene.player.x<120')
     release=press(page,'right',mobile);page.wait_for_function('GOTHIC.scene.player.x>125',timeout=4000);release();check(label+' restart remains playable',state(page)['x']>125)
     if mobile:
      page.set_viewport_size({'width':390,'height':844});page.wait_for_function('GOTHIC.phase==="paused"');page.set_viewport_size({'width':844,'height':390});page.wait_for_function('GOTHIC.phase==="running"');check(label+' orientation pauses and resumes',True)
     page.screenshot(path=str(OUT/(label+'.png')));context.close()
   browser.close()
 check('No uncaught live browser exceptions',not errors,errors);result['success']=True
except Exception as e:
 result['failure']=str(e);traceback.print_exc()
finally:
 result.update(passed=sum(c['passed'] for c in checks),failed=sum(not c['passed'] for c in checks));(OUT/'live-results.json').write_text(json.dumps(result,indent=2));print('LIVE RESULT',result['success'],result['passed'],result['failed'],flush=True)
 if not result['success']:raise SystemExit(1)
