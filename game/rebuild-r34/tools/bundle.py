"""Byte-exact immutable release bundle. Verifies all raster assets fully, and JS syntax."""
from pathlib import Path
from PIL import Image
import sys,json,base64,hashlib,subprocess
R=Path(__file__).resolve().parents[1];edition=int(sys.argv[1])if len(sys.argv)>1 else 3
m=json.loads((R/'assets/manifest.json').read_text());assets=[]
for a in m['assets']:
 p=R/a['file'];data=p.read_bytes();assert len(data)==a['bytes'];assert hashlib.sha256(data).hexdigest()==a['sha256']
 with Image.open(p) as im:im.verify()
 with Image.open(p) as im:im.load();assert im.size==(a['width'],a['height'])
 if a.get('frames'):assert a['frames']*a['frameWidth']==a['width'] and a['frameHeight']==a['height']
 assets.append(dict(a,data='data:image/png;base64,'+base64.b64encode(data).decode()))
(R/'src/assets.js').write_text('window.GOTHIC_ASSETS='+json.dumps(assets,separators=(',',':'))+';')
order=['src/shell.js','vendor/phaser-3.90.0.min.js','src/config.js','src/assets.js','src/audio.js','src/hud.js','src/world.js']
if edition>=4:order.append('src/combat.js')
order+=['src/scene.js','src/boot.js'];scripts=[]
for f in order:
 subprocess.run(['node','--check',str(R/f)],check=True,capture_output=True)
 text=(R/f).read_text()
 if f=='src/config.js':text=text.replace("build:'gothic-stages-r3',edition:3",f"build:'gothic-{'combat'if edition>=4 else'stages'}-r{edition}',edition:{edition}")
 scripts.append('<script>\n'+text.replace('</script','<\\/script')+'\n</script>')
html=(R/'index.template.html').read_text().replace('/*STYLE*/',(R/'style.css').read_text()).replace('<!--SCRIPTS-->','\n'.join(scripts));out=R/'releases'/('gothic-r'+str(edition));out.mkdir(exist_ok=True);(out/'index.html').write_text(html)
info={'edition':edition,'sha256':hashlib.sha256(html.encode()).hexdigest(),'bytes':len(html.encode()),'assets':len(assets),'sourceHashes':{f:hashlib.sha256((R/f).read_bytes()).hexdigest()for f in order}};(out/'build.json').write_text(json.dumps(info,indent=2));print(json.dumps(info,indent=2))
