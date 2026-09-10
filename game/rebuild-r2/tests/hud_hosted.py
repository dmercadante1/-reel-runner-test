from pathlib import Path
from playwright.sync_api import sync_playwright
import json,traceback
R=Path(__file__).resolve().parents[1];H=(R/'Gothic-Horror-Playable.html').read_text();checks=[];errors=[]
def test(n,b,detail=None):
 checks.append({'name':n,'passed':bool(b),'detail':detail});print(('PASS 'if b else'FAIL ')+n,flush=True)
 (R/'evidence/r2-hud-checks.json').write_text(json.dumps({'checks':checks,'errors':errors},indent=2))
 if not b:raise AssertionError(n)
with sync_playwright()as pw:
 b=getattr(pw,'webkit').launch(headless=True)
 for width,height,mobile in [(1280,816,False),(1216,1242,False),(844,390,True),(667,375,True),(568,320,True),(390,844,True)]:
  ctx=b.new_context(viewport={'width':width,'height':height},is_mobile=mobile,has_touch=mobile,device_scale_factor=1);p=ctx.new_page();p.set_default_timeout(6000);p.on('pageerror',lambda e:errors.append(str(e)));p.goto('http://127.0.0.1:40723/',wait_until='load');p.wait_for_function('GOTHIC.phase==="ready"');label=f'{width}x{height}'
  bounds=p.evaluate('''()=>{let names=['life-meter','film-meter','capture-value','checkpoint','pause'];return {w:innerWidth,overflow:document.documentElement.scrollWidth>innerWidth,items:names.map(id=>{let r=document.getElementById(id).getBoundingClientRect();return {id,x:r.x,y:r.y,right:r.right,bottom:r.bottom,w:r.width,h:r.height}}),footer:document.querySelector('footer').getBoundingClientRect().toJSON(),main:document.querySelector('main').getBoundingClientRect().toJSON()}}''')
  test(label+' HUD stays within viewport',not bounds['overflow'] and all(v['x']>=0 and v['right']<=width+.1 and v['bottom']<=height+.1 for v in bounds['items']),bounds)
  test(label+' HUD does not overlap gameplay area',bounds['footer']['top']>=bounds['main']['bottom'])
  if mobile and height>width:
   test(label+' portrait prevents hidden start',p.locator('#start').is_hidden() and 'Rotate' in p.locator('#overlay-copy').inner_text());p.screenshot(path=str(R/'evidence/r2-portrait.png'))
  else:
   test(label+' start button visible',p.locator('#start').is_visible());p.locator('#start').click();p.wait_for_function('GOTHIC.phase==="running"');p.wait_for_timeout(500);test(label+' starts and ticks',p.evaluate('GOTHIC.scene.tick>5'))
   if width==1280:
    p.screenshot(path=str(R/'evidence/r2-desktop-hud.png'));test('HUD starts with five life units',p.locator('#hearts i:not(.empty)').count()==5 and p.locator('#life-value').inner_text()=='5/5')
    p.keyboard.down('Space');p.wait_for_timeout(400);p.keyboard.up('Space');test('Film readout and bar track gameplay film',p.evaluate('Number(document.getElementById("film-value").textContent)===Math.round(GOTHIC.scene.film)&&document.getElementById("film").value===Math.round(GOTHIC.scene.film)&&GOTHIC.scene.film<100'))
    p.evaluate('GOTHIC.scene.damage(GOTHIC.scene.enemies[0],GOTHIC.scene.time.now)');test('Damage dims exactly one heart',p.locator('#hearts i.empty').count()==1 and p.locator('#life-meter').get_attribute('aria-valuenow')=='4')
    p.locator('#pause').click();test('HUD pause changes to resume',p.evaluate('GOTHIC.phase==="paused"')and p.locator('#pause').inner_text()=='RESUME');p.locator('#pause').click();test('HUD resume unpauses',p.evaluate('GOTHIC.phase==="running"')and p.locator('#pause').inner_text()=='PAUSE')
    p.evaluate('GOTHIC.scene.captured=2;GOTHIC.scene.checkpoint=1440;GOTHIC.scene.renderHud()');test('Capture slots and checkpoint update',p.locator('#capture-value').inner_text()=='2/6'and p.locator('#capture-slots i.filled').count()==2 and p.locator('#checkpoint').inner_text()=='CHECKPOINT SAVED')
   if width==844:p.screenshot(path=str(R/'evidence/r2-mobile-hud.png'))
  ctx.close()
 test('HUD/launch checks no uncaught errors',not errors,errors)
 b.close()
print('HUD TOTAL',len(checks),'passed',sum(x['passed']for x in checks),flush=True)
