# Campus explorer

Open 3D models of New Jersey college campuses, built in Blender from free public data, with a browser viewer you can orbit, fly and walk through. Montclair State University is the first campus.

**Live viewer:** https://jamditis.github.io/campus-explorer/

This is a work in progress, not a survey or an as-built record. Anything inferred rather than measured is marked UNVERIFIED in the notes and in object names.

## What's here

```
index.html, app.js, style.css   Static three.js viewer (no build step), served by GitHub Pages
models/main/                    Campus as meshopt-compressed GLB tiles + manifest.json
vendor/                         three.js r170, GLTF loader, meshopt decoder, three-mesh-bvh (MIT)
blender/
  smoke_test.py                 Headless Blender check that CI runs on a tiny generated scene
  montclair-state/scripts/      Archive of the bpy scripts used to build the Montclair State scene,
                                one folder per working session (historical, run inside Blender 4.5)
tools/
  web-export/                   Blender → GLB tile export, leaf tinting, manifest and screenshots
  ci/                           Repo guard and viewer reference checks used by CI
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

Orbit with the mouse, switch to Fly or Walk from the panel, and use Top view for a plan view.

## How the models are built

- **Blender 4.5 LTS**, CPU-only, scripted with `bpy`. Each working session saves a backup, makes targeted edits, renders checks and records what changed.
- **Layered builds.** A new section starts as a hybrid layered build (terrain, paving, curbs, buildings, planting), then unification passes stitch the seams. Areas that are already fine-tuned are not rebuilt.
- **Wobble-free edges.** Curbs, walks and lot edges are straight runs or true arcs fitted to the aerial, flush with their neighbours.
- **Soft light** and a physically based sky set from Montclair's latitude and longitude.
- **Web edition.** `tools/web-export/` splits the scene into 160 m tiles, exports each in its own low-memory Blender process, and optimizes them with gltf-transform. Procedural materials become flat colours, lawn grass and some interiors are left out, and trees are thinned.

## Refreshing the viewer after a day's modelling

On the modelling box, read-only against the main `.blend`, inside a session that holds the scene lock:

1. Write the session ID to `web/SOURCE_VERSION` and the main file's save time (ET) to `web/SOURCE_SAVED` in the scenes folder.
2. Run `tools/web-export/build_web.sh`. It plans tiles, exports each tile in its own low-memory Blender process, tints leaves, optimizes with gltf-transform (meshopt, webp, join, instance) and writes `manifest.json`.
3. Serve the output with `python3 -m http.server` and take headless screenshots with `tools/web-export/shoot.mjs`.
4. Copy the new `models/` (and any viewer changes) into a branch of this repo and open a PR. Pages redeploys from `main` a minute or two after merge.

The exporter keeps only images on an allowlist and refuses anything named ortho, naip, aerial, photo or mask.

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
