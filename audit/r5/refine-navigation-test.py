"""Replace overshooting host-timed waypoint steering in the automation only."""
from pathlib import Path
p=Path('game/rebuild-r5/tests/r5_playthrough.py');s=p.read_text()
if 'from navigation_probe import walk_to, jump_to' not in s:
    assert 'import json,time,os,traceback' in s
    s=s.replace('import json,time,os,traceback','import json,time,os,traceback\nfrom navigation_probe import walk_to, jump_to')
    a=s.index('def walk(');b=s.index('def ferry_cross():')
    s=s[:a]+'def walk(x,limit=15):return walk_to(p,keys,info,x,limit)\ndef jump(x):return jump_to(p,keys,info,x)\n'+s[b:]
    p.write_text(s)
print('Waypoint test agent now observes braking and arrival per frame. Five-pixel tolerance, all 30 encounters, all four moving-platform crossings, and game bytes are unchanged.')
