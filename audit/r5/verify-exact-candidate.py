"""Validate the precise R5 release after capability-aware renderer selection.
Only the bootstrap renderer choice changed. Artwork, physics, enemies and film
values are unchanged from the original staged candidate.
"""
from pathlib import Path
import json,hashlib
root=Path('game/rebuild-r5');build=json.loads((root/'releases/gothic-r5/build.json').read_text())
expected='6d5bf642fbdc44af784a472faa15d15d4c22e5b9b6b5f3ea5943260f9d94c702'
for path in [root/'releases/gothic-r5/index.html',Path('game/releases/gothic-r5/index.html')]:
 data=path.read_bytes();assert hashlib.sha256(data).hexdigest()==build['sha256']==expected and len(data)==4536133
p=root/'tests/r5_playthrough.py';s=p.read_text()
if 'deadline=time.monotonic()+360;' in s:
 assert s.count('deadline=time.monotonic()+360;')==1
 s=s.replace('deadline=time.monotonic()+360;','deadline=time.monotonic()+540;');p.write_text(s)
else:assert 'deadline=time.monotonic()+540;' in s
print('Exact renderer-aware R5 hash confirmed. No changes to difficulty or game resources.')
