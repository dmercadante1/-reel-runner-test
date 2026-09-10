"""Actual keyboard-only, 30-encounter, four-ferry traversal. No position/health overrides."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import json,time,os,traceback
from navigation_probe import walk_to, jump_to
R=Path(__file__).resolve().parents[1];engine=os.getenv('BROWSER','chromium');checks=[];errors=[];held=set();p=None

def ck(n,v,d=None):
 checks.append({'name':n,'passed':bool(v),'detail':d});print(('PASS 'if v else'FAIL ')+n,flush=True)
 if not v:raise AssertionError((n,d))
def info():return p.evaluate('''(()=>{const s=GOTHIC.scene,f=s.platforms.find(p=>p.def.ferry);return {phase:GOTHIC.phase,stage:s.stageIndex,x:s.player.x,y:s.player.y,bottom:s.player.body.bottom,vy:s.player.body.velocity.y,ground:s.player.body.blocked.down||s.player.body.touching.down,film:s.film,hp:s.health,cap:s.captured,total:s.total,clock:s.clock,flash:s.flashUntil-s.clock,hurt:s.hurtUntil-s.clock,flip:s.player.flipX,stats:s.stats,gap:s.stage.gaps[0],exit:s.stage.exit.x,ferry:f&&{x:f.zone.x,top:f.zone.body.top,vx:f.zone.body.velocity.x,width:f.def.width},pickups:s.pickups.filter(p=>p.obj.active&&p.kind==='film').map(p=>({x:p.x,y:p.y})),enemies:s.enemies.filter(e=>e.active&&e.getData('state')!=='capturing').map(e=>({x:e.x,dy:e.body.center.y-s.player.body.center.y,state:e.getData('state'),type:e.getData('type')}))};})()''')
def keys(want):
 global held
 for k in held-want:p.keyboard.up(k)
 for k in want-held:p.keyboard.down(k)
 held=set(want)
def wait(ms=50):p.wait_for_timeout(ms)
def walk(x,limit=15):return walk_to(p,keys,info,x,limit)
def jump(x):return jump_to(p,keys,info,x)
def ferry_cross():
 s=info();left,right=s['gap'];stage=s['stage'];resp=s['stats']['respawns'];keys(set());walk(left-29);end=time.monotonic()+23
 while time.monotonic()<end:
  s=info();f=s['ferry']
  if f['x']<left+96 and f['vx']<8:break
  wait(70)
 else:raise AssertionError(('Ferry never approaches near bank',s))
 keys({'ArrowRight','ArrowUp'});wait(100);keys({'ArrowRight'});end=time.monotonic()+3
 while time.monotonic()<end:
  s=info();f=s['ferry']
  if abs(s['bottom']-f['top'])<3 and s['ground'] and s['x']>f['x']-f['width']/2-10:keys(set());break
  d=f['x']-s['x'];keys({'ArrowRight'}if d>9 else{'ArrowLeft'}if d< -9 else set());wait(30)
 else:raise AssertionError(('Did not land on ferry',s))
 ck('Stage '+str(stage+1)+' jumped aboard moving ferry',s['stats']['respawns']==resp,s)
 # Wait for actual transport, keeping player centered only through ordinary keyboard movement.
 end=time.monotonic()+24
 while time.monotonic()<end:
  s=info();f=s['ferry']
  if f['x']>right-105 and f['vx']>0:break
  keys(set());wait(60)
 else:raise AssertionError(('Ferry did not carry player to far bank',s))
 ck('Stage '+str(stage+1)+' rides over unjumpable gap',s['x']>right-145 and s['stats']['respawns']==resp,s)
 departure={'ArrowRight','ArrowUp'}
 if s['film']>=20 and s['flash']<=0 and any(0<e['x']-s['x']<190 for e in s['enemies']):departure.add('x')
 keys(departure);wait(110);keys({'ArrowRight'});end=time.monotonic()+3
 while time.monotonic()<end:
  s=info()
  if s['x']>right+30:break
  wait(30)
 keys(set());p.wait_for_function('Math.abs(GOTHIC.scene.player.body.bottom-316)<3',timeout=3500)
 ck('Stage '+str(stage+1)+' exits ferry safely',info()['x']>right and info()['stats']['respawns']==resp,info())
try:
 with sync_playwright() as pw:
  kw={'executable_path':'/usr/bin/chromium','args':['--no-sandbox']} if engine=='chromium' and not os.getenv('GITHUB_ACTIONS') else {}
  b=getattr(pw,engine).launch(**kw);p=b.new_page(viewport={'width':1280,'height':720});p.set_default_timeout(12000);p.on('pageerror',lambda e:errors.append(str(e)));p.set_content((R/'releases/gothic-r5/index.html').read_text(),wait_until='load');p.wait_for_function('GOTHIC.phase==="ready"');ck('31 validated raster textures, 30 planned encounters',p.evaluate('GOTHIC_ASSETS.length===31&&GOTHIC_CONFIG.totalEncounters===30'))
  p.locator('#start').click();seen=set();crossed=set();balcony=False;lastRespawns=0;collectedRoutes=set();deadline=time.monotonic()+540;last=time.monotonic()
  while time.monotonic()<deadline:
   s=info()
   if s['phase']=='complete':break
   if s['stats']['respawns']!=lastRespawns:
    keys(set());lastRespawns=s['stats']['respawns']
    if s['x']<s['gap'][0]:crossed.discard(s['stage'])
    if s['stage']==1:balcony=False
    print('RECOVERY: route recalculated after fall/death',s,flush=True)
   if s['phase']=='transition':keys(set());wait(350);continue
   if s['phase']!='running':raise AssertionError(s)
   if s['stage']not in seen:
    keys(set());seen.add(s['stage']);ck('Enter stage '+str(s['stage']+1),True);p.screenshot(path=str(R/f'evidence/r5-{engine}-stage-{s["stage"]}.png'))
   if time.monotonic()-last>8:print('PLAY',s,flush=True);last=time.monotonic()
   if s['stage'] not in collectedRoutes and 420<s['x']<650 and s['cap']>=1:
    keys(set())
    if s['stage']==0:walk(491);jump(550);walk(583);jump(678);walk(690);jump(805)
    elif s['stage']==1:walk(438);jump(496);walk(531);jump(633);walk(654);jump(770)
    elif s['stage']==2:walk(429);jump(490);walk(537);jump(625);walk(666);jump(782);walk(835);jump(938)
    elif s['stage']==3:walk(499);jump(558);walk(600);jump(706);walk(734);jump(870)
    collectedRoutes.add(s['stage']);ck('Stage '+str(s['stage']+1)+' optional supply platform route',True,info());continue
   if s['x']>s['gap'][0]-150 and s['stage'] not in crossed:
    # Clear enemies still on near bank before boarding.
    near=[e for e in s['enemies']if e['x']<s['gap'][0]]
    if not near:ferry_cross();crossed.add(s['stage']);continue
   if s['stage']==1 and not s['enemies'] and not balcony:
    keys(set());walk(2369);jump(2450);ck('Cathedral stair landing',abs(info()['bottom']-270)<4,info());walk(2488);jump(2585);ck('Cathedral upper balcony landing',abs(info()['bottom']-222)<4,info());balcony=True;continue
   target=min(s['enemies'],key=lambda e:abs(e['x']-s['x'])) if s['enemies'] else None
   if target and abs(target['x']-s['x'])<275:
    direction='ArrowLeft'if target['x']<s['x'] else'ArrowRight';desired={'Space'}
    if abs(target['x']-s['x'])>150 or s['flip']!=(target['x']<s['x']):desired.add(direction)
    if abs(target['x']-s['x'])<192 and target['state']in['windup','attack']and s['flash']<=0 and s['film']>=20:desired.add('x')
    if abs(target['dy'])>73:desired={'ArrowRight'}
    if s['film']<3:
     supplies=[q for q in s['pickups']if q['y']>270 and (q['x']<s['gap'][0])==(s['x']<s['gap'][0])]
     if supplies:
      supply=min(supplies,key=lambda q:abs(q['x']-s['x']));desired={'ArrowRight'if supply['x']>s['x']else'ArrowLeft'}
   else:desired={'ArrowRight'}
   keys(desired);wait(80)
  keys(set());s=info();ck('Complete four-stage keyboard traversal',s['phase']=='complete',s);ck('All thirty encounters captured',s['total']==30);ck('Every stage required a ferry crossing',len(crossed)==4 and s['stats']['ferryBoardings']>=4,s['stats']);ck('No uncaught browser errors',not errors,errors);p.screenshot(path=str(R/f'evidence/r5-{engine}-complete.png'));b.close()
except Exception as e:
 traceback.print_exc();checks.append({'name':'fatal','passed':False,'detail':str(e)})
finally:
 result={'engine':engine,'build':json.loads((R/'releases/gothic-r5/build.json').read_text()),'suite':'keyboard-only playthrough','passed':sum(c['passed'] for c in checks),'failed':sum(not c['passed'] for c in checks),'checks':checks,'errors':errors};(R/f'evidence/r5-{engine}-playthrough.json').write_text(json.dumps(result,indent=2));print('RESULT',result['passed'],result['failed'],flush=True)
 if result['failed']:raise SystemExit(1)
