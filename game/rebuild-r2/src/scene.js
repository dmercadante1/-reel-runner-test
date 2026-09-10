'use strict';
(()=>{
const C=GOTHIC_CONFIG,G=GOTHIC;
class GothicHorror extends Phaser.Scene{
 constructor(){super('GothicHorror');}
 init(){this.player=null;this.health=C.hero.health;this.film=C.film.max;this.captured=0;this.checkpoint=110;this.hurtUntil=0;this.invUntil=0;this.recoilUntil=0;this.emptyUntil=0;this.jumpBuffered=-1;this.lastGround=-1000;this.jumpHeld=false;this.playerState=null;this.lastHud='';this.tick=0;this.hurtCount=0;this.assetErrors=[];G.scene=this;G.phase='loading';G.clearInputs();}
 preload(){
   this.load.on('loaderror',file=>this.assetErrors.push(file.key));
   this.load.on('progress',n=>{document.getElementById('overlay-copy').textContent=`Loading verified artwork… ${Math.round(n*100)}%`;});
   for(const a of GOTHIC_ASSETS){if(a.frames)this.load.spritesheet(a.key,a.data,{frameWidth:a.frameWidth,frameHeight:a.frameHeight});else this.load.image(a.key,a.data);}
 }
 create(){
  if(this.assetErrors.length){G.fail('Artwork could not be decoded: '+this.assetErrors.join(', '));return;}
  for(const a of GOTHIC_ASSETS){const tex=this.textures.get(a.key),img=tex?.getSourceImage();if(!img||img.width!==a.width||img.height!==a.height){G.fail(`Invalid texture: ${a.key}`);return;}tex.setFilter(Phaser.Textures.FilterMode.NEAREST);if(a.frames&&tex.frameTotal-1!==a.frames){G.fail(`Incorrect frame count: ${a.key}`);return;}}
  this.physics.world.setBounds(0,0,C.worldWidth,C.height);this.cameras.main.setBounds(0,0,C.worldWidth,C.height).setBackgroundColor('#070d16');
  // One verified, full-composition background, not a cropped strip stretched to the screen.
  this.backdrops=[];for(let i=0;i<3;i++)this.backdrops.push(this.add.image(i*640,0,'courtyard').setOrigin(0).setFlipX(i%2===1).setScrollFactor(.18,0).setDepth(-30));
  this.solids=this.physics.add.staticGroup();
  const floor=this.add.zone(C.worldWidth/2,C.floorY+22,C.worldWidth,44);this.physics.add.existing(floor,true);this.solids.add(floor);
  for(let x=0;x<C.worldWidth;x+=448)this.add.image(x,C.floorY,'stone').setOrigin(0).setDepth(-5);
  this.ledges=[];for(const platform of C.platforms){
   // Artwork and collision share the same top and width. No invisible floating ledges.
   this.add.image(platform.x-platform.width/2,platform.top,'stone').setOrigin(0).setCrop(0,0,platform.width,18).setDepth(-4);
   const z=this.add.zone(platform.x,platform.top+5,platform.width,10);this.physics.add.existing(z,true);this.ledges.push(z);
  }
  this.animations();
  this.player=this.physics.add.sprite(110,240,'hero-brace',0).setOrigin(.5,1).setDepth(20).setCollideWorldBounds(true);
  this.player.body.setSize(30,79).setOffset(41,27);this.player.setMaxVelocity(C.hero.speed,600);
  this.physics.add.collider(this.player,this.solids);
  for(const p of this.ledges)this.physics.add.collider(this.player,p,null,(a,b)=>a.body.velocity.y>=0&&a.body.prev.y+a.body.height<=b.body.top+7);
  this.enemies=[];for(const [type,x] of C.spawns)this.spawn(type,x);
  this.fx=this.add.graphics().setDepth(25);this.beam=this.add.graphics().setDepth(19);this.vortices=[];
  this.cursors=this.input.keyboard.createCursorKeys();this.keys=this.input.keyboard.addKeys('A,D,W,SPACE,C,P,R');
  this.input.keyboard.on('keydown-P',()=>G.pause('manual',!G.pauseReasons.has('manual')));
  this.input.keyboard.on('keydown-ESC',()=>G.pause('manual',!G.pauseReasons.has('manual')));
  this.input.keyboard.on('keydown-R',()=>this.scene.restart());
  this.cameras.main.startFollow(this.player,true,.12,1,-110,0);this.cameras.main.setDeadzone(60,360);this.cameras.main.roundPixels=true;
  this.checkpointLabel=this.add.text(C.checkpointX,181,'CHECKPOINT',{fontFamily:'monospace',fontSize:'8px',color:'#bed1d8',backgroundColor:'#101b24',padding:{x:4,y:3}}).setOrigin(.5).setDepth(35);
  this.exitLabel=this.add.text(C.exitX,182,'COURTYARD EXIT\nCAPTURE ALL SIX',{fontFamily:'monospace',fontSize:'9px',align:'center',color:'#ead9a7',backgroundColor:'#111b23',padding:{x:6,y:5}}).setOrigin(.5).setDepth(35);
  this.physics.pause();G.phase='ready';this.renderHud();
  const overlay=document.getElementById('overlay');overlay.hidden=false;document.getElementById('overlay-title').textContent='GOTHIC HORROR';document.getElementById('overlay-copy').textContent='Six creatures. One roll of film. Capture them and reach the far gate.';const start=document.getElementById('start');start.hidden=false;start.textContent='PRESS START';
  document.getElementById('build').textContent='BUILD R2';
  if(G.pauseReasons.has('portrait')){start.hidden=true;document.getElementById('overlay-copy').textContent='Rotate your phone to landscape to enter.';}
  this.events.once('shutdown',()=>{this.enemies=[];this.vortices=[];G.clearInputs();});
 }
 animations(){
  const spec=[['hero-walk',0,7,10],['hero-brace',0,3,4],['hero-recoil',0,3,10],['hero-jump',0,3,9],['hero-hurt',0,3,9]];
  for(const [key,start,end,rate]of spec)if(!this.anims.exists(key))this.anims.create({key,frames:this.anims.generateFrameNumbers(key,{start,end}),frameRate:rate,repeat:key==='hero-walk'||key==='hero-brace'?-1:0});
  for(const type of Object.keys(C.enemies))for(const [state,start,end,rate]of [['walk',0,3,6],['attack',4,5,8],['resist',6,7,8]]){const key=type+'-'+state;if(!this.anims.exists(key))this.anims.create({key,frames:this.anims.generateFrameNumbers(type,{start,end}),frameRate:rate,repeat:state==='attack'?0:-1});}
 }
 spawn(type,x){const cfg=C.enemies[type];const e=this.physics.add.sprite(x,cfg.floating?298:C.floorY+6,type,0).setOrigin(.5,1).setDepth(18).setFlipX(true);e.body.setSize(type==='monster'?53:35,type==='monster'?85:80).setOffset(type==='monster'?30:38,26);e.setCollideWorldBounds(true);e.setData({type,state:'walk',capture:0,attackAt:0,nextAttack:0,baseY:298,hit:false,baseScale:1});if(cfg.floating)e.body.setAllowGravity(false);else this.physics.add.collider(e,this.solids,null,a=>!['resist','pull','capturing'].includes(a.getData('state')));e.play(type+'-walk');this.enemies.push(e);return e;}
 pose(state){if(this.playerState===state)return;this.playerState=state;this.player.play('hero-'+state,true);}
 damage(enemy,time){if(time<this.invUntil||G.phase!=='running')return;this.health--;this.hurtCount++;this.hurtUntil=time+C.hero.hurtMs;this.invUntil=time+C.hero.invulnerabilityMs;this.player.setVelocity(this.player.x<enemy.x?-155:155,-125);this.pose('hurt');G.audio.play('hurt');this.cameras.main.shake(90,.003);if(this.health<=0){this.health=C.hero.health;this.film=C.film.max;this.player.body.reset(this.checkpoint,230);this.player.setVelocity(0);this.invUntil=time+1600;this.hurtUntil=time+150;for(const e of this.enemies)if(e.active&&Math.abs(e.x-this.checkpoint)<110)e.body.reset(this.checkpoint+160,C.floorY+6);}this.renderHud();}
 attack(e,time){const cfg=C.enemies[e.getData('type')],dx=this.player.x-e.x,dy=this.player.body.center.y-e.body.center.y;let state=e.getData('state');if(state==='attack'){
   const age=time-e.getData('attackAt');e.setVelocityX(age>=cfg.attackMs&&age<cfg.attackMs+160?Math.sign(dx)*70:0);
   if(age>=cfg.attackMs&&age<cfg.attackMs+160&&!e.getData('hit')&&Math.abs(dx)<59&&Math.abs(dy)<52){e.setData('hit',true);this.damage(e,time);}
   if(age>cfg.attackMs+220){e.setData('state','walk');e.play(e.getData('type')+'-walk');}return;
  }
  if(Math.abs(dx)<61&&Math.abs(dy)<50&&time>=e.getData('nextAttack')){e.setData({state:'attack',attackAt:time,nextAttack:time+cfg.cooldown,hit:false});e.setVelocityX(0);e.play(e.getData('type')+'-attack');return;}
  e.setVelocityX(Math.abs(dx)<380?Math.sign(dx)*cfg.speed:0);
  // Source sprites face right; flip only when chasing to the left.
  e.setFlipX(dx<0);
  if(cfg.floating)e.setVelocityY((e.getData('baseY')+Math.sin(time*.002)*11-e.y)*3);
 }
 capture(e,time,dt){const cfg=C.enemies[e.getData('type')];let c=Math.min(1,e.getData('capture')+dt/cfg.resistance);e.setData('capture',c);
  const state=c>.42?'pull':'resist';if(e.getData('state')!==state){e.setData('state',state);e.play(e.getData('type')+'-resist');}
  e.body.setAllowGravity(false);const dir=this.player.flipX?-1:1,targetX=this.player.x+dir*42,targetY=this.player.y-35;
  e.setVelocityX(Math.sign(targetX-e.x)*Math.min(C.capture.pullSpeed,Math.abs(targetX-e.x)*5)*(c>.42?1:.28));
  e.setVelocityY((targetY-e.y)*c*2);e.setTint(0xd5efff);e.setAngle(Math.round(Math.sin(time*.025)*3*c));e.setScale(1-c*.23);
  if(c>=1){e.setData('state','capturing');e.body.enable=false;e.anims.stop();const swirl=this.add.image(e.x,e.y-45,'spiral').setDepth(24).setBlendMode(Phaser.BlendModes.ADD);this.vortices.push(swirl);
    this.tweens.add({targets:[e,swirl],x:targetX,y:targetY-10,scaleX:.08,scaleY:.08,alpha:0,duration:210,onComplete:()=>{e.destroy();swirl.destroy();}});this.captured++;this.film=Math.min(C.film.max,this.film+C.film.reward);this.recoilUntil=time+150;G.audio.play('capture');this.pose('recoil');}
 }
 drawBeam(time){const dir=this.player.flipX?-1:1,px=this.player.x+dir*26,py=this.player.y-66,g=this.beam;
  for(let band=-2;band<=2;band++){g.lineStyle(1,0xbde4f5,band===0?.65:.25);g.beginPath();g.moveTo(Math.round(px),Math.round(py));for(let j=1;j<=18;j++){const t=j/18;g.lineTo(Math.round(px+dir*C.capture.range*t),Math.round(py+band*23*t+Math.sin(time*.012+j+band)*2));}g.strokePath();}
  g.fillStyle(0xe5f5ff,.8);for(let i=0;i<25;i++){const t=((i*.137+time*.0005)%1),x=px+dir*C.capture.range*(1-t),y=py+Math.sin(i*2.4)*(1-t)*50;g.fillRect(Math.round(x),Math.round(y),1,1);}
 }
 renderHud(){G.hud.render(this);}

 update(time,delta){if(G.phase!=='running'||!this.player)return;this.tick++;const dt=Math.min(delta/1000,.05),p=this.player,t=G.inputs;
  const left=t.left||this.cursors.left.isDown||this.keys.A.isDown,right=t.right||this.cursors.right.isDown||this.keys.D.isDown,held=t.beam||this.keys.SPACE.isDown||this.keys.C.isDown,jump=t.jump||this.cursors.up.isDown||this.keys.W.isDown;
  let beam=held&&this.film>0&&time>=this.emptyUntil&&time>=this.hurtUntil;
  if(p.body.blocked.down||p.body.touching.down)this.lastGround=time;
  if(jump&&!this.jumpHeld)this.jumpBuffered=time;this.jumpHeld=jump;
  if(time>=this.hurtUntil){const direction=Number(right)-Number(left),speed=beam?C.hero.filmSpeed:C.hero.speed,target=direction*speed;const v=p.body.velocity.x+Phaser.Math.Clamp(target-p.body.velocity.x,-(direction?C.hero.acceleration:C.hero.drag)*dt,(direction?C.hero.acceleration:C.hero.drag)*dt);p.setVelocityX(v);if(direction)p.setFlipX(direction<0);
   if(this.jumpBuffered>=0&&time-this.jumpBuffered<C.hero.jumpBufferMs&&time-this.lastGround<C.hero.coyoteMs){p.setVelocityY(C.hero.jump);this.jumpBuffered=-1;this.lastGround=-1000;G.audio.play('jump');}
   this.pose(time<this.recoilUntil?'recoil':beam?'brace':!p.body.blocked.down?'jump':Math.abs(v)>8?'walk':'brace');
  }
  p.setAlpha(time<this.invUntil?(Math.floor(time/80)%2?.48:1):1);
  this.beam.clear();this.fx.clear();if(beam){this.film=Math.max(0,this.film-C.film.drain*dt);if(this.film===0)this.emptyUntil=time+C.film.emptyLockMs;this.drawBeam(time);}else this.film=Math.min(C.film.max,this.film+C.film.recover*dt);
  for(const e of this.enemies){if(!e.active||e.getData('state')==='capturing')continue;const cfg=C.enemies[e.getData('type')],dx=(e.x-p.x)*(p.flipX?-1:1),dy=Math.abs(e.body.center.y-p.body.center.y),targeted=beam&&dx>12&&dx<C.capture.range+26&&dy<C.capture.halfHeight;
   if(targeted)this.capture(e,time,dt);else{if(['resist','pull'].includes(e.getData('state'))){e.setData('state','walk');e.setScale(1).setAngle(0).clearTint();e.body.setAllowGravity(!cfg.floating);e.play(e.getData('type')+'-walk');}e.setData('capture',Math.max(0,e.getData('capture')-dt*C.capture.releaseDecay));this.attack(e,time);}
   const c=e.getData('capture');if(c>0&&e.active){const x=Math.round(e.x),y=Math.round(e.y-e.displayHeight+12);this.fx.lineStyle(1,0xc6e6f2,.8);this.fx.strokeRect(x-18,y,36,4);this.fx.fillStyle(0xbcecff,.9).fillRect(x-17,y+1,34*c,2);}
  }
  if(p.x>C.checkpointX&&this.checkpoint===110){this.checkpoint=C.checkpointX;this.checkpointLabel.setText('CHECKPOINT SAVED').setColor('#b7e6c5');G.audio.play('checkpoint');}
  if(p.x>C.exitX&&this.captured===C.spawns.length){G.phase='complete';this.physics.pause();G.clearInputs();document.getElementById('overlay').hidden=false;document.getElementById('overlay-title').textContent='GOTHIC HORROR — CAPTURED';document.getElementById('overlay-copy').textContent='All six creatures are on film. The courtyard is clear.';document.getElementById('start').textContent='PLAY AGAIN';}
  this.renderHud();
 }
}
window.GOTHIC_SCENE=GothicHorror;
})();
