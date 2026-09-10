"""Real-keyboard collision fixtures, separate from the full level playthrough.
At 152 px/s, the wave overlaps the player about 690-1020 ms after creation.
The jump clears the wave height about 68-773 ms after takeoff. Thus a 200-ms
jump can correctly be hit while landing; successful probes use 300-420 ms.
The existing grounded control must still take damage. No runtime changes.
"""
def check_shockwave_dodge(page, fixture, check, snapshot):
    trials=[]
    for delay in (300,360,420):
        fixture(page)
        born=page.evaluate('''()=>{
            const s=GOTHIC.scene,e=s.enemies[0];
            e.body.reset(260,322);e.setData({stunUntil:1e9,nextAttack:1e9});
            window.__probeWave=GOTHIC_COMBAT.shoot(s,e,'wave',-1);
            return s.clock;
        }''')
        page.wait_for_function('(t)=>GOTHIC.scene.clock>=t',arg=born+delay,timeout=4000)
        page.keyboard.down('ArrowUp')
        try:
            page.wait_for_function('GOTHIC.scene.player.body.bottom<285',timeout=2000)
        finally:
            page.keyboard.up('ArrowUp')
        page.wait_for_function('!window.__probeWave.active||window.__probeWave.x<GOTHIC.scene.player.body.left-25',timeout=4000)
        airborne=snapshot(page)
        page.wait_for_function('GOTHIC.scene.player.body.blocked.down||GOTHIC.scene.player.body.touching.down',timeout=4000)
        landed=snapshot(page)
        details={'jumpDelaySimulationMs':delay,'afterProjectilePassed':airborne,'afterLanding':landed}
        trials.append(details)
        check('Jump evades ground shockwave at '+str(delay)+' ms',
              landed['health']==5 and landed['stats']['damage']==0 and landed['stats']['dodged']>=1 and landed['stats']['attacks']==0,
              details)
    check('Shockwave dodge works across three reaction timings',len(trials)==3,trials)
