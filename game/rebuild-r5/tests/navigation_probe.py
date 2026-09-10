"""Keyboard-only waypoint steering with braking and frame-observed arrival.
A fixed 35-ms host polling loop can miss a five-pixel waypoint on a busy CI
renderer, reverse at full speed, and oscillate until timeout. This observer waits
inside requestAnimationFrame and accounts for the game's real stopping distance.
It never writes player position, velocity, health, film, or enemy state.
"""
import time

def _sample(page):
    return page.evaluate('''(()=>{const s=GOTHIC.scene,p=s.player;return {phase:GOTHIC.phase,stage:s.stageIndex,x:p.x,bottom:p.body.bottom,vx:p.body.velocity.x,vy:p.body.velocity.y,clock:s.clock,tick:s.tick,fps:GOTHIC.game.loop.actualFps,left:s.cursors.left.isDown,right:s.cursors.right.isDown,ground:p.body.blocked.down||p.body.touching.down,respawns:s.stats.respawns}})()''')

def walk_to(page, keys, info, target, limit=15):
    end=time.monotonic()+limit;trace=[]
    while time.monotonic()<end:
        s=_sample(page);trace.append(s)
        if abs(s['x']-target)<5 and abs(s['vx'])<4:
            keys(set());return
        direction=1 if s['x']<target else -1
        predicted=s['x']+s['vx']*abs(s['vx'])/(2*1600)
        if abs(predicted-target)<5 or abs(s['x']-target)<5:
            keys(set())
        else:
            keys({'ArrowRight' if direction>0 else 'ArrowLeft'})
            page.wait_for_function('''a=>{const p=GOTHIC.scene.player;const v=p.body.velocity.x;const stop=v*v/(2*GOTHIC_CONFIG.hero.drag);return GOTHIC.phase!=='running'||a.direction*(p.x-a.target)>=-Math.max(3,stop+Math.abs(v)*.035)}''',arg={'direction':direction,'target':target},timeout=max(1000,int((end-time.monotonic())*1000)))
            keys(set())
        page.wait_for_function("GOTHIC.phase!=='running'||Math.abs(GOTHIC.scene.player.body.velocity.x)<3",timeout=2500)
        if info()['phase']!='running':raise AssertionError(('Navigation interrupted',target,trace))
    raise AssertionError(('Waypoint steering timeout',target,trace))

def jump_to(page, keys, info, target):
    start=_sample(page);direction='ArrowRight' if start['x']<target else 'ArrowLeft'
    keys({'ArrowUp',direction})
    page.wait_for_function('GOTHIC.scene.player.body.velocity.y<-40',timeout=2500)
    keys({direction})
    walk_to(page,keys,info,target,limit=7)
    page.wait_for_function('GOTHIC.scene.player.body.blocked.down||GOTHIC.scene.player.body.touching.down',timeout=4000)
    if info()['stats']['respawns']!=start['respawns']:raise AssertionError(('Jump waypoint caused a fall',target,info()))
