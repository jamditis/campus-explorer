# Blender add-ons and extensions (Blender 4.5.14 LTS, box)

Installed 2026-10-08 ET. Extensions came from extensions.blender.org via `blender -c extension install -s -e <id>`
(online access had to be enabled in preferences first). Legacy add-ons were unzipped into
`~/.config/blender/4.5/scripts/addons/` and enabled headless with `addon_utils.enable(..., persistent=True)` plus `save_userpref`.
All enabled and saved in user prefs. Verified headless (`blender -b`) on 2026-10-08.

| Name | Version | Source | License | Installed | Why it helps |
|---|---|---|---|---|---|
| BlenderGIS | 2.2.14 (master) | https://github.com/domlysz/BlenderGIS | GPL-3.0 | yes (legacy) | Imports georeferenced rasters, DEMs, shapefiles and OSM and keeps a scene CRS, so terrain and footprints land at real coordinates. GDAL is not installed in Blender's Python, so GeoTIFF import falls back to its basic reader; the project pipeline does GIS work outside Blender with pyproj/rasterio/laspy instead. |
| Blosm (Blender-OSM) free version | 2.7.28 (release branch) | https://github.com/vvoovv/blosm | GPL-3.0 | yes (legacy) | One-click OSM building/road import with heights; free version is GPL on GitHub (premium features are paid and were not used). |
| Sun Position | 4.4.0 | extensions.blender.org/add-ons/sun-position | GPL | yes | Sets the sun from latitude, longitude, date and time; the scene is wired to Montclair (40.86, -74.197), UTC-4. |
| Node Wrangler | 3.55 (bundled core add-on) | ships with Blender | GPL | yes | Faster PBR material setup (Ctrl+Shift+T loads ambientCG texture sets in one step). |
| fSpy importer | 1.0.3 | https://github.com/stuffmatic/fSpy-Blender | GPL-3.0 | yes (legacy) | Imports cameras solved in the free fSpy desktop app (https://fspy.io), for matching render cameras to reference photos. The fSpy app itself is a GUI app and was not installed on the headless box. |
| Archimesh | 1.2.5 | extensions.blender.org | GPL-2.0+ | yes | Parametric doors, windows, stairs and rooms for detailed facades and entrances. |
| Bool Tool | 2.1.0 | extensions.blender.org | GPL | yes | Quick boolean cuts for window recesses, arches and entry openings. |
| Extra Mesh Objects | 0.4.1 | extensions.blender.org | GPL-3.0+ | yes | Extra primitives (gears, pipes, beams, balusters) for railings, columns and site furniture. |
| MeasureIt | 1.8.3 | extensions.blender.org | GPL-3.0+ | yes | On-model dimensions to check footprints and heights against GIS measurements. |
| Precision Drawing Tools | n/a | - | - | no | Not found in the extensions.blender.org repository for 4.5; skipped. |
| Archipack | n/a | - | - | no | Not evaluated further: the free 1.x line targets Blender 2.8-2.9 and the current version is paid. Archimesh covers the free need. |
| Poly Haven / ambientCG asset add-ons | n/a | - | - | no (script instead) | The official Poly Haven Blender add-on is paid. Wrote `montclair-state/scripts/fetch_textures.py`, which downloads CC0 ambientCG PBR sets directly. |
| Sky / HDRI | built-in | Nishita sky texture (Cycles) | GPL (Blender) | yes (built-in) | Physically based sky driven by the same sun elevation/azimuth as the sun lamp. Poly Haven CC0 HDRIs can be pulled the same way if a cloudy or overcast look is needed. |

Python GIS tooling outside Blender (box venv `/workspace/nj-scenes/.venv`): pyproj, shapely 2.2, rasterio, laspy[lazrs], scipy, numpy, pillow.

Added 2026-10-08 ~11:40 AM ET (parallel stream): **Sapling Tree Gen** (`sapling_tree_gen`, extensions.blender.org, GPL-2.0+), installed with
`blender -c extension install -s -e sapling_tree_gen`; works headless via `bpy.ops.curve.tree_add(**preset)`. Used for the tree assets in `assets/campus_assets.blend`.
