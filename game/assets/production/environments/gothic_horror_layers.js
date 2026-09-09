window.MWCAM_ENVIRONMENT = {
  id: 'gothic-horror',
  worldWidth: 4300,
  baseHeight: 720,
  layers: [
    { key: 'playPlane',   file: './assets/production/environments/gothic_playplane.png?v=native-scale-fix',  depth: -5, scrollFactor: 1.00, repeat: true, pixelScale: 1.25, y: 650, alpha: 1.00, productionReady: true },
    { key: 'foreground',  file: './assets/production/environments/gothic_foreground.png?v=native-scale-fix', depth:  6, scrollFactor: 1.08, repeat: true, pixelScale: 1.00, y: 700, alpha: 0.82, productionReady: true }
  ],
  atmosphere: { fogDepth: 4, moonDepth: -20, practicalLightDepth: 5 },
  collisionVisible: false,
  notes: 'Recovery build: valid 1024x128 raster strips render near native scale instead of being stretched to 720px tall. Full sky/castle/architecture restoration follows after gameplay verification.'
};