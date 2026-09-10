'use strict';
window.GOTHIC = {phase:'loading', errors:[], inputs:{left:false,right:false,jump:false,beam:false}, pauseReasons:new Set(), cleanup:[]};
(()=>{
  const G=window.GOTHIC;
  const $=id=>document.getElementById(id);
  G.fail=function(message){const text=String(message);G.errors.push(text);G.phase='error';$('overlay').hidden=false;$('overlay-title').textContent='BUILD COULD NOT START';$('overlay-copy').textContent=text;$('start').hidden=true;$('reload').hidden=false;console.error(text);};
  window.addEventListener('error',e=>G.fail(e.message||'A required script failed to load.'));
  window.addEventListener('unhandledrejection',e=>G.fail(e.reason?.message||e.reason));
  G.clearInputs=()=>{G.clearPointers?.();Object.keys(G.inputs).forEach(k=>G.inputs[k]=false);document.querySelectorAll('[data-input]').forEach(el=>el.classList.remove('pressed'));G.scene?.input.keyboard?.resetKeys();if(G.scene?.player?.body)G.scene.player.setVelocityX(0);};
  G.pause=(reason,active)=>{if(active)G.pauseReasons.add(reason);else G.pauseReasons.delete(reason);G.clearInputs();if(!G.scene||G.phase==='loading'||G.phase==='error'||G.phase==='ready'||G.phase==='complete')return;
    if(G.pauseReasons.size){G.phase='paused';G.scene.physics.pause();$('overlay').hidden=false;$('overlay-title').textContent=G.pauseReasons.has('portrait')?'ROTATE TO LANDSCAPE':'PAUSED';$('overlay-copy').textContent='Your progress is safe.';$('start').textContent='RESUME';$('start').hidden=G.pauseReasons.has('portrait');}
    else{G.phase='running';G.scene.physics.resume();$('overlay').hidden=true;}G.hud?.render(G.scene);};
  window.addEventListener('blur',()=>G.pause('focus',true));
  window.addEventListener('focus',()=>G.pause('focus',false));
  document.addEventListener('visibilitychange',()=>G.pause('hidden',document.hidden));
  const orientation=()=>{const portrait=matchMedia('(pointer:coarse)').matches && innerHeight>innerWidth;G.pause('portrait',portrait);if(G.phase==='ready'){ $('start').hidden=portrait;$('overlay-copy').textContent=portrait?'Rotate your phone to landscape to enter.':'Six creatures. One roll of film. Capture them and reach the far gate.';}};
  window.addEventListener('resize',orientation);orientation();
  $('pause').onclick=()=>G.pause('manual',!G.pauseReasons.has('manual'));
  $('fullscreen').onclick=async()=>{try{if(document.fullscreenElement)await document.exitFullscreen();else await $('shell').requestFullscreen();}catch{$('hint').textContent='Fullscreen is unavailable here. Landscape play still works.';}};
  $('reload').onclick=()=>location.reload();
  $('start').onclick=()=>{G.audio?.unlock();if(G.phase==='complete'){G.scene.scene.restart();return;}if(G.phase==='ready'){G.phase='running';G.scene.physics.resume();$('overlay').hidden=true;if(G.pauseReasons.size)G.pause('start-check',false);}else if(G.phase==='paused'){G.pauseReasons.delete('manual');G.pauseReasons.delete('focus');G.pause('hidden',document.hidden);}};
  window.addEventListener('keydown',e=>{if((e.code==='Enter'||e.code==='Space')&&G.phase==='ready'&&!$('start').hidden){e.preventDefault();$('start').click();}});
  if(typeof $('shell').requestFullscreen!=='function')$('fullscreen').hidden=true;
  const pointers=new Map();G.clearPointers=()=>pointers.clear();
  document.querySelectorAll('[data-input]').forEach(el=>{
    const key=el.dataset.input;
    const off=e=>{pointers.delete(e.pointerId);G.inputs[key]=[...pointers.values()].includes(key);el.classList.toggle('pressed',G.inputs[key]);};
    el.addEventListener('pointerdown',e=>{e.preventDefault();if(G.phase!=='running')return;pointers.set(e.pointerId,key);G.inputs[key]=true;el.classList.add('pressed');el.setPointerCapture(e.pointerId);G.audio?.unlock();},{passive:false});
    el.addEventListener('pointerup',off);el.addEventListener('pointercancel',off);el.addEventListener('lostpointercapture',off);
  });
  window.addEventListener('blur',()=>pointers.clear());
})();
