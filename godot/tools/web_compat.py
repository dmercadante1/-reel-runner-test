"""Use Emscripten's own shader-copy fallback for the 4.7.2 WebKit final blit.
The WASM/engine is unchanged. No GL error suppression or skipped rendering.
See Godot issue #122816. Fail closed if the pinned JS template changes.
"""
from pathlib import Path
import hashlib,json
p=Path('build/godot-m1/index.js');source=p.read_text()
old='context.defaultFboForbidBlitFramebuffer=false;'
new='context.defaultFboForbidBlitFramebuffer=true;'
assert source.count(old)==1, 'Expected exactly one pinned Emscripten offscreen framebuffer choice'
before=hashlib.sha256(p.read_bytes()).hexdigest();p.write_text(source.replace(old,new))
Path('godot/evidence/web-compatibility.json').write_text(json.dumps({'engine':'4.7.2.stable','file':'index.js','before_sha256':before,'after_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'change':'Use existing shader-copy presentation path instead of glBlitFramebuffer','upstream':'https://github.com/godotengine/godot/issues/122816','suppresses_errors':False,'wasm_modified':False},indent=2))
