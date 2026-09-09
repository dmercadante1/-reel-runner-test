# GOTHIC HORROR — Production Art Direction

## Step 2 — Resolution / Pixel Scale / Framing

This document is the locked production target for the high-detail raster rebuild. It supersedes the programmer-art scale of earlier prototypes.

### Internal game resolution
- Logical gameplay canvas: **640 × 360** (16:9).
- Desktop output: integer 2× at 1280×720 when possible; larger displays scale by integer multiples / letterbox rather than smoothing.
- Mobile landscape: same 640×360 composition, fitted without changing world proportions.
- Phaser: `pixelArt: true`, antialias off, roundPixels on. CSS: `image-rendering: pixelated`.

### Visual density
- Target: high-end late-1990s 2D / 32-bit Gothic action game density.
- Pixel art must be authored at final logical pixel resolution. Do **not** draw vector shapes and pixelate them afterward.
- No procedural rectangle people, geometric heads, flat programmer-art platforms, or vector substitutes in production screenshots.
- Background painting may use many colors and painterly dithering, but individual pixels / clusters must remain visible at native scale.

### Hero scale
- Cameraman visible body height in gameplay: **92–104 logical pixels**, roughly 26–29% of screen height.
- Master animation cell: **128 × 128 px** minimum; allow **144 × 144** for camera/coat overhang if required.
- Realistic adult anatomy: approximately 7–7.5 heads tall. No chibi/block proportions.
- Shoulder movie camera must remain readable at normal gameplay zoom.

### Enemy scale bands
- Skeleton: 92–104 px tall, narrow silhouette.
- Ghoul / zombie: 96–110 px, hunched asymmetrical silhouette.
- Vampire: 100–112 px, tall elegant silhouette / coat or cape.
- Ghost: 100–125 px apparent height, floating and variable lower edge.
- Demon / monster: 110–145 px depending on type.
- Werewolf: 115–135 px, broad shoulders / digitigrade legs.
- No knights in the enemy roster.

### Camera framing
- Hero rests approximately **34% from the left edge** while moving right, leaving visual space for threats and the magnetic camera field.
- Ground baseline approximately **78–82% down the screen**.
- Normal gameplay should show approximately 5.5–7 hero-heights horizontally.
- Camera should move with restrained dead-zone behavior rather than constantly centering the hero.
- Capture/brace may bias framing slightly toward the aimed direction but must not zoom or smooth the pixels.

### Environment production sizes
- Each authored Gothic room/courtyard module: **1280–1920 logical px wide × 360–540 px high** before parallax extension.
- Separate raster layers: sky/far silhouette, architecture, playable masonry, props/vegetation, foreground occlusion, atmosphere/light masks.
- Foreground and playable surfaces must be illustrated assets with collision shapes laid over them; collision geometry itself should not be visible.

### Title
**GOTHIC HORROR**

Do not use “The Black House” in production UI or level titling.

### Visual acceptance test
Before a future playable build is presented as an art milestone, a still frame at 640×360 must read as authored high-detail Gothic pixel art even with the HUD hidden. If the scene depends on Phaser primitives to look finished, it fails this test.
