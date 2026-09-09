# MAN WITH A MOVIE CAMERA — Asset Rebuild Milestone

This branch is the new asset-driven Phaser build. It is intentionally modular so artwork, HUD, level data, controls, audio and capture tuning can be changed independently.

## Target
- Late-90s high-detail pixel art rather than procedural primitives.
- Desktop and mobile landscape from one codebase.
- Shoulder-camera hero.
- Magnetic camera cone captures enemies rather than shooting them.
- Horror vertical slice first; other genres inherit the systems only after this reaches the visual/gameplay bar.

## Structure
- `game/config.js` — tuning values and asset paths.
- `game/horror.js` — Horror level scene/gameplay.
- `game/ui.css` — responsive desktop/mobile HUD and controls.
- `assets/horror/` — authored background and sprite sheets.

Characters/backgrounds should be swappable without changing gameplay code. Capture strength, movement, enemy resistance and HUD presentation are separately configurable.