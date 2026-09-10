# M1 — browser delivery verified; physical phone approval remains open

2026-09-10. Source tested: `2336262` on `godot-640-foundation`.

Fresh GitHub Actions run: https://github.com/dmercadante1/-reel-runner-test/actions/runs/34530397668
Artifact: `10173332319`, `godot-m1-fresh-proof`. Reports are retained in `docs/m1-evidence/` so they do not depend on artifact expiry.

## Executed and inspected

- Official Godot 4.7.2 native import, all eight native regressions, and single-threaded Compatibility Web export passed. The CI import/native/export logs contain no script, parse or engine errors.
- Chromium 151.0.7922.34 and WebKit 26.5, Linux x64 GitHub-hosted runner: 26 browser checks per engine, 52 total, zero failures and zero page/console errors.
- Tests include actual keyboard motion/braking, short versus held jumps, immediate key-down/up, filming, simultaneous movement/filming/jump, independent touch release, blur/pause/resume, buffered-jump cleanup, rotation cleanup, audio activation and mute, 844×390 / 390×844 / 1024×768 layouts, integer desktop scaling, fullscreen and unavailable-fullscreen fallback, and honest shortcut guidance.
- Chromium uses browser-native CDP multi-touch delivery. WebKit uses DOM PointerEvents with a capture stub because its automation surface lacks a native multi-touch API. These are not physical phone tests.
- Actual canvas screenshots verify exact colors, transparency/blending, 640×360 internal resolution, 1280×720 integer display and nearest-neighbor 2× pixel blocks. Desktop and mobile-sized screenshots were visually inspected. The in-app Chromium preview was also opened and started visibly.
- Sustained WebGL error polling: twelve zeros in each engine, in addition to clean console logs. No errors are swallowed.
- Local HTTP load to ready: Chromium 909 ms; WebKit 2115 ms. Late sampled p95 frame time was 16.67 ms in both. These are unthrottled CI/local-load measurements, not phone or cellular performance. Download payload is approximately 40 MB uncompressed, mostly engine WASM. AudioContext was running at 44.1 kHz; audibility on physical speakers was not certified.

## Export failure diagnosis and rendering fix

The original mobile compression preset requests ETC2/ASTC without enabling those texture imports. This reproduces Godot's generic preset validation failure. The calibration textures do not need VRAM compression, so the trial disables both compression options. Engine and template paths are pinned and explicitly validated.

Stock 4.7.2 emits a persistent WebKit final-blit error, matching upstream https://github.com/godotengine/godot/issues/122816. An initially attempted exact-framebuffer guard did not resolve it and was removed. `tools/web_compat.py` makes one fail-closed, recorded change to exported `index.js`: select Emscripten's existing shader-copy presentation fallback instead of `glBlitFramebuffer`. The shader still performs presentation; no drawing is skipped and no GL error is suppressed. Engine WASM is unchanged. Before/after JS hashes are in `web-compatibility.json`.

The Chromium touch harness was corrected against Chromium's actual `CreateWebTouchEvents` implementation: a partial release sends the ended contact, not the still-held contacts. Failed earlier runs remain failed; only the final fresh run satisfies this checkpoint.

## Publication and remaining approval

The tested artifact is published only at:
https://dmercadante1.github.io/-reel-runner-test/game/previews/godot-m1-20260910-01/

Publication commit adds that directory only. Existing root and all R5 files are preserved. See `served-verification.json` for served-byte verification and preservation hashes when available.

Physical phone, audible sound and the user's playfeel approval remain open. Test landscape/portrait, simultaneous two-thumb movement + quick Jump, Film release while moving, audio after Start, switching apps and resuming. Engine choice remains provisional until that physical-device check.

## Character approval

The separate 640×360 character approval study remains local to the user. No likeness-derived artwork is included in this checkpoint or public preview. Model and motion approval remain open.
