## What this changes

<!-- One or two sentences. Name the campus, building, lot or path. -->

## Type of change

- [ ] Wobble or geometry fix (seams, holes, poke-through, floating or buried pieces)
- [ ] New area or building
- [ ] Materials, textures or markings
- [ ] Web viewer
- [ ] Scripts, tooling or CI
- [ ] Documentation

## Evidence

<!-- What the change is based on. Joe's photos beat OSM, LiDAR and the ortho. -->

- [ ] Source: <!-- e.g. NJ 2020 ortho, NJ LiDAR 2023 DTM, OSM way 123456, a public photo link -->
- [ ] Anything inferred rather than measured is marked UNVERIFIED in the PR and in object names or notes

## Checks

- [ ] No .blend files, reference photos, ortho/aerial imagery or LiDAR rasters added (`python3 tools/ci/repo_guard.py`)
- [ ] `ruff check .` passes
- [ ] Edges are straight runs or true arcs, flush with neighbouring surfaces
- [ ] Lot paving was only raised, never lowered
- [ ] Viewer changes: opened `index.html` locally (`python3 -m http.server`) with no console errors

## Before / after

<!-- Renders or viewer screenshots of the same view, before and after. Renders only, no reference photos. -->
