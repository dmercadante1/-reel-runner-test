(()=>{
const panel=document.createElement('section');panel.innerHTML='<button id="chapter-run">Run chapter playthrough</button><button id="chapter-continue">Test from saved room</button><pre id="chapter-log" style="white-space:pre-wrap">Ready</pre>';document.body.append(panel);
const log=document.getElementById('chapter-log'),wait=ms=>new Promise(r=>setTimeout(r,ms)),s=()=>M1Bridge.state,checks=[];
let sent={};const act=(n,v=true)=>{if(sent[n]!==v){M1Bridge.send(n,v);sent[n]=v}};const cmd=n=>M1Bridge.send(n,true);const stop=()=>{for(const n of ['move_left','move_right','jump','record'])act(n,false)};
async function until(fn,time=15000){const t=performance.now();while(!fn()){if(performance.now()-t>time)throw Error('Timeout '+JSON.stringify(s()));await wait(30)}}
function check(name,ok){checks.push({name,passed:ok,room:s().room});log.textContent=checks.map(c=>(c.passed?'PASS ':'FAIL ')+c.name).join('\n');if(!ok)throw Error(name)}
async function capture(name){await new Promise(requestAnimationFrame);const blob=await new Promise(r=>canvas.toBlob(r,'image/png'));await fetch('/capture/'+name+'.png',{method:'POST',body:blob})}
async function walk(x,time=8000){const t=performance.now();while(Math.abs(s().x-x)>5){if(performance.now()-t>time)throw Error('Walk blocked toward '+x+' '+JSON.stringify(s()));const right=s().x<x;act('move_right',right);act('move_left',!right);await wait(30)}stop();await wait(160)}
async function leap(x){await until(()=>s().grounded);const right=s().x<x,t=performance.now();act('move_right',right);act('move_left',!right);while(right?s().x<x-5:s().x>x+5){if(performance.now()-t>15000)throw Error('Jump route blocked '+JSON.stringify(s()));if(s().grounded){act('jump');await wait(350);act('jump',false);await wait(90)}else await wait(35)}stop();await until(()=>s().grounded);await wait(100)}
async function fight(){let lastJump=0,beam=false,pull=false;const t=performance.now();while(!s().gate_open){if(s().phase==='defeated')throw Error('Defeated '+JSON.stringify(s()));if(performance.now()-t>90000)throw Error('Combat timeout '+JSON.stringify(s()));
 if(s().room===5&&s().feet>310){await leap(375);continue;}
 const enemy=s().enemies.find(e=>!['capturing','captured'].includes(e.phase));if(!enemy){stop();await wait(80);continue;}
 if(s().room===7&&enemy.kind==='vampire'&&s().feet>275){await walk(453);await leap(505);continue;}
 if(s().grounded&&enemy.y-s().feet>47){stop();cmd('drop');M1Bridge.send('drop',false);await wait(450);continue;}
 const gap=enemy.x-s().x;const facing=gap>=0?1:-1;let direction=0;let film=false;
 if(enemy.kind==='dracula'&&enemy.phase==='exposed'&&s().super_charges>0&&s().super_left<=0&&Math.abs(gap)<180){const before=enemy.exposure;stop();act(facing>0?'move_right':'move_left',true);await wait(100);stop();cmd('super_shot');await wait(160);check('Rare reel powers boss Super',s().enemies[0].exposure>=before+1.5);await capture('chapter-super-shot');}

 if(enemy.phase==='watch'){if(Math.abs(gap)>145)direction=facing;else if(Math.abs(gap)<105)direction=-facing;}
 else if(enemy.phase==='windup'){if(Math.abs(gap)<195)direction=-facing;}
 else if(enemy.phase==='attack'){if(Math.abs(gap)<150)direction=-facing;}
 else if(enemy.phase==='exposed'){
  if(Math.abs(gap)>150)direction=facing;
  film=Math.abs(gap)<180&&Math.abs(enemy.y-s().feet)<46;
  // Facing remains toward the target after the retreat, even while stationary.
  if(direction===0&&s().facing!==facing){stop();act(facing>0?'move_right':'move_left',true);await wait(35);act(facing>0?'move_right':'move_left',false);}

 }
 if(s().grounded&&(s().projectiles||[]).some(p=>{const eta=(s().x-p.x)/p.vx;return eta>0&&eta<.36&&Math.abs(s().feet-(p.y+(p.kind==='orb'?25:8)))<24})&&performance.now()-lastJump>700){act('jump');lastJump=performance.now();setTimeout(()=>act('jump',false),350)}
 act('move_right',direction>0);act('move_left',direction<0);act('record',film);
 if(s().film<1&&!s().reload_left){M1Bridge.send('reload',true);M1Bridge.send('reload',false)}
 if(film&&!beam){beam=true;await wait(180);await capture('chapter-'+s().room+'-beam')}
 if(s().enemies.some(e=>e.phase==='capturing')&&!pull){pull=true;await capture('chapter-'+s().room+'-capture')}
 await wait(55);
 }stop();await wait(150);}
const run=async(event)=>{checks.length=0;sent={};try{const startRoom=event.target.id==='chapter-continue'?s().room:0;cmd(startRoom?'resume':'new_game');await until(()=>s()?.phase==='running'&&s().grounded);for(let room=startRoom;room<9;room++){
 await until(()=>s().room===room&&s().phase==='running');await wait(250);await capture('chapter-'+room+'-start');
 if(room===0){await walk(249);await leap(367)}
 if(room===3){await walk(214);await leap(328)}
 if(room===5){await walk(252);await leap(369)}
 await fight();check('Room '+room+' encounters captured',s().gate_open);await capture('chapter-'+room+'-clear');
 if(room===0&&s().feet>235){await leap(370)}
 if(room===3&&s().feet>310){await leap(330)}
 if(room===5&&s().feet>310){await leap(380)}
 if(room===4){await walk(361);await leap(414);await walk(436);await leap(500)}
 if(room===5){await walk(447);await leap(504)}
 if(room===7){await walk(455);await leap(520)}
 act('move_right');await until(()=>s().phase==='transition'||s().phase==='chapter_complete');stop();check('Room '+room+' exit reached',true);
 }
 check('Dracula chapter completed',s().phase==='chapter_complete');await capture('chapter-ending');window.__chapterResult={passed:true,checks,state:s()};await fetch('/capture/chapter-browser-playthrough.json',{method:'POST',body:JSON.stringify({passed:true,checks,state:s(),physical_phone_tested:false,input_method:'browser engine action bridge'},null,2)});
 }catch(e){stop();window.__chapterResult={passed:false,checks,error:String(e),state:s()};log.textContent+='\nFAIL '+e;await capture('chapter-failure');await fetch('/capture/chapter-browser-playthrough.json',{method:'POST',body:JSON.stringify({passed:false,checks,error:String(e),state:s()},null,2)})}};document.getElementById('chapter-run').onclick=run;document.getElementById('chapter-continue').onclick=run;
})();
