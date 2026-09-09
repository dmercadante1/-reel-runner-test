# MAN WITH A MOVIE CAMERA — modular build

This branch deliberately separates art, tuning and systems so changes do not require full rewrites.

## Editable pieces
- `game/config.js`: movement, jump, capture beam, enemy resistance/speed, HUD toggles, audio levels, asset paths.
- `assets/characters/`: replace a character sheet without changing level/gameplay code.
- `assets/horror/`: replace/revise background layers independently.
- `game/levels/horror.js`: encounter positions, platforms, doors and collision only.
- `game/systems/capture.js`: magnetic camera mechanic only.
- `game/ui/hud.js`: HUD only.
- `game/input.js`: desktop keyboard + mobile touch/gamepad mapping only.

## Input targets
Desktop: A/D or arrows move, W/up jump, Space/C camera capture, F fullscreen.
Mobile landscape: left/right, jump, CAM; safe-area aware. Portrait shows Rotate to Play.

## Art target
Late-1990s high-end 2D console/arcade pixel art: authored sprite sheets and background layers. No procedural block characters in production builds.