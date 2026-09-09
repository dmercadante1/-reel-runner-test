window.MWCAM_CONFIG = {
  build: 'production-raster-15c-batch1',
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
    scale: 0.78,
    frame: { width: 128, height: 128, count: 8 },
    animations: {
      idle: { frames: [0], rate: 1 },
      walk: { start: 0, end: 7, rate: 10 },
      brace: { frames: [0], rate: 1 },
      jump: { frames: [2], rate: 1 },
      hurt: { frames: [6], rate: 1 }
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
    skeleton: { resistance: 1.00, speed: 64, scale: 0.78, frame: { width: 128, height: 128, count: 4 }, walkRate: 7 },
    ghoul:    { resistance: 1.28, speed: 54, scale: 0.84, frame: { width: 128, height: 128, count: 4 }, walkRate: 6 },
    vampire:  { resistance: 1.48, speed: 70, scale: 0.82, frame: { width: 128, height: 128, count: 4 }, walkRate: 8 },
    monster:  { resistance: 1.85, speed: 42, scale: 1.02, frame: { width: 128, height: 128, count: 4 }, walkRate: 5 },
    werewolf: { resistance: 1.62, speed: 86, scale: 0.96, frame: { width: 128, height: 128, count: 4 }, walkRate: 9 },
    ghost:    { resistance: 1.36, speed: 58, scale: 0.90, frame: { width: 128, height: 128, count: 4 }, walkRate: 6, floating: true }
  },
  horror: {
    worldWidth: 4300,
    floorY: 610,
    checkpointX: 2250,
    platforms: [
      [720, 505, 330], [1410, 455, 290], [2130, 510, 350], [2880, 440, 300], [3560, 505, 340]
    ],
    spawns: [
      ['skeleton', 620, 500], ['ghoul', 1050, 520], ['vampire', 1510, 505],
      ['monster', 2070, 490], ['ghost', 2570, 470], ['werewolf', 3020, 505],
      ['skeleton', 3410, 520], ['vampire', 3780, 500], ['ghoul', 4060, 510]
    ]
  },
  hud: {
    showHealth: true,
    showFilm: true,
    showCaptured: true,
    title: 'GOTHIC HORROR',
    subtitle: 'LEVEL 1'
  },
  audio: { musicVolume: 0.16, sfxVolume: 0.30 },
  assets: {
    background: 'assets/horror/courtyard.png',
    hero: 'assets/production/characters/hero_walk.png',
    enemyAtlas: 'assets/production/characters/enemy_atlas.png'
  }
};