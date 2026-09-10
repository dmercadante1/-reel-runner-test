"""Frame-local browser keyboard navigation. Only dispatches input events.
Headless CI runs software rendering around 17fps: round trips for each steering
change can overshoot narrow waypoints by 20px. Keep navigation in the browser's
animation loop, still exercising the real keyboard handlers/physics. Acceptance
also checks arrows with Playwright's native keyboard API separately.
"""
def walk_to(page, keys, info, target, limit=15):
    keys(set())
    report=page.evaluate('''({target,limit})=>new Promise(resolve=>{
      const started=performance.now(),trace=[];let held=0,previous=started;
      const send=(name,type,code)=>window.dispatchEvent(new KeyboardEvent(type,{key:name,code:name,keyCode:code,which:code,bubbles:true,cancelable:true}));
      const steer=direction=>{if(direction===held)return;if(held)send(held>0?'ArrowRight':'ArrowLeft','keyup',held>0?39:37);held=direction;if(held)send(held>0?'ArrowRight':'ArrowLeft','keydown',held>0?39:37);};
      const finish=(ok,reason)=>{steer(0);resolve({ok,reason,target,trace});};
      const frame=()=>{const now=performance.now(),s=GOTHIC.scene,p=s.player,v=p.body.velocity.x,d=target-p.x;
        const dt=Math.min(.12,Math.max(1/60,(now-previous)/1000));previous=now;
        trace.push({x:p.x,vx:v,bottom:p.body.bottom,clock:s.clock,fps:GOTHIC.game.loop.actualFps,left:s.cursors.left.isDown,right:s.cursors.right.isDown});
        if(GOTHIC.phase!=='running'){finish(false,'Scene interrupted');return;}
        if(Math.abs(d)<5&&Math.abs(v)<4){finish(true,'Arrived');return;}
        if(now-started>limit*1000){finish(false,'Keyboard waypoint timeout');return;}
        const brake=v*v/(2*GOTHIC_CONFIG.hero.drag)+Math.abs(v)*dt;
        const stop=Math.abs(d)<4||(Math.sign(v)===Math.sign(d)&&brake>=Math.abs(d));
        steer(stop?0:Math.sign(d));requestAnimationFrame(frame);
      };requestAnimationFrame(frame);
    })''',{'target':target,'limit':limit})
    keys(set())
    if not report['ok']:raise AssertionError(report)

def jump_to(page, keys, info, target):
    start=info();direction='ArrowRight' if start['x']<target else 'ArrowLeft'
    keys({'ArrowUp',direction})
    page.wait_for_function('GOTHIC.scene.player.body.velocity.y<-40',timeout=2500)
    keys({direction});walk_to(page,keys,info,target,limit=7)
    page.wait_for_function('GOTHIC.scene.player.body.blocked.down||GOTHIC.scene.player.body.touching.down',timeout=4000)
    if info()['stats']['respawns']!=start['stats']['respawns']:raise AssertionError(('Jump caused a fall',target,info()))
