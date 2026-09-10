# Gothic Horror: verified rebuild R1 — NOT deployed

The interrupted candidate source was not available as a mounted runnable package. This continuation rebuilt a complete, independently tested candidate from the intact original conversation artwork and saved the actual source, not just status notes.

## Exact files and durable recovery

Single-file playable HTML: `Man-With-A-Movie-Camera-Gothic-Horror.html`
- 2,328,048 bytes
- SHA-256: `ad81acb050f901e17d2551f0bc205f0f9cfde350775acedbd0e42b82f2bade2f`
- All engine code, game code and 14 PNG assets embedded. No game/CDN asset downloads.

Full source/archive: `Gothic-Horror-Rebuild.zip`
- 29,575,062 bytes
- SHA-256: `714a4c265c271bdb35e57041df5c89edd3293e8ae6cda7f5183a21c5ace4d4f3`
- Includes complete original source boards, prepared raster assets, extraction/build scripts, modular JS, exact playable HTML, tests, audit evidence and actual gameplay screenshots/recording.

Saved in the user's ChatGPT Library folder `/Man With A Movie Camera/`:
- Archive: file_00000000bf1881f581eb04451cd30c8c, library_file_id libfile_8cddfcc730908191acf614f61705e53f
- Playable HTML: file_000000009ffc81f58d201543ba2fbb70, library_file_id libfile_cf0ba3f94b988191ac05aef53a302083
- Test results: file_0000000060e881f58d9e52530703ec01, library_file_id libfile_580890eef8ac8191baabed4073189734

Use Files materialize with the actual file_id to recover the exact archive. Do not reconstruct the game from this summary or copy image data manually from conversation text.

## Executed acceptance results

42 passed, 0 failed, no fatal interruption, no uncaught JavaScript exceptions. These are new executed tests, not the prior unverified 33-check claim.

Verified in Chromium:
- correct texture dimensions and frame slicing for 14 fully validated PNGs;
- actual visible rendered player pixels (image comparison with sprite hidden); game loop and 16:9 canvas;
- keyboard movement, jump, landing, pause and focus recovery;
- keyboard-only traversal, all six creatures captured, reaching the exit and completing the level (no position/health overrides in that playthrough);
- restart resets encounters;
- controlled physics scenarios for the lower authored ledge, enemy attacks, invulnerability and checkpoint respawn;
- empty-film cooldown and recharge;
- WebGL/default renderer and explicit Canvas fallback;
- mobile-emulated 16:9 framing, actual CDP simultaneous touch movement/camera, touch jump, pointer release, portrait pause and landscape resume;
- deliberate bad-image injection shows a blocking diagnostic instead of silently substituting a black square.

The first acceptance pass exposed a restart issue (clearing input on a destroyed player body); it was fixed before the final full 42-check pass. An incorrect scalar movement helper was caught by the initial smoke test and replaced before acceptance.

## Remaining / publication gate

Main and the existing GitHub Pages entry have NOT been modified. No claim that the live link is repaired.
The exact checked HTML still needs a safe binary-preserving transfer to the publication path and verification of the deployed bytes. Current connector writes do not accept a local binary file directly. Do not repeat the earlier malformed/truncated PNG uploads.
New-candidate Safari/WebKit and physical-iPhone tests remain outstanding.
Art direction is not final approval: complete raster background and masonry are present, but not all five independent environment layers; some concept-board-extracted animation poses still need cleanup and the walking camera silhouette needs consistency with film-camera action poses.

For local desktop use, open the downloaded self-contained HTML in Chrome and press ENTER THE COURTYARD. Arrows or A/D move; Up or W jumps; hold Space/C to capture; P pauses; R restarts.
