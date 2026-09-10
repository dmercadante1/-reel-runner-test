# Man With A Movie Camera — Gothic Horror R3 / R4

## Two separately preserved editions

R3 adds Courtyard, Cathedral, Catacombs and Ramparts, twelve encounters, scene transitions, articulated raster walking legs, stronger camera illumination and an in-canvas HUD.

R4 builds on the same stages with six telegraphed enemy attacks, camera flash defense, projectile blocking, jumping over low attacks, an elevated Cathedral gate, a Catacomb crossing, moving/lift platforms and a collapsing ledge. R2 remains at its original immutable URL.

Keyboard: A/D or Left/Right move; W or Up jump; hold Space/C to film; X/Shift flashes in R4; P pauses; R restarts. Enter starts. Phone landscape uses movement, jump, FLASH and FILM controls. Pause/fullscreen icons are inside the HUD. Physical devices have not been certified by browser emulation.

## Edit small files, not embedded image strings

- `src/config.js`: movement, jumping, health, film, stage dimensions, spawns, platform definitions, enemy cooldowns/ranges and attack timing.
- `src/world.js`: parallax scenery, floor segments, one-way/moving/collapsing platforms, pickups.
- `src/scene.js`: player/capture state, checkpoints and stage transitions.
- `src/combat.js`: R4 windup/active/recovery attacks, projectiles, flash and defense.
- `src/hud.js`: native Phaser HUD and feedback.
- `src/shell.js`, `style.css`, `index.template.html`: accessible startup and mobile input/layout.
- `assets/manifest.json`: complete PNG dimensions, frame counts, SHA-256 and provenance.

`tools/prepare_r34.py` produces the new assets from the intact original artwork in `sources/` and the preserved R2 raster sprites. The twelve stride frames articulate the original leg pixels; they are not twelve independently hand-redrawn animation cels. The additional environments are detailed raster compositions, not a claim that every original concept-art layer has been independently authored. Animation continuity and scenery repetition can still be refined without rebuilding physics.

## Reproducible production

1. Install Python dependencies Pillow, numpy, scipy, scikit-image and Playwright 1.57.0; Node is needed for syntax checks.
2. Run `python game/rebuild-r34/tools/prepare_r34.py` from the repository root.
3. Run `python game/rebuild-r34/tools/bundle.py 3` and `python game/rebuild-r34/tools/bundle.py 4`.
4. Install browser engines with `python -m playwright install --with-deps chromium webkit`.
5. Run each test for each engine using `BROWSER=chromium` / `BROWSER=webkit`. On local systems the scripts assume `/usr/bin/chromium`; set `GITHUB_ACTIONS=true` to use Playwright-managed browsers instead.
6. Tests: `tests/playthrough.py 3`, `tests/playthrough.py 4`, `tests/mechanics.py`, `tests/presentation.py` (all inside this directory).
7. Publish only the tested bytes, under a NEW versioned release directory. Do not overwrite an existing release artifact. Compare SHA-256 before and after deployment.

The full playthrough tests use keyboard input rather than teleporting or overriding health/enemies. Separate mechanics fixtures intentionally isolate attack/platform scenarios; they are not represented as full playthroughs. Presentation tests check six viewport shapes, real canvas-only HUD, Canvas fallback, short flash taps and explicit corrupted-image failure. Physical Safari/iPhone verification is separate from Linux WebKit and phone emulation.

## Safety and recovery

Each stage has an entry recovery point and a mid-stage checkpoint. Health/film recover at stage transitions; fallen characters return to the checkpoint. Film-consuming defense has a cooldown and cannot be spammed. R2 and R3 can be selected directly even after the root points to R4.

Browser release results, actual screenshots and both immutable build hashes are saved under `evidence/`. A source/build commit is not a deployment or a successful test: use `release-gates.json` plus the served-build workflow result as evidence.
