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

- [x] Southwest corner, phase 1 (`blender/scripted/`, `sw_` tiles): Normal Avenue with the grade crossing, the station lot, Carlisle Road, the whole of Sprague Field with its 2025 markings, the west grandstand and press box, the east bleachers, light poles, fences and the hedge. Scripted from public evidence (2025 drone and station photographs, NJ 2020 ortho, 3DEP LiDAR 2017 and 2014, OpenStreetMap); inferred parts are UNVERIFIED in the object names and plan files
- [x] North-east district (`blender/scripted/northeast/`): CarParc Diem, Dinallo Heights, Machuga Heights, the Student Recreation Center, the District Energy Plant, six parking lots with their stalls, Yogi Berra Drive, Webster Road and the walks, the softball field and tennis courts with rule-book lines, two transmission towers, trees from the LiDAR canopy. Outlines and heights are from the LiDAR; building looks (colours, window grids, floor counts) are estimates, UNVERIFIED
- [x] Stadium district (`blender/scripted/stadium/`): Yogi Berra Stadium with its 2024 synthetic turf on the fitted 2020 layout, seating sections, outfield wall, foul poles, light poles and scoreboard; the Yogi Berra Museum; the running track (8 lanes, fitted to the lane lines) and the soccer field with rule-book lines; the softball backstop, seats and clubhouse; three lots, Yogi Berra Drive and Webster Road to the loop. Building looks, fence heights and the track's red tone are estimates, UNVERIFIED
- [x] West strip (`blender/scripted/west/`): Carlisle Road north of the south-west area as one fitted arc, Lots 30 and 30S with fitted stall rows, the Webster Road mouth, the College Avenue junction with its islands, stop bars and crosswalk, Lot 33, walks, lamps and trees. The south-west area's Carlisle Road is refitted where it was off (north end, centre line, east edge, lane dashes)
- [x] The Village (`blender/scripted/village/`): Clove Road, the Village Road loop and 2.6 km of walks; Hawk Crossings, Sinatra Hall, Williams, Fenwick, Paul and Count Basie halls and the Abbott and Costello Center from LiDAR outlines and roof heights; nine lots with about 850 fitted stalls; the three solar canopies over Lot 61; the detention basin; trees from the LiDAR canopy. The four zones were digitised in parallel and then checked against each other by an independent review, twice. Building looks, lamp heights and the stalls under the canopies are estimates, UNVERIFIED
- [x] Overlook Corporate Center block (`blender/scripted/overlook/`): the 12-storey octagonal office tower with its green roof and stepped tiers (many university administrative offices are in it), the east wing, the garage (6 levels), the east lot, the loop road and drives, the quarry ground toward the stadium. Outlines and heights from the LiDAR; facades are estimates and the east lot's stall rows are inferred (the paint cannot be read in the 2020 ortho), UNVERIFIED
- [x] Fix-up pass over the six scripted areas (2026-11-20). Format: sunken roof areas and a second roof colour (`wells`), garage ramp bays, paint on a deck's roof, `water` surfaces, `arrow`, `crosswalk` and `text` markings, a solid concrete seating `bowl`, `free_edges`. Used for: the Overlook tower's roof well, its wing's white roof in a green rim and the garage roof (201 stalls); CarParc Diem's roof (208 stalls) and ramp; the Village basin pond, pool and pool fence; Yogi Berra Stadium's concrete bowl; lacrosse and field hockey lines on Sprague Field and lacrosse lines on the soccer field (seen in the ortho and photos, sized by the rule books); track lane numbers; lane arrows, crosswalks and stop bars read from the ortho in every area; the east platform canopy; two walled enclosures and a third transmission tower in the north-east; Webster Road beyond its mouth, the Feliciano drop-off loop and the lot by University Hall
- [ ] Overlook block: lamps (no pole returns, no shadows outside the deck's shadow); the east lot's stall rows stay inferred (2023 NAIP cars suggest two rows lie 1 to 3 m further west); solar panels on the wing's south roof; the tower's flat top is up to 6 m too wide on its four short sides; the pond lies outside the footprint
- [ ] The Village: lamps along roads and walks (two placed; the rest cannot be told from bollards and signs), stop bars at the lot exits and pavement words (not readable), roof overhangs, a stream under the woods (OSM, not visible), the east rim of the terraced basin by the Clove Road junction and the north solar canopy's corner (both past the footprint); the TV Tower building and the building beside it at the south end are left outside; the big lot and bus lot north-west of Lot 61 belong to a later area
- [ ] West strip: stalls along the deck's south face (hidden by its roof), the shadowed south half of the lot by University Hall, pavement words under the junction arrows, a hatched accessible aisle in Lot 33; a step of about 0.5 m where the edge leaves University Hall's north-west corner (the main model's ground beside the building stands 1.3 to 2.9 m above the LiDAR; lower it there in the main file); a main-model tree stands in the aisle east of the loop's tail
- [ ] Stadium district: the 2024 bullpens, hitting facility and storage building (2025 satellite imagery shows them behind the centre-field wall, but its registration is 2 to 7 m off, so no position is fixed; the 2020 storage building there is probably gone), single chairs, handrails and vomitories of the bowl, the museum's roof overhang over the first-base seats, the hawk logo (the university's artwork), unread marks in the track chute; Floyd Hall Arena and the quarry ground north of y 1105
- [ ] North-east district: the power line's conductors (no wire returns in the 2017 or 2014 LiDAR, so no sag; arm heights are measured and recorded in the plan notes), light poles on the deck roof, hairpin row ends and arrows on the deck roof (not readable), equipment inside the enclosures; the enclosure east of the Energy Plant follows the 2017 LiDAR walls, while the 2020 ortho shows a wider band round it (a photo would settle it); the third tower is of another type than the lattice kit
- [ ] Southwest corner: the midfield logo (the university's artwork), field hockey penalty spots and hash marks, the brick band on the east platform (the platform is the north model's), words before the Carlisle Road arrows (not readable)
- [ ] Viewer: water reflects the sky only; the pool has the pond's colour. A lawn-coloured wedge of the main model's context terrain stands over the north-east corner of Pittser Field's turf (trim it in `make_chunks.py`). The main model's reed grass is tinted as lawn
- [ ] North model: the track and platforms stand about 0.65 m above the LiDAR ground; the southwest build lifts its ground to them along the corridor until the track is lowered
- [ ] Toward the communication school: Carlisle Road north of the field, Lot 42 north part, the maintenance building, then the Red Hawk Deck, College Avenue, Cole Hall and CCOM in the main model

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
- [x] Unused vertex data dropped from tiles (`tools/web-export/compact.mjs`): `gltf-transform optimize --instance` left a second, unreferenced copy of every instance transform in the files
- [ ] Decimated copies of buildings for far tiles
- [x] Phones (lite profile): only the nine tiles nearest the view stay in memory; far tiles are unloaded as the view moves
- [ ] Phones: show the far versions (`lod/`, 41 MB for the whole campus) of the tiles outside the memory budget, so the lite profile still shows the full campus
- [x] Trees used 2 to 4 times in a tile are instances (`tree_instance.mjs`), instance rotations are packed as 16-bit values, far versions carry half-size images
- [ ] Share repeated images between tiles: 18 of 20 MB of tile images are byte-identical repeats (the main leaf texture alone is 130 copies); write each once and point the tiles at it
- [ ] Tree trunks and branches are 13.8 M of the campus's 36 M triangles (measured 2026-11-19): a middle level of detail for trees between the full mesh and the crown impostor
- [ ] Lighter far field: `skirt.glb` is 4.2 M triangles and `context.glb` 2.2 M plus 3.1 M in instances, drawn in every view. A coarser skirt away from the campus would cut the fixed cost of each frame most
- [ ] Measure on a mid-range laptop GPU and record fps per quality level here
