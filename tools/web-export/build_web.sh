#!/bin/bash
# Repeatable web export: main .blend -> per-tile GLBs -> optimized (meshopt + webp) -> web/campus/models/main/
# usage: bash scripts/web/build_web.sh [FILE]   (honours the scene .lock convention: run it inside a session that holds it)
set -u
fail(){ echo "$(date +%T) FAILED: $*" >&2; exit 1; }
R=/workspace/nj-scenes; W=$R/scripts/web; B=$R/web/build; S=$R/web/campus/models/main
FILE=${1:-$R/montclair-state/montclair_state.blend}; BL=/workspace/opt/blender/blender
mkdir -p $B/raw $S
gate(){ until ! pgrep -x blender >/dev/null && [ $(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo) -ge ${GATE:-6000} ]; do sleep 5; done; }
if [ "${SKIP_PLAN:-0}" != 1 ]; then
  gate; FILE=$FILE $BL -b --factory-startup --python-exit-code 1 --python $W/plan_chunks.py 2>&1 | grep -E "^N |MEM|rror"
  [ "${PIPESTATUS[0]}" -eq 0 ] || fail "chunk planning"
  python3 $W/make_chunks.py || fail "make_chunks"
fi
CHUNKS=$(python3 -c "import json;print(' '.join(json.load(open('$W/chunks.json'))))") || fail "read chunks.json"
if [ -z "${ONLY:-}" ]; then
  # Full build: drop raw and published tiles that are no longer in the chunk plan,
  # so removed or moved geometry doesn't linger in the manifest.
  for f in $B/raw/*.glb $S/*.glb; do
    [ -e "$f" ] || continue
    [[ " $CHUNKS " == *" $(basename "$f" .glb) "* ]] || { echo "prune stale $f"; rm -f "$f"; }
  done
fi
for C in $CHUNKS; do
  [ -n "${ONLY:-}" ] && [[ " $ONLY " != *" $C "* ]] && continue
  gate; echo "$(date +%T) export $C"
  rm -f $B/raw/$C.glb
  DEC=0.5; [ $C = context ] && DEC=0.3; DECIMATE=$DEC FILE=$FILE CHUNK=$C OUT=$B/raw/$C.glb WD_MIN=900 bash $R/montclair-state/scripts/ws33/wd.sh $BL -b --factory-startup --python-exit-code 1 --python $W/export_web.py 2>&1 | grep --line-buffered -E "WEB (appended|materials|WROTE|MEM)|rror|Trace|WATCH"
  [ "${PIPESTATUS[0]}" -eq 0 ] && [ -s $B/raw/$C.glb ] || fail "export $C (no new GLB; not publishing)"
done
cd $R/web/tools
for f in $B/raw/*.glb; do
  C=$(basename $f .glb); [ -n "${ONLY:-}" ] && [[ " $ONLY " != *" $C "* ]] && continue
  RATIO=0.5; ERR=0.0015; [ $C = context ] && { RATIO=0.35; ERR=0.004; }
  echo "$(date +%T) optimize $C"
  node $W/tint_leaves.mjs $f || fail "tint $C"
  npx gltf-transform optimize $f $S/$C.glb --compress meshopt --texture-compress webp --texture-size 1024 \
     --simplify false --join true --instance true --flatten true 2>&1 | grep -iE "error|warn" | head -3
  [ "${PIPESTATUS[0]}" -eq 0 ] || fail "optimize $C"
done
python3 $W/manifest.py || fail "manifest"
ls -la $S; du -sh $R/web/campus
