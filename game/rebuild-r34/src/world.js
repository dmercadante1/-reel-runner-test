'use strict';
window.GOTHIC_WORLD={
 build(s){const C=GOTHIC_CONFIG,W=s.stage.worldWidth;s.physics.world.setBounds(0,-80,W,560);s.cameras.main.setBounds(0,0,W,360).setBackgroundColor('#07101b');s.backdrops=[];
 const sf=s.stage.scroll,count=Math.ceil((W*sf+640)/640)+1;
 for(let i=0;i<count;i++)s.backdrops.push(s.add.image(i*640,0,s.stage.background).setOrigin(0).setScrollFactor(sf,0).setDepth(-30));
 // Cropped raster columns/arches establish a nearer depth plane, never an opaque foreground over the hero.
 if(s.stage.id!=='courtyard')for(let x=220;x<W;x+=420){s.add.image(x,310,'arch').setOrigin(.5,1).setAlpha(s.stage.id==='ramparts'?.82:.36).setDepth(-12);}
 s.solids=s.physics.add.staticGroup();s.platforms=[];s.pickups=[];
 const segments=s.edition===4&&s.stage.id==='catacombs'?[[0,710],[878,W]]:[[0,W]];s.floorSegments=segments;
 for(const [x0,x1]of segments){const z=s.add.zone((x0+x1)/2,C.floorY+30,x1-x0,60);s.physics.add.existing(z,true);s.solids.add(z);for(let x=x0;x<x1;x+=448){const width=Math.min(448,x1-x);s.add.image(x,C.floorY,'stone').setOrigin(0).setCrop(0,0,width,44).setDepth(-4);}}
 for(const def of s.stage.platforms)this.platform(s,def);
 if(s.edition===4&&s.stage.id==='cathedral')this.platform(s,{x:1640,top:222,width:190});
 if(s.edition===4&&s.stage.id==='catacombs')s.add.text(665,334,'CHASM · JUMP',{fontFamily:'monospace',fontSize:'8px',color:'#dcc994'}).setOrigin(.5).setDepth(26);
 if(s.edition===4&&s.stage.id==='catacombs'){this.platform(s,{x:708,top:286,width:112});this.platform(s,{x:896,top:280,width:110});this.platform(s,{x:796,top:292,width:96,motion:{axis:'x',distance:38,speed:28}});}
 for(const p of s.stage.pickups){const a=s.add.image(p.x,p.y,p.kind==='heart'?'heart':'spiral').setDepth(14).setScale(p.kind==='heart'?1.3:.29);s.pickups.push({obj:a,...p,baseY:p.y});}
 s.checkpointLabel=s.add.text(s.stage.checkpoint,286,'◆ SAVE',{fontFamily:'monospace',fontSize:'8px',color:'#abbea7',backgroundColor:'#12221d',padding:{x:4,y:2}}).setOrigin(.5).setDepth(32);
 let top=s.edition===4&&s.stage.id==='cathedral'?222:s.stage.exit.top;s.exitTop=top;
 s.gate=s.add.image(s.stage.exit.x,top,'arch').setOrigin(.5,1).setTint(0x8598ad).setDepth(12);
 s.exitLabel=s.add.text(s.stage.exit.x,top-160,'SEAL: '+s.stage.enemies.length,{fontFamily:'monospace',fontSize:'8px',color:'#ccbfa0',backgroundColor:'#101823',padding:{x:5,y:3}}).setOrigin(.5).setDepth(30);
 s.stageBanner=s.add.text(320,75,s.stage.name,{fontFamily:'Georgia',fontSize:'20px',color:'#e9dab7',stroke:'#07101b',strokeThickness:4}).setOrigin(.5).setScrollFactor(0).setDepth(120);
 s.tweens.add({targets:s.stageBanner,alpha:0,delay:1800,duration:900});
 s.lights=[];for(let x=220;x<W;x+=410)s.lights.push(s.add.image(x,268,'lens-halo').setTint(s.stage.palette).setAlpha(.13).setScale(.5).setBlendMode(Phaser.BlendModes.ADD).setDepth(-8));
 },
 platform(s,def){const w=def.width,z=s.add.zone(def.x,def.top+6,w,12);s.physics.add.existing(z,!!(!def.motion));z.body.setSize(w,12);if(def.motion){z.body.setAllowGravity(false);z.body.setImmovable(true);z.body.setFriction(1,1);}z.body.checkCollision.down=false;z.body.checkCollision.left=false;z.body.checkCollision.right=false;
 const art=s.add.image(def.x-w/2,def.top,'stone').setOrigin(0).setCrop(0,0,w,18).setDepth(2);const p={zone:z,art,def,collapseAt:0,returnAt:0,startX:def.x,startY:def.top+6};s.platforms.push(p);return p;},
 connect(s){s.physics.add.collider(s.player,s.solids);for(const p of s.platforms)s.physics.add.collider(s.player,p.zone,()=>{s.onPlatform=p;if(p.def.crumble&&s.edition===4&&!p.collapseAt)p.collapseAt=s.clock+850;},(a,b)=>b.body.enable&&a.body.velocity.y>=-1&&a.body.prev.y+a.body.height<=b.body.top+8);},
 update(s,dt){const now=s.clock;
 for(const p of s.platforms){const m=p.def.motion,b=p.zone.body;if(m&&b.enable){const axis=m.axis,target=(axis==='x'?p.startX:p.startY)+Math.sin(now*.001*m.speed/m.distance)*m.distance,position=axis==='x'?p.zone.x:p.zone.y,v=Phaser.Math.Clamp((target-position)*8,-m.speed,m.speed);if(axis==='x')b.setVelocity(v,0);else b.setVelocity(0,v);}
 p.art.setPosition(p.zone.x-p.def.width/2,p.zone.y-6);
 if(p.collapseAt){p.art.setTint(Math.floor(now/100)%2?0xcab088:0xffffff);if(now>p.collapseAt){b.enable=false;p.art.setVisible(false);p.collapseAt=0;p.returnAt=now+3300;}}
 if(p.returnAt&&now>p.returnAt){b.enable=true;p.art.setVisible(true).clearTint();p.returnAt=0;}}
 for(const p of s.pickups){if(!p.obj.active)continue;p.obj.y=p.baseY+Math.sin(now*.004)*3;if(Math.abs(s.player.x-p.x)<28&&Math.abs(s.player.body.center.y-p.obj.y)<48){if(p.kind==='heart')s.health=Math.min(GOTHIC_CONFIG.hero.health,s.health+1);else s.film=Math.min(100,s.film+30);s.toast(p.kind==='heart'?'LIFE +1':'FILM +30');p.obj.destroy();GOTHIC.audio.play('checkpoint');s.stats.pickups++;}}
 for(let i=0;i<s.lights.length;i++)s.lights[i].setAlpha(.11+.03*Math.sin(now*.009+i*3));
 }
};
