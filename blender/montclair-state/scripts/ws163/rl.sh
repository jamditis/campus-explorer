cd /workspace/nj-scenes/montclair-state
B=$1; shift
for c in "$@"; do echo "$(date +%T) R $c $(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo)"
CAMS="$c" LEAN=${LEAN:--350,-262,-275,-140} DIR=${DIR:-wip} OUT_TAG=${OUT_TAG:-ws163} SAMP=${SAMP:-14} PCT=${PCT:-60} TEXLIM=${TEXLIM:-1024} WD_MIN=1500 bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b --factory-startup $B --python scripts/ws163/lean163.py 2>&1 | grep -E "WROTE|LEAN|rror|Trace|WATCH"; done; echo END
