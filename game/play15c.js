(()=>{
const C=window.MWCAM_CONFIG||{};
const A=window.MWCAM_ASSETS||{};
const M=window.MWCAM_ENEMY_ATLAS||{frameWidth:128,frameHeight:128,rows:{skeleton:0,ghoul:4,vampire:8,monster:12,werewolf:16,ghost:20}};
const TYPES=['skeleton','ghoul','vampire','monster','werewolf','ghost'];
const BODIES={
  skeleton:{w:44,h:94,ox:42,oy:24},ghoul:{w:54,h:92,ox:37,oy:27},vampire:{w:46,h:98,ox:41,oy:22},
  monster:{w:72,h:108,ox:28,oy:16},werewolf:{w:66,h:104,ox:31,oy:18},ghost:{w:50,h:86,ox:39,oy:24}
};
const touch={left:false,right:false,jump:false,beam:false};
class GothicHorror extends Phaser.Scene{
  constructor(){super('GothicHorror');this.health=C.player?.maxHealth||5;this.film=C.film?.max||100;this.captured=0;this.dead=false;this.jumpLatch=false;}
  preload(){
    if(A.courtyard)this.load.image('courtyard',A.courtyard);
    this.load.spritesheet('hero',A.hero,{frameWidth:C.player.frame.width,frameHeight:C.player.frame.height});
    this.load.spritesheet('enemyAtlas',A.enemyAtlas,{frameWidth:M.frameWidth||128,frameHeight:M.frameHeight||128});
  }
  create(){
    const worldW=C.horror.worldWidth;
    this.physics.world.setBounds(0,0,worldW,720);this.cameras.main.setBounds(0,0,worldW,720);this.cameras.main.setBackgroundColor('#070910');
    if(this.textures.exists('courtyard'))for(let i=0;i<6;i++)this.add.image(i*900,365,'courtyard').setOrigin(0,.5).setDisplaySize(960,498).setScrollFactor(.24).setAlpha(.52).setTint(0x647594).setDepth(-10);
    this.solids=this.physics.add.staticGroup();
    const floor=this.add.rectangle(worldW/2,C.horror.floorY+45,worldW,110,0x141319).setVisible(true);this.physics.add.existing(floor,true);this.solids.add(floor);
    (C.horror.platforms||[]).forEach(([x,y,w])=>{const p=this.add.rectangle(x,y,w,24,0x2d2932);this.physics.add.existing(p,true);this.solids.add(p)});
    this.makeAnimations();
    this.player=this.physics.add.sprite(170,500,'hero',0).setScale(C.player.scale).setDepth(8).setCollideWorldBounds(true);
    this.player.body.setSize(50,104).setOffset(39,20);this.physics.add.collider(this.player,this.solids);
    this.enemies=this.physics.add.group();
    (C.horror.spawns||[]).forEach(([type,x,y])=>this.spawn(type,x,y));
    this.physics.add.collider(this.enemies,this.solids);this.physics.add.overlap(this.player,this.enemies,(p,e)=>this.hurt(e));
    this.beam=this.add.graphics().setDepth(6);this.bars=this.add.graphics().setDepth(12);
    this.cursors=this.input.keyboard.createCursorKeys();this.keys=this.input.keyboard.addKeys('A,D,W,SPACE');
    this.cameras.main.startFollow(this.player,true,.09,.09,-170,35);this.cameras.main.roundPixels=true;this.cameras.main.setDeadzone(130,75);
    this.bindTouch();this.updateHud();
  }
  frameRange(type){const start=Number(M.rows?.[type]);return Number.isFinite(start)?{start,end:start+3}:null;}
  makeAnimations(){
    this.anims.create({key:'hero-walk',frames:this.anims.generateFrameNumbers('hero',{start:0,end:7}),frameRate:C.player.animations.walk.rate,repeat:-1});
    TYPES.forEach(type=>{const range=this.frameRange(type),cfg=C.enemies?.[type];if(!range||!cfg)return;this.anims.create({key:type+'-walk',frames:this.anims.generateFrameNumbers('enemyAtlas',range),frameRate:cfg.walkRate,repeat:-1})});
  }
  spawn(type,x,y){
    const cfg=C.enemies?.[type],range=this.frameRange(type),body=BODIES[type];if(!cfg||!range||!body)return;
    const e=this.enemies.create(x,y,'enemyAtlas',range.start).setScale(cfg.scale).setDepth(8);
    e.setData('type',type);e.setData('capture',0);e.setData('resistance',cfg.resistance);e.setData('baseScale',cfg.scale);e.setData('baseY',y);
    e.body.setSize(body.w,body.h).setOffset(body.ox,body.oy);
    if(cfg.floating){e.body.setAllowGravity(false);e.body.checkCollision.down=false;}
    e.play(type+'-walk');return e;
  }
  bindTouch(){
    document.querySelectorAll('#touch button').forEach(b=>{const k=b.dataset.k,on=e=>{e.preventDefault();touch[k]=true},off=e=>{e.preventDefault();touch[k]=false};b.addEventListener('pointerdown',on);b.addEventListener('pointerup',off);b.addEventListener('pointercancel',off);b.addEventListener('pointerleave',off)});
    const fs=document.getElementById('fullscreen');if(fs)fs.onclick=()=>document.documentElement.requestFullscreen?.();
  }
  hurt(e){if(this.dead||this.player.getData('inv'))return;this.player.setData('inv',true);this.health--;this.player.setVelocity(this.player.x<e.x?-180:180,-190);this.cameras.main.shake(120,.005);this.time.delayedCall(800,()=>this.player.setData('inv',false));if(this.health<=0){this.dead=true;this.time.delayedCall(250,()=>{this.health=C.player.maxHealth;this.film=C.film.max;this.player.setPosition(170,500).setVelocity(0,0);this.dead=false;this.player.setData('inv',false);this.updateHud()})}this.updateHud();}
  captureEnemy(e,dt){const type=e.getData('type'),cfg=C.enemies[type],rate=C.capture.baseRate/cfg.resistance;let c=e.getData('capture')+rate*dt;e.setData('capture',c);const dir=this.player.flipX?-1:1;e.x+=dir*-C.capture.pullStrength*dt*.18;if(c>=1){this.captured++;this.film=Math.min(C.film.max,this.film+C.film.captureReward);e.destroy();this.updateHud();}}
  update(time,dtMs){
    if(this.dead)return;const dt=Math.min(dtMs/1000,.05),left=touch.left||this.cursors.left.isDown||this.keys.A.isDown,right=touch.right||this.cursors.right.isDown||this.keys.D.isDown,jump=touch.jump||this.cursors.up.isDown||this.keys.W.isDown,beamHeld=touch.beam||this.cursors.space.isDown||this.keys.SPACE.isDown,canBeam=beamHeld&&this.film>0;
    const speed=canBeam?C.player.captureMoveSpeed:C.player.speed;if(left){this.player.setVelocityX(-speed);this.player.setFlipX(true)}else if(right){this.player.setVelocityX(speed);this.player.setFlipX(false)}else this.player.setVelocityX(this.player.body.velocity.x*.72);
    if(Math.abs(this.player.body.velocity.x)>12&&!canBeam)this.player.play('hero-walk',true);else this.player.anims.stop();if(jump&&this.player.body.blocked.down&&!this.jumpLatch&&!canBeam){this.player.setVelocityY(C.player.jumpVelocity);this.jumpLatch=true}if(!jump)this.jumpLatch=false;
    this.enemies.children.iterate(e=>{if(!e?.active)return;const type=e.getData('type'),cfg=C.enemies[type],dx=this.player.x-e.x;if(cfg.floating){e.y=e.getData('baseY')+Math.sin((time+e.x)*.003)*18;if(Math.abs(dx)<560)e.setVelocityX(Phaser.Math.Clamp(dx*.12,-cfg.speed,cfg.speed))}else if(Math.abs(dx)<560)e.setVelocityX(Phaser.Math.Clamp(dx*.2,-cfg.speed,cfg.speed));else e.setVelocityX(0);e.setFlipX(dx<0);});
    this.beam.clear();this.bars.clear();if(canBeam){this.film=Math.max(0,this.film-C.film.drainPerSecond*dt);const dir=this.player.flipX?-1:1,px=this.player.x+dir*38,py=this.player.y-22,range=C.capture.range,spread=C.capture.spread;this.beam.fillStyle(C.capture.beamColor,C.capture.beamAlpha).beginPath().moveTo(px,py).lineTo(px+dir*range,py-spread/2).lineTo(px+dir*range,py+spread/2).closePath().fillPath();this.enemies.children.iterate(e=>{if(!e?.active)return;const dx=(e.x-this.player.x)*dir,dy=Math.abs(e.y-this.player.y);if(dx>0&&dx<range&&dy<spread*.72)this.captureEnemy(e,dt)});}else this.film=Math.min(C.film.max,this.film+C.film.recoverPerSecond*dt);
    this.enemies.children.iterate(e=>{if(!e?.active)return;const c=e.getData('capture')||0;if(c>0){this.bars.fillStyle(0x0b0d13,.85).fillRect(e.x-31,e.y-76,62,7);this.bars.fillStyle(0x9fe8ff,1).fillRect(e.x-29,e.y-74,58*Math.min(1,c),3)}});this.updateHud();
  }
  updateHud(){const el=document.getElementById('status');if(el)el.innerHTML=`GOTHIC HORROR · <span class="life">LIFE ${this.health}</span> · <span class="film">FILM ${Math.round(this.film)}</span> · CAPTURED ${this.captured}/${(C.horror.spawns||[]).length}`;}
}
new Phaser.Game({type:Phaser.AUTO,parent:'game',width:1280,height:720,pixelArt:true,antialias:false,roundPixels:true,physics:{default:'arcade',arcade:{gravity:{y:900},debug:false}},scale:{mode:Phaser.Scale.FIT,autoCenter:Phaser.Scale.CENTER_BOTH},scene:[GothicHorror]});
})();
