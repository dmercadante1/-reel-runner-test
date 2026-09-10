from playwright.sync_api import sync_playwright
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
 page=b.new_page(viewport={'width':1280,'height':816});errors=[];logs=[]
 page.on('pageerror',lambda e:errors.append(str(e)));page.on('console',lambda m:logs.append(m.type+':'+m.text) if m.type in ['error','warning'] else None)
 page.set_content((ROOT/'Gothic-Horror-Playable.html').read_text(),wait_until='load');page.wait_for_timeout(1400)
 print(page.evaluate('({phase:GOTHIC.phase,errors:GOTHIC.errors,text:document.getElementById("overlay-copy").textContent})'))
 page.screenshot(path=str(ROOT/'evidence/title-screen.png'))
 page.locator('#start').click();page.wait_for_timeout(700)
 page.screenshot(path=str(ROOT/'evidence/actual-gameplay.png'))
 print('errors',errors,'logs',logs[-10:]);print(page.evaluate('({phase:GOTHIC.phase,player:{x:GOTHIC.scene.player.x,y:GOTHIC.scene.player.y},tick:GOTHIC.scene.tick})'))
 b.close()
