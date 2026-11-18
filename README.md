# Campus explorer · Montclair State

A browser preview of the work-in-progress 3D model of the Montclair State University campus, built in Blender as part of an NJ campus modelling project. Orbit, fly, or walk (first or third person) through the main campus.

Live: https://jamditis.github.io/campus-explorer/

## What this is

A static three.js viewer with no build step. `index.html`, `style.css` and `app.js` are the viewer; `models/main/` holds the campus as meshopt-compressed GLB tiles (`context.glb` for terrain and surroundings, plus 160 m tiles `t_<x>_<y>.glb`) and a `manifest.json` with the source snapshot time. three.js r170, its GLTF loader, the meshopt decoder and three-mesh-bvh are vendored in `vendor/` under their MIT licences. Every file is under 95 MB.

This is a work in progress, not a survey or an as-built record. The browser edition simplifies the Blender model: procedural materials become flat colours, only CC0 ambientCG textures and authored leaf atlases are kept, trees are thinned, lawn grass and some interiors are left out, and the distant ground is a plain plane.

Reference photographs, aerial or ortho imagery and .blend files are not included. The exporter only keeps images on an allowlist and refuses anything named ortho, naip, aerial, photo or mask.

## Refreshing after a day's modelling

On the modelling box (read-only against the main .blend, inside a session that holds the scene lock):

1. `echo ws2xx > /workspace/nj-scenes/web/SOURCE_VERSION` and put the main file's save time (ET) in `/workspace/nj-scenes/web/SOURCE_SAVED`.
2. `bash /workspace/nj-scenes/scripts/web/build_web.sh` plans tiles, exports each tile in its own low-memory Blender process, tints leaves, optimizes with gltf-transform (meshopt, webp, join, instance) and writes the manifest into `/workspace/nj-scenes/web/campus/`.
3. Test with `python3 -m http.server` in that folder and `node /workspace/nj-scenes/scripts/web/shoot.mjs` for headless screenshots.
4. Copy the folder over this repo's contents (keep this README and `.nojekyll`), commit and push. GitHub Pages redeploys in a minute or two.

Map data © OpenStreetMap contributors (ODbL). Elevation from public NJ/USGS LiDAR.
