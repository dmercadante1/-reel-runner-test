from pathlib import Path
import hashlib,json
root=Path('build/godot-m1');report={}
for p in sorted(root.iterdir()):
 if p.is_file() and p.name!='manifest.json':report[p.name]={'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
(root/'manifest.json').write_text(json.dumps({'files':report,'engine':'4.7.2.stable','internal_resolution':[640,360],'production_art':False},indent=2))
