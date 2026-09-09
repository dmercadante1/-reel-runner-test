window.MWCAM_ENVIRONMENT = {
  id: 'gothic-horror',
  worldWidth: 4300,
  baseHeight: 720,
  layers: [
    { key: 'sky',          file: './assets/production/environments/gothic_sky.png',          depth: -60, scrollFactor: 0.04, repeat: true,  heightScale: 1.08, y: 720, alpha: 1.00, productionReady: true },
    { key: 'castle',       file: './assets/production/environments/gothic_castle.png',       depth: -50, scrollFactor: 0.13, repeat: true,  heightScale: 1.00, y: 720, alpha: 0.92, productionReady: true },
    { key: 'architecture', file: './assets/production/environments/gothic_architecture.png', depth: -30, scrollFactor: 0.38, repeat: true,  heightScale: 0.98, y: 720, alpha: 1.00, productionReady: true },
    { key: 'playPlane',    file: './assets/production/environments/gothic_playplane.png',    depth:   0, scrollFactor: 1.00, repeat: true,  heightScale: 1.00, y: 720, alpha: 1.00, productionReady: true },
    { key: 'foreground',   file: './assets/production/environments/gothic_foreground.png',   depth:  20, scrollFactor: 1.10, repeat: true,  heightScale: 1.03, y: 724, alpha: 0.96, productionReady: true }
  ],
  atmosphere: {
    fogDepth: 14,
    moonDepth: -55,
    practicalLightDepth: 12
  },
  collisionVisible: false,
  notes: '15D-3C composition tune. Raster layers provide all visible Gothic architecture; collision geometry remains independent and invisible in final presentation.'
};
