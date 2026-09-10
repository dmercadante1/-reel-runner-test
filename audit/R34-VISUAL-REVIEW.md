# R3/R4 final visual review

The initial R3/R4 builds passed 230 staging checks and 91 served-site checks, but manual review of the actual Cathedral screenshot then caught a semantic asset error: source-board labels were being tiled into the interior.

The source file in the previously approved R2 archive is a 1099x733 preview of the 1536x1024 board used for crop coordinates. Both files are valid PNGs, so file/CRC/dimension checks on the OUTPUT did not catch this. The correction explicitly normalizes the input to its documented coordinate space BEFORE cropping columns, windows, arches, masonry and sky rows. Original archive data is not relabeled or overwritten. New source-coordinate provenance is saved in game/rebuild-r34/evidence/art-coordinate-review.json. No OCR or arbitrary black-box replacement was used.

The corrected raster cathedral and catacombs have been visually inspected locally: masonry, complete pillars, stained glass, torchlit alcoves and statues are now present, without presentation-board headings. Actual CI gameplay screenshots must also be inspected before promotion. These staged fixes use new immutable game/releases/gothic-r3a/ and gothic-r4a/ paths; original R2/R3/R4 releases remain intact.

A final locomotion correction also removes the filming state from ahead of movement in the grounded animation priority. Moving while filming now uses the twelve-frame textured leg stride; standing still uses the brace cycle. Hurt, jump and capture recoil still override movement. The independent tests/locomotion.py exercises both editions with real keyboard input, tracks at least three different stride frames during camera use, checks that light remains on, checks return to stationary brace, and checks jumping while filming. No physics or combat strength is changed by this correction.

This record is not a new passing release report. Use the fresh release-gates.json, actual screenshots, served-build hash checks and the eventual LIVE checkpoint to determine final release status. Automated functional checks are not a substitute for visual/art review.
