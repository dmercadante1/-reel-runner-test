(()=>{
const touch={left:false,right:false,jump:false,beam:false};
class RecoveryScene extends Phaser.Scene{
  constructor(){super('RecoveryScene');this.jumpLatch=false;}
  create(){
    const W=3200,H=720;
    this.physics.world.setBounds(0,0,W,H);
    this.cameras.main.setBounds(0,0,W,H);
    this.cameras.main.setBackgroundColor('#11131a');

    this.add.text(32,28,'RUNTIME OK',{fontFamily:'monospace',fontSize:'34px',fontStyle:'bold',color:'#ffffff',backgroundColor:'#186f35',padding:{x:12,y:8}}).setScrollFactor(0).setDepth(1000);
    this.add.text(32,92,'ASSET-FREE RECOVERY BUILD · MOVE ← → / A D · JUMP ↑ / W',{fontFamily:'monospace',fontSize:'18px',color:'#ffe59a'}).setScrollFactor(0).setDepth(1000);

    for(let x=0;x<W;x+=160){
      const h=120+((x/160)%4)*55;
      this.add.rectangle(x+80,610-h/2,120,h,0x242936,1).setDepth(-10);
      this.add.rectangle(x+80,610-h+18,70,8,0x5f6675,1).setDepth(-9);
    }
    this.add.rectangle(W/2,642,W,156,0x1b1e26,1).setDepth(-8);
    this.add.rectangle(W/2,610,W,6,0xe8d9b0,1).setDepth(-7);

    const floor=this.add.rectangle(W/2,665,W,110,0x000000,0).setVisible(false);
    this.physics.add.existing(floor,true);

    const g=this.make.graphics({x:0,y:0,add:false});
    g.fillStyle(0xffffff,1); g.fillRect(20,2,24,24);
    g.fillStyle(0x66ccff,1); g.fillRect(14,28,36,44);
    g.fillStyle(0xffd166,1); g.fillRect(4,34,10,30); g.fillRect(50,34,10,30);
    g.fillStyle(0xff6b6b,1); g.fillRect(16,72,12,38); g.fillRect(36,72,12,38);
    g.fillStyle(0x000000,1); g.fillRect(23,10,5,5); g.fillRect(36,10,5,5);
    g.generateTexture('diagnosticHero',64,112); g.destroy();

    this.player=this.physics.add.sprite(180,500,'diagnosticHero').setDepth(10).setCollideWorldBounds(true);
    this.player.body.setSize(50,108).setOffset(7,2);
    this.physics.add.collider(this.player,floor);

    this.cursors=this.input.keyboard.createCursorKeys();
    this.keys=this.input.keyboard.addKeys('A,D,W,SPACE');
    this.cameras.main.startFollow(this.player,true,.12,.10,-180,20);
    this.cameras.main.roundPixels=true;
    this.bindTouch();
    this.bindLifecycle();
    const el=document.getElementById('status'); if(el) el.textContent='RUNTIME OK · ASSET-FREE';
  }
  clearInput(){touch.left=touch.right=touch.jump=touch.beam=false;this.jumpLatch=false;if(this.player?.body)this.player.setVelocityX(0);}
  bindLifecycle(){const clear=()=>this.clearInput();window.addEventListener('blur',clear,{passive:true});document.addEventListener('visibilitychange',()=>{if(document.hidden)clear()},{passive:true});window.addEventListener('orientationchange',clear,{passive:true});}
  bindTouch(){document.querySelectorAll('#touch button').forEach(b=>{const k=b.dataset.k;const on=e=>{e.preventDefault();touch[k]=true;b.setPointerCapture?.(e.pointerId)};const off=e=>{e.preventDefault();touch[k]=false};b.addEventListener('pointerdown',on,{passive:false});b.addEventListener('pointerup',off,{passive:false});b.addEventListener('pointercancel',off,{passive:false});b.addEventListener('lostpointercapture',off,{passive:false});});const fs=document.getElementById('fullscreen');if(fs)fs.onclick=()=>document.documentElement.requestFullscreen?.();}
  update(){
    const left=touch.left||this.cursors.left.isDown||this.keys.A.isDown;
    const right=touch.right||this.cursors.right.isDown||this.keys.D.isDown;
    const jump=touch.jump||this.cursors.up.isDown||this.keys.W.isDown||this.keys.SPACE.isDown;
    if(left){this.player.setVelocityX(-235);this.player.setFlipX(true);}
    else if(right){this.player.setVelocityX(235);this.player.setFlipX(false);}
    else this.player.setVelocityX(this.player.body.velocity.x*.72);
    if(jump&&this.player.body.blocked.down&&!this.jumpLatch){this.player.setVelocityY(-430);this.jumpLatch=true;}
    if(!jump)this.jumpLatch=false;
  }
}
new Phaser.Game({type:Phaser.AUTO,parent:'game',width:1280,height:720,pixelArt:true,antialias:false,roundPixels:true,physics:{default:'arcade',arcade:{gravity:{y:900},debug:false}},scale:{mode:Phaser.Scale.FIT,autoCenter:Phaser.Scale.CENTER_BOTH},scene:[RecoveryScene]});
})();