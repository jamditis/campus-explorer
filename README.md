# Campus explorer

Open 3D models of New Jersey college campuses, built in Blender from free public data, with a browser viewer you can orbit, fly and walk through. Montclair State University is the first campus.

**Live viewer:** https://jamditis.github.io/campus-explorer/

This is a work in progress, not a survey or an as-built record. Anything inferred rather than measured is marked UNVERIFIED in the notes and in object names.

## What's here

```
index.html, app.js, look.js,    Static three.js viewer (no build step), served by GitHub Pages
style.css, viewer/              (viewer/ holds the modules; see docs/VIEWER.md)
models/manifest.json            The campus as one scene: every tile of every exported model, listed once
models/main/, models/north/     Meshopt-compressed GLB tiles of the two Blender files, 160 m squares
vendor/                         three.js r170, GLTF loader, meshopt decoder, three-mesh-bvh (MIT)
blender/
  smoke_test.py                 Headless Blender check that CI runs on a tiny generated scene
  montclair-state/scripts/      Archive of the bpy scripts used to build the Montclair State scene,
                                one folder per working session (historical, run inside Blender 4.5)
tools/
  web-export/                   Blender → GLB tile export, leaf tinting, manifests, and unify.py that joins the scenes
  places/                       Builds viewer/places.json (names and positions) from OpenStreetMap
  viewer-test/                  Headless smoke test and the standard before/after screenshots
  ci/                           Repo guard and viewer reference checks used by CI
tests/                          Unit tests for the viewer's pure modules (node --test)
notes/
  UNIFY_SWEEP.md                Ranked breakage and wobble list, worst first, with status
  BOUNDARY.md                   How the modelled area was chosen and extended
  DATA.md, ADDONS.md            Data inputs and the free Blender add-ons used
AGENTS.md                       Operating rules for AI coding agents (also CLAUDE.md, CODEX.md, GEMINI.md)
```

The `.blend` models are not in git. Each day's model is attached to a [GitHub Release](https://github.com/jamditis/campus-explorer/releases) instead (about 180 MB per file).

## Using the viewer

Open the live link, or run it locally:

```sh
python3 -m http.server 8000
# then open http://localhost:8000/
```

The campus is one scene. The nearest tiles load first and the rest stream in while you look around.

- **Orbit, fly, walk.** Mouse and keyboard, touch sticks on a phone, or a gamepad. Walk follows the modelled ground, climbs steps and slides along walls. Press `?` for the full list of controls.
- **Find a place.** Search any named building, lot or field and fly to it. Labels and a minimap drawn from the model keep you oriented. Names and positions come from OpenStreetMap.
- **Real sunlight.** Pick a date and time: the sun sits where it really is over the campus. After dark the lamps glow.
- **Measure.** Click points on the model for distance, horizontal run, height difference, slope and bearing. The readout at the bottom gives latitude, longitude and NAVD88 elevation. These are model values, not survey values.
- **Tour and hunt.** A guided tour of the main buildings, and a landmark hunt to play on foot.
- **Share.** The address bar always holds a link to the exact view; Photo saves a picture.

The viewer draws only when something changes, redraws shadows only when they move, and lowers the resolution while the view is moving on a slow GPU. Quality has three levels.

## How the models are built

- **Blender 4.5 LTS**, CPU-only, scripted with `bpy`. Each working session saves a backup, makes targeted edits, renders checks and records what changed.
- **Layered builds.** A new section starts as a hybrid layered build (terrain, paving, curbs, buildings, planting), then unification passes stitch the seams. Areas that are already fine-tuned are not rebuilt.
- **Wobble-free edges.** Curbs, walks and lot edges are straight runs or true arcs fitted to the aerial, flush with their neighbours.
- **Soft light** and a physically based sky set from Montclair's latitude and longitude.
- **Web edition.** `tools/web-export/` splits each Blender file (main and north campus) into 160 m tiles, exports each in its own low-memory Blender process, and optimizes them with gltf-transform. Materials keep the model's colours and a category; the viewer lays tileable CC0 textures over them in world space, paints the lot markings from the model's own line work, and adds a sky, sun shadows, fog and (on High) ambient occlusion. The two files share one origin and overlap in the middle; until they are merged in Blender, `unify.py` shows one file's tile per square (seams at those tile edges are UNVERIFIED). Lawn grass blades and some interiors are left out, trees are thinned, and small objects fade out with distance. See [docs/ROADMAP.md](docs/ROADMAP.md) for what is still missing.

## Refreshing the viewer after a day's modelling

On the modelling box, read-only against the `.blend` files, between modelling sessions (the script waits for the scene lock):

1. Run `SCENE=main SOURCE_VERSION=<session id> SOURCE_SAVED="<main save time, ET>" bash tools/web-export/build_web.sh` from this checkout, then the same with `SCENE=north`. Point it at a frozen copy of the main file (for example `montclair_state_ws214c.blend`) so a session can't change it mid-export. Before every Blender process it waits for the scene `.lock` to be free, for no other Blender, and for the memory gate. It plans tiles, exports each tile, fixes leaf UVs and tints, optimizes with gltf-transform (meshopt, webp, join, instance, no palette), composes the paint layers and writes `models/<scene>/manifest.json`. Any failed tile stops the build before anything is published; tiles no longer in the plan are pruned.
2. Leave `textures/` alone unless you are changing the CC0 set (credits in `textures/CREDITS.md`).
3. The build ends with `python3 tools/web-export/unify.py`, which rewrites `models/manifest.json` so the viewer shows every exported tile as one campus (see "One campus" in [docs/VIEWER.md](docs/VIEWER.md)). Run it yourself if you rebuilt only some tiles.
4. Take the standard before/after screenshots with `node tools/viewer-test/shoot.mjs <outdir>` and run `node tools/viewer-test/smoke.mjs`. Both need Playwright with Chromium.
5. Commit `models/` (and any viewer changes) on a branch and open a PR. Pages redeploys from `main` a minute or two after merge.

The exporter keeps only images on an allowlist and refuses anything named ortho, naip, aerial, photo or mask. The paint layers are composed from the model's own authored line-work tiles and are written as `paint_*.webp`.

## Contributing

Wobble reports with a screenshot are the most useful thing you can send: use the [wobble report form](https://github.com/jamditis/campus-explorer/issues/new?template=wobble-report.yml). Code, script and viewer changes go through pull requests into `main`, which is protected and needs the `lint`, `viewer` and `repo-guard` checks to pass. See [CONTRIBUTING.md](CONTRIBUTING.md). AI coding agents should read [AGENTS.md](AGENTS.md) first.

## Data sources and credits

The models are built from free public data. The source data is credited here but **not redistributed** in this repository.

| Source | Used for | Licence |
|---|---|---|
| [NJ Office of GIS](https://njgin.nj.gov/) 2020 natural-colour orthoimagery (0.1 m) | Tracing edges, stalls, markings and paving | NJ public data; credited, not redistributed |
| NJ / [USGS 3DEP](https://www.usgs.gov/3d-elevation-program) LiDAR and DEMs | Terrain, grades and building heights | Public domain (USGS); NJ data credited |
| [OpenStreetMap](https://www.openstreetmap.org/copyright) | Building footprints, roads, paths, names | © OpenStreetMap contributors, [ODbL](https://opendatacommons.org/licenses/odbl/) |
| [ambientCG](https://ambientcg.com/) | PBR textures | CC0 |
| Blender add-ons listed in [notes/ADDONS.md](notes/ADDONS.md) | Modelling helpers | GPL (not redistributed) |

Reference photographs, including Joe's own campus photos, guide the modelling but are never committed. Where a photo disagrees with OSM, LiDAR or the ortho, the photo wins.

## Licence

- **Code** (scripts, viewer, tools, CI): [MIT](LICENSE).
- **Models and written content** (GLB tiles, released .blend files, notes, renders): [CC BY 4.0](LICENSE-CONTENT). Credit "Joe Amditis, Campus explorer" and keep the OpenStreetMap attribution, since parts of the geometry are derived from OSM data.
- **Vendored libraries** in `vendor/` keep their own MIT licences.

Map data © OpenStreetMap contributors. Created by [Joe Amditis](https://github.com/jamditis).
