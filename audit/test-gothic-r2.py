"""Run the actual imported game through HTTP, in independent browser engines."""
import functools, hashlib, http.server, json, os, pathlib, re, subprocess, sys, threading
from playwright.sync_api import sync_playwright
ROOT=pathlib.Path.cwd();R=ROOT/'game/rebuild-r2';E=R/'evidence';E.mkdir(exist_ok=True)
H=(R/'Gothic-Horror-Playable.html').read_text()
assert hashlib.sha256(H.encode()).hexdigest()=='99676e652482b652eadfcb87bf7411ebbfe11bcefffa87b7aa60fdfc98962839'
# Parse every inline script with Node before browser execution.
for i,code in enumerate(re.findall(r'<script[^>]*>(.*?)</script>',H,re.S)):
 p=pathlib.Path('/tmp/gothic-script-'+str(i)+'.js');p.write_text(code);subprocess.run(['node','--check',str(p)],check=True,stdout=subprocess.DEVNULL)
handler=functools.partial(http.server.SimpleHTTPRequestHandler,directory=str(ROOT))
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),handler);threading.Thread(target=server.serve_forever,daemon=True).start()
URL='http://127.0.0.1:'+str(server.server_port)+'/'
engine=os.environ.get('BROWSER','chromium');assert engine in ('chromium','webkit')
launch="b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])"
replacement="b=getattr(pw,'"+engine+"').launch(headless=True)"
source=(R/'tests/acceptance.py').read_text();assert launch in source;source=source.replace(launch,replacement)
old="p.set_content(H.replace('type:Phaser.AUTO','type:Phaser.CANVAS')if canvas else H,wait_until='load')"
new="p.route('**/game/releases/gothic-hud-r2/',lambda route:route.fulfill(body=H.replace('type:Phaser.AUTO','type:Phaser.CANVAS'),content_type='text/html')) if canvas else None;p.goto('"+URL+"',wait_until='load')"
assert old in source;source=source.replace(old,new)
if engine=='webkit':
 # CDP is Chromium-only. WebKit phone layout and real taps are tested separately below.
 start=source.index('  c,p=load(b,mobile=True)');end=source.index('  c=b.new_context();p=c.new_page();a=json.loads',start)
 source=source[:start]+source[end:]
source=source.replace("'scope':'Chromium real renders, WebGL default/Canvas; mobile emulation with CDP multitouch. NOT Safari or physical phone.'","'scope':'"+engine+" hosted exact R2 bytes; physical devices not tested'")
script=R/'tests/acceptance_hosted.py';script.write_text(source)
run=subprocess.run([sys.executable,str(script)],timeout=360)
report=json.loads((E/'acceptance-results.json').read_text());(E/(engine+'-acceptance.json')).write_text(json.dumps(report,indent=2))
assert run.returncode==0 and report['fatal'] is None and report['failed']==0,report
assert report['passed']>30,report
# Repeat original HUD checks with the real HTTP document, not a synthetic DOM.
source=(R/'tests/hud.py').read_text();assert launch in source;source=source.replace(launch,replacement).replace('p.set_content(H)',"p.goto('"+URL+"',wait_until='load')")
script=R/'tests/hud_hosted.py';script.write_text(source);subprocess.run([sys.executable,str(script)],timeout=150,check=True)
hud=json.loads((E/'r2-hud-checks.json').read_text());(E/(engine+'-hud.json')).write_text(json.dumps(hud,indent=2));assert all(x['passed'] for x in hud['checks']) and not hud['errors']
# More than just reset counts: play after every restart; do not change game values.
extra=[];errors=[]
with sync_playwright() as pw:
 b=getattr(pw,engine).launch(headless=True);ctx=b.new_context(viewport={'width':1280,'height':816});p=ctx.new_page();p.on('pageerror',lambda e:errors.append(str(e)));p.goto(URL);p.wait_for_function('GOTHIC.phase==="ready"')
 for cycle in range(4):
  p.locator('#start').click();p.wait_for_function('GOTHIC.phase==="running"');p.wait_for_timeout(350);x=p.evaluate('GOTHIC.scene.player.x');p.keyboard.down('ArrowRight');p.wait_for_timeout(350);p.keyboard.up('ArrowRight');assert p.evaluate('GOTHIC.scene.player.x')>x+25
  p.keyboard.down('ArrowUp');p.wait_for_timeout(140);assert p.evaluate('GOTHIC.scene.player.body.velocity.y')<0;p.keyboard.up('ArrowUp');p.keyboard.press('r');p.wait_for_function('GOTHIC.phase==="ready"');assert p.evaluate('GOTHIC.scene.captured===0&&GOTHIC.scene.health===5')
  extra.append({'name':'Replay '+str(cycle+1)+' moves and jumps','passed':True})
 assert not errors,errors;p.screenshot(path=str(E/(engine+'-replay.png')));ctx.close()
 # A real tap goes through the browser's pointer system, not injected game state.
 ctx=b.new_context(viewport={'width':844,'height':390},is_mobile=True,has_touch=True,device_scale_factor=2);p=ctx.new_page();p.on('pageerror',lambda e:errors.append(str(e)));p.goto(URL);p.wait_for_function('GOTHIC.phase==="ready"');p.locator('#start').tap();p.wait_for_function('GOTHIC.phase==="running"');p.wait_for_timeout(400);p.locator('#pause').tap();p.wait_for_function('GOTHIC.phase==="paused"');p.locator('#pause').tap();p.wait_for_function('GOTHIC.phase==="running"');extra.append({'name':'Phone emulation real Start/Pause/Resume taps','passed':True});p.screenshot(path=str(E/(engine+'-phone.png')));ctx.close();b.close()
assert not errors,errors
summary={'engine':engine,'htmlSHA256':hashlib.sha256(H.encode()).hexdigest(),'httpRoot':URL,'acceptancePassed':report['passed'],'hudPassed':len(hud['checks']),'extraChecks':extra,'uncaughtErrors':errors,'physicalDeviceTested':False,'success':True}
(E/(engine+'-release.json')).write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2));server.shutdown()
