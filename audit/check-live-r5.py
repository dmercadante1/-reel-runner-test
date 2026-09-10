"""Actual-site R5 verification, including native HUD, mobile input and offline relaunch.
No game-state overrides. Engine phone emulation is not physical-device testing.
"""
import os,json,hashlib,pathlib,time,urllib.request,traceback
from playwright.sync_api import sync_playwright
BASE=os.getenv('GOTHIC_SITE','https://dmercadante1.github.io/-reel-runner-test/')
R5=BASE+'game/releases/gothic-r5/'
OUT=pathlib.Path('r5-live-evidence');OUT.mkdir(exist_ok=True)
BUILD=json.loads(pathlib.Path('game/releases/gothic-r5/build.json').read_text())
checks=[];errors=[]
def ck(name,ok,detail=None):
 checks.append({'name':name,'passed':bool(ok),'detail':detail});print(('PASS 'if ok else'FAIL ')+name,flush=True)
 if not ok:raise AssertionError((name,detail))
def read(url):
 with urllib.request.urlopen(urllib.request.Request(url,headers={'Cache-Control':'no-cache'}),timeout=25) as r:return r.read()
def state(p):return p.evaluate('({phase:GOTHIC.phase,x:GOTHIC.scene.player.x,bottom:GOTHIC.scene.player.body.bottom,film:GOTHIC.scene.film,tick:GOTHIC.scene.tick,flash:GOTHIC.scene.stats.flashes})')
def native(p,x,y,touch=False):
 b=p.locator('canvas').bounding_box();w=p.evaluate('GOTHIC.viewWidth');X=b['x']+x*b['width']/w;Y=b['y']+y*b['height']/360
 (p.touchscreen.tap(X,Y) if touch else p.mouse.click(X,Y))
result={'success':False,'physicalDeviceTested':False,'checks':checks,'errors':errors,'build':BUILD}
try:
 last=None
 for _ in range(65):
  try:
   data=read(R5+'?verify='+str(time.time_ns()));last=hashlib.sha256(data).hexdigest()
   if last==BUILD['sha256']:break
  except Exception as e:last=type(e).__name__
  time.sleep(4)
 ck('Public R5 bytes equal the tested build',last==BUILD['sha256'] and len(data)==BUILD['bytes'],{'sha256':last,'bytes':len(data) if 'data'in locals()else None})
 m=json.loads(read(R5+'manifest.webmanifest'));ck('Served app manifest is release-scoped standalone landscape',m['display']=='standalone' and m['scope']=='./' and m['orientation']=='landscape')
 ck('Served worker is release-scoped',b'request.url.startsWith(BASE)' in read(R5+'sw.js'))
 for n in [180,192,512]:ck('App icon '+str(n)+' is a PNG',read(R5+f'icon-{n}.png').startswith(b'\x89PNG\r\n\x1a\n'))
 ck('R4 remains byte-identical and directly playable',hashlib.sha256(read(BASE+'game/releases/gothic-r4a/')).hexdigest()=='5c07df9c37fe86fd6eba4cb72ce27fa6bef82c23a4c2348ee81d658fc6c6b2d4')
 with sync_playwright() as pw:
  for engine in ['chromium','webkit']:
   browser=getattr(pw,engine).launch()
   for mobile in [False,True]:
    label=engine+('-phone-emulated'if mobile else'-desktop');w,h=(844,390)if mobile else(1280,720)
    context=browser.new_context(viewport={'width':w,'height':h},has_touch=mobile,is_mobile=mobile)
    p=context.new_page();p.on('pageerror',lambda e,l=label:errors.append({'case':l,'error':str(e)}));p.set_default_timeout(15000)
    try:
     p.goto(BASE+'?r5verify='+str(time.time_ns()),wait_until='load');p.wait_for_function('window.GOTHIC&&GOTHIC.phase==="ready"')
     ck(label+' actual root reaches R5', '/gothic-r5/' in p.url and p.evaluate('GOTHIC_CONFIG.edition===5'),p.url)
     ck(label+' all 31 images loaded',p.evaluate('GOTHIC_ASSETS.length===31&&GOTHIC_ASSETS.every(a=>GOTHIC.scene.textures.exists(a.key))'))
     ck(label+' in-canvas protagonist portrait',p.evaluate('GOTHIC.scene.hudPortrait.visible&&GOTHIC.scene.hudPortrait.texture.key==="portrait"&&GOTHIC.scene.hudPortrait.depth===1000'))
     ck(label+' 30 configured encounters and four chasms',p.evaluate('GOTHIC_CONFIG.totalEncounters===30&&GOTHIC_CONFIG.stages.every(s=>s.gaps[0][1]-s.gaps[0][0]>=380&&s.ferry)'))
     b=p.locator('canvas').bounding_box();v=p.evaluate('GOTHIC.viewWidth');ck(label+' undistorted high-density screen',abs(b['width']/b['height']-v/360)<.02 and p.evaluate('GOTHIC.scene.cameras.main.zoom===2'))
     if mobile:ck(label+' mobile uses available height',b['height']>=h*.95)
     (p.locator('#start').tap()if mobile else p.locator('#start').click());p.wait_for_function('GOTHIC.phase==="running"')
     a=state(p);p.keyboard.down('ArrowRight');p.wait_for_function('(x)=>GOTHIC.scene.player.x>x+16',arg=a['x']);p.keyboard.up('ArrowRight');ck(label+' right arrow moves',state(p)['x']>a['x']+12)
     a=state(p);p.keyboard.down('ArrowLeft');p.wait_for_function('(x)=>GOTHIC.scene.player.x<x-16',arg=a['x']);p.keyboard.up('ArrowLeft');ck(label+' left arrow moves',state(p)['x']<a['x']-12)
     p.keyboard.press('ArrowUp');p.wait_for_function('GOTHIC.scene.player.body.bottom<275');ck(label+' quick up arrow jumps',True);p.wait_for_function('GOTHIC.scene.player.body.blocked.down||GOTHIC.scene.player.body.touching.down')
     a=state(p)
     if mobile:p.locator('[data-input="beam"]').tap()
     else:p.keyboard.down('Space')
     p.wait_for_function('(n)=>GOTHIC.scene.beaming&&GOTHIC.scene.film<n-2',arg=a['film'])
     if mobile:p.locator('[data-input="beam"]').tap()
     else:p.keyboard.up('Space')
     p.wait_for_function('!GOTHIC.scene.beaming');before=state(p)['film'];p.wait_for_timeout(450)
     ck(label+' film use does not instantly refill',state(p)['film']<=before+.1,{'before':before,'after':state(p)['film']})
     p.keyboard.press('x');p.wait_for_function('GOTHIC.scene.stats.flashes===1');ck(label+' flash defense works',True)
     native(p,v-52,27,mobile);p.wait_for_function('GOTHIC.phase==="paused"');ck(label+' native HUD pause works',True)
     (p.locator('#start').tap()if mobile else p.locator('#start').click());p.wait_for_function('GOTHIC.phase==="running"')
     p.evaluate('window.__oldRun=GOTHIC.scene.stats');p.keyboard.press('r');p.wait_for_function('GOTHIC.phase==="running"&&GOTHIC.scene.stats!==window.__oldRun');ck(label+' restart completes',True)
     if mobile:
      if engine=='chromium':
       cdp=context.new_cdp_session(p);box=p.locator('#move-pad').bounding_box();px=box['x']+box['width']*.82;py=box['y']+box['height']*.43
       pt=lambda i,x,y:{'id':i,'x':x,'y':y,'radiusX':4,'radiusY':4,'force':1}
       p.locator('[data-input="beam"]').tap();p.wait_for_function('GOTHIC.scene.beaming');left=pt(1,px,py)
       cdp.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[left]});p.wait_for_function('GOTHIC.inputs.right&&GOTHIC.scene.beaming')
       ck(label+' thumb pad and latched film operate together',True)
       jb=p.locator('[data-input="jump"]').bounding_box();right=pt(2,jb['x']+jb['width']/2,jb['y']+jb['height']/2)
       cdp.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[left,right]});p.wait_for_function('GOTHIC.scene.player.body.bottom<285&&GOTHIC.scene.beaming')
       ck(label+' two thumbs move jump and film simultaneously',True);cdp.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]});p.wait_for_function('!GOTHIC.inputs.right')
      else:
       box=p.locator('#move-pad').bounding_box();p.mouse.move(box['x']+box['width']*.82,box['y']+box['height']*.45);p.mouse.down();p.wait_for_function('GOTHIC.inputs.right');p.mouse.up();ck(label+' thumb-pad pointer capture clears',not p.evaluate('GOTHIC.inputs.right'))
      p.set_viewport_size({'width':390,'height':844});p.wait_for_function('GOTHIC.phase==="paused"');ck(label+' rotate clears held and latched inputs',p.evaluate('Object.values(GOTHIC.inputs).every(x=>!x)'));p.set_viewport_size({'width':844,'height':390});p.wait_for_function('GOTHIC.phase==="running"')
     native(p,p.evaluate('GOTHIC.viewWidth')-18,27,mobile);p.wait_for_function('!!document.fullscreenElement||!!document.webkitFullscreenElement||!document.getElementById("display-help").hidden')
     full=p.evaluate('!!document.fullscreenElement||!!document.webkitFullscreenElement')
     ck(label+' fullscreen button works or explains browser limitation',full or p.locator('#display-help').is_visible(),{'nativeFullscreen':full})
     if full:p.evaluate('document.exitFullscreen?document.exitFullscreen():document.webkitExitFullscreen()')
     else:p.locator('#close-display').click()
     p.evaluate('window.__oldRun=GOTHIC.scene.stats');p.keyboard.press('r');p.wait_for_function('GOTHIC.phase==="running"&&GOTHIC.scene.stats!==window.__oldRun');p.screenshot(path=str(OUT/(label+'.png')))
     p.wait_for_function('navigator.serviceWorker&&navigator.serviceWorker.controller',timeout=20000)
     ck(label+' release-scoped worker controls app',p.evaluate('navigator.serviceWorker.controller.scriptURL.includes("/gothic-r5/sw.js")'))
     context.set_offline(True);p.reload(wait_until='load');p.wait_for_function('GOTHIC.phase==="ready"');ck(label+' cached game relaunches offline',p.evaluate('GOTHIC_ASSETS.length===31'))
     context.set_offline(False)
    except Exception as e:
     checks.append({'name':label+' fatal','passed':False,'detail':str(e)});traceback.print_exc()
     try:p.screenshot(path=str(OUT/(label+'-failure.png')))
     except:pass
    finally:context.close()
   browser.close()
 ck('No uncaught served-game errors',not errors,errors);result['success']=all(c['passed']for c in checks)
except Exception as e:result['failure']=str(e);traceback.print_exc()
finally:
 result.update(passed=sum(c['passed']for c in checks),failed=sum(not c['passed']for c in checks));(OUT/'live-results.json').write_text(json.dumps(result,indent=2));print('LIVE RESULT',result['success'],result['passed'],result['failed'],flush=True)
 if not result['success']:raise SystemExit(1)
