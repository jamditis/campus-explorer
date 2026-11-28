// The campus tiles as the site build's manifest lists them (tools/web-export/manifest.py), from the committed tile
// names: manifest.json is built with the site, not committed (#136). Not a test file itself.
import { readdirSync } from 'node:fs';

const TILE = 160; // metres, as manifest.py
/** [{ file, center: [x, z] }] for every centred tile in models/main (n_, sw_ or plain t_<x>_<y>.glb). */
export function campusTiles() {
  const dir = new URL('../models/main/', import.meta.url);
  return readdirSync(dir).flatMap(file => {
    const m = /^(?:n_|sw_)?t_(-?\d+)_(-?\d+)\.glb$/.exec(file);
    return m ? [{ file, center: [(+m[1] + 0.5) * TILE, -(+m[2] + 0.5) * TILE] }] : [];
  });
}
