'use strict';
(async()=>{
 const G=GOTHIC_CONFIG?GOTHIC:null,C=GOTHIC_CONFIG;
 try{
  if(!window.Phaser)throw Error('Engine unavailable.');
  for(const a of GOTHIC_ASSETS){
   const bytes=Uint8Array.from(atob(a.data.split(',')[1]),c=>c.charCodeAt(0));
   if(bytes.length!==a.bytes)throw Error('Incomplete artwork '+a.key);
   if(crypto.subtle){const hash=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))).map(x=>x.toString(16).padStart(2,'0')).join('');if(hash!==a.sha256)throw Error('Artwork checksum mismatch '+a.key);}
  }
  // A browser may expose WebGL through a very slow software rasterizer. Use the
  // same full-resolution art and game logic through Canvas in that case only.
  let renderer=Phaser.AUTO,probe=null;
  G.rendererSelection={mode:'auto',reason:'Accelerated graphics available'};
  try{
   const canvas=document.createElement('canvas');
   probe=canvas.getContext('webgl',{failIfMajorPerformanceCaveat:true,antialias:false});
   if(!probe){renderer=Phaser.CANVAS;G.rendererSelection={mode:'canvas',reason:'No accelerated WebGL context'};}
   else{
    const ext=probe.getExtension('WEBGL_debug_renderer_info');
    const name=ext?String(probe.getParameter(ext.UNMASKED_RENDERER_WEBGL)):'';
    if(/swiftshader|llvmpipe|softpipe|software rasterizer|microsoft basic render/i.test(name)){
     renderer=Phaser.CANVAS;G.rendererSelection={mode:'canvas',reason:'Software WebGL fallback'};
    }
   }
  }catch{renderer=Phaser.CANVAS;G.rendererSelection={mode:'canvas',reason:'Graphics capability probe unavailable'};}
  finally{try{probe?.getExtension('WEBGL_lose_context')?.loseContext();}catch{}}
  G.layout();
  G.game=new Phaser.Game({type:renderer,parent:'game',width:G.viewWidth*C.renderScale,height:360*C.renderScale,pixelArt:true,antialias:false,roundPixels:true,disableContextMenu:true,physics:{default:'arcade',arcade:{gravity:{y:C.hero.gravity},debug:false}},scale:{mode:Phaser.Scale.FIT,autoCenter:Phaser.Scale.CENTER_BOTH},scene:[GOTHIC_SCENE]});
 }catch(e){G.fail(e.message);}
})();
