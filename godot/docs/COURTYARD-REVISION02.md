# Courtyard revision 02

Latest user notes implemented in the same stage; other stages and published previews remain unchanged.

- Eight screens (5120 logical units), capture quota eight, four ordinary reel pickups, three collectible hearts, two silver reels. Hearts replace the prior automatic four-capture heal.
- Hold Down/S or D-pad down to crouch, move at 42% speed, and use a 38-unit collider. Headroom query prevents standing through a ceiling. Down+Jump drops through one-way ledges; existing service passage remains Down.
- Four health portraits; healthy, tired, cut/bloody lip, bruised/exhausted. New crouch movement/filming and upward-camera poses preserve the approved face and clothing.
- Exposed capture 0.42s skeleton / 0.60s wolf, defensive rate 20%. Jump-acquired lock persists within 230 horizontal / 145 vertical units while exposed; ends when vulnerability ends or Film is released. Upward pose/beam follow elevated targets.
- Enemy-body separation and 0.32s hit recoil, with a short vertical bounce; crouching evades the skeleton's high slash. General projectile visuals remain outside this two-enemy stage (neither throws fireballs).
- New unstretched 3:1 mountain panorama, new grounded masonry kit and opaque trees, four HUD portraits and raster beam/film artwork. World-space architecture origins remain fixed. Rendering scroll now uses a CanvasLayer; physics world does not move with the camera. Collectibles draw in front of fountain/architecture. New artwork replaces the earlier stretched sky and translucent physical scenery.
- Kenney CC0 recorded Foley for footsteps, cloth/jump, landing, impact, mechanical camera/reload, reel and heart pickups; pitch-varied creaks/swishes for enemies. Old simple music is muted pending later composition. No Nintendo audio used. Audio listening on user's devices remains unverified.
- Full screen button and F shortcut. In-app desktop browser confirmed native fullscreen at 1280×800 viewport with 1280×720 game canvas.

18 focused native checks pass; arranged-state mechanics plus input-only traversal across eight screens with enemies removed for geometry isolation. Four actual browser input checks pass (crouch, stand, backward film, capture). Direct Safari/iPhone access remains unavailable as documented in prior handoff, so verification is explicitly in-app Chromium fallback; no slow-machine matrix or new permission request. Source changes after these gameplay checks only refine aiming art and collectible draw order; Final export visually inspected; served-byte verification recorded with the published preview. All elevated ledges now have grounded architectural supports.
