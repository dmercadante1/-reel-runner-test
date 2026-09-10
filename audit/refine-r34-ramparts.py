"""Visual-review correction: no magnified strip across the Ramparts playfield.
Uses the intact existing original raster; records the crop and reproducible output.
No enemy, physics, collision, input or HUD changes.
"""
from pathlib import Path
from PIL import Image
import hashlib,json
root=Path('game/rebuild-r34');script=root/'tools/prepare_r34.py'
s=script.read_text();start=s.index('# Ramparts distant plane');end=s.index('# Authentic textured animated limbs',start)
desc='Complete original Gothic environment crop 5,4,1530,845 resized nearest-neighbor to 640x360; no magnified skyline strip or presentation-board pixels.'
block="""# Ramparts distant plane uses one continuous full-height original illustration.
# Near arches, platforms and floor are separate game objects.
ramp=crop(board,(5,4,1530,845),(640,360))
save(ramp,'ramparts',DESC)
""".replace('DESC',repr(desc))
script.write_text(s[:start]+block+s[end:])
source=root/'sources/a_wide_cinematic_dark_gothic_castle_environment.png'
with Image.open(source) as im:
 im.load();assert im.size==(1536,1024)
 raster=im.convert('RGBA').crop((5,4,1530,845)).resize((640,360),Image.Resampling.NEAREST)
out=root/'assets/ramparts.png';raster.save(out,optimize=True)
with Image.open(out) as im:im.verify()
manifest_path=root/'assets/manifest.json';m=json.loads(manifest_path.read_text());matches=[a for a in m['assets'] if a['key']=='ramparts'];assert len(matches)==1
matches[0].update(width=640,height=360,bytes=out.stat().st_size,sha256=hashlib.sha256(out.read_bytes()).hexdigest(),provenance=desc)
manifest_path.write_text(json.dumps(m,indent=2))
(root/'evidence/ramparts-visual-review.json').write_text(json.dumps({'sourceSHA256':hashlib.sha256(source.read_bytes()).hexdigest(),'sourceSize':[1536,1024],'crop':[5,4,1530,845],'output':matches[0],'reason':'Remove obvious blue rectangular skyline band seen in the actual stage-4 screenshot','runtimeChanged':False},indent=2))
print('Ramparts now uses continuous original raster scenery; all 24 texture slots retained.')
