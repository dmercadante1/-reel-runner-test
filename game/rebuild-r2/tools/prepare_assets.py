"""Reproducible extraction from complete approved conversation artwork, not broken repo exports."""
from pathlib import Path
from PIL import Image, ImageDraw
import numpy as np
from scipy import ndimage as ndi
import hashlib, json, io, struct, zlib
ROOT=Path(__file__).resolve().parents[1]; SRC=ROOT/'sources'; OUT=ROOT/'assets';OUT.mkdir(exist_ok=True)
records=[]; sheets={}
def verify(p):
 data=p.read_bytes(); assert data[:8]==b'\x89PNG\r\n\x1a\n';pos=8
 while pos<len(data):
  n=struct.unpack('>I',data[pos:pos+4])[0];end=pos+n+12;assert end<=len(data)
  assert (zlib.crc32(data[pos+4:pos+8+n])&0xffffffff)==struct.unpack('>I',data[pos+8+n:end])[0]
  tag=data[pos+4:pos+8];pos=end
  if tag==b'IEND':break
 assert tag==b'IEND' and pos==len(data)
 with Image.open(p) as im:im.verify()
 with Image.open(p) as im:im.load();return im.size

def save(key,im,source,extra={}):
 p=OUT/(key+'.png');im.save(p,optimize=True);size=verify(p)
 records.append(dict(key=key,file='assets/'+p.name,width=size[0],height=size[1],bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),source=source,**extra))
 return im

def crop_sprite(name,box):
 # Coordinates refer to the 1100px-wide inspection copy; calculate on the full source.
 source=Image.open(SRC/name).convert('RGBA');r=source.width/1100
 box=tuple(round(v*r) for v in box);im=source.crop(box);a=np.asarray(im).copy()
 rgb=a[:,:,:3].astype(float)
 # Remove only the teal-black board background. Preserve neutral-black camera/hat pixels.
 border=np.concatenate([rgb[0],rgb[-1],rgb[:,0],rgb[:,-1]])
 dark=border[np.max(border,axis=1)<40]
 median=np.median(dark,axis=0) if len(dark) else np.array([4,14,18])
 bg=(np.linalg.norm(rgb-median,axis=2)<14)&(np.max(rgb,axis=2)<44)
 lab,n=ndi.label(~bg);counts=np.bincount(lab.ravel());counts[0]=0
 keep=np.isin(lab,np.where(counts>=7)[0]);keep=ndi.binary_fill_holes(keep)
 bridged=ndi.binary_closing(keep,iterations=2)
 connected,n=ndi.label(bridged);sizes=np.bincount(connected.ravel());sizes[0]=0
 if n:
  main=connected==int(sizes.argmax()); nearby=ndi.binary_dilation(main,iterations=6)
  keep &= nearby

 a[:,:,3]=np.where(keep,255,0);im=Image.fromarray(a);bb=im.getbbox();assert bb
 return im.crop(bb),box

def sheet(key,name,boxes,height=88):
 frames=[];realboxes=[]
 for box in boxes:
  im,b=crop_sprite(name,box); realboxes.append(b)
  scale=min(height/im.height,94/im.width)
  im=im.resize((max(1,round(im.width*scale)),max(1,round(im.height*scale))),Image.Resampling.LANCZOS)
  # Explicit binary alpha and common pixel scale, no soft halos.
  alpha=im.getchannel('A').point(lambda a:255 if a>=120 else 0);im.putalpha(alpha)
  cell=Image.new('RGBA',(112,112));cell.alpha_composite(im,((112-im.width)//2,106-im.height));frames.append(cell)
 atlas=Image.new('RGBA',(112*len(frames),112))
 for i,im in enumerate(frames):atlas.alpha_composite(im,(112*i,0))
 save(key,atlas,name,dict(crops=realboxes,frameWidth=112,frameHeight=112,frames=len(frames)))
 sheets[key]=frames

hero='a_wide_dark_cinematic_pixel_art_game_concept_cha.png'
film='a_wide_pixel_art_game_sprite_sheet_concept_board.png'
sheet('hero-walk',hero,[(x,214,x+49,310) for x in [665,716,767,818,870,922,973,1025]],88)
sheet('hero-brace',film,[(x,198,x+62,300) for x in [15,80,145,212]],88)
sheet('hero-recoil',film,[(x,328,x+76,422) for x in [13,90,163,239]],82)
sheet('hero-jump',film,[(x,329,x+77,423) for x in [341,421,502,583]],82)
sheet('hero-hurt',hero,[(x,451,x+53,535) for x in [293,352,410,468]],84)
sk='a_dark_detailed_pixel_art_concept_sheet_game_de.png'
sheet('skeleton',sk,[(x,196,x+43,282) for x in [207,249,293,335]]+[(5,309,70,400),(72,310,124,400),(502,310,565,400),(566,310,629,400)],90)
gh='a_wide_concept_art_sprite_sheet_poster_in_dark_g.png'
sheet('ghoul',gh,[(x,197,x+43,282) for x in [208,250,292,333]]+[(6,311,70,394),(68,311,125,394),(503,311,559,397),(562,311,621,397)],87)
en='a_dark_atmospheric_pixel_art_game_design_animatio.png'
sheet('vampire',en,[(x,148,x+37,216) for x in [12,47,84,121]]+[(205,148,253,216),(253,148,318,216),(440,148,480,216),(480,148,511,216)],92)
sheet('monster',en,[(x,261,x+49,330) for x in [11,61,110,155]]+[(205,260,257,330),(256,260,320,330),(429,260,477,330),(477,260,520,330)],99)
sheet('werewolf',en,[(x,375,x+48,443) for x in [11,60,107,153]]+[(206,375,257,443),(256,375,318,443),(431,375,477,443),(480,375,535,443)],98)
sheet('ghost',en,[(x,483,x+46,560) for x in [12,60,108]]+[(160,483,206,560),(205,483,247,560),(244,483,286,560),(393,483,451,560),(477,483,539,560)],91)
# Whole illustrated Gothic scene: explicitly crop to 16:9, then sample at game resolution.
env='a_wide_cinematic_dark_gothic_castle_environment.png';im=Image.open(SRC/env).convert('RGB')
save('courtyard',im.crop((0,0,1536,864)).resize((640,360),Image.Resampling.LANCZOS).quantize(colors=160,dither=Image.Dither.NONE),env,dict(crop=[0,0,1536,864],use='far background, not collision'))
# Masonry from the same source. Top surface is retained and floor collision matches its top.
save('stone',im.crop((460,716,1536,864)).resize((448,62),Image.Resampling.LANCZOS).quantize(colors=96,dither=Image.Dither.NONE),env,dict(crop=[460,716,1536,864],use='walkable stone; top is floorY'))
# The actual spiral illustration from the film-camera effects board (transparent cutout).
spiral,box=crop_sprite(film,(109,462,173,527));spiral=spiral.resize((52,52),Image.Resampling.LANCZOS)
save('spiral',spiral,film,dict(crop=list(box),use='raster capture vortex'))
manifest={'build':'gothic-verified-20260909-r1','logicalViewport':[640,360],'assets':records}
(ROOT/'assets/manifest.json').write_text(json.dumps(manifest,indent=2))
# Readable asset inventory and actual sheet preview for QA.
rows=len(sheets);contact=Image.new('RGB',(112*8,rows*132),(26,31,39));d=ImageDraw.Draw(contact)
for row,(key,frames) in enumerate(sheets.items()):
 d.text((5,row*132+3),key,fill='white')
 for i,f in enumerate(frames):contact.paste(f,(i*112,row*132+20),f)
contact.save(ROOT/'evidence/sprite-inspection.png')
print('VALIDATED',len(records),'complete PNGs;',sum(r['bytes'] for r in records),'bytes')
