# Fresh production plan — approved 640 x 360 direction

## Decisions carried forward

Working title: MAN WITH A MOVIE CAMERA. Title, character names and genre labels are data, not baked into environment artwork. Primary inspiration: Castlevania: Symphony of the Night atmosphere, exploration and encounter spacing; secondary inspiration: expressive, readable platforming such as Rayman. This is original game art and mechanics, not copied assets or level layouts.

Nine genres, four stages each, remain the LONG-TERM content plan: Gothic, Horror, Western, Sci-Fi, Noir, Documentary, Action, Comedy and Fantasy. Gothic castle spaces are distinct from modern haunted-house/hotel Horror. Do not begin manufacturing 36 stages before the prototype has a coherent, approved quality standard.

Four selectable protagonist slots: everyday cameraman (navy-blue Hartford Whalers cap, Black Watch navy/green plaid, jeans, sneakers; face based on the user's actual photo when supplied for character production); woman cinematographer; naturally proportioned Hitchcock-inspired older director; proposed veteran documentarian (fourth design still provisional). Shared essential jump reach and mechanics, individually designed bodies, camera handling, portraits and animation. Finish one character first, then extend to four.

Approved art target: exact 640 x 360 reference in visual-target.json. It establishes composition, density, atmosphere and naturalistic proportions, not approved anatomy, exported layers, sprite sheets or animation. Target character size 60–72 px standing is a proposal pending a game-size comparison. HUD stays inside the composition with a consistent protagonist portrait. Render crisp nearest-neighbor pixels; do not mix arbitrarily scaled character/background assets. Integer desktop scaling and phone fit/wider view must be tested separately before locking the display policy.

R5 is a preserved reference only. Do not reuse its imperfect sprite sheets, slice a concept collage into production layers, import its runtime, or change its live route. New work lives on godot-640-foundation in godot/. Versioned new preview URLs come later, after passing the relevant milestone.

## Milestones and approval gates

M0 — Foundation and reference lock (STARTED in this commit)
Deliverables: isolated project, exact target identity, named milestones, editable title/roster data, movement resource, development-only test room, input actions and source tests. Mark complete only after project import/native smoke results are inspected. No public deployment.

M1 — Engine and delivery proof
Candidate: pinned Godot 4.7.2, GDScript, Compatibility renderer, single-threaded Web. Export a tiny representative scene and verify actual rendered pixels, keyboard movement, quick jump taps, touch multi-input, audio start, focus recovery, viewport scaling and fullscreen/install fallback. Capture performance and loading metrics with identified device/browser. Test Chromium and WebKit, then the user's actual phone. Engine choice is provisional until this test; no automatic switch to another engine without explaining findings. A headless native test does NOT pass this gate.

M2 — Character and motion standard
First approval: everyday cameraman at real 640 x 360 gameplay scale, with consistent portrait and motion-picture film camera. Then coherent idle, turn, walk/run, jump, fall, landing, filming while standing/moving, reel reload and hurt. Use clean, deliberately authored poses with consistent anchors and silhouettes. Validate any generated frames individually and in a loop; never label a concept-board strip a ready animation. Compare the same character against the actual approved environment direction. No cosmetic variants substituted for four distinct characters.

M3 — Core playfeel and camera encounter
Internal geometry only, explicitly labeled as test art. Tune acceleration, braking, variable jump height, coyote time, buffered input and camera follow. Add one telegraphed enemy: read attack -> evade/interrupt -> film vulnerable moment -> capture. Film is scarce and replenished chiefly by pickups. Avoid a resource soft lock; decide checkpoint/retry rules deliberately rather than reintroducing rapid automatic refill. Test a short keyboard/controller/two-thumb control set. Do not give every enemy the same hold-button vacuum response. Timing, readability, visual/audio feedback and actual player feel need review in addition to test results.

M4 — One finished Gothic room (FIRST SUBSTANTIAL VERTICAL SLICE)
A short playable space with the approved cameraman, one finished enemy, upper bridge/lower crypt route inspired by the reference, one worthwhile platform challenge, a film pickup/optional route, checkpoint/exit, layered environment, integrated portrait HUD, light effects and sound. Rebuild artwork as separate clean layers and reusable architecture; collision is authored independently and matches the visible surfaces. Not a long horizontal wallpaper. Review a real gameplay recording and device playtest against the approved still before claiming reference fidelity.

M5 — Full Gothic level
Only after M4 approval: expand to four stages, establish room pacing, varied traversal/combat/exploration, unlockable paths, multiple enemies and a finale. Proposed stage identities remain Courtyard, Cathedral, Catacombs and Ramparts; detailed layouts are not locked. A stage is complete only after visual, movement, resource-balance, checkpoint and device checks. Not every room is locked until every enemy is captured.

M6 — Cast and other genres
Complete the other three selectable protagonists under the same standards, then extend systems through genre-specific content packs. Prototype each genre's distinctive interaction before mass-producing its four stages. Documentary may document behavior/weather/locations rather than capture wildlife as combat trophies. Game-wide save, progression, accessibility and distribution receive explicit milestones when scope is approved.

## Local edits, not whole-game rebuilds

Movement tuning is a reusable Resource; characters refer to it, not duplicate values. Each room is a separate editable scene, built from reusable platform/hazard/checkpoint scenes. Enemy attack definitions are resources; filming/capture is a shared component. Character art/animation, controller, camera mechanics, HUD and game naming are separate concerns. Swapping a background must not change collision. Moving a platform must not require re-exporting an environment atlas. A jump change legitimately requires a route-reachability retest.

Assets get exact dimensions, pivots, frame counts, alpha validation and source provenance before integration. Use real binary uploads or checked build artifacts, never manually transcribed binary strings. Animation transitions and camera consistency need motion review, not just PNG validation. Sources and reproducible build scripts remain editable; public releases are immutable.

## Progress reporting

Every completed batch records: files/commit, tests actually executed, screenshot/clip when relevant, outstanding failures and exact next task. A workflow running is not a passed build. Functional success is separate from art approval and playfeel approval. No background/notification promises without an actual supported mechanism. Do not send the user diagnostic blocks as the final visual result.

Immediate next task after M0: M1 web/mobile feasibility and M2 everyday-character model approval. Do not start the Cathedral or create more marketing boards yet.

## Current checkpoint — 2026-09-10

M0 native foundation is complete. M1 browser delivery has passed fresh native, Chromium/WebKit and rendered-pixel verification; a separate technical preview is published. Physical-phone/audibility/playfeel approval remains open. See CHECKPOINT-M1.md. R5 and its root link are preserved. The separate character approval study remains local and is not published in this repository.

## Film mechanic revision — 2026-09-10

Flash is replaced by Reload. The current test carries up to three spare reels, starts with two, and consumes one to restore the active film to full after 0.65 seconds. Filming uses 12 seconds per active reel. Movement and jumping remain available during reload; filming pauses. Full-film and empty-reserve reload attempts spend nothing. Pickups stay available when reserves are full. No passive refill. These values are provisional playfeel tuning, separate from character art approval. Reset explicitly restarts the lab and inventory; falling only resets position and preserves inventory.
