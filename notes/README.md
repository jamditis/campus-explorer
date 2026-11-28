# Notes

Working notes from the modelling sessions, published as-is. Times are US Eastern. Session IDs such as `ws205` match the folders in `blender/montclair-state/scripts/`. Coordinates are local scene metres.

- `UNIFY_SWEEP.md` is the ranked list of breakage and wobbles, worst first, with what was fixed and what is still UNVERIFIED.
- `BOUNDARY.md` records how the modelled area was drawn and extended.
- `DATA.md` lists data inputs and their licences. The data itself is not in this repo.
- `ADDONS.md` lists the free Blender add-ons used.

## 2026-11-28: what an export commits (for the hourly modelling sessions)
From #136 on, an export commits only its tiles (`models/main/*.glb`, each final, images and geometry inside) and `models/main/sources.json` (snapshot labels, superseded ground). `build_web.sh` no longer writes `lod/`, `tex/`, `geo/` or `manifest.json`; `.gitignore` refuses them. The `site` workflow builds those with `tools/web-export/site.sh` after every merge and deploys to Pages, so two export PRs no longer collide on shared files. To look at an export before the PR: `npm ci --prefix tools/web-export`, `tools/web-export/site.sh`, then the viewer-test tools serve `_site/`.
