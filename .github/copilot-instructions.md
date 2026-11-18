# Copilot review instructions — campus-explorer

Project context and the full rules live in [AGENTS.md](../AGENTS.md). Flag these on every PR:

1. **Forbidden files.** Any `.blend`, anything under `refs/`, ortho/aerial/NAIP imagery, LiDAR rasters or point clouds (`.tif`, `.las`, `.laz`), `.npz`/`.npy` grids, renders, exports, or files near 95 MB. Also any token, password or personal contact detail.
2. **No AI-authorship attribution.** No "Generated with ..." notes or `Co-authored-by` trailers in commits, PR bodies or docs.
3. **UNVERIFIED labels.** Geometry or layout that is inferred rather than measured must say UNVERIFIED in the PR and object names.
4. **Wobble rules.** Edges should be straight runs or true arcs, flush with neighbours. Lot paving is only raised, never lowered. Markings are painted into the asphalt material.
5. **Viewer.** No build step, no CDN imports, no bundler. `vendor/` and `models/` are generated or vendored; flag hand edits.
6. **Session archive.** `blender/montclair-state/scripts/` is a historical record; flag refactors of it. New helpers belong in `blender/` or `tools/`.
7. **CI.** Don't add path filters to `.github/workflows/ci.yml` (it emits the required `lint`, `viewer` and `repo-guard` checks), and don't weaken `tools/ci/repo_guard.py`.
