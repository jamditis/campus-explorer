#!/bin/bash
# Build the site that GitHub Pages serves (.github/workflows/pages.yml) from the committed files: the viewer, and
# models/main with everything generated from the tiles. The generated part is what used to be committed by every
# tile PR, so two PRs always collided on it (#136): the far versions (lod/, lod.mjs), the shared images and
# geometry (tex/, geo/: share_tex.mjs, share_geo.mjs), the tree stand-ins in the far versions (tree_points.mjs)
# and manifest.json (manifest.py). Each tile's own steps (compact, tree instances, filters, zero-area triangles)
# stay in build_web.sh, so a committed tile is final; this script only adds what depends on several tiles.
#   tools/web-export/site.sh [OUT]          (default OUT: _site in the checkout)
# Needs `npm ci --prefix tools/web-export` (Node tools) and python3. LOD_CACHE (default .lodcache in the
# checkout) keeps far versions by tile hash and tool version, so a run rebuilds only the tiles that changed.
set -euo pipefail
W=$(cd "$(dirname "$0")" && pwd); R=$(cd "$W/../.." && pwd)
OUT=$(realpath -m "${1:-$R/_site}"); CACHE=$(realpath -m "${LOD_CACHE:-$R/.lodcache}")
S=$OUT/models/main
t0=$(date +%s); say() { echo "site: $* ($(( $(date +%s) - t0 )) s)"; }

# 1. the served files: everything in git except sources, tools, tests and notes
rm -rf "$OUT"; mkdir -p "$OUT" "$CACHE"
cd "$R"
git ls-files -z | grep -zvE '^(\.|blender/|tools/|tests/|docs/|notes/|tasks/|[^/]+\.md$|ruff\.toml$)' \
  | xargs -0 cp --parents -t "$OUT"
touch "$OUT/.nojekyll"
say "copied $(find "$OUT" -type f | wc -l) files"

# 2. tiles as committed, with any shared images and geometry back inside them; far versions are rebuilt below
cd "$W"
rm -rf "$S/lod"
node share_tex.mjs "$S" --embed | tail -1
node share_geo.mjs "$S" --embed | tail -1
mkdir -p "$S/lod"

# 3. far versions, from the cache when the tile and the tools are unchanged
LOD_ARGS="RATIO=0.1 ERR_M=0.5"  # the far-version settings build_web.sh uses
# the cache key covers everything a far version depends on: settings, scripts and the pinned packages
tools=$( (echo "$LOD_ARGS"; cat lod.mjs pack.mjs tex.mjs package-lock.json) | sha256sum | cut -c1-16)
built=0 cached=0
for f in "$S"/*.glb; do
  c=$(basename "$f")
  [[ $c =~ ^(n_|sw_)?t_-?[0-9]+_-?[0-9]+\.glb$ ]] || continue
  key=$CACHE/$tools-$(sha256sum "$f" | cut -c1-32)
  if [ -e "$key.glb" ]; then cp "$key.glb" "$S/lod/$c"; cached=$((cached + 1))
  elif [ -e "$key.none" ]; then cached=$((cached + 1))  # lod.mjs wrote none: the tile draws at every distance
  else
    env $LOD_ARGS node lod.mjs "$f" "$S/lod/$c" >/dev/null
    if [ -e "$S/lod/$c" ]; then cp "$S/lod/$c" "$key.glb"; else touch "$key.none"; fi
    built=$((built + 1))
  fi
done
say "far versions: $built built, $cached from the cache"
ls "$S"/lod/*.glb >/dev/null 2>&1 && node drop_zero.mjs "$S"/lod/*.glb | tail -1

# 4. what several tiles share, the tree stand-ins, the manifest
node share_tex.mjs "$S" | tail -1
node share_geo.mjs "$S" | tail -1
node tree_points.mjs "$S"
OUT=$S KEEP_SOURCES=1 TZ=America/New_York python3 manifest.py  # its times are written as ET
find "$S" -size +95M | grep . && { echo "site: a file over 95 MB" >&2; exit 1; }
say "done: $(du -sh "$OUT" | cut -f1), models/main $(du -sh "$S" | cut -f1)"
