> Historical handoff. Fresh implementation, executed verification and preview publication are now recorded in [CHECKPOINT-M1.md](CHECKPOINT-M1.md). Physical-phone approval remains open.

# M1 continuation handoff — verification remains open

This note distinguishes previously inspected results from code that still needs execution. R5, main, and the public game root must remain unchanged.

## Last inspected facts

M0: source commit 134cf897f7174f1ee5ed21b7b168e1b32ca57334 passed eight native movement checks in run 34500238884. These were native headless checks, not web or art certification.

M1 baseline export attempts 34501889786 and 34502450348 FAILED with Godot's generic Web Trial preset configuration error. Engine and template downloads succeeded. Do not report those runs as successful exports. The exact cause has not yet been demonstrated by a successful reproduction/fix.

A reproducible toolkit was retained by run 34502450348: artifact 10162416654, Godot-M1-Toolkit.zip (official Godot 4.7.2 executable plus single-threaded web debug/release template ZIPs). Source/export logs are artifact 10162424589, Godot-M0-Source-and-Export-Log.zip. Artifacts expire, so read their current status before relying on them.

## Prepared but not published implementation

Git tree fb6636de2b9cddbdd2c6cbcad8804a1c3e21a03b was successfully created using base tree 16b4279be063ddf8dc390fbae29c7668d09f420b. It contains a test-only web_trial scene/controller, input-action bridge, telemetry, deterministic pixel-alpha calibration chart and short audio tone generator, revised project main scene, and a Web Trial export preset. It has NOT been verified as a working web export. Inspect the tree before making it reachable in a source commit; don't overwrite later work.

The planned custom HTML shell and Playwright browser test still need to be confirmed present or added. Export preset refers to res://web/trial.html. Required protocol: JavaScript M1Bridge.attach(callback) and M1Bridge.report(JSON_string); commands start/resume/pause/reset, move_left/right/jump/record/defend/sound. Godot state reports phase, x, feet, velocities, grounded, ticks, jumps, landings, recording, audio events, frame metrics, viewport and production_art:false.

## Next bounded batch

1. Recover toolkit/source locally or in CI; diagnose the actual export preset error rather than assume a fix. Validate paths/templates and renderer options against the pinned engine.
2. Complete custom shell with explicit loading/error states, start button, 640x360 canvas display policy, separate touch-pointer tracking, blur/rotation cleanup, pause/reset/audio controls, and honest fullscreen fallback.
3. Import and export. Require errors to fail the job; generate a byte-integrity manifest. Then run actual Chromium/WebKit keyboard, short/held jump, rendered pixel, touch/pointer, audio-unlock, focus, sizing and fullscreen checks. Browser emulation does not certify a physical phone or audible output.
4. Review screenshots. Publish ONLY a new, clearly labeled technical-preview directory after its browser checks pass. Keep old root and R5 byte-identical. Verify served bytes and startup before giving a working-link claim.
5. M2 remains separate: recover the user's actual photo, approve the model at 60–72px, then build/review coherent animation. Do not reuse R5's imperfect sprites or label the calibration rectangle as cameraman art.

## Character reference to inspect

The current-conversation upload named Screenshot 2026-09-09 at 12.20.13 PM.png, file_0000000029f08211940d3508fdbcf31a, may be the original user reference and must be visually inspected before using a likeness. The tartan reference is file_000000002ea082118ed1ba0606d2f30e. The user-specified outfit is Hartford Whalers cap, Black Watch plaid, jeans and sneakers; the prop is a motion-picture film camera, not a video camera. Do not invent unseen photo contents.

## Current status

No M1 browser pass, hosted preview, final cameraman drawing, or animation approval is established by this note. This continuation encountered unreadable tool responses across multiple interfaces, so it does not assert new successful tests or publication. The precise state must be recovered from current branch files and executed run evidence on continuation. Do not ask the user for new GitHub/Dropbox permissions to resolve a tool-output visibility problem.
