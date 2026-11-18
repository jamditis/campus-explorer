# usage: srun CULL CAM NAME FILE DIR [CHAIN]  (env KEEPALL=1 keeps every modifier; KEEPMOD names)
cd /workspace/nj-scenes/montclair-state
srun(){ until ! pgrep -x blender >/dev/null && [ $(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo) -ge ${GATE:-2500} ]; do sleep 2; done; T=$(date +%Y%m%d-%H%M); echo "$(date +%T) $3 $(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo)"
 FILE=$PWD/$4 CHAIN="${6:-}" CAM="$2" CULL="$1" OUTF=$PWD/renders/$5/${T}_$3.jpg SAMP=${SAMP:-12} PCT=${PCT:-55} WD_MIN=${WDM:-900} bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b --factory-startup --python scripts/ws212/subrend212.py 2>&1 | grep -E "WROTE|SUB205|Trace|rror|WATCH|MEM189"; }
