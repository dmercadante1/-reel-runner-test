'use strict';
// Lives outside the canvas; never rebuild DOM every animation frame.
(()=>{const $=id=>document.getElementById(id);let cache={};GOTHIC.hud={render(s){
const max=GOTHIC_CONFIG.hero.health,life=Math.max(0,s.health),film=Math.round(s.film),cap=s.captured,total=GOTHIC_CONFIG.spawns.length,saved=s.checkpoint>110;
if(life!==cache.life){$('life-meter').setAttribute('aria-valuenow',life);$('life-value').textContent=life+'/'+max;[...$('hearts').children].forEach((e,i)=>e.classList.toggle('empty',i>=life));cache.life=life;}
if(film!==cache.film){$('film').value=film;$('film').setAttribute('aria-valuetext',film+' percent film remaining');$('film-value').textContent=film;$('film-meter').classList.toggle('low',film<25);cache.film=film;}
if(cap!==cache.cap){$('capture-value').textContent=cap+'/'+total;[...$('capture-slots').children].forEach((e,i)=>e.classList.toggle('filled',i<cap));cache.cap=cap;}
if(saved!==cache.saved){$('checkpoint').textContent=saved?'CHECKPOINT SAVED':'FIND THE FAR GATE';$('checkpoint').classList.toggle('saved',saved);cache.saved=saved;}
const message='LIFE '+life+' OF '+max+' · CAPTURED '+cap+' OF '+total+(saved?' · CHECKPOINT SAVED':'');if(message!==cache.message){$('status').textContent=message;cache.message=message;}
const paused=GOTHIC.phase==='paused';if(paused!==cache.paused){$('pause').textContent=paused?'RESUME':'PAUSE';$('pause').setAttribute('aria-label',paused?'Resume game':'Pause game');cache.paused=paused;}
},reset(){cache={};}};})();
