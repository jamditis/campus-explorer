# Blender

- `smoke_test.py` builds a tiny generated scene, checks the straight-run, true-arc and raise-only paving rules on it, renders one small Cycles CPU frame and exports a GLB. CI runs it with Blender 4.5 LTS (`.github/workflows/blender-smoke.yml`).
- `montclair-state/scripts/` is the archive of `bpy` scripts from the Montclair State working sessions, one folder per session (`ws205/`, `ws214/` and so on), plus top-level build and camera scripts such as `build_scene.py`. They were run on the modelling box against the main `.blend`, often exec'd with shared globals, so many will not run standalone and paths point at the box layout (`/workspace/nj-scenes/...`). Treat them as a record of how the scene was built. CI only syntax-checks them.

- `southwest/` is a scripted build of the southwest corner (Montclair Heights station surroundings, Normal Avenue, Carlisle Road, Sprague Field). It makes its own `.blend` from plan files and public evidence, and every run rebuilds it whole. Start with [southwest/README.md](southwest/README.md).

The models themselves are on [Releases](https://github.com/jamditis/campus-explorer/releases), not in git.
