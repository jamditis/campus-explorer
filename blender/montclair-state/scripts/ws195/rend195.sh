cd /workspace/nj-scenes/montclair-state
DLR=${DLR:-$(( $(date +%s) + 1500 ))}
F=${F:-montclair_state_ws173a.blend}; TAG=${TAG:-ws173a}
for c in $LIST; do
 until ! pgrep -x blender >/dev/null && [ $(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo) -ge ${RGATE:-10500} ]; do
   [ $(date +%s) -ge $DLR ] && { echo "$(date +%T) RENDER TIMEOUT"; exit 3; }; sleep 5; done
 echo "$(date +%T) R $c $(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo)"
 CAMS="$c" DIR=wip OUT_TAG=$TAG SAMP=16 PCT=60 TEXLIM=${TEXLIM:-1024} CHILD=${CHILD:-1.0} CULL=${CULL:--380,-260,-300,-140} WD_MIN=1500 bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b --factory-startup $F --python scripts/ws195/render195.py 2>&1 | grep -E "WROTE|rror|Trace|WATCH"
done; echo "$(date +%T) ALL DONE"
