"""Real-input checks: filming must not freeze walking legs."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import os,json,traceback
R=Path(__file__).resolve().parents[1];engine=os.getenv('BROWSER','chromium');checks=[];errors=[]
def ck(name,ok,detail=None):
 checks.append({'name':name,'passed':bool(ok),'detail':detail});print(('PASS ' if ok else 'FAIL ')+name,flush=True)
 if not ok:raise AssertionError((name,detail))
try:
 with sync_playwright() as pw:
  kw={'executable_path':'/usr/bin/chromium','args':['--no-sandbox']} if engine=='chromium' and not os.getenv('GITHUB_ACTIONS') else {}
  b=getattr(pw,engine).launch(**kw)
  for edition in [3,4]:
   p=b.new_page(viewport={'width':1280,'height':720});p.on('pageerror',lambda e:errors.append(str(e)))
   p.set_content((R/f'releases/gothic-r{edition}/index.html').read_text(),wait_until='load');p.wait_for_function('GOTHIC.phase==="ready"');p.locator('#start').click();p.wait_for_function('GOTHIC.scene.player.body.blocked.down||GOTHIC.scene.player.body.touching.down')
   p.keyboard.down('ArrowRight');p.keyboard.down('Space');p.wait_for_function('GOTHIC.scene.beaming && GOTHIC.scene.playerState==="walk"')
   frames=[]
   for _ in range(6):
    frames.append(p.evaluate('GOTHIC.scene.player.frame.name'));p.wait_for_timeout(95)
   ck(f'R{edition} legs animate during camera use',len(set(frames))>=3,frames)
   ck(f'R{edition} camera light stays active during stride',p.evaluate('GOTHIC.scene.light.visible&&GOTHIC.scene.beaming&&GOTHIC.scene.player.body.velocity.x>20'))
   p.keyboard.up('ArrowRight');p.wait_for_function('Math.abs(GOTHIC.scene.player.body.velocity.x)<4&&GOTHIC.scene.playerState==="brace"');ck(f'R{edition} stationary filming returns to brace',True)
   p.keyboard.down('ArrowUp');p.wait_for_function('GOTHIC.scene.playerState==="jump"&&GOTHIC.scene.player.body.bottom<285');p.keyboard.up('ArrowUp');ck(f'R{edition} jumping overrides stride while light remains active',p.evaluate('GOTHIC.scene.beaming'))
   p.keyboard.up('Space');p.screenshot(path=str(R/f'evidence/r{edition}-{engine}-filming-locomotion.png'));p.close()
  ck('No uncaught locomotion errors',not errors,errors);b.close()
except Exception as e:
 traceback.print_exc();checks.append({'name':'fatal','passed':False,'detail':str(e)})
finally:
 result={'engine':engine,'checks':checks,'errors':errors,'passed':sum(c['passed'] for c in checks),'failed':sum(not c['passed'] for c in checks)}
 (R/f'evidence/{engine}-locomotion.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
 if result['failed']:raise SystemExit(1)
