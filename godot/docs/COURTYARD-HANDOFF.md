# The Gatekeeper — first playable room, 2026-09-10

The user authorized the character action set, one playable Gothic room, and preparation for phone testing together. This is the first room study, ready for motion/playfeel review; it is not a claim of final M4 approval or physical-phone certification.

## Implemented

- 68-pixel everyday cameraman, navy cap, matching portrait and shared clean-edge shader. Twenty-four authored source poses drive ten action states: idle, turn, run, jump, fall, land, film, film while running, reload, hurt. Grounded poses have measured foot anchors. Airborne poses retain a shared body reference. The review jump/fall arc uses the same 330 px/s launch and 1000 px/s² gravity; reload uses the same 0.65 seconds.
- Independent original background, modular stone architecture, arch/gate/brazier assets and guardian atlas. Platforms and gate collision are authored separately. Upper bridge, three pass-through return steps in the open gap, lower crypt film pickups, checkpoint and exit. Down/S or the down touch button drops through the small steps, never the solid bridge.
- One guardian: 0.85-second warning, locked-direction low sweep, 1.8-second recovery/exposure window. Capture requires 1.25 seconds filming within range, on the same height and facing the guardian. Filming outside the exposure window still consumes film but cannot capture it. A sweep can hit once per attack. Jumping clears the low strike. Capture removes gate collision and reveals the open arch.
- Existing finite film / three-spare / full-reload rules retained. Three health points and brief hit immunity. Retry deliberately restores full film, two spares and health at the last checkpoint; this prevents resource soft locks. No passive refill.
- Ambient wind and distinct pitched action/warning cues, mute, focus pause/release, fullscreen fallback, responsive touch controls and built-in character action review.

## Verification and limits

Current native checks: 22 courtyard checks plus the original 17 movement/film regression checks. The courtyard suite verifies capture timing/facing, one-hit sweep, jump evasion, actual bridge crossing, actual traversal of all three crypt return steps, drop control, solid bridge safety, pickups, reload pause/resume, checkpoint reset, gate completion and review overlay reset.

Current Chromium browser story: ten passing checks through actual Godot WebAssembly. The local verification harness sends engine input events through the same browser bridge; it does not claim physical touches. Captured run: pickup, reload, bridge crossing, pause/resume, timed jump with no damage, capture and gate exit. No browser errors; 60 fps and 16.67 ms p95 reported on this Mac. The standard M1 Chromium/WebKit touch delivery proof is prior evidence, not a claim that the new room has been tested on current Safari or a phone.

Safari inspection could not run because native computer-use permissions remained pending. Physical phone, audible output, sustained phone performance and two-thumb comfort remain open. The local native environment denies Godot user-data/log directory creation; gameplay assertions passed, and no script/import/export failures or audio-resource leaks remain in the final run.

The official WebKit framebuffer compatibility patch is applied after export, as in M1. Final output hashes, current local native/browser reports, videos, action frames, and phone-layout measurements are in the local review package.

## Source and build

Run `scenes/gothic_room.tscn` in the Godot editor or export the `Courtyard` preset. The existing M1 main scene and `Web Trial` preset remain separate. The Courtyard feature selects the new room at export. After export, apply the same narrow `context.defaultFboForbidBlitFramebuffer=false` to `true` runtime replacement used by `tools/web_compat.py` (point the script at the courtyard output). Do not change the WASM binary.

Character atlases and `atlas.json` are under `assets/private-character/`, intentionally ignored by Git because publication of likeness-derived artwork requires explicit permission. The full local package includes those files and is self-contained for editing/export. Non-personal Gothic assets and all game code remain on godot-640-foundation. The current local browser preview is on port 8768.

## Publication boundary

No new public room preview has been published. R5, the root link, and both M1 technical previews are untouched. Earlier automatic approval review rejected uploading the photo-derived cameraman to GitHub without specific permission. Ask for permission to publish that artwork to dmercadante1/-reel-runner-test / its GitHub Pages preview only after the reviewable local package is complete. Once approved, verify the complete new room in Chromium and WebKit before adding a new immutable preview directory. Do not overwrite R5 or earlier previews.

## Next review

Review the supplied character action video and actual gameplay video, then play the local room. After publication permission, finish WebKit verification and provide the phone link. Record device/browser, sound, rotation/focus recovery, two-thumb comfort, jump feel, film/reload balance, and encounter readability. Do not mark phone or final room approval complete before those results exist.
