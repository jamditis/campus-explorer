# Viewer roadmap: realistic and complete

**Goal: one unified campus.** The viewer shows a single scene: main campus, north campus and Sprague Library/Café Diem at their real coordinates, on shared terrain, with no scene picker. Today the browser export merges tiles from several source `.blend` files that share one Blender origin; the long-term goal is a single `.blend` (see "One scene" below).

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
- [x] Surface relief and roughness for the textured categories (derivative bump from each texture's displacement channel, roughness modulation)
- [x] Asphalt and concrete warmed and desaturated, with less sky reflection, so lots don't read blue at eye level
- [x] Instanced grass tufts near the camera on lawn surfaces (Medium/High, walk height only, fade out by ~18 m)
- [x] Window glass: darker tint, low roughness, stronger reflection; lamp and light glass left light
- [x] More facade materials get a category in the export (roof tile courses, eaves, soffits, fascia, bark, light massing)
- [x] Window glass with fake rooms behind it (interior mapping: 3.6 m bays, 3.4 m storeys, some rooms lit), reflection by Fresnel
- [x] Normal maps (ambientCG NormalGL, triplanar) for the textured categories; displacement bump stays for stone and metal
- [ ] Glass: per-building tint and room layouts that follow the real floor heights
- [ ] Bake Blender procedural detail (stains, panel joints, dirt bands) into textures for the hero buildings
- [ ] Spruce and other conifer cards: check every conifer material exports its opacity map
- [x] Street trees at the edge of the far-field: instanced trees snapped down to the ground after load (filler crowns without ground stay hidden)

## Completeness

- [x] Far-field land cover over the 4 km skirt from OpenStreetMap (woods, parks, water, roads, mapped buildings), about 36,000 far-field trees on wooded and residential land, and extruded houses (`tools/web-export/landcover.py`)
- [x] Far-field buildings are real footprints only: OpenStreetMap where mapped, otherwise Microsoft Global ML Building Footprints (ODbL). Heights from USGS 3DEP LiDAR where it covers the footprint: the 40th percentile of the highest last return (class-6 building points where a dataset has them; neither NJ cloud here does) inside the footprint shrunk by 1 m, minus the surrounding ground. Last returns and the shrunk footprint keep overhanging tree canopy out, which had turned some houses into towers. A height above what the footprint plausibly allows (11 m under 250 m², 15 m under 600 m², 24 m under 2,500 m², unless OSM building:levels or height says more) is capped and the building goes in the UNVERIFIED mesh; elsewhere the footprint layer's own height estimate, scaled to match the LiDAR-measured buildings (those, the capped ones and the few OSM buildings with no height anywhere, are in the separate `far_houses_height_UNVERIFIED` mesh). The generated placeholder houses are gone; where no footprint exists the ground stays bare
- [ ] Far-field LiDAR vintage: heights come from the 2017 NW 6-County cloud (public Entwine bucket) and the 2014 Sandy cloud (both streamed from the public Entwine bucket); 98% of far buildings are covered. The 2023 NE 6-County cloud is newer but only on rockyweb (rate-limited to one slow connection); swap it in when it reaches the Entwine bucket

- [x] One unified scene: north campus merged into `models/main/` at its real coordinates (`n_` tiles), scene selector removed
- [x] Export refresh: `SCENE=main bash tools/web-export/build_web.sh` then `SCENE=north ...` (north merges against main's plan); prunes stale tiles, fails without publishing on any export error
- [x] Sprague Library and Café Diem: every object in `north/sprague_cafe_src.blend` is already in the main file at the same coordinates, so it ships with the main tiles
- [x] Place names, search, labels, minimap, guided tour and landmark hunt (names and positions from OpenStreetMap)
- [x] Georeferenced readout (latitude, longitude, NAVD88 elevation), compass, scale bar and measuring tool
- [ ] Per-object names and evidence notes in the viewer: the exporter joins meshes by material, so a clicked surface cannot be traced to its Blender object. Export a `places`-style index of objects (name, bounds, UNVERIFIED flag) from Blender before joining
- [ ] Lawn grass particle systems (excluded from the export today; needs the instanced-grass item above)
- [ ] Interiors that matter (CCOM first floor, lounges): currently exported with their tiles but culled early by the small-object cull; give them their own tile and only load them in walk mode nearby
- [ ] People placeholders and task chairs (excluded)
- [ ] Daily refresh as a routine after the evening modelling session

## One scene

The browser merge rules live in `tools/web-export/make_chunks.py` (merge mode). Main wins wherever it has geometry: north objects with the same name as a main object are skipped; north ground and trees on main ground are skipped; a north building (grouped by name prefix) is skipped when most of it overlaps a main building; north terrain is clipped to the 10 m cells main's ground doesn't cover. Alignment was checked against OSM: Montclair Heights station (OSM node at local −454, −266) sits on north's platform objects, and the shared Sprague objects have identical coordinates in both files.

- [x] Terrain seam: north terrain is trimmed against main's actual ground faces at 1 m (not 10 m squares) and the faces along main's edge are kept 12 cm lower, tucked under main's edge, so there are no cracks and no z-fighting
- [ ] North detail on buildings main also has (Dickson, Finley, Feliciano, Life Hall) is dropped in favour of main's version; it comes back when the hourly sessions merge north into main
- [ ] Merge the north campus into the main `.blend` (owned by the hourly modelling sessions, not the viewer). Once merged, drop the merge mode and export one file
- [ ] Retire `north/sprague_cafe_src.blend` once nothing references it

## Performance

- [x] Meshopt geometry compression, WebP textures, GPU instancing of repeated meshes
- [x] Streaming: the view opens after the far-field ground and the four nearest tiles; the rest load nearest-first around the view, with geometry decoded in workers
- [x] Draw on demand (nothing is drawn while the view is still); shadows redrawn only when the sun, the focus or the scene changes
- [x] Adaptive resolution while the view moves; full resolution when it stops
- [x] Collision BVHs built on demand per mesh, big terrain meshes split into 96 m cells
- [x] Screen-size culling of small meshes (a cheap LOD) and a Low / Medium / High quality toggle
- [ ] KTX2 (Basis) textures: KTX-Software 4.4 is on the export box, but `gltf-transform etc1s` skips the existing WebP textures and the UASTC output is larger than WebP; needs a PNG intermediate step
- [x] Per-instance culling for instanced trees (frustum and distance), with low-poly crown impostors past 220 / 420 / 700 m (Low / Medium / High) out to 2.6 km
- [ ] Decimated copies of buildings for far tiles
- [x] Phones (lite profile): only the nine tiles nearest the view stay in memory; far tiles are unloaded as the view moves
- [ ] Phones: show the far versions (`lod/`, 41 MB for the whole campus) of the tiles outside the memory budget, so the lite profile still shows the full campus
- [ ] Measure on a mid-range laptop GPU and record fps per quality level here
