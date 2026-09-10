# HUD / access R2 checkpoint — NOT published

The exact R1 archive was recovered and verified (SHA-256 714a4c265c271bdb35e57041df5c89edd3293e8ae6cda7f5183a21c5ace4d4f3). No replacement of the original 14 PNG assets was required.

R2 adds a dedicated HUD outside the canvas: five life hearts and count, perforated film gauge/value, captured count/slots, checkpoint status, Pause/Resume, and fullscreen when supported. PRESS START plus keyboard Enter start the scene. Pointer bookkeeping is cleared on input reset.

Executed new Chromium HUD/start checks: 30 passed, no uncaught JS errors. Viewports: desktop 1280x816 and 1216x1242; touch 844x390, 667x375, 568x320; portrait 390x844. Actual screenshots and tests/hud.py are in the package. Physical iPhone and WebKit remain untested for R2.

The complete gameplay rerun reached 23 passed checks, including keyboard-only full traversal, all six captures, completion and encounter reset, but exceeded its 120-second process limit after reset. Do NOT call this an all-suite pass. Investigate the post-restart continuation. The earlier R1 42-check evidence is labeled separately, not reused as R2 results.

Saved exact complete files in ChatGPT Library /Man With A Movie Camera/:
- Gothic-Horror-HUD-R2.zip: file_00000000a86c81f5a62c0313587489eb; libfile_5e8bbfb4642c8191af457e036c04bc30. 30,428,471 bytes; SHA-256 73e413af85d24ae0921af6439566ecd34ea5ca92ab555f7e19cddc5e1386cd80.
- Man-With-A-Movie-Camera-Gothic-Horror-R2.html: file_00000000498c81f59bd2f3ef93494adb; libfile_8407c07365bc8191bf4b94638031732c. 2,334,349 bytes; SHA-256 99676e652482b652eadfcb87bf7411ebbfe11bcefffa87b7aa60fdfc98962839.
- Gothic-Horror-HUD-Checks.json: file_00000000d78481f5bd0e3c11f24ef391; libfile_d47518167250819190b5f2ea87a247c2.

Current GitHub connector does not accept a local-file upload. The connected Vercel deploy_to_vercel action advertises zero arguments but rejects invocation because target/name/files are required. No deployment happened. Shell network is unavailable. Do not repeat unverified manual base64 uploads.

A Dropbox plugin connection was suggested as a byte-preserving upload/share bridge, not a new game host. It is not confirmed connected. Once the connection is confirmed, recover/upload exact candidate bytes, stage via checksum-verified import, test hosted Chromium/WebKit and restart, then release to the existing root only after passing. Main is intentionally unchanged. User cannot download/start via the current sandbox link; do not send that link again as a hosted game.
