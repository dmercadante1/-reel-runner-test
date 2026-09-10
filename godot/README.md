# MAN WITH A MOVIE CAMERA — fresh 640 x 360 production

This is a NEW Godot project, not R6 of the old Phaser runtime. The R5 reference remains at `game/releases/gothic-r5/`. Do not change the repository root, legacy release bytes or main to publish this foundation.

Start here: `docs/PRODUCTION.md`. The approved visual reference is identified exactly in `docs/visual-target.json`; it is a generated composition target, NOT an asset sheet or proof of finished animation.

Current content: Godot project settings, editable movement tuning, an intentionally unillustrated internal movement lab, input actions, four roster definitions and native smoke tests. No finished player artwork, capture mechanic, enemy, Gothic room, browser export or mobile touch UI is claimed complete.

Candidate engine: Godot 4.7.2, GDScript, Compatibility renderer. Web preset is single-threaded. Engine acceptance remains conditional on the early browser and physical-phone trial. Never substitute a headless import check for rendered-browser verification.

Open `project.godot` in the matching editor. Controls in the internal lab: Left/Right or A/D, Up or W. Motion values are editable in `data/default_movement.tres`. Run `godot --headless --path godot --editor --import --quit`, then `godot --headless --path godot --script tests/native_smoke.gd` from the repository root. These are developer instructions; the user should receive a hosted preview for review, not be required to program or run commands.

Export command after installing matching templates: `godot --headless --path godot --export-release "Web Trial" ../build/godot-web-trial/index.html`. The build folder must exist. Native testing alone does not establish web compatibility. Do not export publicly before the delivery milestone.
