const { chromium, webkit } = require('playwright');
const fs = require('node:fs');
const path = require('node:path');
const http = require('node:http');
const crypto = require('node:crypto');
const root = process.cwd();
fs.mkdirSync('audit-results', { recursive: true });
const types = { '.js': 'text/javascript', '.css': 'text/css', '.html': 'text/html', '.png': 'image/png' };
const server = http.createServer((req, res) => {
  const name = decodeURIComponent(new URL(req.url, 'http://localhost').pathname);
  const file = path.resolve(root, '.' + (name.endsWith('/') ? name + 'index.html' : name));
  if (!file.startsWith(root + path.sep)) { res.writeHead(403).end(); return; }
  try { res.setHeader('Content-Type', types[path.extname(file)] || 'application/octet-stream'); res.end(fs.readFileSync(file)); }
  catch { res.writeHead(404).end(); }
});
const intercept = `Object.defineProperty(window,'Phaser',{configurable:true,set(P){const Game=P.Game;P.Game=new Proxy(Game,{construct(T,args){const g=Reflect.construct(T,args);window.__auditGame=g;return g}});Object.defineProperty(window,'Phaser',{value:P,writable:true,configurable:true})}});`;
(async () => {
  await new Promise(r => server.listen(8099, '127.0.0.1', r));
  const results = [];
  for (const [engine, type] of [['chromium', chromium], ['webkit', webkit]]) {
    const browser = await type.launch({ headless: true });
    for (const [label, url] of [
      ['live-root', 'https://dmercadante1.github.io/-reel-runner-test/'],
      ['live-fresh', 'https://dmercadante1.github.io/-reel-runner-test/game/play.html?audit=' + Date.now()],
      ['local-unchanged', 'http://127.0.0.1:8099/game/play.html']
    ]) {
      const page = await browser.newPage({ viewport: { width: 1216, height: 1242 } });
      await page.addInitScript(intercept);
      const record = { engine, label, requestedUrl: url, errors: [], requests: [], logs: [] };
      page.on('pageerror', e => record.errors.push(e.stack || e.message));
      page.on('console', m => { if (m.type() !== 'log') record.logs.push(m.type() + ': ' + m.text()); });
      page.on('response', async r => {
        record.requests.push({ url: r.url(), status: r.status() });
        if (/phaser.*\.js/.test(r.url())) {
          try { const b = await r.body(); fs.writeFileSync('audit-results/phaser.min.js', b); record.phaserSha256 = crypto.createHash('sha256').update(b).digest('hex'); } catch {}
        }
      });
      try {
        await page.goto(url, { waitUntil: 'networkidle', timeout: 45000 });
        await page.waitForTimeout(1500);
        record.finalUrl = page.url();
        record.html = await page.content();
        record.stateBefore = await page.evaluate(() => {
          const g = window.__auditGame, s = g?.scene.getScenes(true)[0], c = document.querySelector('canvas');
          const rect = e => e ? JSON.parse(JSON.stringify(e.getBoundingClientRect())) : null;
          return { status: document.getElementById('status')?.textContent, version: window.Phaser?.VERSION,
            canvas: c && { width:c.width,height:c.height,rect:rect(c),style:c.getAttribute('style') }, parent:rect(document.getElementById('game')),
            renderer:g?.renderer.type, scene:s?.sys.settings.key,
            player:s?.player && {x:s.player.x,y:s.player.y,width:s.player.width,height:s.player.height,visible:s.player.visible,alpha:s.player.alpha,depth:s.player.depth,texture:s.player.texture.key,frame:s.player.frame.name},
            camera:s?.cameras.main && {x:s.cameras.main.scrollX,y:s.cameras.main.scrollY,zoom:s.cameras.main.zoom},
            objects:s?.children.list.map(o=>({type:o.type,x:o.x,y:o.y,visible:o.visible,depth:o.depth,text:o.text,texture:o.texture?.key})) };
        });
        await page.screenshot({path:'audit-results/' + engine + '-' + label + '-before.png'});
        await page.keyboard.down('ArrowRight'); await page.waitForTimeout(650); await page.keyboard.up('ArrowRight');
        await page.keyboard.down('ArrowUp'); await page.waitForTimeout(200); await page.keyboard.up('ArrowUp');
        record.stateAfter = await page.evaluate(() => { const s=window.__auditGame?.scene.getScenes(true)[0];return s?.player && {x:s.player.x,y:s.player.y,velocity:{x:s.player.body.velocity.x,y:s.player.body.velocity.y}}; });
        await page.screenshot({path:'audit-results/' + engine + '-' + label + '-after.png'});
      } catch (e) { record.errors.push(String(e)); }
      results.push(record); await page.close();
    }
    await browser.close();
  }
  fs.writeFileSync('audit-results/browser.json', JSON.stringify(results, null, 2));
  console.log(JSON.stringify(results.map(({html, ...r}) => r), null, 2));
  server.close();
})().catch(e => { console.error(e); server.close(); process.exitCode = 1; });
