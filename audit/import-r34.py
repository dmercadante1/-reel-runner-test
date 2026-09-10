"""Stage reproducible R3/R4 sources. Original artwork comes from the already-approved R2 archive."""
import base64,gzip,hashlib,io,json,os,pathlib,shutil,time,urllib.request,urllib.error,zipfile
from cryptography.hazmat.primitives.asymmetric import rsa,padding
from cryptography.hazmat.primitives import hashes,serialization
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
REPO='dmercadante1/-reel-runner-test';BRANCH='gothic-r3-r4-release';DEST=pathlib.Path('game/rebuild-r34')
ZIP_HASH='73e413af85d24ae0921af6439566ecd34ea5ca92ab555f7e19cddc5e1386cd80'
PACK_HASH='02a7dc8137d8d6b48dc87e8341af8cfc99c9feea174e2e8b76a247727f032ad6'
JSON_HASH='e87d65087ba787adbae97cbdb5e06f5a64985cfcf80a0e6f7dbb9828f80a262f'
# A subsequent test-only run keeps the actual editable source, rather than reapplying the transport.
if (DEST/'sources/wide_cinematic_concept_art_game_design_board_in_a.png').exists():
 print('Original source artwork is already staged; preserving editable R34 source.');raise SystemExit(0)
parts=[]
for i in range(5):
 p=pathlib.Path(f'audit/r34/source-{i:02}.b64');s=p.read_text().strip()
 # Explicit transport correction; both complete SHA-256 checks below are still mandatory.
 if i==0:s=s.replace('eKd+/bq5v41mrOi','eKd+/bq5vwrOi');p.write_text(s)
 parts.append(s)
packed=base64.b64decode(''.join(parts),validate=True)
assert hashlib.sha256(packed).hexdigest()==PACK_HASH,'Text transport damaged: not importing'
raw=gzip.decompress(packed);assert hashlib.sha256(raw).hexdigest()==JSON_HASH
files=json.loads(raw);assert len(files)==15
for name,text in files.items():
 rel=pathlib.PurePosixPath(name);assert not rel.is_absolute() and '..' not in rel.parts
 assert name.endswith(('.js','.py','.html','.css'))
 p=DEST/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)
for name in ['assets','vendor']:
 shutil.copytree(pathlib.Path('game/rebuild-r2')/name,DEST/name,dirs_exist_ok=True)
shutil.copyfile(DEST/'assets/manifest.json',DEST/'assets/r2-manifest.json')
for name in ['evidence','sources','releases']:(DEST/name).mkdir(parents=True,exist_ok=True)
print('Verified all 15 source files; no PNG data was transported through tool text.',flush=True)
run=os.environ['GITHUB_RUN_ID'];token=os.environ['GITHUB_TOKEN']
def api(path,method='GET',body=None):
 req=urllib.request.Request('https://api.github.com/repos/'+REPO+'/'+path,data=None if body is None else json.dumps(body).encode(),method=method,headers={'Authorization':'Bearer '+token,'Accept':'application/vnd.github+json','Content-Type':'application/json'})
 with urllib.request.urlopen(req,timeout=30) as res:return json.load(res)
private=rsa.generate_private_key(public_exponent=65537,key_size=2048)
public=private.public_key().public_bytes(serialization.Encoding.PEM,serialization.PublicFormat.SubjectPublicKeyInfo).decode()
keypath='audit/r34-public-key.json';body={'branch':BRANCH,'message':'Publish one-run PUBLIC transfer key '+run,'content':base64.b64encode(json.dumps({'run':run,'publicKey':public}).encode()).decode()}
try:body['sha']=api('contents/'+keypath+'?ref='+BRANCH)['sha']
except urllib.error.HTTPError as e:
 if e.code!=404:raise
api('contents/'+keypath,'PUT',body);print('Public transfer key ready for run '+run,flush=True)
request=None
for _ in range(120):
 time.sleep(5)
 try:
  f=api('contents/audit/r34-transfer-request.json?ref='+BRANCH);candidate=json.loads(base64.b64decode(f['content']))
  if str(candidate.get('run'))==run:request=candidate;break
 except urllib.error.HTTPError as e:
  if e.code!=404:raise
if request is None:raise RuntimeError('No encrypted read request received; main is unchanged')
dec=lambda s:base64.b64decode(s,validate=True)
key=private.decrypt(dec(request['key']),padding.OAEP(mgf=padding.MGF1(hashes.SHA256()),algorithm=hashes.SHA256(),label=None))
url=AESGCM(key).decrypt(dec(request['nonce']),dec(request['ciphertext']),run.encode()).decode()
from urllib.parse import urlparse
u=urlparse(url);assert u.scheme=='https' and any(u.hostname==x or u.hostname.endswith('.'+x) for x in ['dropbox.com','dropboxusercontent.com','dropboxapi.com'])
print('::add-mask::'+url,flush=True)
try:
 with urllib.request.urlopen(url,timeout=120) as res:archive=res.read(40000001)
except Exception:raise RuntimeError('Single-use download failed; request a fresh link') from None
assert len(archive)==30428471 and hashlib.sha256(archive).hexdigest()==ZIP_HASH,'Original archive mismatch'
z=zipfile.ZipFile(io.BytesIO(archive));assert z.testzip() is None
names={'sources/a_wide_cinematic_dark_gothic_castle_environment.png':'a_wide_cinematic_dark_gothic_castle_environment.png','evidence/wide_cinematic_concept_art_game_design_board_in_a.png':'wide_cinematic_concept_art_game_design_board_in_a.png'}
source_hashes={}
from PIL import Image
for rel,name in names.items():
 data=z.read('Gothic-Horror-Rebuild/'+rel)
 with Image.open(io.BytesIO(data)) as im:im.verify()
 (DEST/'sources'/name).write_bytes(data);source_hashes[name]=hashlib.sha256(data).hexdigest()
(DEST/'source-integrity.json').write_text(json.dumps({'approvedArchiveSHA256':ZIP_HASH,'textPackSHA256':PACK_HASH,'sourceFiles':source_hashes,'sourceCode':{n:hashlib.sha256(t.encode()).hexdigest() for n,t in files.items()},'run':run,'status':'staged only; not a browser test or deployment'},indent=2))
url=None;key=None;private=None
print('Complete original PNG sources recovered and verified. R2/main remain unchanged.',flush=True)
