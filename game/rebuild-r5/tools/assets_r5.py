"""High-density raster production from intact, already-approved artwork.
No generated substitute characters. World and collision units remain unchanged.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageEnhance,ImageFilter
import numpy as np,json,hashlib,shutil
R=Path(__file__).resolve().parents[1];B=R.parent/'rebuild-r34';A=R/'assets';A.mkdir(exist_ok=True)
for folder in ['vendor','sources']:
 shutil.copytree(B/folder,R/folder,dirs_exist_ok=True)
manifest=json.loads((B/'assets/manifest.json').read_text());out=[]
for a in manifest['assets']:
 p=B/a['file'];shutil.copy2(p,R/a['file']);out.append(dict(a))
parts=Image.open(B/'sources/wide_cinematic_concept_art_game_design_board_in_a.png').convert('RGBA')
assert parts.size==(1099,733),parts.size
board=Image.open(B/'sources/a_wide_cinematic_dark_gothic_castle_environment.png').convert('RGBA');assert board.size==(1536,1024)
def save(key,im,desc,**kw):
 global out
 p=A/(key+'.png')
 if key in ['courtyard','cathedral','catacombs','ramparts']:
  im.convert('RGB').quantize(colors=256,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE).save(p,optimize=True)
 else:im.convert('RGBA').save(p,optimize=True)
 with Image.open(p) as v:v.verify()
 a={'key':key,'file':'assets/'+p.name,'width':im.width,'height':im.height,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'provenance':desc,**kw};out=[v for v in out if v['key']!=key];out.append(a)
def resized(im,size):return im.resize(size,Image.Resampling.NEAREST)
def grade(im,brightness=1.08,contrast=1.08):
 alpha=im.getchannel('A');im=ImageEnhance.Contrast(im.convert('RGB')).enhance(contrast);im=ImageEnhance.Brightness(im).enhance(brightness);im=im.filter(ImageFilter.UnsharpMask(radius=.6,percent=70,threshold=4));im.putalpha(alpha);return im
# Full source composition rather than enlarging the previous 640px derivative.
wide=grade(resized(board.crop((5,4,1530,845)),(1280,720)),1.10,1.05)
save('courtyard',wide,'Full original 1536px illustration cropped 5,4,1530,845; 1280x720 raster, displayed in 640x360 world units.')
save('ramparts',grade(wide,1.06,1.02),'Continuous full-source ramparts composition at double the prior raster density.')
# Normalize original preview coordinates ONCE. Crop only clean masonry/art, no sheet headings.
canonical=resized(parts,(1536,1024))
def cut(box,size):return resized(canonical.crop(box),size)
def matte(im):
 a=np.array(im);a[:,:,3]=np.where(a[:,:,:3].max(2)<23,0,a[:,:,3]);return Image.fromarray(a)
wall=grade(cut((483,662,583,739),(192,128)),1.12,1.08)
column=grade(matte(cut((29,438,73,574),(110,470))),1.07,1.05)
window=cut((1451,677,1502,772),(126,254))
arch=grade(Image.open(B/'assets/arch.png').convert('RGBA'),1.10,1.10)
statue=grade(Image.open(B/'assets/statue.png').convert('RGBA'),1.08,1.08)
save('arch',arch,'Reviewed R4a raster arch; highlight and silhouette contrast pass.')
save('column',resized(column,(72,245)),'Complete source column, clean alpha and contrasting stone highlights.')
save('statue',statue,'Reviewed statue texture with stone highlight pass.')
def masonry():
 im=Image.new('RGBA',(1280,720),(10,14,24,255))
 for y in range(0,720,128):
  for x in range(-96 if y%256 else 0,1280,192):im.alpha_composite(ImageEnhance.Brightness(wall).enhance(.74),(x,y))
 return im
cat=masonry()
# Continuous deep bays, with wide stone piers, stained glass and separate torch props in the runtime.
for x in [108,490,880]:
 alc=grade(cut((1336,670,1513,774),(322,232)),.80,1.08);cat.alpha_composite(alc,(x-30,322));cat.alpha_composite(grade(window,1.22,1.08),(x+44,103))
for x in [-22,350,738,1122]:cat.alpha_composite(column,(x,78))
save('cathedral',cat,'1280x720 raster masonry nave: complete piers, source stained glass, full candle alcoves; no sheet labels.')
crypt=masonry();niche=grade(cut((1156,669,1323,775),(220,336)),.87,1.12)
for x in [55,365,675,985]:crypt.alpha_composite(niche,(x,126));crypt.alpha_composite(resized(statue,(105,225)),(x+44,338))
for x in [-20,280,590,900,1210]:crypt.alpha_composite(ImageEnhance.Brightness(column).enhance(.77),(x,117))
save('catacombs',crypt,'1280x720 crypt with source niches and statuary, separated structural pillars and sharper masonry.')
# The actual approved portrait, with hat, beard and Black Watch shirt. No stand-in face.
portrait=grade(parts.crop((455,23,622,178)),1.12,1.08)
save('portrait',resized(portrait,(96,96)),'Approved character portrait from original board at actual 455,23,622,178 coordinates; hat, beard, Black Watch tartan.')
# Readable sprite outlines/texture, without changing source frames or the animation anatomy.
for a in list(out):
 if a.get('frames'):
  im=Image.open(B/a['file']).convert('RGBA');save(a['key'],grade(im,1.09,1.07),'R4a validated raster frames: modest contrast/highlight pass; original silhouettes/poses unchanged.',**{k:a[k]for k in ['frames','frameWidth','frameHeight']})
# Clean independent source torch and leaf clusters; scene animation flickers the light, not the canvas.
torch=matte(parts.crop((216,310,259,410)));save('torch',resized(grade(torch,1.15,1.04),(34,78)),'Original source hanging flame/lantern crop 216,310,259,410.')
leaf=matte(parts.crop((482,316,548,409)));save('branch',resized(leaf,(100,142)),'Original isolated leafless tree from environment-prop board.')
# Film reel icon, pixel-grid aligned UI/pickup art. Not a character fallback.
reel=Image.new('RGBA',(28,26));d=ImageDraw.Draw(reel);d.ellipse((2,1,25,24),fill='#817259',outline='#dcc595',width=2);d.ellipse((10,9,17,16),fill='#171b23')
for x,y in [(8,5),(18,5),(6,15),(20,15)]:d.ellipse((x-2,y-2,x+2,y+2),fill='#22252d')
d.line((16,23,26,23),fill='#c5bb95',width=2);save('film-reel',reel,'New pixel-grid film canister pickup; visually distinct from capture swirl.')
# Distinct bone and energy-projectile pixels, rather than reusing the reel/capture icon.
bone=Image.new('RGBA',(17,9));d=ImageDraw.Draw(bone);d.rectangle((4,3,12,5),fill='#d9c7a7');d.line((4,3,12,3),fill='#f3e7ce');
for x,y in [(1,1),(1,5),(12,1),(12,5)]:d.ellipse((x,y,x+3,y+3),fill='#e9dbc1',outline='#a89b82')
save('bone-shot',bone,'Pixel-grid thrown bone with articulated ends, not a film pickup icon.')
bolt=Image.new('RGBA',(19,19));d=ImageDraw.Draw(bolt);d.polygon([(9,0),(12,6),(18,9),(12,12),(9,18),(6,12),(0,9),(6,6)],fill='#633f8fa0');d.polygon([(9,3),(11,7),(15,9),(11,11),(9,15),(7,11),(3,9),(7,7)],fill='#b7a1f7');d.ellipse((7,7,11,11),fill='#ecdbff');save('magic-bolt',bolt,'Pixel-grid vampire energy bolt with a pale core and stepped violet edge.')
# Atmospheric raster, layered sparsely so the stage stays readable.
y,x=np.mgrid[0:64,0:256];a=(np.sin(x/33+y/18)+np.sin(x/19-y/24)+2)/4;edge=(1-np.abs(y-32)/32)**2
fog=np.zeros((64,256,4),dtype='uint8');fog[:,:,:3]=[144,170,192];fog[:,:,3]=np.uint8(a*edge*43);save('mist',Image.fromarray(fog),'Low-opacity multi-wave raster mist; animated as two small independent depth layers.')
# Crisp higher-density floor from the canonical reviewed masonry sample, rather than full poster strips.
stone=grade(Image.open(B/'assets/stone.png').convert('RGBA'),1.13,1.12);save('stone',stone,'Reviewed collision-aligned stone tile with improved local highlight contrast.')
for entry in out:
 p=R/entry['file']
 with Image.open(p) as im:im.load();assert im.size==(entry['width'],entry['height'])
 assert hashlib.sha256(p.read_bytes()).hexdigest()==entry['sha256']
(A/'manifest.json').write_text(json.dumps({'build':'gothic-r5','renderScale':2,'assets':out},indent=2))
# Home Screen icons use the same approved portrait; never a new identity.
for size in [180,192,512]:
 icon=Image.new('RGBA',(size,size),'#0c1420');pad=round(size*.07);icon.alpha_composite(resized(portrait,(size-2*pad,size-2*pad)),(pad,pad));ImageDraw.Draw(icon).rectangle((pad,pad,size-pad-1,size-pad-1),outline='#c5a867',width=max(2,size//80));icon.save(A/f'icon-{size}.png')
print('Validated',len(out),'raster assets. Portrait uses the actual approved head and shirt.')
