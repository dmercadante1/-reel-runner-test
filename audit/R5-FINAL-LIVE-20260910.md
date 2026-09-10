# Current published release — Gothic Horror R5

Verified 2026-09-10. This checkpoint supersedes earlier messages saying R5 was waiting for publication. The existing root and game/play.html now lead to the working R5 release.

## Play

https://dmercadante1.github.io/-reel-runner-test/game/releases/gothic-r5/

No permission changes, Dropbox transfers, local downloads or installations are required for online play. PRESS START begins. Desktop: Left/Right arrows or A/D move; Up/W jumps; hold Space/C to film; X/Shift flashes; P pauses; R restarts.

## Exact published game and executed verification

- R5 HTML: 4,536,133 bytes, SHA-256 `6d5bf642fbdc44af784a472faa15d15d4c22e5b9b6b5f3ea5943260f9d94c702`.
- Staging run **34478607719**: **188 passed**, zero failed, no uncaught browser errors. Both Chromium and WebKit completed the 30-encounter, four-ferry level traversal and the separate controls, resource, platform and presentation suites. Full reports are in `game/rebuild-r5/evidence/`; summary is `release-gates.json`.
- The gate's final evidence-copy step initially failed because an empty output directory did not exist in a fresh checkout. The directory is now preserved by a tracked README; the failed gate alone was rerun and passed. Passing browser jobs were not falsely replaced or relabeled.
- Release promotion was a non-destructive fast-forward to `3fe3417f912313c42b945eca5727f0fcb401e7f7`. Earlier R4a and older releases remain unchanged.
- Final actual-site run **34481109095**, tested commit **34367abc334237d370b4b1192d2862ed729fb398**: **77 passed**, zero failed, no uncaught browser errors. It verified the exact deployed HTML and app worker, opened the actual root, and tested Chromium/WebKit desktop and phone-emulated startup, arrows, quick jump taps, camera/flash, scarce film, portrait HUD, pause, restart, mobile input, fullscreen response, service-worker scope and cached offline relaunch. Chromium additionally exercised real CDP simultaneous touches. Artifact **10153624753**, `gothic-r5-live-evidence`, holds the detailed results and actual hosted screenshots.

## Implemented user requests

- Desktop arrow movement and Up-arrow jumping, including buffered quick taps.
- Higher-density rendering and four more detailed 1280x720 environment textures, revised lighting/atmosphere and sprite contrast. Camera physics retain their original logical units; mobile widens the view rather than squeezing it into a fixed aspect ratio.
- The approved protagonist's portrait appears in the native in-canvas HUD alongside life, film, stage/capture counts, checkpoint status and flash cooldown.
- Thirty encounters: Courtyard 6, Cathedral 8, Catacombs 8, Ramparts 8.
- Four mandatory 380–510-unit chasm crossings using moving stone platforms. Elevated supply routes, the Cathedral balcony exit, lift and collapsing ledges also remain. Non-lethal falls cost life and return to the checkpoint without restoring film.
- Film no longer rapidly fills to 100. Emergency recovery is delayed 3.2 seconds, runs at 0.8 units/second and stops at 24. Reels, captures and one-time checkpoint supplies are the main replenishment sources; film carries between stages.
- Mobile uses a left thumb movement pad and a right action cluster. FILM toggles by default so the right thumb can jump while recording. Settings offer directional buttons, hold-to-film and larger buttons. Held/toggled inputs clear on rotation, focus loss and recovery.
- Native fullscreen is requested where supported; unsupported browsers receive explicit instructions. A landscape standalone Home Screen web app, portrait icons and a release-scoped cache worker are included.

## Final fixes and remaining limits

Software-only WebGL was too slow on the CI renderer. The bootstrap now selects Canvas when a hardware-accelerated WebGL context is unavailable or the renderer reports a known software implementation. Artwork resolution and gameplay difficulty were not reduced to pass tests.

The first online checks passed but WebKit offline reload failed with an internal loading error. The installed-app worker was changed from network-first to cache-first for this immutable release; the final fresh public-site run passed offline reload in both engines. The core HTML remained byte-identical through that worker-only correction, and the builder now reproduces the worker from `src/service-worker.template.js`.

Physical iPhone testing and testing the shipping Safari application were not performed. Linux WebKit/phone emulation do not certify hardware performance or installed-app chrome on a real phone. On iPhone browsers without native game fullscreen, Safari Share -> Add to Home Screen -> Open as Web App when offered -> launch the icon in landscape is the intended standalone route.

This is a playable review release, not a declaration that every animation has been hand-redrawn or that all scenery has final commercial-game polish. Further art continuity and difficulty tuning can be made in the modular source without repeating the asset rebuild.

Editable source: `game/rebuild-r5/src/`; gameplay values and stages in `config.js`, platforms in `world.js`, attacks in `combat.js`, HUD in `hud.js`, controls/app support in `shell.js`, renderer selection in `boot.js`. Build with `tools/bundle.py`. Preserve the published HTML and use a new release path for subsequent gameplay/art revisions.
