# MAN WITH A MOVIE CAMERA — Horror sprite contract

The Black House runtime is built to consume authored PNG sprite sheets with transparent backgrounds and nearest-neighbor rendering. Do not draw gameplay characters from Phaser geometry except as a temporary missing-asset fallback.

## Hero — cameraman
- File: `game/assets/horror/hero_sheet.png`
- Frame: 106 × 126 px
- Target visual scale in game: 0.82
- Realistic adult proportions; shoulder-mounted film camera; long coat; readable hands/feet; no oversized block head.
- Animation states are expected to remain independently replaceable. Current first-pass walk range: frames 0–5.
- Planned authored states: idle, walk, jump, brace/CAM, hurt, capture recoil.

## Skeleton
- File: `game/assets/horror/skeleton_sheet.png`
- Frame: 129 × 144 px
- Target scale: 0.78
- Planned states: idle, walk, magnetic resist, attack, capture collapse.

## Ghoul
- File: `game/assets/horror/ghoul_sheet.png`
- Frame: 120 × 140 px
- Target scale: 0.82
- Planned states: idle, shamble, lunge, magnetic resist, capture collapse.

## Armored undead knight
- File: `game/assets/horror/knight_sheet.png`
- Frame: 133 × 149 px
- Target scale: 0.88
- Planned states: idle, heavy walk, attack, brace/resist, capture collapse.

## Art target
Dense late-90s 2D pixel art: Symphony of the Night / high-end Neo Geo / CPS2 / 32-bit-era authored sprite quality. Painterly pixel shading, believable anatomy and cloth/armor weight, multiple value steps, selective highlights, and silhouettes that remain readable against moonlit Gothic backgrounds.

## Background
- File: `game/assets/horror/courtyard.png`
- Authored layers should preserve clear foreground/midground/background separation and work with parallax.
- Avoid smooth vector shapes. Masonry, foliage, statues, ironwork, windows, mist, candlelight, crypt details, and architectural wear should all be rendered as visible pixel art.

## Runtime rule
Art can improve repeatedly without rewriting gameplay. Keep frame dimensions stable where possible; animation ranges and scales belong in `game/config.js`.