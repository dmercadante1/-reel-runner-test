"""Read-only audit. Never modifies source files or Git refs."""
import base64, hashlib, io, json, pathlib, re, subprocess, zlib, struct
from PIL import Image
OUT=pathlib.Path('audit-results'); OUT.mkdir(exist_ok=True)
def git(*args):return subprocess.check_output(['git',*args])
def inspect(data,name):
 r={'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'prefix':data[:24].hex(),'valid':False}
 if name.lower().endswith('.svg'):
  import xml.etree.ElementTree as ET
  try:
   e=ET.fromstring(data);r.update(valid=e.tag.endswith('svg'),kind='svg',attributes=e.attrib)
  except Exception as e:r['error']=str(e)
  return r
 if not data.startswith(b'\x89PNG\r\n\x1a\n'):
  r['error']='Not a PNG binary'
  if data.startswith(b'iVBOR'):
   r['kind']='Base64 text mislabeled as PNG'
   try:
    b=base64.b64decode(data,validate=True);r['decoded']=inspect(b,'decoded.png')
   except Exception as e:r['base64Error']=str(e)
  return r
 r['kind']='PNG'; r['headerSize']=list(struct.unpack('>II',data[16:24])); pos=8;r['chunks']=[]
 try:
  while pos<len(data):
   n=struct.unpack('>I',data[pos:pos+4])[0];tag=data[pos+4:pos+8];end=pos+12+n
   r['chunks'].append({'tag':tag.decode('ascii','replace'),'length':n,'offset':pos,'complete':end<=len(data)})
   if end>len(data):raise ValueError('Truncated '+tag.decode('ascii','replace')+' chunk')
   crc=struct.unpack('>I',data[pos+8+n:end])[0]
   if zlib.crc32(data[pos+4:pos+8+n])&0xffffffff!=crc:raise ValueError('CRC mismatch '+str(tag))
   pos=end
   if tag==b'IEND':break
  if r['chunks'][-1]['tag']!='IEND':raise ValueError('Missing IEND')
  with Image.open(io.BytesIO(data)) as im:im.verify()
  with Image.open(io.BytesIO(data)) as im:
   im.load();a=im.convert('RGBA').getchannel('A');r.update(valid=True,size=list(im.size),mode=im.mode,alphaRange=list(a.getextrema()),transparentPixels=a.histogram()[0])
 except Exception as e:r['error']=str(e)
 return r
refs=git('for-each-ref','--format=%(refname:short) %(objectname)','refs/remotes/origin').decode().splitlines()
branches={};blobs={}
for row in refs:
 name,sha=row.split(' ',1)
 if name.endswith('/HEAD'):continue
 files=[]
 for entry in git('ls-tree','-rl',sha).decode().splitlines():
  meta,path=entry.split('\t',1);mode,kind,blob,size=meta.split()
  files.append({'path':path,'sha':blob,'bytes':int(size)})
  if path.lower().endswith(('.png','.svg','.jpg','.jpeg','.webp','.gif','.wav','.mp3','.ogg')):
   blobs.setdefault(blob,{'paths':[],'refs':[]})['paths'].append(path);blobs[blob]['refs'].append(name)
 branches[name]={'sha':sha,'files':files}
# Historical assets, including replaced and deleted objects.
for line in git('rev-list','--objects','--all').decode().splitlines():
 if ' ' not in line:continue
 blob,path=line.split(' ',1)
 if path.lower().endswith(('.png','.svg')):blobs.setdefault(blob,{'paths':[path],'refs':['history']})
for sha,b in blobs.items():
 b['paths']=sorted(set(b['paths']));b['refs']=sorted(set(b['refs']))
 data=git('cat-file','blob',sha);b.update(inspect(data,b['paths'][0]))
 if b['valid'] and b['kind']=='PNG':
  p=OUT/'valid-historical-assets';p.mkdir(exist_ok=True);(p/(sha+'.png')).write_bytes(data)
(OUT/'repository.json').write_text(json.dumps({'branches':branches,'assets':blobs},indent=2))
(OUT/'history.txt').write_bytes(git('log','--all','--date=iso-strict','--format=%H %ad %s'))
# Read-only evidence archive, every branch snapshot. No credentials or .git directory.
for name,b in branches.items():
 (OUT/('snapshot-'+name.split('/')[-1]+'.tar')).write_bytes(git('archive',b['sha']))
print(json.dumps({'branches':{k:{'sha':v['sha'],'files':len(v['files'])} for k,v in branches.items()},'assetBlobs':len(blobs),'validAssets':sum(b['valid'] for b in blobs.values())},indent=2))
