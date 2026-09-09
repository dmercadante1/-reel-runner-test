(()=>{
const touch={left:false,right:false,jump:false,beam:false};
class RecoveryScene extends Phaser.Scene{
  constructor(){super('RecoveryScene');this.jumpLatch=false;}
  preload(){
    this.load.on('loaderror',file=>{const el=document.getElementById('status');if(el)el.textContent='ASSET ERROR: '+(file?.key||'UNKNOWN');});
    this.load.spritesheet('hero','./assets/production/characters/hero_walk.png?v=recovery-1',{frameWidth:128,frameHeight:128});
    this.load.image('playPlane','./assets/production/environments/gothic_playplane.png?v=recovery-1');
  }
  create(){
    const W=4300,H=720;
    this.physics.world.setBounds(0,0,W,H);
    this.cameras.main.setBounds(0,0,W,H);
    this.cameras.main.setBackgroundColor('#07080c');

    // Safe diagnostic backdrop. The verified play-plane strip is decorative only.
    this.add.rectangle(W/2,330,W,660,0x0a0b11,1).setDepth(-20);
    for(let x=0;x<W;x+=1024){
      if(this.textures.exists('playPlane')){
        const bg=this.add.image(x,620,'playPlane').setOrigin(0,1).setDepth(-10).setScale(2,2);
        bg.texture.setFilter(Phaser.Textures.FilterMode.NEAREST);
      }
    }
    this.add.rectangle(W/2,642,W,156,0x101116,1).setDepth(-8);
    this.add.rectangle(W/2,610,W,4,0x574d45,1).setDepth(-7);

    const floor=this.add.rectangle(W/2,665,W,110,0x000000,0).setVisible(false);
    this.physics.add.existing(floor,true);

    this.anims.create({key:'hero-walk',frames:this.anims.generateFrameNumbers('hero',{start:0,end:7}),frameRate:10,repeat:-1});
    this.player=this.physics.add.sprite(180,500,'hero',0).setScale(.82).setDepth(10).setCollideWorldBounds(true);
    this.player.body.setSize(46,104).setOffset(41,20);
    this.physics.add.collider(this.player,floor);

    this.cursors=this.input.keyboard.createCursorKeys();
    this.keys=this.input.keyboard.addKeys('A,D,W,SPACE');
    this.cameras.main.startFollow(this.player,true,.12,.10,-180,20);
    this.cameras.main.roundPixels=true;

    this.bindTouch();
    this.bindLifecycle();
    this.setStatus('RUNTIME OK · MOVE: ← → / A D · JUMP: ↑ / W');
  }
  setStatus(msg){const el=document.getElementById('status');if(el)el.textContent=msg;}
  clearInput(){touch.left=touch.right=touch.jump=touch.beam=false;this.jumpLatch=false;if(this.player?.body)this.player.setVelocityX(0);}
  bindLifecycle(){const clear=()=>this.clearInput();window.addEventListener('blur',clear,{passive:true});document.addEventListener('visibilitychange',()=>{if(document.hidden)clear()},{passive:true});window.addEventListener('orientationchange',clear,{passive:true});}
  bindTouch(){document.querySelectorAll('#touch button').forEach(b=>{const k=b.dataset.k;const on=e=>{e.preventDefault();touch[k]=true;b.setPointerCapture?.(e.pointerId)};const off=e=>{e.preventDefault();touch[k]=false};b.addEventListener('pointerdown',on,{passive:false});b.addEventListener('pointerup',off,{passive:false});b.addEventListener('pointercancel',off,{passive:false});b.addEventListener('lostpointercapture',off,{passive:false});});const fs=document.getElementById('fullscreen');if(fs)fs.onclick=()=>document.documentElement.requestFullscreen?.();}
  update(){
    const left=touch.left||this.cursors.left.isDown||this.keys.A.isDown;
    const right=touch.right||this.cursors.right.isDown||this.keys.D.isDown;
    const jump=touch.jump||this.cursors.up.isDown||this.keys.W.isDown;
    if(left){this.player.setVelocityX(-235);this.player.setFlipX(true);this.player.play('hero-walk',true);}
    else if(right){this.player.setVelocityX(235);this.player.setFlipX(false);this.player.play('hero-walk',true);}
    else {this.player.setVelocityX(this.player.body.velocity.x*.72);this.player.anims.stop();this.player.setFrame(0);}
    if(jump&&this.player.body.blocked.down&&!this.jumpLatch){this.player.setVelocityY(-430);this.jumpLatch=true;}
    if(!jump)this.jumpLatch=false;
  }
}
new Phaser.Game({type:Phaser.AUTO,parent:'game',width:1280,height:720,pixelArt:true,antialias:false,roundPixels:true,physics:{default:'arcade',arcade:{gravity:{y:900},debug:false}},scale:{mode:Phaser.Scale.FIT,autoCenter:Phaser.Scale.CENTER_BOTH},scene:[RecoveryScene]});
})();