#!/bin/bash
# Repeatable web export: a campus .blend -> per-tile GLBs -> optimized (meshopt + webp) -> models/<scene>/
# usage: SCENE=main|north bash tools/web-export/build_web.sh [FILE]
#   One unified campus: north is merged into models/main at its real coordinates (same Blender origin).
#   Run main first; the north run reads main's plan and skips anything main already has.
#   SITE   = viewer checkout to publish into (default: this repo); tiles land in $SITE/models/$SCENE
#   ONLY   = "t_0_0 context" to rebuild some tiles; SKIP_PLAN=1 to reuse the last chunk plan
#   SOURCE_VERSION / SOURCE_SAVED = label shown in the viewer (default: file mtime)
# Read-only on the .blend. Waits for /workspace/nj-scenes/.lock and montclair-state/.lock to be free, for no other Blender, and for
# the memory gate, before every Blender process (the hourly modelling sessions use the same rules).
set -u
fail(){ echo "$(date +%T) FAILED: $*" >&2; exit 1; }
W=$(cd "$(dirname "$0")" && pwd); R=/workspace/nj-scenes; SCENE=${SCENE:-main}
SITE=${SITE:-$(cd "$W/../.." && pwd)}; S=$SITE/models/main; WORK=$R/web/build/$SCENE; B=$WORK
case $SCENE in
  main) DEF=$R/montclair-state/montclair_state.blend; PREFIX="" ;;
  north) DEF=$R/montclair-state/north/montclair_north.blend; PREFIX=n_; export MERGE_WITH=$R/web/build/main
         [ -f $MERGE_WITH/chunks.json ] && [ -f $MERGE_WITH/source.txt ] || fail "run SCENE=main first (north merges against main's plan)"
         export MAIN_FILE=$(cat $MERGE_WITH/source.txt) ;;  # north terrain is trimmed against main's ground
  *) fail "unknown SCENE $SCENE" ;;
esac
FILE=${1:-$DEF}; BL=/workspace/opt/blender/blender; LOCKS="$R/.lock $R/montclair-state/.lock"
# objects the main file links from other .blends (plans written before objects.json had "lib")
LIBS=${LIBS:-$R/montclair-state/north/sprague_cafe_src.blend}
export WORK FILE PREFIX SCENE LIBS
mkdir -p $B/raw $S
[ -f $WORK/img_avg.json ] || cp $R/scripts/web/img_avg.json $WORK/ 2>/dev/null
locked(){ for l in $LOCKS; do [ -e $l ] && return 0; done; return 1; }
# never start Blender while an hourly session holds either scene lock, while another Blender runs,
# or below the memory gate; the watchdog (wd.sh) kills the export if MemAvailable drops under 1.5 GB
gate(){ until ! locked && ! pgrep -x blender >/dev/null && [ $(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo) -ge ${GATE:-6000} ]; do sleep 5; done; }
if [ "${SKIP_PLAN:-0}" != 1 ]; then
  gate; WD_MIN=1500 bash $R/montclair-state/scripts/ws33/wd.sh $BL -b --factory-startup --python-exit-code 1 --python $W/plan_chunks.py 2>&1 | grep -E "^N |MEM|rror"
  [ "${PIPESTATUS[0]}" -eq 0 ] || fail "chunk planning"
  python3 $W/make_chunks.py || fail "make_chunks"
fi
[ $SCENE = main ] && echo "$FILE" > $WORK/source.txt  # the north run trims its terrain against this file
CHUNKS=$(python3 -c "import json;print(' '.join(json.load(open('$WORK/chunks.json'))))") || fail "read chunks.json"
if [ -z "${ONLY:-}" ]; then
  # Full build: drop raw and published tiles that are no longer in the chunk plan,
  # so removed or moved geometry doesn't linger in the manifest.
  for f in $B/raw/*.glb $S/*.glb; do
    [ -e "$f" ] || continue
    c=$(basename "$f" .glb)
    [[ $c == far_* ]] && continue  # far-field houses come from landcover.py, not the chunk plan
    if [ -n "$PREFIX" ]; then [[ $c == ${PREFIX}* ]] || continue; else [[ $c == n_* ]] && continue; fi
    [[ " $CHUNKS " == *" $c "* ]] || { echo "prune stale $f"; rm -f "$f" "$f".leaf.json "$f".paint.json; }
  done
fi
for C in $CHUNKS; do
  [ -n "${ONLY:-}" ] && [[ " $ONLY " != *" $C "* ]] && continue
  # REUSE_RAW=1 resumes an interrupted build: tiles whose raw export already exists are not re-exported
  [ "${REUSE_RAW:-0}" = 1 ] && [ -s $B/raw/$C.glb ] && { echo "reuse raw $C"; continue; }
  gate; echo "$(date +%T) export $C"
  rm -f $B/raw/$C.glb
  DEC=0.5; case $C in *context) DEC=0.3 ;; skirt) DEC=0.6 ;; esac
  DECIMATE=$DEC CHUNK=$C OUT=$B/raw/$C.glb WD_MIN=1500 bash $R/montclair-state/scripts/ws33/wd.sh $BL -b --factory-startup --python-exit-code 1 --python $W/export_web.py 2>&1 | grep --line-buffered -E "WEB (appended|from libraries|missing library|trimmed|main ground|WARNING|materials|WROTE|MEM)|rror|Trace|WATCH"
  [ "${PIPESTATUS[0]}" -eq 0 ] && [ -s $B/raw/$C.glb ] || fail "export $C (no new GLB; not publishing)"
done
cd $R/web/tools
for f in $B/raw/*.glb; do
  C=$(basename $f .glb); [ -n "${ONLY:-}" ] && [[ " $ONLY " != *" $C "* ]] && continue
  echo "$(date +%T) optimize $C"
  node $W/tint_leaves.mjs $f || fail "tint $C"
  # no palette: materials keep their names and the 'cat' extras the viewer textures by
  npx gltf-transform optimize $f $S/$C.glb --compress meshopt --texture-compress webp --texture-size 1024 \
     --simplify false --palette false --join true --instance true --flatten true 2>&1 | grep -iE "error|warn" | head -3
  [ "${PIPESTATUS[0]}" -eq 0 ] || fail "optimize $C"
  [ "${KEEP_RAW:-0}" = 1 ] || rm -f $f  # disk is tight: raw exports are large and rebuilt every run
  # far-distance version of each campus tile (lod/<tile>.glb): instances and small parts dropped, rest
  # simplified to ~0.5 m error without tearing; the viewer swaps to it past a quality-set distance
  if [[ $C == t_* || $C == n_t_* ]]; then
    mkdir -p $S/lod; cp $W/lod.mjs ./lod.mjs  # run from here so it resolves this folder's node_modules
    RATIO=0.1 ERR_M=0.5 node lod.mjs $S/$C.glb $S/lod/$C.glb >/dev/null || fail "lod $C"
  fi
done
# drop far versions whose tile is gone
for f in $S/lod/*.glb; do [ -e "$f" ] && [ ! -e $S/$(basename $f) ] && { echo "prune stale $f"; rm -f "$f"; }; done
[ $SCENE = main ] && { OUT=$S python3 $W/paint.py || fail "paint"; }
# far-field land cover, trees and houses from OpenStreetMap (needs pyproj/shapely: GEO_PY) and the OSM
# map tiles in $OSM (api.openstreetmap.org/api/0.6/map, ~1 km tiles over the 4 km skirt)
GEO_PY=${GEO_PY:-/workspace/opt/geo/bin/python}; OSM=${OSM:-$R/web/build/landcover}
if [ $SCENE = main ] && [ -x "$GEO_PY" ] && ls $OSM/*.osm >/dev/null 2>&1; then
  OSM=$OSM OUT=$S RAW=$WORK WORK_MAIN=$WORK WORK_NORTH=$R/web/build/north $GEO_PY $W/landcover.py || fail "landcover"
  rm -f $S/far_houses.glb
  (cd $R/web/tools && npx gltf-transform optimize $WORK/far_houses.raw.glb $S/far_houses.glb --compress meshopt --simplify false --palette false --join false) \
    || fail "far houses optimize (not publishing)"
  [ -s $S/far_houses.glb ] || fail "far houses"; rm -f $WORK/far_houses.raw.glb
fi
OUT=$S python3 $W/manifest.py || fail "manifest"
find $S -size +95M | grep . && fail "file over 95 MB"
ls -la $S; du -sh $S
