window.MWCAM_ENVIRONMENT = {
  id: 'gothic-horror',
  worldWidth: 4300,
  baseHeight: 720,
  layers: [
    { key: 'playPlane',   file: './assets/production/environments/gothic_playplane.png',  depth: -5, scrollFactor: 1.00, repeat: true, heightScale: 1.00, y: 720, alpha: 1.00, productionReady: true },
    { key: 'foreground',  file: './assets/production/environments/gothic_foreground.png', depth:  6, scrollFactor: 1.08, repeat: true, heightScale: 0.34, y: 720, alpha: 0.88, productionReady: true }
  ],
  atmosphere: {
    fogDepth: 4,
    moonDepth: -20,
    practicalLightDepth: 5
  },
  collisionVisible: false,
  notes: 'Step 20 hotfix: invalid/corrupted sky, castle and architecture binaries temporarily excluded. Valid play plane and foreground remain; foreground is below player/enemy depth so gameplay stays visible.'
};
