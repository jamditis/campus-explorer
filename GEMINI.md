# GEMINI.md — campus-explorer

Guidance for Gemini CLI sessions. These are hard constraints. The canonical contract is [AGENTS.md](AGENTS.md); read it first.

## What this is

Open 3D models of NJ college campuses (Blender 4.5 LTS, free public data) and a static three.js viewer on GitHub Pages. Montclair State first. `.blend` files live on Releases, never in git.

## Hard rules

1. Follow every rule in `AGENTS.md`: designer mindset, UNVERIFIED labels, Joe's photos beat OSM/LiDAR/ortho, straight runs and true arcs, layered builds then unification, raise-only lot paving, markings painted into the asphalt, soft light and free data only.
2. Never commit `.blend` files, `refs/` or any reference photo, ortho/aerial imagery, LiDAR rasters or point clouds, `.npz`/`.npy`, renders, exports or secrets. Run `python3 tools/ci/repo_guard.py` before pushing.
3. All changes go through a PR into `main`. The `lint`, `viewer` and `repo-guard` checks must pass and conversations must be resolved. Opening a PR does not authorize merging it.
4. Before a visual PR, render the same view before and after and attach both.
5. Don't refactor `blender/montclair-state/scripts/`; it's a historical record. New helpers go in `blender/` or `tools/`.
6. Viewer: no build step, no CDN, no bundler. Regenerate `models/` with `tools/web-export/`; don't hand-edit tiles.

## Git identity

```sh
git config user.name "Joe Amditis"
git config user.email "6799804+jamditis@users.noreply.github.com"
```

No AI attribution in commits, PRs, issues or docs. No `Co-authored-by` trailers of any kind.
