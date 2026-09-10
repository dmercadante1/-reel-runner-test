"""Build a single, offline-playable file from exact source bytes; validate all raster assets first."""
from pathlib import Path
import json,base64,hashlib,re
ROOT=Path(__file__).resolve().parents[1]
manifest=json.loads((ROOT/'assets/manifest.json').read_text())
for a in manifest['assets']:
 data=(ROOT/a['file']).read_bytes();assert len(data)==a['bytes'];assert hashlib.sha256(data).hexdigest()==a['sha256'];a['data']='data:image/png;base64,'+base64.b64encode(data).decode()
js='window.GOTHIC_ASSETS='+json.dumps(manifest['assets'],separators=(',',':'))+';'
(ROOT/'src/assets.js').write_text(js)
order=['src/shell.js','vendor/phaser-3.90.0.min.js','src/config.js','src/assets.js','src/audio.js','src/hud.js','src/scene.js','src/boot.js']
scripts='\n'.join('<script>\n'+(ROOT/p).read_text().replace('</script','<\\/script')+'\n</script>' for p in order)
html=(ROOT/'index.template.html').read_text().replace('/*STYLE*/',(ROOT/'style.css').read_text()).replace('<!--SCRIPTS-->',scripts)
(ROOT/'Gothic-Horror-Playable.html').write_text(html)
(ROOT/'build.json').write_text(json.dumps({'build':manifest['build'],'sha256':hashlib.sha256(html.encode()).hexdigest(),'bytes':len(html.encode()),'files':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in order},'artAssets':len(manifest['assets'])},indent=2))
print('BUNDLED',len(html.encode()),'bytes')
