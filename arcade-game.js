(() => {
  if(!document.body.classList.contains('skin-arcade')) return;
  const footer=document.querySelector('footer');
  if(!footer) return;
  const launch=document.createElement('button');
  launch.className='arcade-game-launch';
  launch.type='button';
  launch.textContent='INSERT COIN / PLAY REEL RUNNER';
  footer.prepend(launch);
  let raf=0,game=null;
  const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
  function openGame(){
    const overlay=document.createElement('div');
    overlay.className='arcade-game-overlay';
    overlay.innerHTML=`<div class="arcade-game-cabinet">
      <div class="arcade-game-top"><span class="arcade-game-title">REEL RUNNER</span><span>DM ARCADE SYSTEM · 1 CREDIT</span><button class="arcade-game-close" type="button">EXIT</button></div>
      <div class="arcade-game-screen"><canvas width="640" height="480"></canvas><div class="arcade-game-start"><div class="arcade-game-start-inner"><h2>REEL RUNNER</h2><p>STEER THE CAMERA. COLLECT FILM REELS. AVOID THE RED STATIC.</p><button type="button">PRESS START</button></div></div></div>
      <div class="arcade-game-hud"><span class="game-score">SCORE 000000</span><span class="game-lives">LIVES 3</span><span class="game-hi">HI 000000</span></div>
      <div class="arcade-game-touch"><button data-dir="left">◀</button><button data-dir="boost">●</button><button data-dir="right">▶</button></div>
      <div class="arcade-game-help">← → / A D TO MOVE · SPACE TO BOOST</div>
    </div>`;
    document.body.appendChild(overlay);
    document.body.style.overflow='hidden';
    const canvas=overlay.querySelector('canvas'),ctx=canvas.getContext('2d'),start=overlay.querySelector('.arcade-game-start'),startBtn=start.querySelector('button');
    const scoreEl=overlay.querySelector('.game-score'),livesEl=overlay.querySelector('.game-lives'),hiEl=overlay.querySelector('.game-hi');
    const keys={left:false,right:false,boost:false};
    let high=Number(localStorage.getItem('dm-reel-runner-hi')||0);
    hiEl.textContent=`HI ${String(high).padStart(6,'0')}`;
    const stars=Array.from({length:85},()=>({x:Math.random()*640,y:Math.random()*480,s:Math.random()<.8?1:2,v:20+Math.random()*55}));
    function reset(){game={running:true,score:0,lives:3,time:0,spawn:0,speed:155,flash:0,player:{x:320,y:410,w:46,h:28,vx:0},items:[]};updateHud()}
    function updateHud(){scoreEl.textContent=`SCORE ${String(Math.floor(game?.score||0)).padStart(6,'0')}`;livesEl.textContent=`LIVES ${game?.lives??3}`}
    function spawn(){const reel=Math.random()>.34;game.items.push({type:reel?'reel':'hazard',x:28+Math.random()*584,y:-30,r:reel?13:15,v:game.speed*(.72+Math.random()*.45),spin:Math.random()*6.28})}
    function drawPixelCamera(p){ctx.save();ctx.translate(Math.round(p.x),Math.round(p.y));ctx.fillStyle='#176fe8';ctx.fillRect(-22,-10,34,20);ctx.fillStyle='#55b8ff';ctx.fillRect(-18,-6,22,12);ctx.fillStyle='#ffe21f';ctx.fillRect(10,-6,11,12);ctx.fillStyle='#ff4da6';ctx.fillRect(-15,-16,13,6);ctx.fillStyle='#fff';ctx.fillRect(-11,-13,5,3);ctx.restore()}
    function drawReel(it){ctx.save();ctx.translate(Math.round(it.x),Math.round(it.y));ctx.rotate(it.spin);ctx.fillStyle='#d7d7d7';ctx.fillRect(-12,-12,24,24);ctx.fillStyle='#111';ctx.fillRect(-4,-4,8,8);ctx.fillStyle='#333';[[-7,-7],[7,-7],[-7,7],[7,7]].forEach(([x,y])=>ctx.fillRect(x-2,y-2,4,4));ctx.restore()}
    function drawHazard(it){ctx.save();ctx.translate(Math.round(it.x),Math.round(it.y));ctx.fillStyle='#ff2a6d';ctx.fillRect(-14,-14,28,28);ctx.fillStyle='#111';ctx.fillRect(-8,-8,16,4);ctx.fillRect(-8,2,16,4);ctx.fillStyle='#ffe21f';ctx.fillRect(-3,-3,6,6);ctx.restore()}
    function hit(a,b){return Math.abs(a.x-b.x)<(a.w/2+b.r-2)&&Math.abs(a.y-b.y)<(a.h/2+b.r-2)}
    let last=performance.now();
    function loop(now){
      const dt=Math.min(.034,(now-last)/1000);last=now;
      stars.forEach(s=>{s.y+=s.v*dt;if(s.y>480){s.y=0;s.x=Math.random()*640}});
      if(game&&game.running){
        game.time+=dt;game.spawn-=dt;game.flash=Math.max(0,game.flash-dt);
        if(game.spawn<=0){spawn();game.spawn=Math.max(.28,.72-game.time*.008)}
        const accel=keys.boost?690:500,max=keys.boost?330:240;
        if(keys.left)game.player.vx-=accel*dt;if(keys.right)game.player.vx+=accel*dt;if(!keys.left&&!keys.right)game.player.vx*=Math.pow(.001,dt);
        game.player.vx=clamp(game.player.vx,-max,max);game.player.x=clamp(game.player.x+game.player.vx*dt,28,612);
        game.speed=155+Math.min(180,game.time*4.2)+(keys.boost?55:0);
        game.items.forEach(it=>{it.y+=it.v*dt;it.spin+=dt*4});
        for(let i=game.items.length-1;i>=0;i--){const it=game.items[i];if(hit(game.player,it)){if(it.type==='reel'){game.score+=100;game.flash=.08}else{game.lives--;game.flash=.22;game.player.vx*=-.5}game.items.splice(i,1);updateHud();if(game.lives<=0){game.running=false;high=Math.max(high,Math.floor(game.score));localStorage.setItem('dm-reel-runner-hi',high);hiEl.textContent=`HI ${String(high).padStart(6,'0')}`;start.querySelector('h2').textContent='GAME OVER';start.querySelector('p').textContent=`FINAL SCORE ${String(Math.floor(game.score)).padStart(6,'0')}`;startBtn.textContent='PLAY AGAIN';start.style.display='grid'}}else if(it.y>520){game.items.splice(i,1)}}
        game.score+=dt*(keys.boost?16:10);updateHud();
      }
      ctx.fillStyle=game?.flash>0?'#16051f':'#03050e';ctx.fillRect(0,0,640,480);
      stars.forEach((s,i)=>{ctx.fillStyle=i%9===0?'#30a8ff':'#d9e8ff';ctx.fillRect(Math.round(s.x),Math.round(s.y),s.s,s.s)});
      ctx.fillStyle='#071b40';for(let y=0;y<480;y+=32)ctx.fillRect(0,y,640,1);
      if(game){game.items.forEach(it=>it.type==='reel'?drawReel(it):drawHazard(it));drawPixelCamera(game.player)}
      raf=requestAnimationFrame(loop);
    }
    raf=requestAnimationFrame(loop);
    startBtn.addEventListener('click',()=>{reset();start.style.display='none'});
    const close=()=>{cancelAnimationFrame(raf);overlay.remove();document.body.style.overflow='';window.removeEventListener('keydown',kd);window.removeEventListener('keyup',ku)};
    overlay.querySelector('.arcade-game-close').addEventListener('click',close);
    function kd(e){if(['ArrowLeft','a','A'].includes(e.key))keys.left=true;if(['ArrowRight','d','D'].includes(e.key))keys.right=true;if(e.code==='Space'){keys.boost=true;e.preventDefault()}}
    function ku(e){if(['ArrowLeft','a','A'].includes(e.key))keys.left=false;if(['ArrowRight','d','D'].includes(e.key))keys.right=false;if(e.code==='Space')keys.boost=false}
    window.addEventListener('keydown',kd);window.addEventListener('keyup',ku);
    overlay.querySelectorAll('[data-dir]').forEach(btn=>{const dir=btn.dataset.dir;const on=e=>{e.preventDefault();keys[dir]=true},off=e=>{e.preventDefault();keys[dir]=false};btn.addEventListener('pointerdown',on);btn.addEventListener('pointerup',off);btn.addEventListener('pointercancel',off);btn.addEventListener('pointerleave',off)});
  }
  launch.addEventListener('click',openGame);
})();
