'use strict';
// All positions use the same 640x360 world units. Render density does not alter physics.
window.GOTHIC_CONFIG={
 build:'gothic-r5',edition:5,width:640,height:360,renderScale:2,floorY:316,spawnX:190,
 hero:{speed:158,filmSpeed:84,acceleration:1300,drag:1600,jump:-386,gravity:880,health:5,coyoteMs:110,jumpBufferMs:150,hurtMs:260,invulnerabilityMs:1150},
 film:{max:100,drain:12,recover:.8,recoverDelay:3200,recoveryCap:24,emptyLockMs:900,reward:4,flashCost:20,flashCooldown:1700,pickup:25,checkpoint:20,respawn:60},
 capture:{range:247,halfHeight:75,pullSpeed:125,releaseDecay:.16},
 enemies:{
 skeleton:{speed:29,resistance:1.15,attack:'bone',windup:620,cooldown:2100,range:315},
 ghoul:{speed:37,resistance:1.4,attack:'lunge',windup:540,cooldown:1980,range:158},
 vampire:{speed:33,resistance:1.65,attack:'bolt',windup:670,cooldown:2150,range:330},
 ghost:{speed:33,resistance:1.5,attack:'phase',windup:640,cooldown:2350,range:310,floating:true},
 monster:{speed:24,resistance:2.1,attack:'slam',windup:800,cooldown:2700,range:305},
 werewolf:{speed:51,resistance:1.8,attack:'leap',windup:560,cooldown:2280,range:310}
 },
 stages:[
 {id:'courtyard',name:'MOONLIT COURTYARD',subtitle:'The broken causeway.',worldWidth:2530,background:'courtyard',scroll:.26,exit:{x:2440,top:316},checkpoint:1950,
 gaps:[[1460,1870]],ferry:{x:1665,top:260,width:106,motion:{axis:'x',distance:157,speed:62}},
 platforms:[{x:555,top:264,width:140},{x:680,top:215,width:128},{x:1100,top:258,width:132}],
 pickups:[{x:270,y:280,kind:'film'},{x:680,y:190,kind:'film'},{x:1370,y:280,kind:'film'},{x:2150,y:280,kind:'film'}],
 enemies:[['skeleton',482],['ghoul',765],['skeleton',1030],['vampire',1260],['ghoul',2110],['werewolf',2310]],palette:0x90b6ce},
 {id:'cathedral',name:'THE CATHEDRAL',subtitle:'The suspended nave.',worldWidth:2940,background:'cathedral',scroll:.77,exit:{x:2800,top:222},checkpoint:1950,
 gaps:[[1480,1860]],ferry:{x:1670,top:254,width:106,motion:{axis:'x',distance:145,speed:56}},
 platforms:[{x:500,top:262,width:130},{x:635,top:208,width:125},{x:1030,top:260,width:140},{x:2460,top:270,width:135},{x:2590,top:222,width:156},{x:2750,top:222,width:252}],
 pickups:[{x:270,y:280,kind:'film'},{x:635,y:182,kind:'film'},{x:1390,y:280,kind:'film'},{x:2010,y:280,kind:'film'},{x:2590,y:194,kind:'heart'}],
 enemies:[['ghost',500],['skeleton',780],['ghoul',985],['vampire',1250],['ghost',2090],['skeleton',2260],['ghoul',2460],['vampire',2690]],palette:0xe5a360},
 {id:'catacombs',name:'THE CATACOMBS',subtitle:'A ferry above the dead.',worldWidth:3100,background:'catacombs',scroll:.72,exit:{x:3000,top:316},checkpoint:2000,
 gaps:[[1430,1900]],ferry:{x:1665,top:264,width:112,motion:{axis:'x',distance:190,speed:60}},
 platforms:[{x:490,top:265,width:145},{x:640,top:213,width:112,crumble:true},{x:835,top:218,width:154},{x:1150,top:264,width:136},{x:2470,top:260,width:142}],
 pickups:[{x:270,y:280,kind:'film'},{x:835,y:193,kind:'film'},{x:1340,y:280,kind:'film'},{x:2190,y:280,kind:'film'},{x:2470,y:233,kind:'heart'}],
 enemies:[['ghoul',515],['skeleton',775],['monster',1070],['ghoul',1245],['skeleton',2160],['monster',2390],['ghost',2680],['werewolf',2900]],palette:0x8291ac},
 {id:'ramparts',name:'MOONLIT RAMPARTS',subtitle:'The last crossing.',worldWidth:3420,background:'ramparts',scroll:.25,exit:{x:3310,top:316},checkpoint:2250,
 gaps:[[1660,2170]],ferry:{x:1915,top:260,width:120,motion:{axis:'x',distance:210,speed:68}},
 platforms:[{x:565,top:266,width:142},{x:720,top:216,width:150},{x:1020,top:260,width:132,motion:{axis:'y',distance:58,speed:27}},{x:1210,top:205,width:162},{x:2720,top:264,width:144},{x:2870,top:211,width:146}],
 pickups:[{x:270,y:280,kind:'film'},{x:720,y:192,kind:'film'},{x:1210,y:179,kind:'heart'},{x:1560,y:280,kind:'film'},{x:2360,y:280,kind:'film'},{x:2870,y:186,kind:'film'}],
 enemies:[['werewolf',520],['skeleton',810],['vampire',1140],['monster',1420],['ghoul',2410],['vampire',2660],['werewolf',2930],['monster',3180]],palette:0xabcde8}
 ]
};
GOTHIC_CONFIG.totalEncounters=GOTHIC_CONFIG.stages.reduce((n,s)=>n+s.enemies.length,0);
