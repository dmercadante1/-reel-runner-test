"""Fix source coordinate scaling only, then publish under new immutable paths.
The archive contains a 1099x733 preview of a board whose crop coordinates were
specified on the 1536x1024 original. Image decoding alone could not detect this.
"""
from pathlib import Path
from PIL import Image
import json,hashlib
root=Path('game/rebuild-r34');source=root/'sources/wide_cinematic_concept_art_game_design_board_in_a.png'
with Image.open(source) as im:
    im.load();size=im.size
assert size in [(1099,733),(1536,1024)],('Unknown source-board coordinates; review required',size)
p=root/'tools/prepare_r34.py';s=p.read_text();old="parts=source('wide_cinematic_concept_art_game_design_board_in_a.png')"
new=old+"\n# Canonical crop coordinates are for the 1536x1024 original, not the archived preview.\noriginal_parts_size=parts.size\nassert original_parts_size in [(1099,733),(1536,1024)], 'Unrecognized source board size'\nif parts.size!=(1536,1024):parts=parts.resize((1536,1024),Image.Resampling.NEAREST)\nassert board.size==(1536,1024) and parts.size==(1536,1024)"
if 'original_parts_size=parts.size' not in s:
    assert s.count(old)==1;s=s.replace(old,new);p.write_text(s)
(root/'evidence/art-coordinate-review.json').write_text(json.dumps({'source':str(source),'sourceSHA256':hashlib.sha256(source.read_bytes()).hexdigest(),'actualDimensions':size,'cropCoordinateDimensions':[1536,1024],'correction':'Normalize the intact source-board preview before extracting raster crops; no gameplay or physics changes','oldReleasePreserved':True,'newReleasePaths':['game/releases/gothic-r3a/','game/releases/gothic-r4a/']},indent=2))
# Prepare root changes only on the review branch. Older release bytes stay untouched.
for path in ['index.html','game/play.html']:
    p=Path(path);s=p.read_text();assert 'gothic-r4/' in s;p.write_text(s.replace('gothic-r4/','gothic-r4a/'))
p=Path('audit/check-live-r34.py');s=p.read_text();s=s.replace('gothic-r{edition}/','gothic-r{edition}a/').replace('gothic-r3/','gothic-r3a/');p.write_text(s)
p=Path('.github/workflows/gothic-live-check.yml');s=p.read_text().replace('game/releases/gothic-r3/**','game/releases/gothic-r3a/**').replace('game/releases/gothic-r4/**','game/releases/gothic-r4a/**');p.write_text(s)
print('Canonical source coordinates fixed. Prior immutable R2/R3/R4 game files have not been modified.')
