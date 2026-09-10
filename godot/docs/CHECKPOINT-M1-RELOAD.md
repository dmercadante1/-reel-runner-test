# M1 reload revision — 2026-09-10

User revision: navy-blue cameraman cap, no pink edge pixels, replace Flash with Reload and stackable spare film reels.

## Mechanics implemented

The input lab now uses finite film and Reload (R or the touch button). Start with a full 12-second active reel and two spares; pickups stack to a maximum of three spares. Reload consumes one spare, suspends filming for 0.65 seconds, and restores the active film completely. Movement and jumping remain available. Full-camera, already-reloading, and zero-spare requests spend nothing. Holding Reload does not repeat it. Quick keyboard/touch taps are latched until the physics tick. Empty film prevents recording; there is no automatic refill. Pickups stay in the world when reserves are full. Pause freezes reload progress; the reset button/T deliberately restarts inventory, while a fall preserves inventory.

These are provisional playfeel values. This is still an explicitly labeled engine/input lab with calibration shapes, not the finished character/room or enemy encounter.

## Fresh verification

Tested source: fd2921a (full revision recorded in served-verification.json).
GitHub Actions run: 34535892070. Inspected completed success and downloaded artifact 10175442867, then reviewed its JSON reports and rendered screenshot.

- 17 native checks passed: movement regression plus inventory capacity, consumption, reload completion, duplicate/full/empty rejection, and recovery through a pickup.
- 33 Chromium and 33 WebKit browser checks passed. Added tests cover finite film, full-camera rejection, held-key single reload, quick touch reload while moving, complete refill, and actual world pickup collection. Original movement, multi-touch, pause/focus, size, audio-context, fullscreen fallback and GL checks remain passing.
- Both exact-pixel checks passed (1280×720 integer display of a 640×360 canvas).
- No browser/engine console errors. Official runtime WebKit framebuffer workaround remains enabled and recorded with hashes.
- Chromium uses actual CDP touch events; WebKit uses DOM pointer events. A physical phone and audible output remain unverified.

Evidence is in m1-reload-evidence/. Source import/export in CI is clean. The local native run passed its checks but macOS sandbox denied user-data/log creation; the clean CI run is the release proof.

## Separate preview

The exact tested build is published at game/previews/godot-m1-20260910-02/. Publication commit 4f15c5c701d2d0c01c86fe04de2db9b730860e86 adds only that directory. R5, the root link and M1-01 remain untouched. Served bytes must match the artifact manifest; see served-verification.json for final delivery verification.

## Character revision remains local for approval

Standing model, portrait and all eight run/filming poses have a navy-blue cap with the existing emblem. The original pink pixels were magenta backing blended into dark silhouette edges, surviving the old bright-magenta-only filter. The revised rendering shader rejects magenta excess at dark edges as well. All 18 native 640×360 captures have zero added pixels over the 6/255 magenta-excess threshold, including portraits, after excluding unchanged reference pixels. Captures were visually inspected. Revised standalone HTML, motion GIFs, source sheets, edge evidence and ZIP are in the local outputs folder. Photo-derived artwork is not included in GitHub or the public lab.

Character approval and final transparent production sprites remain separate. Reload animation is not yet authored; the user’s approval study covers the standing model and running/filming cycle. Next: user review at game scale, then the rest of the character action set and a reviewed enemy encounter.
