"""Test-harness fixes only. No runtime, asset, health, position or attack changes."""
from pathlib import Path

def replace_once(path,old,new):
    p=Path(path);s=p.read_text()
    if new in s:return
    assert s.count(old)==1,(str(p),'unexpected source; refusing patch')
    p.write_text(s.replace(old,new))

# WebKit screenshots are RGBA, Chromium screenshots RGB. Difference alpha is zero
# for two opaque screenshots; Pillow getbbox(alpha_only=True) otherwise ignores
# real RGB pixel differences. Compare the same color channels in both engines.
replace_once('game/rebuild-r34/tests/playthrough.py',
    'ImageChops.difference(Image.open(BytesIO(before)),Image.open(BytesIO(after))).getbbox()',
    "ImageChops.difference(Image.open(BytesIO(before)).convert('RGB'),Image.open(BytesIO(after)).convert('RGB')).getbbox()")

# Scene.restart is queued. Running/x<120 can still describe the OLD scene before
# the restart processes. Observe replacement of the stats object without changing
# it, then send input only after the new scene has actually initialized.
replace_once('audit/check-live-r34.py',
    '''page.keyboard.press('r');page.wait_for_function('GOTHIC.phase==="running" && GOTHIC.scene.player.x<120')''',
    '''page.evaluate('window.__previousRunStats=GOTHIC.scene.stats');page.keyboard.press('r');page.wait_for_function('GOTHIC.phase==="running" && GOTHIC.scene.stats!==window.__previousRunStats && GOTHIC.scene.player.x<120')''')
print('RGB-comparable visibility test and post-restart synchronization applied. Game bytes unchanged.')
