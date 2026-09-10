'use strict';
window.GOTHIC_HUD={
 create(s){const fixed=o=>o.setScrollFactor(0).setDepth(1000),g=fixed(s.add.graphics());s.hudGraphics=g;s.hudCache='';
 g.fillStyle(0x06101b,.93).fillRect(0,0,640,47);g.lineStyle(1,0x8e7b51,.95).strokeRect(2,2,636,42);g.lineStyle(1,0x394451,1).strokeRect(4,4,632,38);for(const x of[2,632]){g.fillStyle(0xd0b77b).fillRect(x,2,6,2).fillRect(x,2,2,6).fillRect(x,38,2,6).fillRect(x,42,6,2);}
 s.hudHearts=[];for(let i=0;i<5;i++)s.hudHearts.push(fixed(s.add.image(46+i*14,15,'heart').setScale(1.15)));
 const text=(x,y,t,size=8,color='#d7c8a2')=>fixed(s.add.text(x,y,t,{fontFamily:'monospace',fontSize:size+'px',color}));
 text(10,10,'LIFE');text(10,29,'FILM');s.hudFilm=text(163,28,'100',8,'#c4efff');s.hudCapture=text(210,11,'ON FILM 0/3',9);s.hudTotal=text(210,28,'TOTAL 00/12',8,'#8394a3');s.hudStage=text(333,10,'01 / 04',8,'#adc4d4');s.hudName=text(333,26,s.stage.name,8,'#eee0b8');s.hudFlash=text(500,11,s.edition===4?'FLASH READY':'CAMERA',8,'#acdcf1');s.hudSave=text(500,28,'ENTRY SAVED',7,'#829b9c');
 const pause=fixed(s.add.text(598,14,'Ⅱ',{fontFamily:'monospace',fontSize:'15px',color:'#d9c38d'})).setInteractive({useHandCursor:true});pause.on('pointerdown',()=>GOTHIC.pause('manual',true));const full=fixed(s.add.text(620,14,'□',{fontFamily:'monospace',fontSize:'14px',color:'#d9c38d'})).setInteractive({useHandCursor:true});full.on('pointerdown',()=>GOTHIC.fullscreen());
 s.hudGauge=fixed(s.add.graphics());s.hudBottom=text(320,350,s.edition===4?'X / SHIFT: FLASH DEFENSE    •    JUMP LOW ATTACKS':'HOLD SPACE / C TO FILM    •    CAPTURE ALL TO OPEN THE GATE',7,'#b1bfcc').setOrigin(.5,1).setBackgroundColor('#06101be0').setPadding(5,3);
 s.hudToast=text(320,63,'',9,'#e8dcba').setOrigin(.5,0);s.hudStage.setText(String(s.stageIndex+1).padStart(2,'0')+' / 04    GOTHIC HORROR');
 },
 render(s){const life=s.health,film=Math.round(s.film),cap=s.captured,flash=s.edition===4?(Math.max(0,s.flashUntil-s.clock)/1000).toFixed(1):'-',key=[life,film,cap,s.total,s.checkpoint,flash].join(':');if(key===s.hudCache)return;s.hudCache=key;
 s.hudHearts.forEach((h,i)=>h.setAlpha(i<life?1:.22));s.hudFilm.setText(String(film).padStart(3,'0'));s.hudCapture.setText('ON FILM '+cap+'/'+s.stage.enemies.length);s.hudTotal.setText('TOTAL '+String(s.total).padStart(2,'0')+'/12');s.hudSave.setText(s.checkpoint>110?'CHECKPOINT ✓':'ENTRY SAVED');
 s.hudFlash.setText(s.edition===4?(flash>0?'FLASH '+flash+'s':s.film<18?'FLASH: LOW':'FLASH READY'):'CAMERA READY');
 const g=s.hudGauge;g.clear();g.lineStyle(1,0x747c80).strokeRect(40,25,116,13);g.fillStyle(0x09121d).fillRect(41,26,114,11);g.fillStyle(film<20?0xc17a5c:0x9bd7ee).fillRect(43,28,110*film/100,7);for(let x=42;x<155;x+=8){g.fillStyle(0x050c12).fillRect(x,26,3,2).fillRect(x,35,3,2);}
 const status='Stage '+(s.stageIndex+1)+': '+s.stage.name+'. Life '+life+' of 5. Captured '+cap+' of '+s.stage.enemies.length+'. Total '+s.total+' of 12.';if(status!==s.lastStatus){document.getElementById('status').textContent=status;s.lastStatus=status;}
 }
};
