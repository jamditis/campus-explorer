# Contributing to Campus explorer

Thanks for helping. There are two ways in.

## Path A: Report what looks wrong (no code needed)

Open the [live viewer](https://jamditis.github.io/campus-explorer/), find something broken or off, take a screenshot, and file a [wobble or geometry report](https://github.com/jamditis/campus-explorer/issues/new?template=wobble-report.yml). Say where it is (building, lot, path, which side). If you know the real layout from a public source, such as an OSM way, Street View or an official campus map, link it.

Want a building, lot or campus added? Use the [area request form](https://github.com/jamditis/campus-explorer/issues/new?template=area-request.yml).

Please only attach screenshots and photos you have the right to share.

## Path B: Code, scripts and models

### Setup

```sh
git clone https://github.com/jamditis/campus-explorer.git
cd campus-explorer
python3 -m http.server 8000          # viewer at http://localhost:8000/
pip install ruff==0.11.13 && ruff check .
python3 tools/ci/repo_guard.py
```

For Blender work, install [Blender 4.5 LTS](https://www.blender.org/download/lts/4-5/) and run the smoke test:

```sh
blender --background --factory-startup --python-exit-code 1 \
  --python blender/smoke_test.py -- /tmp/smoke
```

The full `.blend` model for each day is attached to a [release](https://github.com/jamditis/campus-explorer/releases). Download it; don't commit it.

### Modelling rules

1. **Edges are straight runs or true arcs**, fitted to the aerial and flush with the surfaces beside them. No wobbles, kinks or faceted curves.
2. **Mark guesses UNVERIFIED** in the object name, notes and PR when something is inferred rather than measured.
3. **Photos beat data.** Where a photo disagrees with OSM, LiDAR or the ortho, follow the photo.
4. **Raise lot paving, never lower it.** The LiDAR terrain is re-snapped by geometry-node modifiers, so grade fixes come from raising paving to meet it.
5. **Layered builds, then unification passes.** Don't rebuild areas that are already fine-tuned; fix their seams.
6. **Paint markings into the asphalt material** (stall lines, symbols, crosswalk bars) rather than modelling them as separate strips.
7. **Soft light and free data only.**

### What never goes in git

`.blend` files, reference photos (`refs/`), ortho or aerial imagery, LiDAR point clouds and rasters, cached terrain grids (`.npz`, `.npy`), renders and export folders, or any secret. `.gitignore` and the `repo-guard` check block these, and every file must stay under 95 MB.

### Pull request process

1. Fork the repo (or create a branch if you have access) from `main`.
2. Make your change. Keep one area or one fix per PR.
3. Run `ruff check .` and `python3 tools/ci/repo_guard.py`.
4. Open a PR using the template, with before/after renders or viewer screenshots for visual changes.
5. `main` is protected: the `lint`, `viewer` and `repo-guard` checks must pass, the branch must be up to date, and every review conversation must be resolved before merge.

## Getting help

Ask in [Discussions](https://github.com/jamditis/campus-explorer/discussions).

## Code of conduct

This project follows the [Contributor Covenant](CODE_OF_CONDUCT.md). Be kind and constructive.
