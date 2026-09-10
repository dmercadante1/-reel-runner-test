# M0 checkpoint — fresh 640 x 360 foundation

Date: 2026-09-10. Development branch: godot-640-foundation.

## Completed in this batch

Source commit 134cf897f7174f1ee5ed21b7b168e1b32ca57334 establishes a new Godot project in godot/, independent of the legacy Phaser runtime. Base/reference commit is cb242c3cefccb47ea73822f6be0051cf6ca8806a. Main, the public root and every earlier release remain unchanged.

The exact approved 640x360 visual target has also been copied to persistent Library:
- Path: /Man With A Movie Camera/Reboot 640/Approved-Gothic-640x360.png
- Library file: libfile_0503d3eb633c81919fcc602d84117499
- File ID: file_00000000edb4821180d905123f02b5bd
- Reference SHA-256: 64a3fc02e319e95fcb9d1472f92c475ba79d0c7757b655e661814e8db3f9c072
- Native dimensions: 640x360; bytes: 461522.
The picture is a composition/art target, not an exported production background or animation sheet. It is preserved in Library, not yet copied as a PNG into GitHub.

Pinned engine 4.7.2-stable (official) imported the project successfully in GitHub Actions run 34500238884. Eight native smoke checks passed: floor landing, right/left movement through input actions, braking, held-jump height, shorter released jump, landing after jumping, and presence of the Up-arrow binding. No script/parse errors occurred in the inspected import/test logs. Artifact 10161530296 contains exact logs and the JSON result.

Test scope is NATIVE HEADLESS physics and source bindings. No rendered game screenshot, browser keyboard, physical controller, phone touch, web performance or production artwork has been verified by these tests.

## Implemented foundation only

Editable movement Resource, player CharacterBody2D controller, keyboard action map, data-driven working title and four roster slots, a clearly labeled unillustrated movement lab, 640x360 viewport settings and a configured single-threaded web export preset. No production artwork, enemy/capture system, Gothic room or complete mobile UI is implemented.

M0 is complete as project setup/native smoke. M1 engine/delivery proof remains OPEN. The Godot choice remains subject to that proof.

## Exact next work

M1: export the small scene for web, prove actual visible output and input in Chromium/WebKit, add/test touch input and inspect scaling/fullscreen/audio/focus behavior, then provide a separate hosted trial for the user's real phone. Keep R5 unchanged. Do not claim phone approval from desktop emulation.

M2: refine the everyday cameraman at approximately 60–72px standing within a real 640x360 composition; validate face/outfit/film-camera design and portrait, then coherent animation in motion. The character's original photo must be available when producing the likeness; do not invent an unseen photo. Four character slots are planned, not four finished characters.

M3 core movement/camera encounter and M4 one genuinely polished Gothic room follow. Do not jump to building four stages or 36 genre stages. Full plan and release/approval rules: docs/PRODUCTION.md.
