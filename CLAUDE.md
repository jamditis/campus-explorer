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
| `viewer/geo.js`, `sun.js`, `schedule.js`, `permalink.js`, `places.js`, `cat.js`, `tone.js`, `*-math.js` | Pure logic, unit tested in `tests/` |
| `viewer/places.json` | Place names from OpenStreetMap, built by `tools/places/build_places.py` |

## Scripted builds index

`blender/scripted/` builds whole areas from plan files, one folder per area (`southwest/`, `west/`, `northeast/`, `stadium/`, `village/`, `overlook/`); its [README](blender/scripted/README.md) has the plan format and the run steps. Run `python3 -m unittest discover -s tests/py` before a PR that touches it.

| File | What it does |
|---|---|
| `blender/scripted/<area>/*.json` | The digitised plan per zone: surfaces, curbs, markings, points; `footprint.json` also holds the supersede rules |
| `geom.py`, `layout.py` | Pure plan geometry (true-arc corners) and the layout shared by paint and ground |
| `terrain.py`, `ground.py`, `paint.py` | Heights (paving graded, soft ground from LiDAR); one seamless ground mesh; paint sheets for road lines, stalls and the football field |
| `stand.py`, `fixtures.py`, `place.py` | Grandstands and fixtures, and where the plan puts them |
| `massing.py`, `building.py` | Buildings from measured parts: roof shapes (pure, tested), walls, windows, deck levels |
| `build.py` | Entry point, run inside Blender |
| `tools/evidence/` | `fetch.py` (ortho, LiDAR, OSM), `overlay.py` (gridded sheets, plan overlay), `dump_tiles.mjs` and `plan.py` (plan of the published tiles), `trees.py` (tree points from the LiDAR canopy) |
| `tools/web-export/supersede.mjs`, `compact.mjs` | Take other sources' ground out of each area's footprint; drop unused vertex data from tiles |

## Git identity

```sh
git config user.name "Joe Amditis"
git config user.email "6799804+jamditis@users.noreply.github.com"
```

`.claude/settings.json` blanks commit and PR attribution so sessions don't add AI trailers. No `Co-authored-by` trailers of any kind.
