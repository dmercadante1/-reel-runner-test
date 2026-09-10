'use strict';
window.GOTHIC_CONFIG={
 build:'gothic-stages-r3',edition:3,width:640,height:360,floorY:316,
 hero:{speed:151,filmSpeed:80,acceleration:1300,drag:1600,jump:-370,gravity:880,health:5,coyoteMs:95,jumpBufferMs:125,hurtMs:260,invulnerabilityMs:1150},
 film:{max:100,drain:10.5,recover:16,emptyLockMs:650,reward:12,flashCost:18,flashCooldown:1300},
 capture:{range:247,halfHeight:75,pullSpeed:125,releaseDecay:.12},
 enemies:{
 skeleton:{speed:27,resistance:1.1,attack:'bone',windup:650,cooldown:2200,range:315},
 ghoul:{speed:34,resistance:1.35,attack:'lunge',windup:560,cooldown:2050,range:158},
 vampire:{speed:30,resistance:1.55,attack:'bolt',windup:720,cooldown:2250,range:330},
 ghost:{speed:30,resistance:1.4,attack:'phase',windup:650,cooldown:2500,range:310,floating:true},
 monster:{speed:22,resistance:2,attack:'slam',windup:820,cooldown:2850,range:305},
 werewolf:{speed:48,resistance:1.7,attack:'leap',windup:580,cooldown:2400,range:310}
 },
 stages:[
 {id:'courtyard',name:'MOONLIT COURTYARD',subtitle:'The gate is open.',worldWidth:1560,background:'courtyard',scroll:.22,exit:{x:1460,top:316},checkpoint:850,
 platforms:[{x:590,top:264,width:132},{x:723,top:212,width:108}],pickups:[{x:720,y:186,kind:'film'}],
 enemies:[['skeleton',445],['ghoul',877],['vampire',1270]],palette:0x7694ae},
 {id:'cathedral',name:'THE CATHEDRAL',subtitle:'Beneath the stained glass.',worldWidth:1750,background:'cathedral',scroll:.78,exit:{x:1640,top:316},checkpoint:870,
 platforms:[{x:470,top:268,width:126},{x:596,top:216,width:120},{x:765,top:216,width:105,motion:{axis:'x',distance:60,speed:32}},{x:920,top:166,width:154},{x:1360,top:270,width:120},{x:1480,top:222,width:164}],pickups:[{x:914,y:142,kind:'heart'}],
 enemies:[['ghost',420],['skeleton',970],['vampire',1370]],palette:0xcc8a55},
 {id:'catacombs',name:'THE CATACOMBS',subtitle:'Something moves below.',worldWidth:1700,background:'catacombs',scroll:.7,exit:{x:1590,top:316},checkpoint:1010,
 platforms:[{x:520,top:264,width:136},{x:659,top:218,width:100,crumble:true},{x:780,top:264,width:105,motion:{axis:'x',distance:55,speed:31}},{x:940,top:268,width:128},{x:1310,top:258,width:120}],pickups:[{x:660,y:195,kind:'film'}],
 enemies:[['ghoul',412],['monster',1080],['skeleton',1420]],palette:0x7e859c},
 {id:'ramparts',name:'MOONLIT RAMPARTS',subtitle:'One last roll before dawn.',worldWidth:1800,background:'ramparts',scroll:.2,exit:{x:1700,top:316},checkpoint:950,
 platforms:[{x:455,top:266,width:124},{x:590,top:220,width:126},{x:732,top:264,width:128,motion:{axis:'y',distance:62,speed:28}},{x:935,top:204,width:166},{x:1340,top:266,width:130},{x:1480,top:212,width:146}],pickups:[{x:931,y:178,kind:'heart'},{x:1480,y:186,kind:'film'}],
 enemies:[['werewolf',450],['vampire',1090],['monster',1460]],palette:0xabc7de}
 ]
};
