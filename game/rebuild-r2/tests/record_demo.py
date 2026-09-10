from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image
from io import BytesIO
R=Path(__file__).resolve().parents[1]
frames=[]
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
 p=b.new_page(viewport={'width':1280,'height':816});p.set_content((R/'Gothic-Horror-Playable.html').read_text());p.wait_for_function('GOTHIC.phase==="ready"');p.locator('#start').click();p.wait_for_timeout(650)
 p.screenshot(path=str(R/'evidence/actual-gameplay.png'))
 p.keyboard.down('ArrowRight')
 for i in range(6):
  p.wait_for_timeout(110);frames.append(Image.open(BytesIO(p.screenshot())).resize((768,490),Image.Resampling.LANCZOS).convert('RGB'))
 p.keyboard.up('ArrowRight');p.keyboard.down('Space')
 for i in range(14):
  p.wait_for_timeout(100);frames.append(Image.open(BytesIO(p.screenshot())).resize((768,490),Image.Resampling.LANCZOS).convert('RGB'))
 p.keyboard.up('Space');p.keyboard.down('ArrowUp')
 for i in range(6):
  p.wait_for_timeout(110);frames.append(Image.open(BytesIO(p.screenshot())).resize((768,490),Image.Resampling.LANCZOS).convert('RGB'))
 p.keyboard.up('ArrowUp');b.close()
frames[0].save(R/'evidence/actual-gameplay.gif',save_all=True,append_images=frames[1:],duration=130,loop=0,optimize=True)
print('Saved real rendered gameplay recording',len(frames),'frames')
