"""Small animation-state correction. Does not change physics, combat, images or input."""
from pathlib import Path
p=Path('game/rebuild-r34/src/scene.js');s=p.read_text()
old="!grounded?'jump':beam?'brace':Math.abs(p.body.velocity.x)>8?'walk':'brace'"
new="!grounded?'jump':Math.abs(p.body.velocity.x)>8?'walk':'brace'"
if old in s:
    assert s.count(old)==1;s=s.replace(old,new);p.write_text(s)
else:assert s.count(new)==1,'Unexpected state selector; manual review required'
print('Moving legs use stride even while filming. Standing still braces; hurt, jumping and capture recoil still override.')
