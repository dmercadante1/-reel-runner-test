"""Derive raster stages and a articulated walk cycle from the approved original artwork.
No drawing-based character fallback. Retains source pixels; validates every output.
"""
from pathlib import Path
from PIL import Image,ImageDraw,ImageEnhance,ImageChops
import numpy as np,json,hashlib,math,shutil
from skimage.transform import PiecewiseAffineTransform,warp
R=Path(__file__).resolve().parents[1];S=R/'sources';A=R/'assets'
old=json.loads((A/'r2-manifest.json').read_text())
provenance=[]
def source(name):
 p=S/name;return Image.open(p).convert('RGBA')
board=source('a_wide_cinematic_dark_gothic_castle_environment.png')
parts=source('wide_cinematic_concept_art_game_design_board_in_a.png')
# Canonical crop coordinates are for the 1536x1024 original, not the archived preview.
original_parts_size=parts.size
assert original_parts_size in [(1099,733),(1536,1024)], 'Unrecognized source board size'
if parts.size!=(1536,1024):parts=parts.resize((1536,1024),Image.Resampling.NEAREST)
assert board.size==(1536,1024) and parts.size==(1536,1024)
def crop(im,box,size=None):
 x=im.crop(box)
 return x.resize(size,Image.Resampling.NEAREST) if size else x
def matte(im,threshold=24):
 ar=np.array(im);mx=ar[:,:,:3].max(axis=2);ar[:,:,3]=np.where(mx<=threshold,0,ar[:,:,3]);return Image.fromarray(ar)
def save(im,key,desc,frames=None,fw=None,fh=None):
 im=im.convert('RGBA');p=A/(key+'.png');im.save(p,optimize=True)
 with Image.open(p) as check:check.verify()
 a={'key':key,'file':'assets/'+p.name,'width':im.width,'height':im.height,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'provenance':desc}
 if frames:a.update(frames=frames,frameWidth=fw,frameHeight=fh)
 provenance.append(a);return im
# Raster building blocks extracted at actual art coordinates. Entire image decoding is checked below.
wall=crop(parts,(483,662,583,739),(96,64))
column=matte(crop(parts,(29,438,73,574),(72,245)))
window=crop(parts,(1451,677,1502,772),(82,154))
alcove=crop(parts,(1156,669,1323,775),(121,180))
statue=matte(crop(parts,(373,440,438,573),(60,125)))
arch=matte(crop(parts,(87,438,172,504),(108,84)))
full=Image.new('RGBA',(108,180));full.alpha_composite(arch);full.alpha_composite(column.resize((16,127),Image.Resampling.NEAREST),(0,53));full.alpha_composite(column.resize((16,127),Image.Resampling.NEAREST),(92,53));arch=full
for key,im,desc in [('column',column,'R2 original design board column crop 29,438,73,574'),('arch',arch,'R2 original design board arch 87,438,172,504 with actual raster pillars'),('statue',statue,'character/environment board statue crop 373,440,438,573')]:save(im,key,desc)
def wallbase():
 im=Image.new('RGBA',(640,360),(8,12,20,255))
 tile=ImageEnhance.Brightness(wall).enhance(.70)
 for y in range(0,360,64):
  for x in range(-48 if y%128 else 0,640,96):im.alpha_composite(tile,(x,y))
 return im
# Cathedral uses masonry, stained-glass windows, columns, and candle scene from original boards.
cat=wallbase();chapel=crop(parts,(1336,670,1513,774),(224,132))
for x in [68,268,468]:
 cat.alpha_composite(ImageEnhance.Brightness(chapel).enhance(.75),(x-21,180))
 cat.alpha_composite(window,(x,76))
for x in [-25,175,375,575]:cat.alpha_composite(column,(x,52))
save(cat,'cathedral','Raster tile collage from the R2 original design board masonry and chapel interior. 640x360, no character/labels baked in.')
crypt=wallbase()
for x in [25,183,341,499]:crypt.alpha_composite(ImageEnhance.Brightness(alcove).enhance(.72),(x,80));crypt.alpha_composite(ImageEnhance.Brightness(statue).enhance(.7),(x+20,178))
for x in [-30,126,284,442,600]:crypt.alpha_composite(ImageEnhance.Brightness(column).enhance(.64),(x,65))
ar=np.array(crypt).astype(float);ar[:,:,0]*=.91;ar[:,:,1]*=.86;ar[:,:,2]*=1.05;ar[:,:,3]=255
save(Image.fromarray(np.uint8(ar.clip(0,255))),'catacombs','Raster masonry, dark niches and stone statues from approved source boards.')
# Ramparts distant plane from source board. Separate near arches handled by the game.
sky=crop(board,(5,4,1530,620),(640,270));ramp=Image.new('RGBA',(640,360),(9,16,28,255));ramp.alpha_composite(sky,(0,30));
far=crop(parts,(920,463,1430,500),(640,82));ramp.alpha_composite(far,(0,236))
save(ramp,'ramparts','Original R2 environment source skyline plus distant castle row from original design board, not a magnified foreground strip.')
# Authentic textured animated limbs: mesh-warp original raster trousers and shoes, independently.
hero=Image.open(A/'hero-walk.png').convert('RGBA').crop((0,0,112,112));upper=hero.copy();upper.paste((0,0,0,0),(0,70,112,112))
# Source polygons separate the two legs. Small overlapping hip patch stays under the shirt.
polys=[[(51,64),(60,69),(54,79),(47,86),(42,92),(40,96),(44,102),(43,107),(35,106),(31,101),(30,94),(33,88),(39,83),(45,75)],[(51,65),(62,67),(66,73),(73,78),(74,86),(74,94),(83,98),(83,106),(68,108),(64,100),(62,92),(62,84),(56,78)]]
# Piecewise mesh around hip, knee and ankle; source frame values are never invented.
source_lines=[[(55,68),(44,84),(36,97)],[(56,68),(68,81),(70,99)]]
def ik(hip,foot,l1=19,l2=19):
 v=np.array(foot)-hip;d=min(np.linalg.norm(v),l1+l2-.1);v=v/(np.linalg.norm(v)+1e-8);a=(l1*l1-l2*l2+d*d)/(2*d);h=math.sqrt(max(0,l1*l1-a*a));return np.array(hip)+v*a+np.array([v[1],-v[0]])*h
frames=[]
for k in range(12):
 phase=2*math.pi*k/12;bob=int(round(-1.3*abs(math.sin(phase))))
 layers=[]
 for j in range(2):
  ph=phase+j*math.pi;hip=np.array([56,68+bob]);foot=np.array([56+17*math.cos(ph),103-max(0,math.sin(ph))*12]);knee=ik(hip,foot)
  mask=Image.new('L',hero.size);ImageDraw.Draw(mask).polygon(polys[j],fill=255);leg=hero.copy();leg.putalpha(ImageChops.multiply(hero.getchannel('A'),mask));src=[];dst=[]
  for si,di,width in zip(source_lines[j],[hip,knee,foot],[8,6,7]):
   for off in [-width,width]:src.append([si[0]+off,si[1]]);dst.append([di[0]+off,di[1]])
  # Fixed ankle-to-shoe offset moves with each foot instead of scaling the shoe away.
  sx,sy=source_lines[j][-1];src.extend([[sx-9,108],[sx+14,108]]);dst.extend([[foot[0]-9,foot[1]+8],[foot[0]+14,foot[1]+8]])
  trans=PiecewiseAffineTransform();trans.estimate(np.array(dst),np.array(src))
  result=warp(np.array(leg),trans,output_shape=(112,112),order=0,preserve_range=True,mode='constant').astype('uint8');layers.append(Image.fromarray(result))
 f=Image.new('RGBA',(112,112));f.alpha_composite(layers[0]);f.alpha_composite(layers[1]);f.alpha_composite(upper,(0,bob));frames.append(f)
walk=Image.new('RGBA',(112*12,112))
for i,f in enumerate(frames):walk.alpha_composite(f,(i*112,0))
save(walk,'hero-stride','12 independently articulated frames derived from R2 hero frame0, limb texture mesh warp. Not duplicate poses or whole-sprite bobbing.',12,112,112)
frames[0].resize((448,448),Image.Resampling.NEAREST).save(R/'evidence/stride-detail.png')
strip=Image.new('RGBA',(12*112,112),(18,25,34,255))
for i,f in enumerate(frames):strip.alpha_composite(f,(112*i,0))
strip.save(R/'evidence/stride-sheet.png')
frames[0].save(R/'evidence/stride-cycle.gif',save_all=True,append_images=frames[1:],duration=85,loop=0,disposal=2)
# Dithered optical light texture. Graphics effect only: approved character/scenery always stays raster.
y,x=np.mgrid[0:160,0:300];fan=7+x*.23;center=80;dist=np.abs(y-center)/(fan+1);noise=((x*13+y*7)%17)/17
alpha=np.clip((1-dist)*(.95-x/420),0,1)*(0.73+noise*.27);alpha[x<4]*=.5
beam=np.zeros((160,300,4),dtype=np.uint8);beam[:,:,:3]=[176,221,253];beam[:,:,3]=np.uint8(alpha*135)
save(Image.fromarray(beam),'camera-light','New quantized/dithered optical light FX. Additive compositing; no external asset dependency.')
y,x=np.mgrid[0:128,0:128];v=np.clip(1-np.sqrt((x-64)**2+(y-64)**2)/64,0,1);gl=np.zeros((128,128,4),dtype=np.uint8);gl[:,:,:3]=[192,229,255];gl[:,:,3]=np.uint8(v**1.6*190)
save(Image.fromarray(gl),'lens-halo','Dither-scale raster lens halo FX.')
# Heart icon raster, carefully grid-aligned UI icon (not a character substitute).
im=Image.new('RGBA',(9,9));d=ImageDraw.Draw(im);d.polygon([(1,1),(3,1),(4,2),(5,1),(7,1),(8,2),(8,4),(4,8),(0,4),(0,2)],fill=(172,42,61));d.line([(1,2),(3,2)],fill=(255,145,133),width=1);save(im,'heart','New 9px in-game life icon.')
entries=[]
for a in old['assets']:
 a=dict(a);a.pop('data',None);entries.append(a)
entries.extend(provenance)
for a in entries:
 p=R/a['file'];assert hashlib.sha256(p.read_bytes()).hexdigest()==a['sha256']
 with Image.open(p) as im:im.verify()
 with Image.open(p) as im:im.load();assert im.size==(a['width'],a['height'])
(R/'assets/manifest.json').write_text(json.dumps({'build':'gothic-r34','assets':entries},indent=2))
print('Prepared & fully decoded',len(entries),'raster textures; unique stride frames',len(set(f.tobytes() for f in frames)))
