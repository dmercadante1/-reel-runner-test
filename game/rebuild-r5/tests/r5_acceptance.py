"""Isolated mechanics and presentation tests, separately labeled from the real-key traversal."""
from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image,ImageChops
from io import BytesIO
import os,json,traceback,time
G_SPAWN_LIMIT=220
R=Path(__file__).resolve().parents[1];engine=os.getenv('BROWSER','chromium');checks=[];errors=[]
def ck(name,ok,detail=None):
 checks.append({'name':name,'passed':bool(ok),'detail':detail});print(('PASS 'if ok else'FAIL ')+name,flush=True)
 if not ok:raise AssertionError((name,detail))
def state(p):return p.evaluate('''(()=>{const s=GOTHIC.scene;return{phase:GOTHIC.phase,x:s.player.x,bottom:s.player.body.bottom,film:s.film,health:s.health,clock:s.clock,stats:s.stats,stage:s.stageIndex,tick:s.tick};})()''')
def open_page(b,w=1280,h=720,mobile=False,init=None):
 p=b.new_page(viewport={'width':w,'height':h},has_touch=mobile,is_mobile=mobile);p.on('pageerror',lambda e:errors.append(str(e)));p.set_default_timeout(10000)
 if init:p.add_init_script(init)
 # Init scripts don't run during set_content; invoke test capability overrides explicitly.
 if init:p.evaluate(init)
 p.set_content((R/'releases/gothic-r5/index.html').read_text(),wait_until='load');p.wait_for_function('window.GOTHIC&&GOTHIC.phase==="ready"');return p

def fixture(p,stage=0):
 if p.evaluate('GOTHIC.phase')=='paused':
  p.keyboard.press('Escape');p.wait_for_function('GOTHIC.phase==="running"')
 p.evaluate('(i)=>{GOTHIC.clearInputs();window.__oldStats=GOTHIC.scene.stats;GOTHIC.scene.scene.restart({stage:i,auto:true});}',stage)
 p.wait_for_function('(i)=>GOTHIC.phase==="running"&&GOTHIC.scene.stageIndex===i&&GOTHIC.scene.stats!==window.__oldStats&&GOTHIC.scene.player?.body?.enable',arg=stage)
 p.evaluate('GOTHIC.scene.enemies.forEach(e=>{e.setData({stunUntil:1e9,nextAttack:1e9});e.setVelocity(0);})')
 p.wait_for_function('GOTHIC.scene.player.body.blocked.down||GOTHIC.scene.player.body.touching.down')
def simwait(p,ms):
 t=state(p)['clock'];p.wait_for_function('(t)=>GOTHIC.scene.clock>=t',arg=t+ms,timeout=max(4000,ms*3))

try:
 with sync_playwright() as pw:
  kw={'executable_path':'/usr/bin/chromium','args':['--no-sandbox']}if engine=='chromium'and not os.getenv('GITHUB_ACTIONS')else{}
  b=getattr(pw,engine).launch(**kw);p=open_page(b)
  ck('All 31 assets decode at declared dimensions',p.evaluate('GOTHIC_ASSETS.length===31&&GOTHIC_ASSETS.every(a=>{const im=GOTHIC.scene.textures.get(a.key).getSourceImage();return im.width===a.width&&im.height===a.height})'))
  ck('Four native 1280x720 environment textures',p.evaluate('["courtyard","cathedral","catacombs","ramparts"].every(k=>GOTHIC.scene.textures.get(k).getSourceImage().width===1280)'))
  ck('Canvas renders at 2x density without changing world units',p.evaluate('GOTHIC.game.scale.width===1280&&GOTHIC.scene.cameras.main.zoom===2&&GOTHIC_CONFIG.floorY===316'))
  ck('Portrait uses approved raster and is in the game HUD',p.evaluate('GOTHIC.scene.hudPortrait.texture.key==="portrait"&&GOTHIC.scene.hudPortrait.scrollFactorX===0&&GOTHIC.scene.hudPortrait.displayWidth===44&&GOTHIC.scene.hudPortrait.depth===1000'))
  # Before start, visual diff is confined to the portrait and excludes moving gameplay.
  p.locator('#overlay').evaluate('(e)=>e.hidden=true');before=p.screenshot();p.evaluate('GOTHIC.scene.hudPortrait.setVisible(false)');p.wait_for_timeout(70);after=p.screenshot();p.evaluate('GOTHIC.scene.hudPortrait.setVisible(true)');box=ImageChops.difference(Image.open(BytesIO(before)).convert('RGB'),Image.open(BytesIO(after)).convert('RGB')).getbbox();ck('Portrait contributes visible screen pixels',box is not None,box)
  p.locator('#overlay').evaluate('(e)=>e.hidden=false');p.locator('#start').click();fixture(p)
  x=state(p)['x'];p.keyboard.down('ArrowRight');p.wait_for_function('(x)=>GOTHIC.scene.player.x>x+25',arg=x);p.keyboard.up('ArrowRight');ck('Right arrow moves player',state(p)['x']>x+20)
  x=state(p)['x'];p.keyboard.down('ArrowLeft');p.wait_for_function('(x)=>GOTHIC.scene.player.x<x-25',arg=x);p.keyboard.up('ArrowLeft');ck('Left arrow moves player',state(p)['x']<x-20)
  p.keyboard.down('ArrowUp');p.wait_for_function('GOTHIC.scene.player.body.bottom<265');p.keyboard.up('ArrowUp');ck('Up arrow jumps',state(p)['bottom']<265);p.wait_for_function('GOTHIC.scene.player.body.blocked.down');ck('Arrow jump lands',abs(state(p)['bottom']-316)<3)
  p.keyboard.down('d');p.wait_for_timeout(180);ck('A/D bindings retained',p.evaluate('GOTHIC.scene.player.body.velocity.x>0'));p.keyboard.up('d');fixture(p)
  p.evaluate('GOTHIC.scene.film=50;GOTHIC.scene.lastFilmUse=GOTHIC.scene.clock');simwait(p,4200);ck('Film above emergency reserve does not auto-refill',abs(state(p)['film']-50)<.01,state(p))
  p.evaluate('GOTHIC.scene.film=8;GOTHIC.scene.lastFilmUse=GOTHIC.scene.clock');simwait(p,1500);ck('No immediate film regeneration after use',abs(state(p)['film']-8)<.01)
  p.evaluate('GOTHIC.scene.lastFilmUse=GOTHIC.scene.clock-5000');a=state(p);simwait(p,1000);z=state(p);ck('Emergency film recovers only 0.8 units/second',.65<z['film']-a['film']<1.1,{'before':a,'after':z})
  p.evaluate('GOTHIC.scene.film=23.8');simwait(p,800);ck('Emergency recharge stops at 24',abs(state(p)['film']-24)<.02)
  p.evaluate('GOTHIC.scene.film=60');a=state(p);p.keyboard.down('Space');simwait(p,700);p.keyboard.up('Space');z=state(p);ck('Camera consumes scarce film while held',7< a['film']-z['film']<10,{'delta':a['film']-z['film']})
  fixture(p);p.evaluate('GOTHIC.scene.film=30;GOTHIC.scene.player.body.reset(GOTHIC.scene.stage.pickups[0].x,322)');p.wait_for_function('GOTHIC.scene.stats.pickups===1');ck('Physical reel pickup restores 25 units',abs(state(p)['film']-55)<.5,state(p))
  fixture(p);p.evaluate('GOTHIC.scene.film=30;GOTHIC.scene.player.body.reset(GOTHIC.scene.stage.checkpoint+4,322)');p.wait_for_function('GOTHIC.scene.stats.checkpoints===1');ck('One-time checkpoint cache adds 20 film',abs(state(p)['film']-50)<.5,state(p))
  p.evaluate('GOTHIC.scene.player.body.reset(GOTHIC_CONFIG.spawnX,322)');simwait(p,50);p.evaluate('GOTHIC.scene.player.body.reset(GOTHIC.scene.stage.checkpoint+4,322)');simwait(p,50);ck('Checkpoint cache cannot be farmed by walking back',state(p)['stats']['checkpoints']==1 and state(p)['film']<51)
  fixture(p);p.evaluate('GOTHIC.scene.film=37;GOTHIC.scene.advance()');p.wait_for_function('GOTHIC.phase==="running"&&GOTHIC.scene.stageIndex===1');ck('Film carries between stages instead of resetting to 100',abs(state(p)['film']-37)<.4)
  fixture(p);p.evaluate('GOTHIC.scene.film=65');p.keyboard.press('x');p.wait_for_function('GOTHIC.scene.stats.flashes===1');ck('Flash costs 20 film',44<=state(p)['film']<=46);p.keyboard.press('x');simwait(p,100);ck('Flash cooldown prevents spamming',state(p)['stats']['flashes']==1)
  for i in range(4):
   fixture(p,i);g=p.evaluate('''(()=>{const s=GOTHIC.scene,[a,b]=s.stage.gaps[0],f=s.platforms.find(p=>p.def.ferry);return {gap:b-a,jump:2*Math.abs(GOTHIC_CONFIG.hero.jump)/GOTHIC_CONFIG.hero.gravity*GOTHIC_CONFIG.hero.speed,noFloor:!s.floorSegments.some(([l,r])=>((a+b)/2)>l&&((a+b)/2)<r),carrier:!!f.zone.body&&f.zone.body.immovable&&f.def.motion.axis==='x'};})()''')
   ck(f'Stage {i+1} has a real gap longer than a jump',g['gap']>g['jump']*2 and g['noFloor'],g);ck(f'Stage {i+1} has an actual moving carrier',g['carrier'])
  fixture(p);p.evaluate('''()=>{const s=GOTHIC.scene,f=s.platforms.find(p=>p.def.ferry);s.player.body.reset(f.zone.x,f.zone.body.top-18);s.player.setVelocity(0);}''');p.wait_for_function('GOTHIC.scene.stats.ferryBoardings===1');points=[]
  for _ in range(15):
   p.wait_for_timeout(90);points.append(p.evaluate('''(()=>{const s=GOTHIC.scene,f=s.platforms.find(p=>p.def.ferry);return [s.player.x,f.zone.x,s.player.body.bottom-f.zone.body.top]})()'''))
  offset=[a-b for a,b,d in points];ck('Moving carrier transports resting player without sliding off',max(a for a,b,d in points)-min(a for a,b,d in points)>20 and max(offset)-min(offset)<4 and all(abs(d)<4 for a,b,d in points),points)
  fixture(p);p.evaluate('GOTHIC.scene.player.body.reset(GOTHIC.scene.stage.gaps[0][0]-10,322)');p.keyboard.down('ArrowUp');p.keyboard.down('ArrowRight');p.wait_for_timeout(120);p.keyboard.up('ArrowUp');p.wait_for_function('GOTHIC.scene.stats.respawns>=1',timeout=7000);p.keyboard.up('ArrowRight');ck('Attempting to jump entire chasm falls and respawns',state(p)['stats']['respawns']==1 and state(p)['x']<G_SPAWN_LIMIT,state(p))
  for i in range(3):
   fixture(p);x=state(p)['x'];p.keyboard.down('ArrowRight');p.wait_for_function('(x)=>GOTHIC.scene.player.x>x+12',arg=x);p.keyboard.up('ArrowRight');ck('Restart cycle '+str(i+1)+' still accepts input',state(p)['x']>x+10)
  # Additional stage visual review snapshots. These are explicitly fixture captures, not playthrough evidence.
  for i in [1,2,3]:fixture(p,i);G=None;p.keyboard.press('p');p.locator('#overlay').evaluate('(e)=>e.hidden=true');p.screenshot(path=str(R/f'evidence/r5-{engine}-visual-stage-{i}.png'))
  p.close()
  for w,h in [(1280,720),(1216,1242),(844,390),(667,375),(568,320),(390,844)]:
   mobile=w<900;p=open_page(b,w,h,mobile);rect=p.locator('canvas').bounding_box();vw=p.evaluate('GOTHIC.viewWidth');ck(f'{w}x{h} screen has no stretch/crop',abs(rect['width']/rect['height']-vw/360)<.02 and rect['x']>=-1 and rect['y']>=-1 and rect['x']+rect['width']<=w+1 and rect['y']+rect['height']<=h+1,rect)
   if mobile and w>h:
    ck(f'{w}x{h} adaptive width uses screen height',rect['height']>h*.95,rect);p.locator('#start').tap();p.wait_for_function('GOTHIC.phase==="running"');p.locator('[data-input="beam"]').tap();p.wait_for_function('GOTHIC.scene.beaming');ck(f'{w}x{h} tap-to-film stays on after release',p.evaluate('GOTHIC.inputs.beam'));p.locator('[data-input="beam"]').tap();p.wait_for_function('!GOTHIC.inputs.beam');ck(f'{w}x{h} second tap switches camera off',True)
    pad=p.locator('#move-pad').bounding_box();x=state(p)['x'];p.mouse.move(pad['x']+pad['width']*.84,pad['y']+pad['height']*.45);p.mouse.down();p.wait_for_function('(x)=>GOTHIC.scene.player.x>x+14',arg=x);p.mouse.up();ck(f'{w}x{h} thumb pad moves and releases',state(p)['x']>x+12 and not p.evaluate('GOTHIC.inputs.right'))
    p.locator('[data-input="jump"]').tap();p.wait_for_function('GOTHIC.scene.player.body.bottom<285');ck(f'{w}x{h} right-hand jump button works',True)
    p.set_viewport_size({'width':390,'height':844});p.wait_for_function('GOTHIC.phase==="paused"');ck(f'{w}x{h} rotation clears all touch inputs',p.evaluate('Object.values(GOTHIC.inputs).every(x=>!x)'));p.set_viewport_size({'width':w,'height':h});p.wait_for_function('GOTHIC.phase==="running"')
   if mobile and h>w:ck('Portrait starts paused with rotate guidance',p.locator('#start').is_hidden())
   p.screenshot(path=str(R/f'evidence/r5-{engine}-layout-{w}x{h}.png'));p.close()
  p=open_page(b,844,390,True);p.locator('#control-mode').select_option('arrows',force=True);p.locator('#film-mode').select_option('hold',force=True);p.locator('#control-size').select_option('1.2',force=True);ck('Alternate arrow/hold/large controls available',p.evaluate('GOTHIC.preferences.movement==="arrows"&&GOTHIC.preferences.film==="hold"&&GOTHIC.preferences.size==="1.2"'));p.locator('#start').tap();box=p.locator('[data-input="beam"]').bounding_box();p.mouse.move(box['x']+box['width']/2,box['y']+box['height']/2);p.mouse.down();p.wait_for_function('GOTHIC.scene.beaming');p.mouse.up();p.wait_for_function('!GOTHIC.inputs.beam');ck('Hold-to-film alternative releases reliably',True);p.close()
  p=open_page(b,844,390,True,'Element.prototype.requestFullscreen=undefined;Element.prototype.webkitRequestFullscreen=undefined;');p.locator('#fullscreen').click();ck('Unsupported fullscreen offers explicit app instructions instead of silently failing',p.locator('#display-help').is_visible() and 'Home Screen' in p.locator('#display-copy').inner_text());p.locator('#close-display').click();ck('Fullscreen help can be dismissed',p.locator('#display-help').is_hidden());p.close()
  manifest=json.loads((R/'releases/gothic-r5/manifest.webmanifest').read_text());ck('Installable app has standalone, landscape and release-scoped start URL',manifest['display']=='standalone'and manifest['orientation']=='landscape'and manifest['scope']=='./')
  ck('Apple standalone metadata and all three icons are packaged',all((R/f'releases/gothic-r5/icon-{n}.png').exists()for n in[180,192,512])and'"apple-mobile-web-app-capable" content="yes"'in(R/'index.template.html').read_text())
  ck('Offline worker is confined to this release scope',"request.url.startsWith(BASE)"in(R/'releases/gothic-r5/sw.js').read_text());ck('No uncaught acceptance exceptions',not errors,errors);b.close()
except Exception as e:
 traceback.print_exc();checks.append({'name':'fatal','passed':False,'detail':str(e)})
finally:
 result={'engine':engine,'suite':'isolated mechanics and presentation','build':json.loads((R/'releases/gothic-r5/build.json').read_text()),'passed':sum(c['passed']for c in checks),'failed':sum(not c['passed']for c in checks),'errors':errors,'checks':checks};(R/f'evidence/r5-{engine}-acceptance.json').write_text(json.dumps(result,indent=2));print('RESULT',result['passed'],result['failed'],flush=True)
 if result['failed']:raise SystemExit(1)
