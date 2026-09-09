window.MWCAM_ENVIRONMENT = {
  id: 'gothic-horror',
  worldWidth: 4300,
  baseHeight: 720,
  layers: [
    { key: 'sky',        file: './assets/production/environments/gothic_sky.png',        depth: -60, scrollFactor: 0.06, repeat: true },
    { key: 'castle',     file: './assets/production/environments/gothic_castle.png',     depth: -50, scrollFactor: 0.16, repeat: true },
    { key: 'architecture',file:'./assets/production/environments/gothic_architecture.png',depth: -30, scrollFactor: 0.42, repeat: true },
    { key: 'playPlane',  file: './assets/production/environments/gothic_playplane.png',  depth:  0, scrollFactor: 1.00, repeat: true },
    { key: 'foreground', file: './assets/production/environments/gothic_foreground.png', depth: 20, scrollFactor: 1.12, repeat: true }
  ],
  atmosphere: {
    fogDepth: 14,
    moonDepth: -55,
    practicalLightDepth: 12
  },
  collisionVisible: false,
  notes: '15D production target: authored raster layers provide all visible Gothic architecture. Phaser geometry is collision-only and must remain invisible.'
};
