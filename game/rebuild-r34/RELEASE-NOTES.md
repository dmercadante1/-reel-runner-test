# Gothic Horror R3 / R4 release notes

Two separately preserved playable editions of MAN WITH A MOVIE CAMERA.

## R3: four stages and presentation

R3 connects Moonlit Courtyard, The Cathedral, The Catacombs and Moonlit Ramparts, with three encounters in each stage, capture-locked gates, mid-stage checkpoints and final completion. The camera uses additive raster light spill and a lens halo. The HUD is a native fixed-depth Phaser layer inside the canvas, with life, film, per-stage/total captures, stage/checkpoint information and pause/fullscreen controls. A twelve-frame stride articulates the original trousers and shoe pixels.

## R4: enemies, defenses and platforms

R4 includes the R3 stages and presentation, plus six telegraphed enemy abilities: skeleton bone throws, ghoul lunges, vampire bolts, ghost phase charges, monster ground waves and werewolf leaps. Camera light intercepts suitable projectiles. X/Shift (FLASH on touch) spends film to interrupt nearby attacks, dispel nearby projectiles and briefly protect the player. Flash cooldown and film cost prevent unlimited defense. Ground shockwaves can be jumped; monsters/ghosts and active werewolf leaps cannot be filmed indiscriminately through their attack windows.

Platforms include one-way static ledges, stairs to the Cathedral's elevated gate, a horizontal carrier, a vertical lift, and a timed collapsing/reforming ledge. R4 adds a real gap crossing in the Catacombs. Collision surfaces align with raster floor/ledge artwork. Falls and lethal damage return the player to the stage's active checkpoint.

## Controls

Arrows or A/D move; Up/W jumps; hold Space/C to film; X/Shift flashes; P pauses; R restarts. Enter or PRESS START begins. Landscape phone controls include arrows, jump, FLASH and FILM.

## Scope

These are playable milestone releases, not a declaration that final animation/art polish is complete. The stride is articulated existing raster art rather than twelve hand-redrawn cels. The environment art is assembled from intact original concept sources; some repetition, anatomy/camera continuity and layer polish remain. Browser emulation does not constitute physical-iPhone or shipping-Safari certification.

A source commit is not a deployment or proof of passing tests. Staging acceptance is recorded in evidence/release-gates.json; the separate served-build workflow verifies the actual public root and both immutable release hashes after promotion. R2 stays unchanged at game/releases/gothic-hud-r2/.
