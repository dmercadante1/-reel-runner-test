# MAN WITH A MOVIE CAMERA — Gothic Horror R5

Editable source for R5. Older releases remain unchanged. Build status comes from `evidence/release-gates.json` and the served-R5 workflow, not from this feature description.

## Gameplay

Courtyard 6 encounters; Cathedral 8; Catacombs 8; Ramparts 8: **30 total**, up from 12. Each stage has a real 380–510-unit chasm crossed by jumping onto, riding and jumping off a moving stone carrier. Elevated supply routes, Cathedral balcony exit, a vertical lift and a collapsing ledge remain. Non-lethal falls cost one life and return to the checkpoint without refilling film or health.

Film drains at 12/second. Passive recovery changes from R4's 16/second to an emergency-only 0.8/second, delayed 3.2 seconds after use and capped at 24. Reels grant 25, captures return 4 and checkpoints supply 20 once. Film carries across stages. Flash costs 20 with a 1.7-second cooldown. Lethal damage restores checkpoint recovery supplies to avoid a permanent dead end. Values and stage positions live in `src/config.js`.

## Artwork and portrait HUD

Twice-density rendering, four 1280x720 environment textures recovered from intact originals, indexed palettes, crisp nearest-neighbor presentation, separate light/fog/foliage accents, improved sprite contrast and projectile artwork. Physics retain the same logical world units. Mobile widens the view instead of distorting or shrinking a fixed 16:9 image.

The native in-game HUD contains the approved hat/beard/plaid protagonist portrait, life hearts, film gauge, stage/encounter totals, checkpoint status and flash cooldown. HUD buttons have enlarged touch zones. Legs continue striding while filming. This is not a claim of new hand-drawn animation cels or final SOTN-quality art everywhere; pose/camera continuity and repeated scenery remain polish opportunities.

## Controls and mobile

Desktop: Left/Right arrows or A/D move; Up or W jumps; hold Space/C to film; X/Shift flashes; P pauses; R restarts. Quick jump taps are buffered. Phaser captures arrow scrolling.

Mobile: left horizontal thumb pad; right-side large JUMP and FILM, smaller FLASH above. Tap-to-toggle FILM frees the right thumb to jump while recording. Pause-screen settings offer arrow buttons, hold-to-film and larger action controls. Each touch pointer is tracked independently; rotation, focus loss, restart and recovery clear stale inputs.

Fullscreen requests use the browser API when available, otherwise a visible help dialog. On iPhone browsers without game fullscreen, Safari Share -> Add to Home Screen, keep Open as Web App on when offered, then launch the icon in landscape. A standalone/landscape manifest, Apple app metadata, portrait icons and release-scoped offline worker are included. No push notifications, device-camera access or microphone access are requested.

Linux WebKit and phone emulation are not physical-iPhone or installed-app certification. That remains a real-device review.

## Reproducible build and evidence

From the repository root, install Pillow, numpy, Playwright 1.57.0 and Node. Run `python game/rebuild-r5/tools/assets_r5.py`, then `python game/rebuild-r5/tools/bundle.py`. Assets are generated from intact `game/rebuild-r34` originals; do not paste binary PNG data through conversation text.

Run `tests/r5_acceptance.py` and `tests/r5_playthrough.py` under this directory, for BROWSER=chromium and BROWSER=webkit. GITHUB_ACTIONS=true selects Playwright-managed Chromium instead of `/usr/bin/chromium` locally. Acceptance uses isolated fixtures; the full traversal uses real keyboard input, without teleporting, disabling enemies or refilling film/health. Test-agent deaths are recorded.

The candidate app is under `game/releases/gothic-r5/`. Complete PNG decoding, dimensions, hashes and JS syntax precede fresh browser tests. Actual stage screenshots must also be inspected. After promotion, `audit/check-live-r5.py` verifies deployed bytes, actual root, old R4 integrity, arrows, native HUD, fullscreen response, simultaneous touches and offline relaunch. A passing local run alone is not a verified hosted release.
