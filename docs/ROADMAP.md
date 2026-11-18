# Viewer roadmap: realistic and complete

**Goal: one unified campus.** The viewer shows a single scene: main campus, north campus and Sprague Library/Café Diem at their real coordinates, on shared terrain, with no scene picker. Today the browser export merges tiles from several source `.blend` files that share one Blender origin; the long-term goal is a single `.blend` (see "One scene" below).

What the browser viewer at <https://jamditis.github.io/campus-explorer/> still needs. Pick an unchecked item, open a PR that references it, and tick it in the same PR. Every visual change needs before/after screenshots of the same views (`tools/web-export/shoot.mjs` takes the standard five).

## Realism

- [x] Procedural sky with matching image-based light, so glass and metal reflect something
- [x] Sun shadows that follow the view (shadow box sized to view distance, texel-snapped)
- [x] AgX tone mapping and light exponential fog
- [x] Ambient occlusion (GTAO) on the High quality setting
- [x] World-space CC0 textures per material category (asphalt, concrete, brick, stucco, roof tile, pavers, lawn, mulch, gravel, stone, metal, wood), tinted by the model's own colours, with a second large-scale layer to hide tiling
- [x] Lot markings painted into the asphalt from the model's own world-XY line work (ws211c, ws213, ws213z layers)
- [x] Real-elevation far-field ground (the 4 km 3DEP skirt, exported with its under-campus geometry nodes) instead of a flat plane
- [x] Surface relief and roughness for the textured categories (derivative bump from each texture's displacement channel, roughness modulation)
- [x] Asphalt and concrete warmed and desaturated, with less sky reflection, so lots don't read blue at eye level
- [x] Instanced grass tufts near the camera on lawn surfaces (Medium/High, walk height only, fade out by ~18 m)
- [x] Window glass: darker tint, low roughness, stronger reflection; lamp and light glass left light
- [x] More facade materials get a category in the export (roof tile courses, eaves, soffits, fascia, bark, light massing)
- [ ] Glass: per-building tint and a fake interior so windows have depth
- [ ] Full normal maps (the bump comes from displacement only)
- [ ] Bake Blender procedural detail (stains, panel joints, dirt bands) into textures for the hero buildings
- [ ] Spruce and other conifer cards: check every conifer material exports its opacity map
- [x] Street trees at the edge of the far-field: instanced trees snapped down to the ground after load (filler crowns without ground stay hidden)

## Completeness

- [x] One unified scene: north campus merged into `models/main/` at its real coordinates (`n_` tiles), scene selector removed
- [x] Export refresh: `SCENE=main bash tools/web-export/build_web.sh` then `SCENE=north ...` (north merges against main's plan); prunes stale tiles, fails without publishing on any export error
- [x] Sprague Library and Café Diem: every object in `north/sprague_cafe_src.blend` is already in the main file at the same coordinates, so it ships with the main tiles
- [ ] Lawn grass particle systems (excluded from the export today; needs the instanced-grass item above)
- [ ] Interiors that matter (CCOM first floor, lounges): currently exported with their tiles but culled early by the small-object cull; give them their own tile and only load them in walk mode nearby
- [ ] People placeholders and task chairs (excluded)
- [ ] Daily refresh as a routine after the evening modelling session

## One scene

The browser merge rules live in `tools/web-export/make_chunks.py` (merge mode). Main wins wherever it has geometry: north objects with the same name as a main object are skipped; north ground and trees on main ground are skipped; a north building (grouped by name prefix) is skipped when most of it overlaps a main building; north terrain is clipped to the 10 m cells main's ground doesn't cover. Alignment was checked against OSM: Montclair Heights station (OSM node at local −454, −266) sits on north's platform objects, and the shared Sprague objects have identical coordinates in both files.

- [ ] Seams to check: the clipped north terrain meets main's terrain on a 10 m cell staircase (both are 1 m LiDAR DTM, so heights agree; small cracks or overlaps are possible along the edge); north detail on buildings main also has (Dickson, Finley, Feliciano, Life Hall) is dropped in favour of main's version
- [ ] Merge the north campus into the main `.blend` (owned by the hourly modelling sessions, not the viewer). Once merged, drop the merge mode and export one file
- [ ] Retire `north/sprague_cafe_src.blend` once nothing references it

## Performance

- [x] Meshopt geometry compression, WebP textures, GPU instancing of repeated meshes
- [x] Nearest tiles load first; far-field ground and context load before everything else
- [x] Screen-size culling of small meshes (a cheap LOD) and a Low / Medium / High quality toggle
- [ ] KTX2 (Basis) textures: KTX-Software 4.4 is on the export box, but `gltf-transform etc1s` skips the existing WebP textures and the UASTC output is larger than WebP; needs a PNG intermediate step
- [ ] Real LODs: decimated copies of buildings and impostor cards for trees past ~300 m
- [ ] Per-instance culling for the big instanced tree meshes (currently whole-tile)
- [ ] Measure on a mid-range laptop GPU and record fps per quality level here
