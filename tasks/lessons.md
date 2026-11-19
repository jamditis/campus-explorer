# Lessons

Rules learned from corrections. Read at the start of a session.

## 2026-11-18: one campus, one scene

- **Correction (Joe, during the viewer upgrade):** "the goal is to have a single unified scene with all buildings and textures and everything in one scene, not multiple scenes."
- **What went wrong:** the viewer work kept the main / north scene switch and built new features (permalinks, places, tests) around a `scene` setting.
- **Rule:** the campus is one scene everywhere: viewer, links, docs, tools. Do not add or keep a scene switch.
- **How it is done:** the export merges the source files into `models/main/` (north tiles carry the `n_` prefix; the manifest's `hide` list drops superseded ground). I first built a viewer-side rule that divided the ground between two tile sets on a 2 m grid. Main gained the export-level merge while I worked, so I removed my rule.
- **Method that worked:** a software top-down render of the tiles showed what each file covers in seconds, when WebGL renders on this machine took many minutes.

## 2026-11-18: mesh names in the tiles are not object names

- The exporter joins meshes by material. A node called "Morehead Hall walls" spans several buildings.
- **Rule:** never show a tile's node name as the identity of what the user clicked. Names in the viewer come from a cited source (OpenStreetMap today).

## 2026-11-18: check compass directions against the axes

- The old default sun used a spherical angle that put it in the north-west sky, which cannot happen at 40.86° N. Viewer space has grid north on **-Z**.
- **Rule:** derive directions from `viewer/geo.js` and `viewer/sun.js`, and test them, instead of typing angles by hand.

## 2026-11-19: short probes beat a long browser test on a machine without a GPU

- **Question (Joe, while a smoke run was in progress):** "do we really need a smoke test"
- **What went wrong:** three full smoke runs of 20 minutes each failed on the test's own fixed waits, not on the viewer. A second browser in parallel also ran the container out of memory.
- **Rule (my reading of the question, not Joe's words):** where WebGL runs in software, check one behaviour with one short probe script (one or two tiles, a few minutes) and run one browser at a time. Keep the full smoke test for a machine with a GPU. Browser tests wait for a condition, never for a fixed time.

## 2026-11-19: fetch main before long work, and again before the pull request

- **What went wrong:** this branch ran for a day without a fetch. Main gained ten pull requests in that time (merged tiles, far versions, a tree module, new materials) that touched the same files. I found out only when I was ready to open the pull request, and one of my features (the ownership grid) duplicated work that main had done better.
- **Rule:** run `git fetch origin main` at the start of each work block and compare `git log HEAD..origin/main`. Merge main early when it touches the same files. Before a design that works around a limit of the data (two tile sets, missing names), check if the export side is already fixing it.

## 2026-11-19: start in the place that was named, not with a survey of everything

- **Correction (Joe, an hour into "improve the fidelity, realism and completeness of the models"):** he stopped a whole-campus survey and said to use any resource on the internet and to "start in the southwest corner by Sprague field and the Montclair heights train station and work your way towards the College of communication and media".
- **What went wrong:** I measured the whole campus (triangle counts, material statistics, a Blender inventory) and was about to wait on whole-campus screenshots before I had changed anything.
- **Rule (my reading):** for a broad modelling ask, pick one area, look at it in the viewer and in the evidence within the first minutes, and start building there. Measure the rest only when a decision needs the number.
- **Method that worked:** fetch the public evidence for the area (NJ 2020 ortho by WMS, 3DEP point clouds from the public EPT bucket, OpenStreetMap) with `tools/evidence/fetch.py`, draw it with a metre grid, and draw the plan of the published tiles over the same grid. The gaps show at once.

## 2026-11-19: check what a neighbour model already has before you draw a boundary

- **What happened:** the first footprint for the southwest build ran to x -300 everywhere. A list of every existing mesh inside it showed the main model's fine-tuned corner south-east of Sprague Field (drive mouth, dumpster enclosure, mulch bed, shrubs from sessions ws162 to ws182) inside the footprint.
- **Rule:** before a new source takes over ground, list every existing mesh inside the proposed footprint (`tools/evidence/dump_tiles.mjs` and `plan.py`), visible or hidden. Keep the footprint out of fine-tuned work; replace only what the evidence shows is wrong, and write down why.

## 2026-11-19: the Overpass API and the 2017 LiDAR have gaps here

- Overpass servers reset or timed out for a small box; the OpenStreetMap API `map` call returned the same elements. `fetch.py osm` falls back to it.
- The 2017 NW 6-County point cloud ends near y -262 (just south of the station shelter). The 2014 Sandy cloud covers the rest. `fetch.py lidar` takes each 10 m block from the newest cloud that has ground there.
- The 2017 cloud has no west grandstand at Sprague Field. Do not take stand heights from it.

## 2026-11-19: paving is a graded surface, not terrain

- **Correction (Joe, on the first southwest build):** "I'm seeing a lot of lumpy and bumpy roads and sidewalks".
- **What went wrong:** road and walk heights were the LiDAR ground smoothed over 2.5 m, and every vertex within 4 m of the footprint edge was bent to the neighbouring model's ground. Measured against a local plane, Normal Avenue left it by up to 23.5 cm, the ring walk by 41 cm and the north plaza by 65 cm. The edge blend alone moved road edges by up to 86 cm, up a bank that stands beside the road.
- **Rule:** grade paving as paving. Smooth it over 5 m from paved cells only; never bend it to a neighbour unless the two are already nearly level; close a real step with a face. Soft ground may bend. This is AGENTS rule 4 (no wobbles) for heights, not only for plan edges.
- **Rule:** measure smoothness before showing a result. `tests/py/test_terrain.py` holds the cases (noisy ground, a bank beside a road, a level neighbour). After the fix: Normal Avenue 4.0 cm away from the crossing, the plaza 2.4 cm, the cross walk 0.4 cm.
- **Still lumpy:** the ring walk (10 cm) and Lot 42 (14 cm) by the west stand, where the 2017 LiDAR has a 3 m bank that the plan does not model as a wall.
