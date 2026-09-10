# MAN WITH A MOVIE CAMERA — Gothic Horror R5

This directory is the editable R5 source. Older R2/R3/R4 releases are preserved unchanged. The current build status is established by `evidence/release-gates.json` and the separate served-R5 workflow, not by this feature document.

## Gameplay and resources

Four expanded stages: Courtyard 6 encounters, Cathedral 8, Catacombs 8, Ramparts 8 (30 total). Each stage has a real 380–510-world-unit gap, longer than a direct jump, crossed by jumping onto and riding a moving stone carrier. Elevated supply routes, the Cathedral balcony exit, a vertical lift and a collapsing ledge remain. Falling costs one life and returns to the active checkpoint; a non-lethal fall does not refill film or health.

Film drains at 12 units/second. It does not automatically refill above a 24-unit emergency reserve. Below that threshold, recovery begins only after 3.2 seconds without camera/flash use, at 0.8 units/second (formerly 14). Collectible reels grant 25, captures return 4 and each checkpoint grants 20 once. Film carries across stages. Flash costs 20 and has a 1.7-second cooldown. Lethal damage restores the checkpoint with recovery supplies, so running out of film does not permanently lock the level. Difficulty and all values remain editable in `src/config.js`.

## Artwork and HUD

The render target is now twice the logical world resolution. Complete source artwork is recovered at 1280x720 for each environment, with an indexed palette, proper nearest-neighbor presentation, separate light/fog/foliage accents, and mild sprite contrast treatment. Camera physics remain in the original 640x360-style units; high-density rendering does not double speeds or collision sizes. Mobile widens the view instead of stretching or shrinking a fixed 16:9 view.

The portrait is the actual approved hat/beard/plaid cameraman from the original concept board, not a newly invented character. It appears with life hearts, film gauge, stage and encounter counts, checkpoint state and flash cooldown in the native game HUD. HUD buttons have larger touch zones. The walking legs continue to animate while filming.

This is an improvement pass, not a claim of newly hand-drawn animation cels or final SOTN-quality art throughout. Character pose/camera continuity and environment repetition still admit further art polish.

## Controls

Desktop: Left/Right arrows or A/D move. Up arrow or W jumps. Hold Space/C to film; X/Shift flashes; P pauses; R restarts. Arrow scrolling is captured by Phaser; quick jump taps are buffered rather than lost between frames.

Mobile defaults to a left horizontal thumb pad and a right action cluster: large JUMP, FILM beside it and smaller FLASH above. FILM is a toggle by default, freeing the right thumb to jump while filming. Pause-screen settings offer left/right buttons, hold-to-film and enlarged action controls. Simultaneous touch pointers are tracked independently and cleared on blur, rotation, restart and checkpoint recovery.

## Fullscreen / app view

The fullscreen control requests native fullscreen when supported. Rejected or unavailable requests produce an explicit help dialog, not a silent no-op. On iPhone browsers that do not expose game fullscreen, use Safari Share -> Add to Home Screen, keep Open as Web App enabled when shown, and launch the new icon in landscape. The build includes a standalone/landscape manifest, Apple app metadata, portrait icons, and a service worker confined to this R5 release URL. No push notifications, account access, microphone or camera access are requested. The film camera is a game mechanic, not device-camera access.

Browser emulation and Linux WebKit do not certify physical-iPhone behavior or performance. Installed-app appearance still needs physical-device review.

## Build and test

From the repository root, install Pillow, numpy and Playwright 1.57.0, with Node available. Run `python game/rebuild-r5/tools/assets_r5.py`, then `python game/rebuild-r5/tools/bundle.py`. The asset tool uses the intact `game/rebuild-r34` source boards already in GitHub. Do not manually paste PNG data into text files.

Tests: `BROWSER=chromium python game/rebuild-r5/tests/r5_acceptance.py` and `BROWSER=chromium python game/rebuild-r5/tests/r5_playthrough.py`, then repeat with `BROWSER=webkit`. Set GITHUB_ACTIONS=true to use Playwright-managed Chromium rather than `/usr/bin/chromium` locally.

The acceptance suite has explicitly isolated mechanics fixtures. The full traversal uses ordinary keyboard input for all 30 captures, all four ferry crossings and completion; it does not teleport the player, disable enemies, refill film or override health. Test-agent deaths are recorded, not hidden as a perfect run.

The new release is `game/releases/gothic-r5/`, built as a self-contained HTML plus manifest, worker and icons. Before promotion, every PNG is decoded and checksummed, JS is syntax checked and fresh Chromium/WebKit reports must pass. After promotion, `audit/check-live-r5.py` checks actual root routing, deployed bytes, old R4 integrity, controls, native HUD, fullscreen handling, multi-touch and offline relaunch.
