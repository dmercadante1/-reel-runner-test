# Gothic Horror chapter — overnight work in progress

User authorized the 1080p chapter, all five stages, six enemy types and Dracula, blue film capture and rare-item Super Shot. No overnight questions or permission prompts; skip blocked work and continue independently. Prior authorization includes the photo-based cameraman in separate GitHub Pages previews. Preserve root/R5 and every earlier preview.

## Current implementation (not yet published or approved)

Nine connected rooms: two Courtyard, two Catacombs, two Cathedral, two Castle, then Dracula's chamber. The chapter has its own scene, script, web shell and export preset. Original room/comparison scenes remain independent. Movement retains 640×360 world coordinates while CanvasItems renders 1920×1080. New backgrounds and six-pose enemy sheets use runtime atlas crops and a keyed shader. The skeleton reuses the existing guardian artwork.

Blue layered beam, animated perforated film ribbons, inward particles and shrinking capture motion are shared effects. Rare silver reels carry up to two Super Shots. Normal foes can have their guard broken; Dracula requires recovery and receives limited extra exposure. Reload restores film from carried spare reels. Four health points, room retries and room-entry localStorage checkpoint are implemented. Saves currently store room number only, not full inventory or ending statistics.

## Evidence inspected so far

- Native chapter smoke: 72 checks passed, zero failed. This covers state transitions, guards, facing, capture completion, Super Shot rules, pause and all room spawns. It does not prove all routes or browser behavior.
- Actual local Godot Web build runs in the in-app Chromium browser at 1920×1080, around 60 FPS. Input-driven traversal has reached room 4 (Drowned Reliquary); all prior encounters and exits passed. The test bot initially failed to jump out of lower recovery steps after combat; route instructions are being corrected. No full-chapter pass yet.
- Inspected actual room screenshots show the cameraman, werewolf, ghoul, skeleton and blue film ribbon effect. Purple edge spill on ghoul prompted a narrower red-preserving, blue-purple key cleanup; that source change still needs re-export and visual verification.
- No chapter WebKit pass or chapter publication yet. Physical iPhone performance/audibility remain unverified.

## Reproduce / continue

Repository: work/reel-runner, branch godot-640-foundation. All overnight work is still uncommitted. Engine: work/engine/Godot.app/Contents/MacOS/Godot (official 4.7.2). Run godot/tools/export_chapter.py from repository root with the engine path. It applies the established Emscripten shader-copy presentation workaround and creates a byte manifest. Private hero source must be present (it is locally).

Local server is work/courtyard-server.cjs on 127.0.0.1:8768; chapter test copy is build/courtyard/chapter. Its HTML contains temporary test controls and must never be published. Clean build/chapter is the release input. Test harness is work/chapter-playtest.js outside the repository; convert the passing harness into a reproducible browser test. Tab 6 in browser 1 is the reusable local browser. Captures are under outputs/courtyard-review/chapter-*.png/json.

Next: finish actual nine-room traversal; fix only demonstrated issues, inspect each stage/enemy/capture/Super, verify phone layouts and checkpoint restart, run actual Chromium and WebKit against the exact candidate, then publish a new immutable preview and verify live bytes. Continue art/motion/audio polish as time permits. Do not call this a finished game or final art approval.

Hourly heartbeat gothic-horror-chapter-overnight was created around 2026-09-11 03:41 UTC. Pause it after eight hours (about 11:41 UTC) or after a complete reviewable first pass and handoff. Do not overlap edits with an active turn.

## Verification update at 04:50 UTC

Source e02e67b / test revision 0cfaeeb ran in workflow 34563084261. WebKit passed all 22 browser checks, the complete nine-room route and two earned Super Shots (21 playthrough checks). Chromium passed startup/input checks but its 14 FPS software renderer caused the bot to overshoot the first bridge approach; no script/engine errors. The bot now anticipates braking and can jump out of recovery steps. Immutable older comparison candidates are no longer redundantly replayed by the chapter workflow; their bytes are unchanged and their previously verified tests remain available. The old Chromium comparison timing test also missed its no-damage window under software rendering.

Visual inspection found a thin magenta edge in the lowest floor strip. All modular surfaces now draw through the same key-cleaned architecture layer. The crypt bottom is solid so Drop cannot pass through it. A generated bronze bell gives the Bell Gallery a distinct prop. Ten optional-route checks are being run, including rare reels and the bottom-floor Drop regression. A fresh candidate export and both-browser pass are still required for publication.
