# Scripted builds

Parts of the campus built whole by script from plan files: one folder per area, one `.blend` for all of them, exported to the viewer as a third source next to the main and north models (`sw_` tiles). Every run rebuilds the whole file from the plan files and scripts here, so the modelling box can make the same objects from this checkout.

| Area folder | What it holds |
|---|---|
| `southwest/` | Montclair Heights station surroundings, Normal Avenue, Carlisle Road, Sprague Field |
| `northeast/` | CarParc Diem, Dinallo Heights, Machuga Heights, the Student Recreation Center, the District Energy Plant, the softball stadium, the tennis courts, and the lots and roads between them |

The engine (`*.py` in this folder) is shared. An area is a folder with a `footprint.json`; object names carry the area or a zone name, and zone names are unique across areas.

Evidence order here: public photographs, then the NJ 2020 ortho (plan), then 3DEP LiDAR (heights), then OpenStreetMap. Joe's photos beat all of these when they exist. Nothing in this folder may be presented as measured unless it was: inferred sizes and positions carry `UNVERIFIED` in the object name and a note in the plan file.

## Run it

```sh
# 1. Evidence per area, into a folder outside the repository named as the area (/workspace/data/<area>)
python3 tools/evidence/fetch.py ortho southwest -560 -380 -200 -50 0.15
python3 tools/evidence/fetch.py lidar southwest -560 -380 -200 -50 0.5
python3 tools/evidence/fetch.py osm   southwest -560 -380 -200 -50

# 2. Paint sheets (system Python with Pillow), then the .blend (Blender 4.5)
#    for every area (or --areas NAME,NAME)
python3 blender/scripted/paint.py /workspace/data
blender -b --factory-startup --python blender/scripted/build.py -- /workspace/data OUT/montclair_southwest.blend

# 3. Tiles for the viewer (see tools/web-export/build_web.sh for the box layout it expects)
SCENE=sw bash tools/web-export/build_web.sh OUT/montclair_southwest.blend
```

`python3 -m unittest discover -s tests/py` checks the geometry helpers and every plan file. CI runs it.

`<area>/edge_heights.json` holds the height of the neighbouring models' ground along the footprint, so the new ground meets it flush. Make it again only when the footprint or the neighbours change, from tiles that still have their ground there (before `supersede.mjs` ran on them):

```sh
node tools/evidence/dump_tiles.mjs /workspace/data/southwest/tiles -560 -380 -200 -50 models/main
python3 tools/evidence/plan.py /workspace/data/southwest/tiles 1.0 --name ground --only "(?i)terrain|ground|skirt|lawn|asphalt|patch|apron|carriageway|walk|turf|fill|platform|ballast" --skip "(?i)far_houses|crown|Tree|roof|bleacher|field_lines|endzone"
python3 blender/scripted/edge.py southwest /workspace/data/southwest/tiles
```

## How it joins the other models

- **One ground.** Inside the footprint (`<area>/footprint.json`) an area owns the ground. `tools/web-export/supersede.mjs` takes the other sources' ground out of their tiles there and lowers the corners of the triangles that reach in, so the old ground dips under the new edge. The rules (which meshes are ground, which things are replaced) are in `<area>/footprint.json` under `supersede`.
- **Changing the footprint.** Removed triangles cannot be put back. If `<area>/footprint.json` changes, export the main and north tiles again (or restore them from before the scripted build) before `SCENE=sw`; `supersede.mjs` stops with a message if a tile was done with other rules.
- **What stays.** The north model's station (tracks, ballast, platforms, shelter, catenary, fences, signs) and its retaining wall at the field's north-east corner stay as they are. The main model's paved corner south-east of the field (drive mouth, dumpster enclosure, shrubs) stays too: the footprint runs round it.
- **What is replaced.** The main model's partial Sprague Field (ws167 to ws189: south-east quarter of the turf, lines, end zone blocks, a goalpost, the south part of the east bleachers, one light pole). Its lines lie about 14 degrees off the field in the 2020 ortho; this build fits the whole field to the ortho (0.15 m corner misfit) and draws the 2025 markings.
- **Paving is graded, soft ground is not.** A road is a built surface: its height is the LiDAR ground smoothed over 5 m using paved cells only, so a bank beside it does not pull it up. Soft ground bends to meet the neighbour's ground along the footprint; paving meets it only where the two are already within 0.15 m (a road that runs on into the next model). Where the neighbour stands higher, a bank face closes the step. A surface with `"grade": false` (a pad on a bank) follows the raw ground.
- **Trees.** Trees of the other models are not touched. Far-field scatter trees and far-field houses inside the footprint are removed.
- **Track level.** The north model's track and platforms stand about 0.65 m above the LiDAR ground. `southwest/station.json` carries a `lifts` entry that raises this build's ground to them along the corridor, eased out over 10 m, so the road meets the rails at the crossing. Remove it when the north track is lowered. Things that stand on a platform carry `base`, the platform top read from the published tiles.

## Frame

Model metres, the same frame as every other source: +X east, +Y grid north, Z NAVD88 metres. Angles are degrees anticlockwise from east. The viewer's Z is minus this Y.

## Files

| File | What it does |
|---|---|
| `geom.py` | Pure plan geometry: paths with true-arc corners, offsets, ribbons, stalls. No bpy |
| `kit.py` | bpy helpers: materials by kind, a mesh `Builder`, placement, a check render |
| `<area>/*.json` | The digitised plan, one file per zone (format below) |
| `terrain.py` | Ground heights from the LiDAR (numpy only): soft ground follows it, paving is graded, lifts, the edge blend |
| `ground.py` | One seamless ground mesh from the plan: terrain, paving, turf, curbs |
| `paint.py` | Draws the marking textures (lines, stalls, field markings) from the plan. System Python with Pillow |
| `layout.py` | Loads the plan files: dense outlines, layers, which surface gets which paint sheet. No bpy |
| `stand.py` | Grandstand, press box and low bleacher builders |
| `fixtures.py` | Light poles, goalposts, scoreboard, fences, crossing gates, lamps, benches and the like |
| `massing.py` | Pure geometry of building parts: gable, hip, shed and mansard roofs, window bays. No bpy |
| `building.py` | Buildings from measured parts: walls, roofs, window rows, parking deck levels |
| `place.py` | Puts stands, fences, hedges, fixtures, trees and buildings where the plan says |
| `edge.py` | Samples the neighbours' ground along the footprint into `<area>/edge_heights.json` |
| `supersede.py` | Writes the rules for `tools/web-export/supersede.mjs` from `<area>/footprint.json` |
| `build.py` | Entry point: `blender -b --python blender/scripted/build.py -- DATA_DIR OUT.blend` |

Evidence is fetched with `tools/evidence/fetch.py` into a data folder outside the repository. `tools/evidence/overlay.py` draws it with a metre grid and draws plan files over it.

## Plan files

```json
{
  "zone": "station",
  "notes": "what was read from which source, and what is a guess",
  "surfaces": [
    {"name": "Station_lot", "kind": "asphalt", "ring": [[x, y], [x, y, r], ...],
     "evidence": "ortho2020", "unverified": "south end hidden by trees"}
  ],
  "strips": [
    {"name": "Normal_Ave_N_walk", "kind": "concrete", "centre": [[x, y], ...], "width": 1.5, "evidence": "ortho2020"}
  ],
  "curbs": [
    {"name": "Normal_Ave_S_curb", "path": [[x, y], ...], "closed": false, "evidence": "ortho2020"}
  ],
  "markings": [
    {"type": "line", "path": [[x, y], ...], "width": 0.1, "colour": "yellow", "dash": [3.05, 9.15]},
    {"type": "area", "ring": [[x, y], ...], "colour": "white"},
    {"type": "stalls", "line": [[x, y], [x, y]], "count": 12, "depth": 5.5, "side": "left", "angle": 90, "colour": "white"}
  ],
  "points": [
    {"name": "Lot_lamp_1", "kind": "lamp", "at": [x, y], "height": 7.5, "evidence": "lidar2017", "unverified": "head type"}
  ]
}
```

- A **path** is a list of `[x, y]` or `[x, y, r]`. `r` rounds that corner with a true arc of radius `r` metres, tangent to both neighbouring runs. Curves are never given as many short segments: use few vertices with radii, so every edge is a straight run or a true arc.
- **surfaces** are closed paths. `kind` is one of `asphalt`, `concrete`, `brick`, `turf`, `lawn`, `mulch`, `gravel`. Where surfaces overlap, the higher layer wins: lawn 0, mulch 1, gravel 2, asphalt 3, turf 4, concrete 5, brick 6. An optional `"layer"` number overrides the kind's layer. Neighbouring surfaces should overlap by a little (0.2 m) instead of leaving a gap; the layer rule then makes one shared edge.
- Paint goes on `asphalt`, `turf` and `gravel` (a clay infield or warning track: painted gravel is drawn in a clay tone). A `lawn` surface takes paint only with `"paint": true` (a mown ball field with chalk lines); it is then shown as even, untinted grass.
- **strips** are open centre paths with a `width` (walks, bands). They become surfaces.
- **curbs** run along the edge between a carriageway and what is behind it, on the carriageway side's edge line. Give them in any direction.
- **markings** are paint. They are drawn into the texture of the surface under them and never become geometry. `stalls`: `count` stalls along `line` give `count + 1` divider lines, each `depth` long, to the `side` ("left" or "right") of the direction from the first point to the second.
- **lifts** (`ring`, `dz`, `feather`) raise the ground inside a ring by `dz`, eased to nothing over `feather` metres outside it. Use one only to meet another model's level, and say why in `unverified`.
- **points** place objects: `lamp`, `light_pole`, `sign`, `gate`, `goalpost`, `scoreboard`, `bench`, `bike_rack`, `ticket_machine`, `mini_high`, `utility_pole`, `pylon` (lattice transmission tower; `angle` is the line direction), `foul_pole` (`angle` along the foul line away from home, `side` of fair ground), `soccer_goal` (`at` the middle of the goal line, `angle` toward the pitch), `scoreboard` (`width`, `board_height`, `clear` under it), `tree`. `height` in metres when the evidence gives one. A `bench` 4 m or longer is a team bench: `angle` is its long direction and it faces the nearest turf (or `facing`).
- **stands** (`ring`, `front` edge, `rows`, `sections`), **fences** (`path`, `height`, `kind`: `chain_link_black`, `netting_black`, `hedge`, or a solid wall: `wall_padded` (a ballpark's outfield wall), `wall_brick`, `wall_concrete`, with optional `colour` and `thickness`) and **buildings** are extra lists a zone may carry. `field_frame` (`centre`, `angle`) fixes the football field; its lines are generated from the rule book, never traced.
- **buildings** are lists of parts; split a building where the roof height or type changes. A part has a `ring`, a `roof` (`flat`, `gable`, `hip`, `shed`), `top` (NAVD88 metres from the LiDAR: parapet top, or ridge) and, for pitched roofs, `eave` (and `ridge_angle` when the ridge does not follow the long side; a shed roof is high on the left of that direction). `base` stands a part on another part's roof. `style` (`dorm`, `hall`, `plant`, `deck`, `shed`), `floors`, `levels` (deck), `wall`, `trim`, `roof_colour` and `windows` (`width`, `height`, `spacing`) set the look. Outline and heights are measured; the window grid and colours are estimates, so every building object is named `_UNVERIFIED`. A part with `height` and no `top` is a plain box that tall.
- **trees**: a `tree` point may carry `species` (`red_maple`, `sugar_maple`, `pin_oak`, `tulip_poplar`, `american_beech`, `sweetgum`, `white_pine`). `tools/evidence/trees.py` writes a zone of tree points from the LiDAR canopy; do not edit that zone by hand.
- `evidence` names the source (`ortho2020`, `lidar2017`, `lidar2014`, `osm`, a photo file name). `unverified` says in a few words what was guessed.
