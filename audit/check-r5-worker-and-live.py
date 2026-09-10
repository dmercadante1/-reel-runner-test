"""Do not test a stale worker while Pages is still deploying a worker-only update."""
from pathlib import Path
import hashlib,runpy,time,urllib.request
base='https://dmercadante1.github.io/-reel-runner-test/game/releases/gothic-r5/'
expected=Path('game/releases/gothic-r5/sw.js').read_bytes()
last='not fetched'
for _ in range(75):
 try:
  req=urllib.request.Request(base+'sw.js?verify='+str(time.time_ns()),headers={'Cache-Control':'no-cache'})
  with urllib.request.urlopen(req,timeout=15) as response:actual=response.read()
  last=hashlib.sha256(actual).hexdigest()
  if actual==expected:break
 except Exception as error:last=type(error).__name__
 time.sleep(2)
else:raise AssertionError(('Pages worker did not match this release',last))
print('Verified exact served service worker SHA-256',last,flush=True)
runpy.run_path('audit/check-live-r5.py',run_name='__main__')
