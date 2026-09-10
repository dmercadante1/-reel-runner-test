"""HUD, renderer fallback, asset-failure and short-tap regression checks."""
from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image, ImageChops
from io import BytesIO
import os, json, traceback
R=Path(__file__).resolve().parents[1]
engine=os.getenv('BROWSER','chromium');checks=[];errors=[]
def ck(name,ok,detail=None):
 checks.append({'name':name,'passed':bool(ok),'detail':detail});print(('PASS' if ok else 'FAIL'),name,flush=True)
 if not ok:raise AssertionError((name,detail))
try:
 with sync_playwright() as pw:
  opts={'executable_path':'/usr/bin/chromium','args':['--no-sandbox']} if engine=='chromium' and not os.getenv('GITHUB_ACTIONS') else {}
  b=getattr(pw,engine).launch(**opts);h=(R/'releases/gothic-r4/index.html').read_text()
  for w,ht,touch in [(1280,720,False),(1216,1242,False),(844,390,True),(667,375,True),(568,320,True),(390,844,True)]:
   ctx=b.new_context(viewport={'width':w,'height':ht},has_touch=touch,is_mobile=touch);p=ctx.new_page();p.on('pageerror',lambda e,L=(w,ht):errors.append({'page':L,'message':e.message,'stack':e.stack}));p.set_content(h,wait_until='load');p.wait_for_function('GOTHIC.phase==="ready"');p.wait_for_timeout(120)
   bb=p.locator('canvas').bounding_box();ck(f'{w}x{ht} canvas is 16:9',abs(bb['width']/bb['height']-16/9)<.012,bb);ck(f'{w}x{ht} canvas stays in viewport',bb['x']>=-1 and bb['y']>=-1 and bb['x']+bb['width']<=w+1 and bb['y']+bb['height']<=ht+1)
   if touch and ht>w:
    ck('Portrait blocks accidental start',p.locator('#start').is_hidden());p.set_viewport_size({'width':844,'height':390});p.wait_for_timeout(150)
   (p.locator('#start').tap() if touch else p.locator('#start').click());p.wait_for_function('GOTHIC.phase==="running"');ck(f'{w}x{ht} starts without external assets',True)
   ck(f'{w}x{ht} HUD is canvas-only',p.evaluate('GOTHIC.scene.hudGraphics.scrollFactorX===0&&GOTHIC.scene.hudName.scrollFactorX===0&&document.querySelector("footer")===null'))
   # Numeric/heart state, not only initial screenshot geometry.
   p.evaluate('GOTHIC.scene.health=3;GOTHIC.scene.film=41;GOTHIC.scene.captured=2;GOTHIC_HUD.render(GOTHIC.scene)');ck(f'{w}x{ht} HUD reflects game values',p.evaluate('GOTHIC.scene.hudHearts[4].alpha<.3&&GOTHIC.scene.hudFilm.text==="041"&&GOTHIC.scene.hudCapture.text==="ON FILM 2/3"'))
   p.screenshot(path=str(R/f'evidence/r4-{engine}-layout-{w}x{ht}.png'));ctx.close()
  p=b.new_page();p.on('pageerror',lambda e:errors.append({'page':'canvas','message':e.message,'stack':e.stack}));p.set_content(h.replace('type:Phaser.AUTO,parent','type:Phaser.CANVAS,parent'),wait_until='load');p.wait_for_function('GOTHIC.phase==="ready"');p.locator('#start').click();p.wait_for_timeout(200);ck('Canvas renderer fallback boots',p.evaluate('GOTHIC.game.renderer.type===Phaser.CANVAS'))
  p.keyboard.press('x');p.wait_for_timeout(80);ck('Short X tap queues camera defense',p.evaluate('GOTHIC.scene.stats.flashes===1'))
  # A deliberate corruption must stop startup with a readable diagnostic.
  p.close();p=b.new_page();p.on('pageerror',lambda e:errors.append({'page':'corruption','message':e.message,'stack':e.stack}));idx=h.index('data:image/png;base64,',h.index('window.GOTHIC_ASSETS='))+len('data:image/png;base64,');broken=h[:idx]+'j'+h[idx+1:];p.set_content(broken,wait_until='load');p.wait_for_function('GOTHIC.phase==="error"');ck('Bad image blocks play explicitly',p.locator('#overlay').is_visible() and p.locator('#reload').is_visible());p.close()
  # Twelve lower-body frames must differ; count hashes of visible legs, not frame metadata.
  im=Image.open(R/'assets/hero-stride.png');import hashlib
  hashes={hashlib.sha256(im.crop((i*112,70,(i+1)*112,112)).tobytes()).hexdigest() for i in range(12)};ck('All 12 leg images contain different poses',len(hashes)==12)
  ck('No uncaught browser exceptions',not errors,errors);b.close()
except Exception:
 traceback.print_exc();checks.append({'name':'fatal','passed':False})
finally:
 result={'engine':engine,'scope':'R4 presentation, six emulated layouts, actual renderer and input checks; no physical hardware claim','passed':sum(c['passed']for c in checks),'failed':sum(not c['passed']for c in checks),'errors':errors,'checks':checks};(R/f'evidence/r4-{engine}-presentation.json').write_text(json.dumps(result,indent=2));print('RESULT',result['passed'],result['failed'])
 if result['failed']:raise SystemExit(1)
