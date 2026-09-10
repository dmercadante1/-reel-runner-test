"""Import only the approved archive. No main writes, no secret URLs in Git history."""
import base64, hashlib, io, json, os, pathlib, time, urllib.request, zipfile
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from PIL import Image
REPO='dmercadante1/-reel-runner-test'; BRANCH='gothic-hud-r2-release'
ZIP_HASH='73e413af85d24ae0921af6439566ecd34ea5ca92ab555f7e19cddc5e1386cd80'
HTML_HASH='99676e652482b652eadfcb87bf7411ebbfe11bcefffa87b7aa60fdfc98962839'
run=os.environ['GITHUB_RUN_ID']; token=os.environ['GITHUB_TOKEN']
def api(path,method='GET',payload=None):
 data=None if payload is None else json.dumps(payload).encode()
 req=urllib.request.Request('https://api.github.com/repos/'+REPO+'/'+path,data=data,method=method,headers={'Authorization':'Bearer '+token,'Accept':'application/vnd.github+json','Content-Type':'application/json'})
 with urllib.request.urlopen(req,timeout=30) as r:return json.load(r)
# Private key never leaves this process. Only its public half is committed.
private=rsa.generate_private_key(public_exponent=65537,key_size=2048)
public=private.public_key().public_bytes(serialization.Encoding.PEM,serialization.PublicFormat.SubjectPublicKeyInfo).decode()
public_path='audit/r2-transfer-public-key.json'
body={'message':'Publish ephemeral transfer PUBLIC key for run '+run,'branch':BRANCH,'content':base64.b64encode(json.dumps({'run':run,'publicKey':public}).encode()).decode()}
try:body['sha']=api('contents/'+public_path+'?ref='+BRANCH)['sha']
except urllib.error.HTTPError as e:
 if e.code!=404:raise
api('contents/'+public_path,'PUT',body)
print('Public transfer key ready for run '+run,flush=True)
request=None
for attempt in range(96):
 time.sleep(5)
 try:
  entry=api('contents/audit/r2-transfer-request.json?ref='+BRANCH)
  candidate=json.loads(base64.b64decode(entry['content']))
  if str(candidate.get('run'))==run:request=candidate;break
 except urllib.error.HTTPError as e:
  if e.code!=404:raise
if request is None:raise RuntimeError('No encrypted transfer request received; main remains unchanged.')
dec=lambda s:base64.b64decode(s,validate=True)
key=private.decrypt(dec(request['key']),padding.OAEP(mgf=padding.MGF1(hashes.SHA256()),algorithm=hashes.SHA256(),label=None))
url=AESGCM(key).decrypt(dec(request['nonce']),dec(request['ciphertext']),run.encode()).decode()
from urllib.parse import urlparse
u=urlparse(url)
if u.scheme!='https' or not any(u.hostname==h or u.hostname.endswith('.'+h) for h in ('dropbox.com','dropboxusercontent.com','dropboxapi.com')):raise ValueError('Not an approved Dropbox download host')
print('::add-mask::'+url,flush=True)
# Single request: do not HEAD, preview, or preflight a single-use URL.
try:
 with urllib.request.urlopen(url,timeout=120) as r:raw=r.read(40000001)
except Exception:raise RuntimeError('One-time Dropbox download failed; obtain a fresh link.') from None
assert len(raw)==30428471,'Archive length mismatch'
assert hashlib.sha256(raw).hexdigest()==ZIP_HASH,'Archive checksum mismatch'
url=None;key=None;private=None
z=zipfile.ZipFile(io.BytesIO(raw));assert z.testzip() is None
prefix='Gothic-Horror-Rebuild/';dest=pathlib.Path('game/rebuild-r2');dest.mkdir(parents=True,exist_ok=True)
keep={'Gothic-Horror-Playable.html','index.template.html','style.css','build.json','README.txt','AUDIT-AND-STATUS.md','RELEASE-R2-STATUS.md'}
for name in z.namelist():
 if not name.startswith(prefix):continue
 rel=pathlib.PurePosixPath(name[len(prefix):])
 if rel.is_absolute() or '..' in rel.parts:raise ValueError('Unsafe archive path')
 if str(rel) not in keep and rel.parts[0] not in ('src','assets','vendor','tools','tests'):continue
 if name.endswith('/'):continue
 p=dest/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(z.read(name))
html=(dest/'Gothic-Horror-Playable.html').read_bytes();assert hashlib.sha256(html).hexdigest()==HTML_HASH
manifest=json.loads((dest/'assets/manifest.json').read_text())
assert len(manifest['assets'])==14
for a in manifest['assets']:
 data=(dest/a['file']).read_bytes();assert len(data)==a['bytes'];assert hashlib.sha256(data).hexdigest()==a['sha256']
 with Image.open(io.BytesIO(data)) as image:image.verify()
 with Image.open(io.BytesIO(data)) as image:image.load();assert list(image.size)==[a['width'],a['height']]
release=pathlib.Path('game/releases/gothic-hud-r2');release.mkdir(parents=True,exist_ok=True);(release/'index.html').write_bytes(html)
def entry(target):return '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Man With A Movie Camera — Gothic Horror</title><meta http-equiv="refresh" content="0;url='+target+'"><script>location.replace('+json.dumps(target)+')</script></head><body style="background:#070d16;color:#ead9a7;font-family:monospace"><a style="color:inherit" href="'+target+'">Play Man With A Movie Camera — Gothic Horror</a></body></html>'
pathlib.Path('index.html').write_text(entry('./game/releases/gothic-hud-r2/'))
pathlib.Path('game/play.html').write_text(entry('./releases/gothic-hud-r2/'))
pathlib.Path('.nojekyll').touch()
pathlib.Path('audit/r2-import-integrity.json').write_text(json.dumps({'archiveSHA256':ZIP_HASH,'htmlSHA256':HTML_HASH,'htmlBytes':len(html),'validRasterAssets':14,'importRun':run,'publication':'staging only; browser tests still required'},indent=2))
print('Exact archive imported. 14 PNGs decoded and hashed. Main NOT changed.',flush=True)
