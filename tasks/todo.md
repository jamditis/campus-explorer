# Model fidelity and completeness, southwest corner first

Joe's ask (2026-11-19): better fidelity, realism and completeness of the models, with optimized geometry and level of detail kept. Start at the southwest corner (Sprague Field, Montclair Heights station) and work toward the College of Communication and Media. Use any free public source.

What the survey found (viewer at `74a6a95`): the campus is 36.1 million triangles (16.7 million plain, 19.3 million instanced; tree trunks and branches are 38% of it). In the southwest corner the station exists, but Normal Avenue, the grade crossing, the station lot, Carlisle Road, the west half of Sprague Field and its west grandstand are missing, and three grounds (4 km skirt, north terrain, main terrain) overlap there.

Method: a scripted build, `blender/scripted/`, makes its own `.blend` from public evidence (2025 drone and station photographs, NJ 2020 ortho, 3DEP LiDAR 2017 and 2014, OpenStreetMap). It is a third export source (`sw_` tiles). Inside its footprint it owns the ground: the export takes the other sources' ground out of their tiles there (`tools/web-export/supersede.mjs`).

## Phase 1: station to Sprague Field

- [x] Evidence tools: `tools/evidence/` (fetch ortho, LiDAR, OSM; plan of the published tiles; gridded overlay)
- [x] Plan format with true-arc corners (`blender/scripted/geom.py`, `README.md`)
- [x] Seamless ground builder: one triangulation for terrain, paving, turf; curbs (`ground.py`)
- [x] Paint sheets: lane lines, stalls, football markings drawn into textures (`paint.py`)
- [x] Digitised plan: roads, station, field (`plan/*.json`), checked against the ortho
- [x] Objects: west grandstand, press box, east bleachers, light poles, goalposts, scoreboard, fences, crossing gates, lot lamps (`stand.py`, `fixtures.py`, `place.py`)
- [x] Trees from the LiDAR canopy (the main model's tree asset) and the hedge row
- [x] Export: `sw` scene in `build_web.sh`, supersede step, manifest, far versions
- [x] Viewer: turf category, see-through fences, paint colour kept on painted sheets
- [x] Before/after screenshots of the same views; triangle and size budget recorded
- [x] Tests, lint, docs (VIEWER.md, ROADMAP.md, README.md, AGENTS.md index, CLAUDE.md index)
- [x] Independent review pass before the PR

## Phase 2: the rest of the map, worst gaps first (Joe, 2026-11-19: all three areas, stacked PRs)

A survey of OpenStreetMap against the published tiles ranks the gaps: the north half of the campus (y above 420) is mostly bare ground; the south half is mostly modelled.

- [x] Engine serves several areas: one plan folder per area under `blender/scripted/`, one `.blend`, one supersede mark per area
- [x] Buildings from measured parts (`massing.py`, `building.py`); trees from the LiDAR canopy (`tools/evidence/trees.py`)
- [x] North-east district (`northeast/`, PR #53, merged 2026-11-19): CarParc Diem, Dinallo Heights, Machuga Heights, Student Recreation Center, District Energy Plant, softball stadium, tennis courts, lots and roads
- [x] Stadium district (`stadium/`, y 826 to 1105; PR #54, merged 2026-11-19): Yogi Berra Stadium, the soccer field, the Village residences, Clove Road and its lots
- [ ] South-west remainder: Pittser Field, Carlisle Road north, Lot 30, the Maintenance Building
- [x] The Village west of the railway (`village/`): Clove Road, Hawk Crossings, Sinatra Hall, the four Village halls, nine lots
- [x] Overlook Corporate Center block and the quarry ground north of the stadium district (`overlook/`; first planned under the wrong name "Floyd Hall Arena block", see lessons)
- [x] West strip (`west/`): the start of the corridor. A survey showed Kasser Theater, Cole Hall, Morehead Hall and the communication school are detailed and sound; the gap was Carlisle Road north and the College Avenue junction, which were bare terrain
- [ ] Red Hawk Deck to Cole Hall, and the communication school (further work needs Joe's photos: the 2020 ortho shows a construction site between Kasser Theater and Cole Hall): scripted additions for what the main model lacks, box scripts (tested on the released `.blend`) for corrections to it
- [ ] Southwest leftovers: midfield logo (the university's artwork: needs Joe's file or permission), lacrosse and field hockey lines, turn arrows, the east platform's brick band, the east canopy

Each area: evidence, plan files (digitised against the ortho and LiDAR, checked by overlay), build, export, before/after screenshots, an independent review, a PR stacked on the one before.

## Review

What was built and how it was checked:

- **Result in the viewer** (same views before and after, `tools/viewer-test/shoot.mjs` views `sw_top`, `sw_station`, `sw_field`, `eye_crossing`): Normal Avenue with centre lines, medians and the gated crossing; the station lot with 63 stalls, islands, lamps, a ticket machine and the mini-high platforms; Carlisle Road; the whole of Sprague Field with rule-book lines, numerals and the 2025 lettering; the west grandstand (22 rows, 5 sections) with its press box; the east bleachers (7 units); five light poles, goalposts, scoreboard, fences, netting, team benches, the hedge and nine trees.
- **Budget.** The southwest tiles are 96,151 plain triangles, 47,226 instanced (trees), 1.8 MB, 12 paint sheets. The whole campus went from 207.5 MB to 174.6 MB and from 16.74 to 16.37 million plain triangles, because the superseded ground left the other tiles (433,162 triangles of the 4 km skirt alone) and `compact.mjs` dropped 33.5 MB of unused instance data.
- **Plan accuracy.** The football field frame fits the four white boundary lines in the 2020 ortho to 0.15 m. Road, lot and stand outlines were drawn over the ortho and corrected until they sat on the image edges (about 0.5 m; the ortho is 0.3 m per pixel).
- **Seams.** After the supersede step, 184 m² of the skirt and 75 m² of the north terrain remain inside the 36,000 m² footprint: thin tucked strips along its 1.2 km edge. Before the cut-in-four rule it was 3,662 m², and one old triangle showed on Normal Avenue.
- **Tests.** `node --test` 121 pass; `python3 -m unittest discover -s tests/py` 18 pass; Ruff clean; `check_viewer_refs.py` and `repo_guard.py` clean.
- **Independent review** (a second agent, read-only) found two bugs and four minor issues; all are fixed: ground patches facing down after `recalc_face_normals`, an unchecked supersede failure in `build_web.sh`, a small-file read in `supersede.mjs`, paint ownership, a seam in closed curbs, and an evidence box 2.5 m short of the footprint.

Not verified (UNVERIFIED), also flagged in object names and plan files:

- Heights and details taken from photographs by eye: stand row rise, press box form, fence and netting heights, lamp heads, crossing mast types, mini-high platform sizes, hedge and tree species.
- The north model's track stands about 0.65 m above the LiDAR ground. This build lifts its ground to it along the corridor (`station.json`, `lifts`). The right fix is in the north model.
- Frame rate on a real GPU: this machine draws WebGL in software.
- The export ran here in a copy of the box's folder layout, from the scripted `.blend` only. The main and north tiles were not re-exported; they were changed only by `supersede.mjs` and `compact.mjs`.

---

# Earlier: viewer upgrade (done)

Plan for the viewer work on branch `joe/wizardly-pasteur-n7mq4j`. Architecture and module contract: [docs/VIEWER.md](../docs/VIEWER.md).

## One campus (added after Joe's correction, 2026-11-18)

- [x] Remove the main / north scene switch from the viewer, links, docs and tools
- [x] Merge main, which now joins the source models at export (`models/main/`, `n_` tiles, `hide` list), and remove the viewer-side ownership grid that it replaces
- [x] Port main's far tile versions, tree level of detail, far trees, land cover, grass tufts and material work into the new modules (`viewer/world.js`, `viewer/scenery.js`, `look.js`)

## Phones and full screen (added on Joe's request, 2026-11-18)

- [x] Full screen button and `F` key; an "immersive" fallback where the browser has no Fullscreen API (iPhone Safari)
- [x] Phone layout: one top bar with search, full screen, controls and the mode switch; portrait and landscape
- [x] Lite profile for phones: nine tiles near the view, eviction, no skirt, lower pixel ratio
- [x] Touch sticks and buttons for fly and walk

## Fast

- [x] Stream tiles: show the view after the far-field ground and the nearest tiles, load the rest nearest-first while you explore
- [x] Decode meshopt geometry in workers; compile shaders before a tile is added
- [x] Draw only when something changed; redraw shadows only when the sun, the focus or the scene changed
- [x] Adaptive resolution: drop resolution while moving on a slow GPU, sharpen when still
- [x] Build collision BVHs on demand near the player instead of for the whole campus when Walk starts
- [x] Ask before streaming the full campus on a data-saver connection

## Accurate

- [x] Sun direction fix: the default sun sits in the north-west sky, which cannot happen at 40.86° N. Use a real date and time
- [x] Time-of-day control with the real solar position for the campus; "now" button
- [x] Georeference in the viewer: latitude, longitude and NAVD88 elevation readout, compass (true north), scale bar
- [x] Overview framing from the real tile extents (the hard-coded box has north and south swapped)
- [x] Measuring tool: distance, horizontal run and height difference between picked points
- [x] Place names and positions from OpenStreetMap, with the source shown; nothing inferred from joined mesh names
- [x] Walk collision: slide along walls, step up curbs and stairs, never fall through gaps

## Fun

- [x] Search and fly to any named building; labels over the model
- [x] Minimap drawn from the model itself; click to go there
- [x] Guided tour
- [x] Landmark hunt in walk mode
- [x] Touch sticks and gamepad support; smoother fly and walk
- [x] Share link that restores the exact view; photo button
- [x] Keyboard shortcuts and a help sheet
- [x] Lamps glow at night

## Quality

- [x] Unit tests (`node --test`) for every pure module; run in CI
- [x] Headless smoke test and standard screenshots that run anywhere (`tools/viewer-test/`)
- [x] Before/after screenshots of the same views
- [x] Favicon and social sharing tags
- [x] Docs: VIEWER.md, README, ROADMAP, AGENTS index
- [x] Independent review pass before the PR

## Review

What was checked, and how:

- Unit tests: 111 pass (`node --test`). They cover the georeference, solar position, tile order, share links, place search, and the arithmetic of the compass, labels, measuring tool and hunt.
- Georeference: `viewer/geo.js` agrees with pyproj to 5.5e-9 m. Building positions in both source models agree with OpenStreetMap to 4 m or better, with no systematic shift.
- Headless browser (software WebGL): smoke test of every mode and tool, plus screenshots at 1280x800, 390x844 (portrait, touch) and 844x390 (landscape, touch). No overlapping controls, no console errors.
- An independent review of the viewer core found 15 defects; all are fixed (commit 77d2500).
- Before/after screenshots of the seven standard views (`tools/viewer-test/shoot.mjs`).

Not verified (UNVERIFIED):

- Phone memory and frame rate. The nine-tile lite budget is an estimate; it was tested only in an emulated phone viewport, not on a device.
- Frame rates. This machine draws with software WebGL, so no real GPU timing exists.
- Reduced-motion behaviour of the tour and labels (coded, not exercised in a browser).

Lessons are in [lessons.md](lessons.md).

## Phase 3: fix-ups, format extensions, water, viewer (Joe, 2026-11-20: "all of the above")

Order: the engine first (plan agents need the new format), then the plans, then one export per PR.

PR A, engine and the first uses of it:
- [ ] Building format: sunken roof areas (`wells`), a rim with a second roof colour, a garage ramp bay; Overlook tower, wing and garage corrected with them
- [ ] Surface kind `water` (a level surface) in the engine, and a water material in the viewer; the Village basin and pool, the Overlook pond
- [ ] Marking types for junctions: `arrow`, `crosswalk`, `text` (lane numbers), drawn from the rule book, never traced
- [ ] Paint on a parking deck's roof level (stalls on CarParc Diem and the Overlook garage)

PR B, stacked on A, the fix-up pass per area from the "not modelled yet" lists in `docs/ROADMAP.md`:
- [ ] Southwest, west, northeast, stadium, village, overlook: one agent per area, then an independent cross-area review, then the export
- [ ] Only what a source shows. Items with no source stay on the list (2024 bullpens, lamps without returns or visible shadows)

PR C, viewer only, from `main`:
- [ ] Pittser Field turf tone (north model)
- [ ] Detail levels at 220 MB: measure, then the cheapest real saving

Blocked: the corridor to the communication school needs Joe's photos (the 2020 ortho shows a construction site there).
