# CLAUDE.md — campus-explorer

Guidance for Claude Code sessions. These are hard constraints. The canonical contract is [AGENTS.md](AGENTS.md); read it first.

## What this is

Open 3D models of NJ college campuses (Blender 4.5 LTS, free public data) and a static three.js viewer on GitHub Pages. Montclair State first. `.blend` files live on Releases, never in git.

## Hard rules

1. Follow every rule in `AGENTS.md`: designer mindset, UNVERIFIED labels, Joe's photos beat OSM/LiDAR/ortho, straight runs and true arcs, layered builds then unification, raise-only lot paving, markings painted into the asphalt, soft light and free data only.
2. Never commit `.blend` files, `refs/` or any reference photo, ortho/aerial imagery, LiDAR rasters or point clouds, `.npz`/`.npy`, renders, exports or secrets. Run `python3 tools/ci/repo_guard.py` before pushing.
3. All changes go through a PR into `main`. The `lint`, `viewer` and `repo-guard` checks must pass and conversations must be resolved. Opening a PR does not authorize merging it.
4. Before a visual PR, render the same view before and after and attach both.
5. Don't refactor `blender/montclair-state/scripts/`; it's a historical record. New helpers go in `blender/` or `tools/`.
6. Viewer: no build step, no CDN, no bundler. Regenerate `models/` with `tools/web-export/`; don't hand-edit tiles. One campus, one scene: no scene switch.

## Viewer index

Contract and review checklist: [docs/VIEWER.md](docs/VIEWER.md). Run `node --test` before a viewer PR. `node tools/viewer-test/smoke.mjs` is an optional browser check; it takes 20 minutes or more where WebGL runs in software.

| File | What it does |
|---|---|
| `app.js` | Entry. Renderer, the shared `app` object, frame loop (draws on demand), modes, sun |
| `look.js` | Sky, sun, shadows, textures, paint, culling, adaptive resolution, quality levels |
| `viewer/world.js` | Streams tiles from `models/main/manifest.json`, swaps far versions; collision (BVH on demand), ray casts |
| `viewer/scenery.js`, `trees.js` | Tree level of detail, far trees, land cover, grass tufts near the camera |
| `viewer/player.js` | Fly and walk movement and collision |
| `viewer/input.js` | Keyboard, pointer lock, touch sticks, gamepad |
| `viewer/camera.js`, `viewer/tour.js` | Eased camera moves; guided tour |
| `viewer/hud.js`, `viewer/labels.js` | Compass, scale bar, position readout, minimap; place labels |
| `viewer/measure.js`, `viewer/hunt.js` | Measuring tool; landmark hunt |
| `viewer/ui.js` | Panel, search, sunlight controls, shortcuts, share link, photo |
| `viewer/geo.js`, `sun.js`, `schedule.js`, `permalink.js`, `places.js`, `cat.js`, `tone.js`, `texshare.js`, `*-math.js` (`rooms`, `pose`, `flight`, ...) | Pure logic, unit tested in `tests/` |
| `viewer/rooms.json` | Room numbers and interior volumes, built by `tools/places/build_rooms.py` from `blender/scripted/<area>/interior.json` |
| `viewer/places.json` | Place names from OpenStreetMap, built by `tools/places/build_places.py` |

## Scripted builds index

`blender/scripted/` builds whole areas from plan files, one folder per area (`southwest/`, `west/`, `northeast/`, `stadium/`, `village/`, `overlook/`, `webster/`, `lot60/`, `core/`, `normal/`, `descent/` (Yogi Berra Drive's descent to Valley Road), and two with no ground of their own: `ccom/`, the College of Communication and Media, and `green/`, the Alumni Green); its [README](blender/scripted/README.md) has the plan format and the run steps. Run `python3 -m unittest discover -s tests/py` before a PR that touches it.

| File | What it does |
|---|---|
| `blender/scripted/<area>/*.json` | The digitised plan per zone: surfaces, curbs, markings, points; `footprint.json` also holds the supersede rules |
| `geom.py`, `layout.py` | Pure plan geometry (true-arc corners) and the layout shared by paint and ground |
| `terrain.py`, `ground.py`, `paint.py` | Heights (paving graded, soft ground from LiDAR, level water); one seamless ground mesh; paint sheets for road lines, stalls and the football field |
| `seam.py`, `supersede.py` | Edges two areas share: the same vertices and heights in both meshes; the rules that cut other sources' ground out of each footprint (`overlap` reaches 0.25 m into a neighbour) |
| `stand.py`, `fixtures.py`, `place.py` | Grandstands (aluminium kit, solid concrete bowl) and fixtures, and where the plan puts them |
| `marks.py` | Shapes of lane arrows, crosswalks and pavement words as paint outlines (pure, tested) |
| `massing.py`, `building.py` | Buildings from measured parts: roof shapes (pure, tested), walls, windows, deck levels, roof wells, ramp bays, paint on a deck roof |
| `rooms.py`, `interior.py` | Interiors from floor plans: partitions with door openings, slabs, room numbers (pure part tested) |
| `adopt.py` | Carries named objects over from the release `.blend` (checked by sha256), optionally moved and corrected by a fix function under `blender/` |
| `build.py` | Entry point, run inside Blender |
| `tools/places/build_rooms.py` | `viewer/rooms.json` from the interior plans; run after an interior plan changes |
| `tools/evidence/` | `fetch.py` (ortho, LiDAR, OSM), `overlay.py` (gridded sheets, plan overlay), `dump_tiles.mjs` and `plan.py` (plan of the published tiles), `trees.py` (tree points from the LiDAR canopy) |
| `tools/web-export/supersede.mjs`, `cut.mjs`, `volume.mjs` | Take other sources' ground out of each area's footprint, cut exactly at the outline; take a building out of the other sources' tiles by a ring |
| `tools/web-export/compact.mjs`, `tree_instance.mjs`, `pack.mjs`, `share_tex.mjs`, `tex.mjs` | Drop unused vertex data and all-white vertex colours, and pack instance rotations; make small tree groups instances; store each repeated image once under `models/main/tex/` |
| `tools/web-export/share_geo.mjs`, `geoshare.mjs`, `inst_filter.mjs` | Store geometry that several files carry byte for byte (the tree meshes) once under `models/main/geo/`; instance transforms through meshopt's exponential and quaternion filters, every vertex within 1 mm |
| `tools/teaser/` | The teaser film: storyboard, frame capture from the viewer, 3D titles, grade, sound mix. Film, frames and audio stay outside the repository |
| `tools/web-export/farcut.mjs`, `skyline.mjs`, `skirt.mjs`, `drop_zero.mjs` | Far field: a skyline stand-in for buildings past 10 km, a lighter far ground, empty triangles dropped |

## Git identity

```sh
git config user.name "Joe Amditis"
git config user.email "6799804+jamditis@users.noreply.github.com"
```

`.claude/settings.json` blanks commit and PR attribution so sessions don't add AI trailers. No `Co-authored-by` trailers of any kind.
