window.MWCAM_CONFIG = {
  build: 'asset-rebuild-03',
  viewport: {
    desktop: { width: 1280, height: 720 },
    mobile: { width: 960, height: 540 },
    preferredOrientation: 'landscape'
  },
  player: {
    speed: 225,
    captureMoveSpeed: 92,
    jumpVelocity: -405,
    maxHealth: 5,
    invulnerabilityMs: 900,
    scale: 0.82,
    frame: { width: 106, height: 126, count: 6 },
    animations: {
      idle: { frames: [0], rate: 1 },
      walk: { start: 0, end: 5, rate: 10 },
      brace: { frames: [0], rate: 1 },
      jump: { frames: [1], rate: 1 },
      hurt: { frames: [4], rate: 1 }
    }
  },
  film: {
    max: 100,
    drainPerSecond: 11,
    recoverPerSecond: 8,
    captureReward: 13,
    emptyLockMs: 450
  },
  capture: {
    range: 470,
    spread: 150,
    pullStrength: 340,
    baseRate: 0.82,
    minScale: 0.14,
    beamColor: 0x8ce8ff,
    beamAlpha: 0.13,
    pulseMs: 90
  },
  enemies: {
    skeleton: { resistance: 1.0, speed: 64, scale: 0.78, frame: { width: 129, height: 144, count: 6 }, walkRate: 7 },
    ghoul: { resistance: 1.28, speed: 54, scale: 0.82, frame: { width: 120, height: 140, count: 6 }, walkRate: 6 },
    knight: { resistance: 1.75, speed: 46, scale: 0.88, frame: { width: 133, height: 149, count: 6 }, walkRate: 5 }
  },
  horror: {
    worldWidth: 4300,
    floorY: 610,
    checkpointX: 2250,
    platforms: [
      [720, 505, 330], [1410, 455, 290], [2130, 510, 350], [2880, 440, 300], [3560, 505, 340]
    ],
    spawns: [
      ['skeleton', 720, 500], ['ghoul', 1120, 520], ['skeleton', 1560, 510], ['knight', 2180, 500],
      ['ghoul', 2700, 480], ['skeleton', 3180, 520], ['knight', 3740, 500]
    ]
  },
  hud: {
    showHealth: true,
    showFilm: true,
    showCaptured: true,
    title: 'THE BLACK HOUSE',
    subtitle: 'OUTER COURTYARD'
  },
  audio: { musicVolume: 0.16, sfxVolume: 0.30 },
  assets: {
    background: 'assets/horror/courtyard.png',
    hero: 'assets/horror/hero_sheet.png',
    skeleton: 'assets/horror/skeleton_sheet.png',
    ghoul: 'assets/horror/ghoul_sheet.png',
    knight: 'assets/horror/knight_sheet.png'
  }
};