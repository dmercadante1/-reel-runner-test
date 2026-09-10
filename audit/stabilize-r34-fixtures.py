"""Repair isolation of physics fixtures, not the game or its difficulty.
A fixture must wait for a new scene's stats/body before altering test enemies.
Dodge assertions must inspect the isolated projectile during simulation time.
Full keyboard playthroughs remain separate and unchanged.
"""
from pathlib import Path
p=Path('game/rebuild-r34/tests/mechanics.py');s=p.read_text()
old=''' p.evaluate('(i)=>GOTHIC.scene.scene.restart({stage:i,auto:true})',i);p.wait_for_timeout(350);p.wait_for_function('GOTHIC.phase==="running"');p.evaluate('GOTHIC.scene.enemies.forEach(e=>{e.setData("stunUntil",1e9);e.setVelocity(0)})');p.wait_for_timeout(150)'''
new=''' p.evaluate('(i)=>{window.__fixtureStats=GOTHIC.scene.stats;GOTHIC.scene.scene.restart({stage:i,auto:true});}',i)
 p.wait_for_function('(i)=>GOTHIC.phase==="running"&&GOTHIC.scene.stageIndex===i&&GOTHIC.scene.stats!==window.__fixtureStats&&GOTHIC.scene.player?.body?.enable',arg=i)
 p.evaluate('GOTHIC.scene.enemies.forEach(e=>{e.setData("stunUntil",1e9);e.setVelocity(0)})')
 p.wait_for_function('GOTHIC.scene.tick>=2&&(GOTHIC.scene.player.body.blocked.down||GOTHIC.scene.player.body.touching.down)')
 assert p.evaluate('GOTHIC.scene.stats.damage===0&&GOTHIC.scene.stats.attacks===0&&GOTHIC.scene.enemies.every(e=>e.getData("stunUntil")>GOTHIC.scene.clock)'), 'Fixture is not isolated from previous scene/AI' '''
if old in s:
 assert s.count(old)==1;s=s.replace(old,new)
else:assert 'window.__fixtureStats' in s
lines=s.splitlines();indices=[i for i,l in enumerate(lines) if "ck('Jump evades ground shockwave'" in l]
assert len(indices)==1
if 'check_shockwave_dodge' not in s:
 lines[indices[0]]='  check_shockwave_dodge(p,fixture,ck,snapshot)'
 s='\n'.join(lines)+'\n';s=s.replace('from platform_probe import check_platform_carry','from platform_probe import check_platform_carry\nfrom shockwave_probe import check_shockwave_dodge')
p.write_text(s)
print('Isolated fresh-scene fixtures and bounded shockwave simulation checks installed. Game runtime and full traversal tests untouched.')
