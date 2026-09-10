# Man With A Movie Camera — Gothic Horror
## Verified rebuild, not a published release

### Current checkpoint
The rebuilt HTML is **2,328,048 bytes**, SHA-256 `ad81acb050f901e17d2551f0bc205f0f9cfde350775acedbd0e42b82f2bade2f`. The current acceptance run completed **42 checks, 0 failures**, with no uncaught JavaScript errors and no fatal test interruption. The test scope is Chromium (WebGL and Canvas), plus Chromium mobile emulation and actual CDP multitouch events. It is not Safari/WebKit certification or a physical-iPhone test.

### Preserved production baseline
Audited GitHub main: `dcdc6410744238065b19c364cb500f081d0055e0`. Deployment artifact: run `34412274190`, artifact `10127702877`. The previous full-tree audit inventoried all 45 tracked main files, eight branch snapshots and historical image blobs. Its machine-readable evidence is included in `audit/`. No game code has been published to main by this continuation.

### Confirmed faults in the original production build
Six of its seven PNG files are not complete valid PNGs. The hero has a 1024×128 header but a truncated IDAT chunk; a header does not prove the image is valid. The enemy atlas is malformed base64 text mislabeled as PNG. The architecture file is five bytes. Sky and castle have invalid image data, and the 512×195 playplane is truncated. Only the opaque 256×62 foreground passes complete PNG validation.

Historical browser replay fails when starting the first enemy animation: Phaser `getFirstTick` reads `duration` from an undefined frame. The rejected enemy texture leaves no real animation frames. Scene creation is interrupted; drawing a background first did not establish that gameplay was running. Separately, stretching the tiny opaque foreground to viewport height enlarged it approximately 11.6 times and could cover other objects.

The prior dimension fix incorrectly assigned environment-image measurements to the characters. Changing those numbers could not reconstruct missing PNG data.

### Diagnostic screenshot discrepancy
The user's screenshot has Recovery-1's specific header and rendering, not Recovery-2's ASSET-FREE label. Recovery-1 still loaded the truncated hero. Its GPU errors include `texImage2D: bad image data`. The exact committed Recovery-2 source displays its colored diagnostic character in the archived Chromium and WebKit audit. The earlier assertion that even the current asset-free character was conclusively broken was unsupported. We cannot prove why the older payload was on that user's device; it is not appropriate to prescribe another cache clear as a proven fix.

### Root and canvas audit
The audited root redirects to `game/play.html?v=recovery-1`. That HTML loads the newer recovery-2 CSS and runtime plus Phaser 3.90.0. Root query labels and actual script payloads had diverged, making versions confusing. The original CSS also forces both canvas dimensions to 100% with `!important`, overriding Phaser's FIT dimensions. The replacement has one identifiable build and leaves canvas width/height to Phaser at a logical 640×360 viewport.

### Rebuilt candidate
Fourteen complete raster assets were extracted from the intact original conversation artwork. Every exported PNG is fully decoded, CRC-checked, dimension-checked and SHA-256 recorded. Original source boards and exact crop coordinates are included. No procedural block-character fallback is loaded. The boot sequence fails visibly if an asset is incomplete, mismatched or cannot decode.

Code is modular: `config.js`, `shell.js`, `audio.js`, `scene.js`, `boot.js`, plus generated `assets.js`. The single HTML bundles these exact sources, the tested Phaser engine and every PNG. It needs no image/CDN downloads. Source tweaks and physics tuning do not require repainting artwork.

The tests include rendered-pixel visibility (not just a boolean visible flag), moving both directions, jumping/landing, a complete keyboard-only run capturing all six creature types and reaching the exit, restart, ledge collision, enemy attack/damage, invulnerability, checkpoint respawn, empty-film cooldown, recharge, focus pause, Canvas fallback, mobile multitouch move/camera, touch jump, orientation pause/resume and deliberate corrupt-asset rejection. Test results and actual screenshots are in `evidence/`.

### Remaining limitations — do not mark the whole project complete
The new candidate is **not yet on the GitHub Pages root**. Safari/WebKit and physical-phone verification remain outstanding. The current environment uses a whole Gothic raster backdrop and separate masonry; it does not restore five independent production depth layers. Source illustrations are concept boards, so some extracted poses need further silhouette/animation cleanup; art-direction approval remains separate from functional tests. The walking camera silhouette needs a consistency pass with the dual-reel film-camera action poses.

### Reproducible commands
`python tools/prepare_assets.py` extracts and validates artwork. `python tools/bundle.py` assembles the standalone HTML. `python tests/acceptance.py` runs the browser checks (Pillow, NumPy, SciPy and Python Playwright are used in the build/test environment; Chromium is installed at /usr/bin/chromium in the current tester). End users only need the HTML, not these development tools.
