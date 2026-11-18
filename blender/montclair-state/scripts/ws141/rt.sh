cd /workspace/nj-scenes/montclair-state
B=$1; shift
for c in "$@"; do echo "$(date +%T) R $c $(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo)"
CAMS="$c" DIR=${DIR:-test} OUT_TAG=${OUT_TAG:-ws141} SAMP=${SAMP:-16} PCT=${PCT:-60} TEXLIM=${TEXLIM:-1024} WD_MIN=${WD_MIN:-1500} bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b --factory-startup $B --python scripts/ws141/render141.py 2>&1 | grep -E "WROTE|rror|Trace|WATCH"; done; echo END
