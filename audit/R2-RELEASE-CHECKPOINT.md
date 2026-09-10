# Gothic Horror R2 release checkpoint

## Transfer complete

The user approved saving `/Gothic-Horror-HUD-R2.zip` in Dropbox and using it to transfer the game to this repository. Upload completed. Archive: 30,428,471 bytes, SHA-256 `73e413af85d24ae0921af6439566ecd34ea5ca92ab555f7e19cddc5e1386cd80`, matching Dropbox content hash `7fb43bf25743c286b8308aa940e93b8888094d4ba032c18181de26804be013e3`.

GitHub Actions run 34427201446 imported the exact bytes. The one-use file URL was passed as an encrypted message; the private decryption key never left the runner. No plaintext Dropbox download URL or account credential was committed. The one-time import workflow was removed after success.

## Executed release gates

The exact self-contained game has SHA-256 `99676e652482b652eadfcb87bf7411ebbfe11bcefffa87b7aa60fdfc98962839` and is 2,334,349 bytes. All 14 prepared PNG assets passed full decoding, dimensions and hash checks. Inline scripts passed Node syntax checks.

Chromium: 42 gameplay/asset/input checks, 30 HUD/layout checks, four additional move/jump/restart cycles and a real phone-emulated Start/Pause/Resume tap sequence passed. No uncaught exceptions.

WebKit: 33 gameplay/asset checks, 30 HUD/layout checks, four additional move/jump/restart cycles and a real phone-emulated Start/Pause/Resume tap sequence passed. No uncaught exceptions. The nine CDP-specific mobile checks are Chromium-only, not falsely counted for WebKit.

Both engines completed the keyboard-only six-creature playthrough and reached the exit. Both independently verified rendered player pixels, movement, jump/landing, attacks/damage, invulnerability, checkpoint respawn, film cooldown/recovery, Canvas fallback and visible failure for a deliberately bad image. Full JSON results and screenshots are under `game/rebuild-r2/evidence/`.

## Runtime and editing paths

`index.html` and legacy `game/play.html` redirect to `game/releases/gothic-hud-r2/index.html`. That immutable HTML contains its own engine and all artwork, avoiding mixed runtime/asset cache versions. `.nojekyll` prevents site processing. Broken historical PNGs and runtime files are retained for audit/history but are not loaded.

Editable source: `game/rebuild-r2/src/`, `style.css`, `index.template.html`, and `assets/`. Rebuild with `python game/rebuild-r2/tools/bundle.py`, test, then publish the resulting bytes under a NEW versioned release directory. Never copy long image-data strings manually.

HUD includes five life hearts and count, perforated film meter/value, captured count/slots, checkpoint state, Pause/Resume and fullscreen where supported. It is outside the canvas and covered by six viewport-layout tests per engine.

## Scope and remaining work

This is a playable R2 review build, not a claim of final art/animation completion. The recovered raster environment and sprites are present, but the original five independent scenery layers and full animation/art continuity polish are not complete. A physical iPhone and shipping Safari app have not been tested; Linux WebKit and phone emulation were tested.

At this checkpoint, main has not yet been promoted. After promotion, `.github/workflows/gothic-live-check.yml` verifies the actual public root, served HTML checksum, and real Chromium/WebKit desktop/mobile-emulated startup. Do not say the public link works until that run succeeds.
