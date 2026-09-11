// Exercises the exact publish candidate through the same input bridge used by touch.
// No privileged state changes, teleport commands, enemy kills, or inventory injection.
const {chromium,webkit}=require('playwright');
const fs=require('fs'),path=require('path'),http=require('http');
const root=path.resolve('preview-candidate/gothic-chapter-01'),out=path.resolve('godot/evidence');
let active='unknown';fs.mkdirSync(out,{recursive:true});
const server=http.createServer((req,res)=>{
 const route=req.url.split('?')[0];
 if(req.method==='POST'&&/^\/capture\/[a-z0-9-]+\.(png|json|webm)$/.test(route)){
  const chunks=[];req.on('data',b=>chunks.push(b));req.on('end',()=>{fs.writeFileSync(path.join(out,active+'-'+path.basename(route)),Buffer.concat(chunks));res.end('saved')});return;
 }
 const name=route==='/'?'index.html':route.slice(1);
 if(!/^[a-z0-9.\-]+$/.test(name)||!fs.existsSync(path.join(root,name))){res.writeHead(404);return res.end()}
 res.setHeader('Content-Type',name.endsWith('.wasm')?'application/wasm':name.endsWith('.js')?'text/javascript':name.endsWith('.html')?'text/html':'application/octet-stream');res.end(fs.readFileSync(path.join(root,name)));
});
(async()=>{await new Promise(r=>server.listen(8767,'127.0.0.1',r));let failed=0;
for(const [name,type] of Object.entries({chromium,webkit})){
 active=name;const report={browser:name,checks:[],errors:[],physical_iphone_tested:false,touch_method:'DOM pointer events; not hardware multi-touch'};let browser,page;
 const check=(name,ok,detail)=>{report.checks.push({name,passed:!!ok,detail});if(!ok)throw Error(name)};
 try{
 browser=await type.launch();page=await browser.newPage({viewport:{width:1304,height:1000},hasTouch:true});
 page.on('pageerror',e=>report.errors.push(String(e)));page.on('console',m=>{if(m.type()==='error')report.errors.push(m.text())});
 await page.goto('http://127.0.0.1:8767');
 const until=fn=>page.waitForFunction(fn,null,{timeout:90000}),s=()=>page.evaluate(()=>M1Bridge.state),wait=ms=>page.waitForTimeout(ms),act=(n,v=true)=>page.evaluate(([n,v])=>M1Bridge.send(n,v),[n,v]);
 await until(()=>M1Bridge.state?.phase==='ready');check('1080p chapter loaded',(await s()).viewport.join(',')==='1920,1080'&&(await s()).room_count===9);
 await page.locator('#start').click();await until(()=>M1Bridge.state.grounded);await wait(300);
 const canvasPixels=async()=>require('pngjs').PNG.sync.read(Buffer.from((await page.locator('#canvas').evaluate(c=>c.toDataURL('image/png'))).split(',')[1],'base64'));
 const firstPixels=await canvasPixels();
 await page.keyboard.down('ArrowRight');await wait(250);await page.keyboard.up('ArrowRight');await wait(180);check('Desktop movement releases',(await s()).x>85&&Math.abs((await s()).vx)<1);
 await page.keyboard.down('Space');await wait(350);await page.keyboard.up('Space');await wait(100);check('Film spends active reel',(await s()).film<12);
 await page.keyboard.press('r');await wait(180);check('Reload spends one spare',(await s()).reload_left>0&&(await s()).spares===1);await wait(700);check('Reload restores full film',(await s()).film===12);
 await page.keyboard.press('x');await wait(160);check('No unearned Super Shot',(await s()).super_charges===0&&(await s()).super_left===0);
 await act('pause');await wait(100);const before=await s();await wait(250);check('Pause freezes chapter and enemy',(await s()).chapter_seconds===before.chapter_seconds&&(await s()).enemies[0].clock===before.enemies[0].clock);await act('resume');
 await page.locator('#motion').click();check('Reduced motion has visible state',(await page.locator('#motion').textContent())==='Motion reduced');await page.locator('#motion').click();
 await page.addScriptTag({path:'godot/tests/chapter_playthrough.js'});await page.locator('#chapter-run').click();
 await page.waitForFunction(()=>window.__chapterResult,null,{timeout:600000});report.playthrough=await page.evaluate(()=>window.__chapterResult);
 check('All nine rooms captured and exited',report.playthrough.passed&&report.playthrough.checks.filter(c=>c.name.startsWith("Room ")).length===18,report.playthrough);
 check('Dracula captured',(await s()).phase==='chapter_complete'&&(await s()).enemies[0].phase==='captured');
 await page.reload();await until(()=>M1Bridge.state?.phase==='ready');check('Checkpoint survives browser reload',(await s()).room===8);
 await page.locator('#new-game').click();await until(()=>M1Bridge.state.room===0&&M1Bridge.state.grounded);check('New chapter resets progress',(await s()).super_charges===0&&(await s()).health===4);await wait(400);
 const resetPixels=await canvasPixels();let same=0,total=0;for(let y=400;y<500;y++)for(let x=300;x<600;x++){const i=(y*1920+x)*4;total++;if(firstPixels.data.readUInt32BE(i)===resetPixels.data.readUInt32BE(i))same++;}check('New chapter redraws the Courtyard background',same/total>.999,{same,total});
 await page.setViewportSize({width:844,height:390});await wait(200);
 await page.locator('[data-action]').evaluateAll(bs=>bs.forEach(b=>b.setPointerCapture=()=>{}));
 const pointer=async(n,id,down)=>page.locator(`[data-action="${n}"]`).dispatchEvent(down?'pointerdown':'pointerup',{pointerId:id,pointerType:'touch',bubbles:true});
 await pointer('move_right',1,true);await pointer('record',2,true);await wait(240);await pointer('move_right',1,false);await wait(100);check('Touch release preserves other held action',(await s()).recording&&!(await s()).actions.move_right);await pointer('record',2,false);
 await pointer('reload',3,true);await pointer('reload',3,false);await wait(800);check('Touch reload works',(await s()).film===12&&(await s()).spares===1);
 for(const [w,h] of [[844,390],[390,844],[1920,1080]]){await page.setViewportSize({width:w,height:h});await wait(180);check(`Layout ${w}x${h}`,await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));await page.screenshot({path:path.join(out,`chapter-${name}-${w}x${h}.png`),fullPage:true})}
 await page.setViewportSize({width:844,height:390});await page.locator('#fullscreen').click();await wait(300);check('Screen-filling view preserves aspect',await page.evaluate(()=>{const r=canvas.getBoundingClientRect();return document.body.classList.contains('immersive')&&r.height>380&&Math.abs(r.width/r.height-16/9)<.01}));
 await page.locator('#screen-controls').click();check('Controls can hide',!(await page.locator('#touch').isVisible()));await page.locator('#screen-controls').click();await page.locator('#screen-exit').click();
 await page.evaluate(()=>document.getElementById('frame').requestFullscreen=undefined);await page.locator('#fullscreen').click();check('Safari fullscreen fallback available',await page.locator('#screen-hint').isVisible());await page.locator('#screen-exit').click();
 await page.evaluate(()=>window.dispatchEvent(new Event('orientationchange')));await wait(150);check('Rotation pauses and releases inputs',(await s()).phase==='paused'&&!(await s()).recording);
 check('No script or engine console errors',report.errors.length===0,report.errors);report.passed=true;
 }catch(e){report.passed=false;report.failure=String(e);failed++;if(page)await page.screenshot({path:path.join(out,`chapter-${name}-failure.png`)}).catch(()=>{});}finally{if(browser)await browser.close();fs.writeFileSync(path.join(out,`chapter-${name}.json`),JSON.stringify(report,null,2));console.log(JSON.stringify(report));}
}
server.close();process.exitCode=failed?1:0;
})().catch(e=>{server.close();console.error(e);process.exitCode=1});
