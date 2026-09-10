'use strict';
window.GOTHIC_CONFIG = Object.freeze({
  build:'gothic-hud-r2', width:640, height:360, worldWidth:2800, floorY:316,
  hero:{speed:144,filmSpeed:72,acceleration:1300,drag:1600,jump:-350,gravity:880,health:5,coyoteMs:75,jumpBufferMs:110,hurtMs:280,invulnerabilityMs:1100},
  film:{max:100,drain:12,recover:14,emptyLockMs:600,reward:11},
  capture:{range:240,halfHeight:78,pullSpeed:110,releaseDecay:.15},
  enemies:{skeleton:{speed:25,resistance:1,attackMs:240,cooldown:1200},ghoul:{speed:31,resistance:1.3,attackMs:260,cooldown:1300},vampire:{speed:39,resistance:1.5,attackMs:230,cooldown:1050},monster:{speed:21,resistance:2,attackMs:340,cooldown:1500},werewolf:{speed:49,resistance:1.6,attackMs:200,cooldown:1100},ghost:{speed:29,resistance:1.2,attackMs:290,cooldown:1250,floating:true}},
  spawns:[['skeleton',450],['ghoul',850],['vampire',1260],['ghost',1650],['monster',2060],['werewolf',2490]],
  checkpointX:1440, exitX:2710,
  platforms:[{x:700,top:263,width:140},{x:817,top:220,width:100}]
});
