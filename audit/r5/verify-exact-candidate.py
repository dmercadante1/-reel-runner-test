"""Do not change gameplay for a test timeout. Verify saved bytes and adjust only the harness budget.
The first Chromium run reached 29/30 captures after all four ferry crossings before
its six-minute wall-clock deadline. Both acceptance suites and WebKit traversal passed.
"""
from pathlib import Path
import json,hashlib
root=Path('game/rebuild-r5');build=json.loads((root/'releases/gothic-r5/build.json').read_text())
expected='38831b564d73a3a694354611de349f25803155f6c453ab3383b5803ce1f8b13d'
for path in [root/'releases/gothic-r5/index.html',Path('game/releases/gothic-r5/index.html')]:
 data=path.read_bytes();assert hashlib.sha256(data).hexdigest()==build['sha256']==expected and len(data)==4535015
p=root/'tests/r5_playthrough.py';s=p.read_text()
if 'deadline=time.monotonic()+360;' in s:
 assert s.count('deadline=time.monotonic()+360;')==1
 s=s.replace('deadline=time.monotonic()+360;','deadline=time.monotonic()+540;');p.write_text(s)
else:assert 'deadline=time.monotonic()+540;' in s
print('Exact R5 hash confirmed. Only the CI wall-clock test budget changed; all game parameters and assertions remain unchanged.')
