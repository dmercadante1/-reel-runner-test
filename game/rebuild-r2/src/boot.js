'use strict';
(async()=>{
 const G=GOTHIC;document.getElementById('build').textContent='BUILD R2';
 try{
  if(typeof Phaser==='undefined')throw Error('Game engine did not load.');
  // Validate every byte before Phaser sees a texture. Never continue with a bad PNG.
  for(const a of GOTHIC_ASSETS){const base=a.data.split(',')[1],raw=Uint8Array.from(atob(base),c=>c.charCodeAt(0));if(raw.length!==a.bytes)throw Error('Incomplete asset: '+a.key);
   if(crypto.subtle){const digest=await crypto.subtle.digest('SHA-256',raw),hex=[...new Uint8Array(digest)].map(v=>v.toString(16).padStart(2,'0')).join('');if(hex!==a.sha256)throw Error('Asset integrity check failed: '+a.key);}
  }
  const C=GOTHIC_CONFIG;G.game=new Phaser.Game({type:Phaser.AUTO,parent:'game',width:C.width,height:C.height,backgroundColor:'#09101a',pixelArt:true,antialias:false,roundPixels:true,disableContextMenu:true,render:{mipmapFilter:'NEAREST'},physics:{default:'arcade',arcade:{gravity:{y:C.hero.gravity},debug:false}},scale:{mode:Phaser.Scale.FIT,autoCenter:Phaser.Scale.CENTER_BOTH},scene:[GOTHIC_SCENE]});
 }catch(e){G.fail(e.message);}
})();
