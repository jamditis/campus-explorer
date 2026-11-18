# Viewer roadmap: realistic and complete

What the browser viewer at <https://jamditis.github.io/campus-explorer/> still needs. Pick an unchecked item, open a PR that references it, and tick it in the same PR. Every visual change needs before/after screenshots of the same views (`node tools/viewer-test/shoot.mjs <outdir>` takes the standard set). The viewer's architecture is in [VIEWER.md](VIEWER.md).

## Realism

- [x] Procedural sky with matching image-based light, so glass and metal reflect something
- [x] Sun shadows that follow the view (shadow box sized to view distance, texel-snapped)
- [x] ACES filmic tone mapping and light exponential fog
- [x] Sunlight from the real solar position for any date and time; lamps glow after dark
- [x] Ambient occlusion (GTAO) on the High quality setting
- [x] World-space CC0 textures per material category (asphalt, concrete, brick, stucco, roof tile, pavers, lawn, mulch, gravel, stone, metal, wood), tinted by the model's own colours, with a second large-scale layer to hide tiling
- [x] Lot markings painted into the asphalt from the model's own world-XY line work (ws211c, ws213, ws213z layers)
- [x] Real-elevation far-field ground (the 4 km 3DEP skirt, exported with its under-campus geometry nodes) instead of a flat plane
- [ ] Normal and roughness maps for the textured categories (currently colour only)
- [ ] Instanced grass blades near the camera on lawn surfaces (cheap, fade out by 30 m)
- [ ] Glass: per-building tint and a fake interior/reflection so windows don't read as flat grey-blue
- [ ] Facades without a category fall back to flat colour: give the main building materials a category in the export (see `CATS` in `tools/web-export/export_web.py`)
- [ ] Bake Blender procedural detail (stains, panel joints, dirt bands) into textures for the hero buildings
- [ ] Spruce and other conifer cards: check every conifer material exports its opacity map
- [ ] Street trees at the edge of the far-field: confirm none float now that the skirt is back

## Completeness

- [x] One campus scene in the viewer: main and north tiles joined by `tools/web-export/unify.py` (no scene switch)
- [ ] Merge the main and north Blender files and export one scene. Until then, where both files cover a 160 m square only one file's tile is shown, so some objects near the seams are missing (UNVERIFIED seams; the dropped tiles are listed under `overlaps` in `models/manifest.json`)
- [x] Export refresh: `SCENE=main bash tools/web-export/build_web.sh` then `SCENE=north ...`; prunes stale tiles, fails without publishing on any export error, rewrites the campus manifest
- [x] Place names, search, labels, minimap, guided tour and landmark hunt (names and positions from OpenStreetMap)
- [x] Georeferenced readout (latitude, longitude, NAVD88 elevation), compass, scale bar and measuring tool
- [ ] Per-object names and evidence notes in the viewer: the exporter joins meshes by material, so a clicked surface cannot be traced to its Blender object. Export a `places`-style index of objects (name, bounds, UNVERIFIED flag) from Blender before joining
- [ ] Lawn grass particle systems (excluded from the export today; needs the instanced-grass item above)
- [ ] Interiors that matter (CCOM first floor, lounges): currently exported with their tiles but culled early by the small-object cull; give them their own tile and only load them in walk mode nearby
- [ ] People placeholders and task chairs (excluded)
- [ ] Shared Sprague/Café Diem source scene (`north/sprague_cafe_src.blend`) as its own scene or merged into north
- [ ] Daily refresh as a routine after the evening modelling session

## Performance

- [x] Meshopt geometry compression, WebP textures, GPU instancing of repeated meshes
- [x] Streaming: the view opens after the far-field ground and the four nearest tiles; the rest load nearest-first around the view, with geometry decoded in workers
- [x] Draw on demand (nothing is drawn while the view is still); shadows redrawn only when the sun, the focus or the scene changes
- [x] Adaptive resolution while the view moves; full resolution when it stops
- [x] Collision BVHs built on demand per mesh, big terrain meshes split into 96 m cells
- [x] Screen-size culling of small meshes (a cheap LOD) and a Low / Medium / High quality toggle
- [ ] KTX2 (Basis) textures: needs `toktx` on the export box; cuts GPU memory roughly 4x
- [ ] Real LODs: decimated copies of buildings and impostor cards for trees past ~300 m
- [ ] Per-instance culling for the big instanced tree meshes (currently whole-tile)
- [ ] Unload far tiles on phones (everything stays in memory once loaded)
- [ ] Measure on a mid-range laptop GPU and record fps per quality level here
