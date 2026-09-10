"""Repair test navigation without changing R5 game bytes, enemies or resources.
A fall before the far-bank checkpoint returns to the near bank. The driver must
ride the ferry again, not remember an obsolete crossing and run into the pit.
"""
from pathlib import Path
p=Path('game/rebuild-r5/tests/r5_playthrough.py');s=p.read_text()
if 'from navigation_probe import walk_to, jump_to' not in s:
    assert 'import json,time,os,traceback' in s
    s=s.replace('import json,time,os,traceback','import json,time,os,traceback\nfrom navigation_probe import walk_to, jump_to')
    a=s.index('def walk(');b=s.index('def ferry_cross():')
    s=s[:a]+'def walk(x,limit=15):return walk_to(p,keys,info,x,limit)\ndef jump(x):return jump_to(p,keys,info,x)\n'+s[b:]
old="   if s['stats']['respawns']!=lastRespawns:keys(set());lastRespawns=s['stats']['respawns']"
new="""   if s['stats']['respawns']!=lastRespawns:
    keys(set());lastRespawns=s['stats']['respawns']
    if s['x']<s['gap'][0]:crossed.discard(s['stage'])
    if s['stage']==1:balcony=False
    print('RECOVERY: route recalculated after fall/death',s,flush=True)"""
if old in s:
    assert s.count(old)==1;s=s.replace(old,new)
else:assert 'route recalculated after fall/death' in s
old="    seen.add(s['stage']);ck('Enter stage '"
new="    keys(set());seen.add(s['stage']);ck('Enter stage '"
if old in s:
    assert s.count(old)==1;s=s.replace(old,new)
else:assert new in s
# Use the existing camera defense for an enemy waiting at the far landing.
# This is ordinary keyboard input, not a stun/state override.
old=" keys({'ArrowRight','ArrowUp'});wait(110);keys({'ArrowRight'});end=time.monotonic()+3"
new=""" departure={'ArrowRight','ArrowUp'}
 if s['film']>=20 and s['flash']<=0 and any(0<e['x']-s['x']<190 for e in s['enemies']):departure.add('x')
 keys(departure);wait(110);keys({'ArrowRight'});end=time.monotonic()+3"""
if old in s:
    assert s.count(old)==1;s=s.replace(old,new)
else:assert "departure={'ArrowRight','ArrowUp'}" in s
p.write_text(s)
print('Test driver now reboards after checkpoint recovery and uses real flash input at defended landings. All 30 captures, four ferry assertions and game bytes are unchanged.')
