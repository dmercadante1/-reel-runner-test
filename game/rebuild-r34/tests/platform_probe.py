"""Follow a moving platform over time; net displacement near its turning point is not a carry test."""
def check_platform_carry(page, check):
    page.evaluate('''()=>{const s=GOTHIC.scene,a=s.platforms.find(p=>p.def.motion);s.player.body.reset(a.zone.x,a.zone.body.top-18);s.player.setVelocity(0);}''')
    page.wait_for_timeout(500)
    samples=[]
    for _ in range(32):
        page.wait_for_timeout(100)
        samples.append(page.evaluate('''()=>{const s=GOTHIC.scene,a=s.platforms.find(p=>p.def.motion);return{playerX:s.player.x,platformX:a.zone.x,bottom:s.player.body.bottom,top:a.zone.body.top,velocity:a.zone.body.velocity.x};}'''))
    grounded=[x for x in samples if abs(x['bottom']-x['top'])<3]
    check('Moving platform supports player',len(grounded)>=len(samples)*.9,{'groundedSamples':len(grounded),'samples':samples})
    px=[x['playerX'] for x in grounded];qx=[x['platformX'] for x in grounded];offsets=[x-y for x,y in zip(px,qx)]
    detail={'playerTravel':max(px)-min(px),'platformTravel':max(qx)-min(qx),'relativeOffsetVariation':max(offsets)-min(offsets)}
    check('Moving platform carries resting player',detail['playerTravel']>12 and detail['platformTravel']>12 and detail['relativeOffsetVariation']<4,detail)
