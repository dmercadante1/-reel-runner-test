"""Import locally tested UTF-8 source only. Images are generated from the intact R4 originals."""
from pathlib import Path
import base64,gzip,hashlib,json
root=Path('game/rebuild-r5')
if (root/'SOURCE-TRANSPORT.json').exists():
 print('R5 editable source is already staged; keeping subsequent explicit changes.');raise SystemExit(0)
parts=[Path(f'audit/r5/source-{n:02}.b64').read_text().strip() for n in range(4)]
packed=base64.b64decode(''.join(parts),validate=True)
assert len(packed)==29886 and hashlib.sha256(packed).hexdigest()=='ad57eda5eddff9885a37d28b9c3066d95f5f0c0412732c7c226a6856a24d5b34','Source transport failed checksum; nothing imported'
raw=gzip.decompress(packed)
assert len(raw)==86698 and hashlib.sha256(raw).hexdigest()=='2f90d23ace50cfbed29ef2f76fa13142224e1f747d671cf85833380ce5d6a31d','Decoded text mismatch'
files=json.loads(raw);assert len(files)==14
for name,text in files.items():
 rel=Path(name);assert not rel.is_absolute() and '..' not in rel.parts and rel.suffix in ['.js','.py','.css','.html']
 path=root/rel;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text,encoding='utf-8')
(root/'evidence').mkdir(exist_ok=True)
(root/'SOURCE-TRANSPORT.json').write_text(json.dumps({'baseCommit':'2a4df8c8b9743b9214c4b9250830ad21c6c4a637','gzipSHA256':hashlib.sha256(packed).hexdigest(),'decodedSHA256':hashlib.sha256(raw).hexdigest(),'sourceHashes':{n:hashlib.sha256(t.encode()).hexdigest() for n,t in files.items()},'status':'Source recovered; not a deployment or a passing CI result'},indent=2))
print('All 14 source files recovered exactly; artwork will be generated from existing repository originals.')
