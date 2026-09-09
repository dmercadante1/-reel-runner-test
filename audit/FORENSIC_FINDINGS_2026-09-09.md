# Gothic Horror: forensic findings

Audit baseline: main dcdc6410744238065b19c364cb500f081d0055e0. Previous production release: 558a8c32006373ffc67c6d37eeab0a361362a307. Evidence: Actions run 34414327541, artifact 10128499089. This branch does not deploy and this report does not mark the rebuilt candidate released.

## Loading chain and publication

At the audited main snapshot, index.html redirects to game/play.html. That document loads play.css, Phaser 3.90.0 and runtime/recovery.js. It does not load the old production config, manifests, enemy atlas, gameplay or capture modules. Root-level arcade files are not part of this active loading chain. The root retained a recovery-1 query while the child document referenced recovery-2. Pages deployment success establishes publication of files, not successful game initialization.

The actual asset-free recovery-2 snapshot renders its diagnostic character and banner in both Chromium and WebKit. The last user screenshot contains the earlier recovery-1 HUD wording and geometry, not the replacement's ASSET-FREE wording. This establishes a version mismatch, not the exact cache mechanism in the user's browser. The Pages completion timestamp also matters. Do not diagnose current code from an unidentified cached screenshot.

## Published PNG inspection

Six of the seven published PNG paths do not contain complete valid images:

| Path basename | Bytes | Finding |
| --- | ---: | --- |
| hero_walk.png | 4435 | Header declares 1024x128 but image data is truncated. |
| enemy_atlas.png | 179490 | Base64 text stored under a PNG filename; not a usable complete binary atlas. |
| gothic_architecture.png | 5 | Not PNG data. |
| gothic_castle.png | 14984 | Missing PNG signature, non-header bytes. |
| gothic_sky.png | 14999 | Missing PNG signature, non-header bytes. |
| gothic_playplane.png | 7509 | Header declares 512x195 but image data is truncated. |
| gothic_foreground.png | 9013 | Complete opaque 256x62 PNG; a small image, not a full background. |

Checks include signatures, chunk boundaries, CRC, IEND, full Pillow decode and alpha. Header dimensions alone are not image validation. Earlier claims of a 32x62 hero confused the foreground with the hero; 64x65 enemy cells were inferred from the play-plane dimensions, not an actual enemy atlas. ATLAS_READY and productionReady labels were not evidence.

## Reproduced runtime failures

Recovery-1 constructs a movable physics body, but WebKit's decoded damaged hero texture has zero visible pixels. Chromium and WebKit can handle this malformed image differently. A loader-error callback is therefore not sufficient protection: actual decoded pixel content must also be checked.

The full production scene creates scenery and the hero, then fails while initializing/playing enemy animations from the invalid atlas. Scene creation does not finish, so later input, follow-camera and HUD setup cannot be treated as working. The raw versions.json records exact exceptions and scene state. This is distinct from an offscreen-player or foreground-only diagnosis.

Foreground sizing was also wrong: 720 divided by a 62-pixel source height yields about 11.61x enlargement. The opaque foreground at depth 20 overlays characters at depth 8. Changing depth cannot repair corrupted character files or an animation exception.

CSS forced width and height to 100% with !important while Phaser FIT also set canvas dimensions. On a tall viewport, the element rectangle and intended 16:9 canvas diverge. Object-fit adds internal letterboxing and makes size/input assumptions unreliable. This is a layout defect, not proof that all texture failures came from CSS.

## Other defects requiring rebuild rather than blind hotfixes

The old runtime included unused movement settings, input overwriting hurt knockback, retained enemy velocity during capture, destruction during live-group iteration, unreachable platforms, arbitrary collision/art offsets, weak vertical attack checks, unused empty-film lockout, parallax-incorrect culling, one-frame capture flashes and no robust completed-level loop. Alternate walk frames were called separate actions without actual pose verification. Earlier committed JS was cut off mid-function; no demonstrated GitHub API size ceiling explains or excuses committing syntactically incomplete payloads.

## Rebuild and release gate

Recovered complete source rasters are available in the conversation workspace. The candidate uses a 640x360 native canvas, transparent normalized sprite cells, real raster courtyard and prop art, invisible aligned collision zones and the requested six enemy types, with no knight enemy. A byte/dimension/alpha/frame validation gate runs before enabling play. Movement, camera capture, film, damage, checkpoint, pickups, pause, touch input and an exit condition are implemented in separated modules.

Local candidate tests and screenshots are separate from the original cross-browser forensic evidence. A demonstrated playthrough or partial checklist is not equivalent to all release gates passing. A scene-replay issue was found during deeper testing; the current candidate uses a fresh document for replay. See the candidate package's acceptance reports for completed results and outstanding failures. Candidate Chromium touch emulation is not a physical phone or Safari certification.

No final-art/Symphony-of-the-Night parity claim is made. Only actual gameplay screenshots may be used for visual review. Main must remain unchanged until candidate runtime, mobile/Safari coverage, image integrity and byte-identical deployment are verified. Never mark a step complete merely because a file write or Pages workflow succeeded.
