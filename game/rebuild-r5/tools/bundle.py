"""Validate full raster bytes and JS, produce an immutable, self-contained R5 app."""
from pathlib import Path
from PIL import Image
import json,base64,hashlib,subprocess,shutil
R=Path(__file__).resolve().parents[1];m=json.loads((R/'assets/manifest.json').read_text());assets=[]
for a in m['assets']:
 p=R/a['file'];data=p.read_bytes();assert len(data)==a['bytes'];assert hashlib.sha256(data).hexdigest()==a['sha256']
 with Image.open(p) as im:im.verify()
 with Image.open(p) as im:im.load();assert im.size==(a['width'],a['height'])
 if a.get('frames'):assert a['frames']*a['frameWidth']==a['width'] and a['frameHeight']==a['height']
 assets.append(dict(a,data='data:image/png;base64,'+base64.b64encode(data).decode()))
(R/'src/assets.js').write_text('window.GOTHIC_ASSETS='+json.dumps(assets,separators=(',',':'))+';')
order=['src/shell.js','vendor/phaser-3.90.0.min.js','src/config.js','src/assets.js','src/audio.js','src/hud.js','src/world.js','src/combat.js','src/scene.js','src/boot.js'];scripts=[]
for f in order:
 subprocess.run(['node','--check',str(R/f)],check=True,capture_output=True);scripts.append('<script>\n'+(R/f).read_text().replace('</script','<\\/script')+'\n</script>')
html=(R/'index.template.html').read_text().replace('/*STYLE*/',(R/'style.css').read_text()).replace('<!--SCRIPTS-->','\n'.join(scripts));out=R/'releases/gothic-r5';out.mkdir(parents=True,exist_ok=True);(out/'index.html').write_text(html)
info={'edition':5,'sha256':hashlib.sha256(html.encode()).hexdigest(),'bytes':len(html.encode()),'assets':len(assets),'sourceHashes':{f:hashlib.sha256((R/f).read_bytes()).hexdigest() for f in order}};(out/'build.json').write_text(json.dumps(info,indent=2))
manifest={'name':'Man With A Movie Camera — Gothic Horror','short_name':'Movie Camera','id':'./','start_url':'./','scope':'./','display':'standalone','display_override':['fullscreen','standalone'],'orientation':'landscape','background_color':'#07101b','theme_color':'#07101b','icons':[{'src':f'./icon-{n}.png','sizes':f'{n}x{n}','type':'image/png','purpose':'any'}for n in [192,512]]}
(out/'manifest.webmanifest').write_text(json.dumps(manifest,indent=2))
for n in [180,192,512]:shutil.copy2(R/f'assets/icon-{n}.png',out/f'icon-{n}.png')
(out/'sw.js').write_text("const CACHE='gothic-r5-"+info['sha256'][:12]+"';const BASE=new URL('./',self.location).href;self.addEventListener('install',e=>e.waitUntil(caches.open(CACHE).then(c=>c.addAll([BASE,BASE+'manifest.webmanifest',BASE+'icon-192.png',BASE+'icon-512.png']))));self.addEventListener('activate',e=>e.waitUntil(self.clients.claim()));self.addEventListener('fetch',e=>{if(e.request.method!=='GET'||!e.request.url.startsWith(BASE))return;e.respondWith(caches.open(CACHE).then(async c=>{try{const r=await fetch(e.request);return r;}catch(error){const saved=await c.match(e.request,{ignoreSearch:true})|| (e.request.mode==='navigate'?await c.match(BASE):null);if(saved)return saved;throw error;}}));});")
print(json.dumps(info,indent=2))
