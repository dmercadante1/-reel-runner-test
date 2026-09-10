# Gothic Horror R3 / R4 release checkpoint

## Exact tested artifacts

- R3: `game/releases/gothic-r3/index.html`, 3,131,447 bytes, SHA-256 `3b37123c494f2f04cfc32965ad0e399f24e653035eedd99a0d3129a4a5261654`.
- R4: `game/releases/gothic-r4/index.html`, 3,137,238 bytes, SHA-256 `96948109f94c603d8fd2b0928685a285d3e4101a689dc7aab23204f885e5c722`.
- Both have 24 complete raster PNGs and their own engine/runtime embedded. Full decoding, dimensions, frame counts, SHA-256 and JavaScript syntax checks ran. Editable source was rebundled and compared byte-for-byte with each staged release.

## Executed acceptance

GitHub Actions run **34437753551** passed every gate. `game/rebuild-r34/evidence/release-gates.json` contains the exact per-report counts and source hashes.

- Chromium: R3 full playthrough 17; R4 full playthrough 21; isolated combat/platform/input fixtures 42; HUD/renderer/layout checks 36. Total 116.
- WebKit: R3 full playthrough 17; R4 full playthrough 21; isolated combat/platform/input fixtures 40; HUD/renderer/layout checks 36. Total 114.
- **230 passed, zero failed, zero uncaught browser exceptions.** Two CDP multi-touch checks are Chromium-specific and not falsely counted as WebKit tests.
- Both editions completed all four stages with all twelve captures in BOTH engines using keyboard input, without player/enemy health or position overrides in the playthrough. R4 climbed the Cathedral stairs/balcony and crossed the Catacomb gap. Separate mechanics tests intentionally use isolated fixtures and are labeled as such.
- Mechanics checks include every attack windup/execution, camera flash cost/cooldown/interruption, projectile interception, jumping shockwaves, damage/invulnerability, checkpoint respawn, one-way ledges, moving-platform carry, collapsing/reforming ledges, pause, repeated restart and mobile-emulated controls/orientation.
- Actual browser screenshots and full JSON evidence are committed under `game/rebuild-r34/evidence/`. Artifact 10136959279 also preserves that run.

## What is implemented

R3: Moonlit Courtyard -> Cathedral -> Catacombs -> Moonlit Ramparts; three captures per stage; gates, checkpoints and completion; twelve-frame articulated raster walking legs; brighter camera spill/lens halo; native in-canvas HUD.

R4: all R3 content plus skeleton bone throws, ghoul lunges, vampire bolts, ghost phase charges, monster shockwaves and werewolf leaps. X/Shift or FLASH spends film to interrupt nearby attacks and briefly defend the player. Camera light intercepts suitable projectiles. Jumping evades low attacks. Platforms include stairs, one-way ledges, horizontal movement, a lift and a timed collapsing ledge. The Cathedral gate is elevated and the Catacombs include a real gap crossing.

## Editing and remaining art scope

Editable files: `game/rebuild-r34/src/`, `style.css`, `index.template.html`, `assets/`, `tools/`, `tests/`. Configuration owns movement, health, film, stage placement and enemy timing. Documentation and feature notes are in that directory.

The twelve stride frames articulate original raster pixels, rather than being twelve separately hand-redrawn cels. Scenery uses complete original conversation artwork and raster compositions, not procedurally drawn block characters. Some scenery repetition, camera/pose continuity and animation blending (including locomotion while filming) remain art-polish work. This is not a claim of final SOTN-level art completion.

Linux WebKit and browser phone emulation were tested. A physical iPhone and shipping Safari app were NOT tested.

## Prior test-harness failures were investigated, not ignored

The moving-platform fixture now checks the whole movement trace and relative player/platform offset, avoiding zero net displacement at a sinusoidal turning point. Pixel comparisons normalize RGB because WebKit returns RGBA screenshots and a zero difference-alpha channel otherwise hides real RGB differences in Pillow getbbox. Initial screenshots are taken before Start to avoid letting enemies attack an unattended player during screenshot processing. Live replay tests wait for the new scene's stats object before sending input, rather than treating the old scene's running flag as restart completion. None of these fixes weakened enemy health or substituted fake characters.

## Publication gate

At this checkpoint the successful candidate is on `gothic-r3-r4-release`, not yet promoted. The prepared root and `game/play.html` point to R4. R3 and the working original R2 are preserved at separate immutable URLs. Main must only be fast-forwarded after checking the branch comparison.

After promotion, `.github/workflows/gothic-live-check.yml` / `audit/check-live-r34.py` verify the actual public root, both served file hashes, and Chromium/WebKit desktop and phone-emulated startup, controls, jump, capture light, native HUD buttons, restart and orientation. Do not call the hosted release verified until that separate run passes.
