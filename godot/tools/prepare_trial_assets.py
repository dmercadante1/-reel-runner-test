"""Deterministic test-only pixel/alpha chart and 100-ms calibration tone, not game art."""
from pathlib import Path
from PIL import Image,ImageDraw
import wave,math,struct,hashlib,json
root=Path(__file__).resolve().parents[1];out=root/'assets';out.mkdir(exist_ok=True)
(root/'evidence').mkdir(exist_ok=True)
im=Image.new('RGBA',(64,64),(0,0,0,0));d=ImageDraw.Draw(im)
colors=['#edca87','#78aec3','#c4786e','#739a80']
for y in range(64):
 for x in range(64):
  if y<24:d.point((x,y),fill=colors[(x//8)%4])
  elif y<44 and (x+y)%2==0:d.point((x,y),fill='#cdd9de')
  elif y>=44 and (x//4+y//4)%2==0:d.point((x,y),fill=(210,200,165,160))
im.save(out/'calibration.png')
with wave.open(str(out/'calibration-tone.wav'),'wb') as w:
 w.setnchannels(1);w.setsampwidth(2);w.setframerate(22050)
 data=[int(14000*math.sin(2*math.pi*(660+i/22050*180)*i/22050)*min(1,i/180)*(1-i/2205)**2) for i in range(2205)]
 w.writeframes(b''.join(struct.pack('<h',v)for v in data))
(root/'evidence/asset-integrity.json').write_text(json.dumps({p.name:{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}for p in out.iterdir()if p.suffix in ['.png','.wav']},indent=2))
