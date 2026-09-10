'use strict';
// R4 combat extension: every attack has a visible tell, finite active window and recovery.
window.GOTHIC_COMBAT={
 canCapture(s,e){const state=e.getData('state'),type=e.getData('type');if(s.clock<e.getData('stunUntil'))return true;if(type==='monster'&&['windup','attack'].includes(state))return false;if(type==='ghost'&&['windup','attack'].includes(state))return false;if(type==='werewolf'&&state==='attack')return false;return true;},
 flash(s){const C=GOTHIC_CONFIG,now=s.clock;if(now<s.flashUntil||s.film<C.film.flashCost||now<s.hurtUntil)return;s.film-=C.film.flashCost;s.flashUntil=now+C.film.flashCooldown;s.invUntil=Math.max(s.invUntil,now+210);s.stats.flashes++;s.recoilUntil=now+180;s.pose('recoil');GOTHIC.audio.play('capture');
 const x=s.player.x,y=s.player.y-49,burst=s.add.image(x,y,'lens-halo').setBlendMode(Phaser.BlendModes.ADD).setDepth(28).setScale(.4);s.tweens.add({targets:burst,scale:3,alpha:0,duration:290,onComplete:()=>burst.destroy()});
 for(const e of s.enemies){if(!e.active||e.getData('state')==='capturing')continue;if(Math.abs(e.x-x)<195&&Math.abs(e.body.center.y-y)<115){e.setData({state:'stunned',stunUntil:now+1150,nextAttack:now+1700,hit:true});e.setVelocity(0).setAlpha(1).setTint(0xc7edff);e.body.setAllowGravity(!C.enemies[e.getData('type')].floating);e.play(e.getData('type')+'-resist');s.stats.blocked++;}}
 for(const p of s.projectiles)if(p.active&&Phaser.Math.Distance.Between(p.x,p.y,x,y)<230){p.destroy();s.stats.blocked++;}
 s.toast('FLASH · ATTACKS INTERRUPTED');
 },
 shoot(s,e,kind,dir){const p=s.add.image(e.x+dir*23,kind==='wave'?311:e.y-54,kind==='wave'?'stone':'spiral').setDepth(24);if(kind==='wave'){p.setCrop(0,0,38,16).setOrigin(0,0);p.setPosition(e.x+dir*20,304);}else p.setScale(kind==='bone'?.17:.22).setTint(kind==='bone'?0xe8ddba:0xc595f5).setBlendMode(Phaser.BlendModes.ADD);
 const dy=s.player.body.center.y-p.y,dx=s.player.x-p.x,ang=Math.atan2(dy,dx);p.setData({kind,vx:kind==='wave'?dir*152:Math.cos(ang)*(kind==='bolt'?136:125),vy:kind==='wave'?0:Math.sin(ang)*(kind==='bolt'?136:125),born:s.clock,passed:false});s.projectiles.push(p);return p;
 },
 updateEnemy(s,e,dt){const C=GOTHIC_CONFIG,now=s.clock,type=e.getData('type'),cfg=C.enemies[type],dx=s.player.x-e.x,dy=s.player.body.center.y-e.body.center.y;let state=e.getData('state');
 if(now<e.getData('stunUntil')){e.setVelocityX(0);if(cfg.floating)e.setVelocityY(0);e.setTint(0xbddff1).setAlpha(1);return;}
 if(state==='stunned'){e.setData('state','walk');e.clearTint();e.play(type+'-walk');state='walk';}
 if(state==='windup'){
  e.setVelocityX(0);const progress=(now-e.getData('attackAt'))/cfg.windup;const x=Math.round(e.x),y=Math.round(e.y-e.displayHeight+2);s.fx.fillStyle(0xffc773,.92).fillRect(x-1,y-10,3,7).fillRect(x-1,y,3,2);s.fx.lineStyle(1,0xffb964,.8).strokeRect(x-16,y-14,32,3);s.fx.fillStyle(0xffc47a).fillRect(x-15,y-13,30*Math.min(1,progress),1);
  e.setTint(Math.floor(now/110)%2?0xffd5a5:0xffffff);
  if(progress>=1){state='attack';e.setData({state,activeAt:now,attackDir:Math.sign(dx)||1,hit:false});e.play(type+'-attack');e.clearTint();s.stats.attacks++;const dir=e.getData('attackDir');
   if(cfg.attack==='bone'||cfg.attack==='bolt')this.shoot(s,e,cfg.attack,dir);
   if(cfg.attack==='slam'){this.shoot(s,e,'wave',1);this.shoot(s,e,'wave',-1);s.toast('SHOCKWAVE · JUMP OR FLASH');}
   if(cfg.attack==='lunge')e.setVelocityX(dir*170);
   if(cfg.attack==='leap'){e.body.setAllowGravity(true);e.setVelocity(dir*155,-255);}
   if(cfg.attack==='phase'){e.setAlpha(.38);e.setVelocity(dir*175,0);}
  }return;
 }
 if(state==='attack'){
  const age=now-e.getData('activeAt'),melee=['lunge','leap','phase'].includes(cfg.attack),windowMs=cfg.attack==='leap'?590:420;
  if(melee&&age<windowMs){if(!e.getData('hit')&&Math.abs(dx)<44&&Math.abs(dy)<49){e.setData('hit',true);s.damage(e);}if(Math.abs(dx)<35&&Math.abs(dy)>=49&&!e.getData('dodged')){e.setData('dodged',true);s.stats.dodged++;}}
  else e.setVelocityX(0);
  if(age>windowMs+220){e.setData({state:'recover',recoverUntil:now+420});e.setVelocityX(0).setAlpha(1);e.clearTint();}return;
 }
 if(state==='recover'){e.setVelocityX(0);if(now>e.getData('recoverUntil')){e.setData('state','walk');e.play(type+'-walk');}return;}
 if(Math.abs(dx)<cfg.range&&Math.abs(dy)<100&&now>=e.getData('nextAttack')){e.setData({state:'windup',attackAt:now,nextAttack:now+cfg.cooldown,dodged:false,hit:false});e.setVelocityX(0);e.play(type+'-attack');return;}
 e.setFlipX(dx<0);e.setVelocityX(Math.abs(dx)<420?Math.sign(dx)*cfg.speed:0);
 // Ground enemies do not blindly walk into the catacomb chasm.
 if(!cfg.floating&&s.floorSegments.length>1){const ahead=e.x+Math.sign(dx)*35;if(!s.floorSegments.some(([a,b])=>ahead>=a&&ahead<=b))e.setVelocityX(0);}
 if(cfg.floating)e.setVelocityY((e.getData('baseY')+Math.sin(now*.002)*13-e.y)*3);
 },
 updateProjectiles(s,dt){const dir=s.player.flipX?-1:1,px=s.player.x+dir*26,py=s.player.y-66;
 for(const p of s.projectiles){if(!p.active)continue;const kind=p.getData('kind');p.x+=p.getData('vx')*dt;p.y+=p.getData('vy')*dt;if(kind!=='wave')p.rotation+=dt*3;
 if(s.clock-p.getData('born')>4200||p.x<0||p.x>s.stage.worldWidth||p.y>360||p.y<45){p.destroy();continue;}
 const dx=(p.x-px)*dir,half=8+Math.max(0,dx)*.23;if(kind!=='wave'&&s.beaming&&dx>0&&dx<GOTHIC_CONFIG.capture.range&&Math.abs(p.y-py)<half){p.destroy();s.stats.blocked++;s.film=Math.min(100,s.film+2);continue;}
 const radius=kind==='wave'?11:8,body=s.player.body,hit=p.x+radius>body.left&&p.x-radius<body.right&&p.y+radius>body.top&&p.y-radius<body.bottom;
 if(hit){s.damage(p);p.destroy();continue;}
 if(Math.abs(p.x-s.player.x)<20&&body.bottom<p.y-radius&&!p.getData('passed')){p.setData('passed',true);s.stats.dodged++;}
 }s.projectiles=s.projectiles.filter(p=>p.active);
 }
};
