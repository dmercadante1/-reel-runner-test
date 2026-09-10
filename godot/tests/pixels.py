from pathlib import Path
from PIL import Image
import json
out=Path('godot/evidence');reports=[]
for engine in ['chromium','webkit']:
 im=Image.open(out/f'{engine}-canvas-2x.png').convert('RGB')
 assert im.size==(1280,720),im.size
 colors=[(237,202,135),(120,174,195),(196,120,110),(115,154,128)]
 for i,c in enumerate(colors):
  x,y=(512+i*8+2)*2,164*2
  actual=im.getpixel((x,y));assert max(abs(a-b) for a,b in zip(actual,c))<=2,(engine,i,actual,c)
  assert all(im.getpixel((x+dx,y+dy))==actual for dx in [0,1] for dy in [0,1]),'nearest-neighbor 2x blocks'
 # Opaque white checker pixels alternate with transparent background. Semi-transparent swatches blend rather than turn opaque.
 bright=im.getpixel((514*2,186*2));dark=im.getpixel((515*2,186*2));alpha=im.getpixel((514*2,208*2))
 assert sum(bright)>500 and sum(dark)<180,(bright,dark)
 assert 65<alpha[0]<200 and 50<alpha[1]<195,(engine,alpha)
 reports.append({'browser':engine,'passed':True,'size':im.size,'checker':[bright,dark],'alpha':alpha})
(out/'rendered-pixels.json').write_text(json.dumps(reports,indent=2));print(reports)
