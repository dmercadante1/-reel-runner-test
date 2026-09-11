"""Export the authorized private-art chapter and prepare its compatibility shell.
Usage: python3 godot/tools/export_chapter.py /path/to/Godot [output-directory]
Run from repository root; private-character source assets must already be present.
"""
from pathlib import Path
import subprocess,sys,hashlib,json,shutil
engine=sys.argv[1]
out=Path(sys.argv[2] if len(sys.argv)>2 else 'build/chapter').resolve()
out.mkdir(parents=True,exist_ok=True)
assert Path('godot/assets/private-character/model.png').exists(), 'Authorized private character source is required'
subprocess.run([engine,'--headless','--path','godot','--export-release','Gothic Chapter',str(out/'index.html')],check=True)
p=out/'index.js';s=p.read_text();old='context.defaultFboForbidBlitFramebuffer=false;'
assert s.count(old)==1,'Pinned web template changed; inspect before export'
p.write_text(s.replace(old,'context.defaultFboForbidBlitFramebuffer=true;'))
manifest=json.loads(Path('godot/web/room.webmanifest').read_text());manifest['name']='Man With A Movie Camera — Gothic Horror';manifest['short_name']='Movie Camera'
(out/'room.webmanifest').write_text(json.dumps(manifest,indent=2))
files={p.name:{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in out.iterdir() if p.is_file() and p.name!='manifest.json'}
(out/'manifest.json').write_text(json.dumps({'build':'gothic-chapter-01','engine':'4.7.2.stable','render':[1920,1080],'world':[640,360],'files':files},indent=2))
print('Prepared chapter:',out)
