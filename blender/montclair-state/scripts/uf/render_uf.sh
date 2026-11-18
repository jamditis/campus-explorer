#!/bin/bash
# Render 4 WIPs for session uf. Usage: TS=YYYYMMDD-HHMM ./render_uf.sh
set -e
cd /workspace/nj-scenes/montclair-state
B=/workspace/opt/blender/blender
F=${BLEND:-montclair_state.blend}
TS=${TS:-$(date +%Y%m%d-%H%M)}
OUT=renders/wip
mkdir -p "$OUT"
free -m | head -2
cams=(
  "UF_CAM_closeup_NormalAve_softend"
  "UF_CAM_eye_NormalAve_from_N"
  "UF_CAM_eye_CollegeHall_from_E"
  "UF_CAM_closeup_CollegeHall_east_arches"
)
for c in "${cams[@]}"; do
  avail=$(free -m | awk '/Mem:/{print $7}')
  echo "=== render $c avail=${avail}MB ==="
  if [ "$avail" -lt 1500 ]; then
    echo "LOW MEM — sync drop_caches attempt"
    sync; echo 3 | sudo tee /proc/sys/vm/drop_caches >/dev/null || true
    sleep 1
  fi
  OUTPATH="$OUT/${TS}_${c}_uf.jpg"
  CAM="$c" OUT="$OUTPATH" $B -b "$F" --python scripts/uf/uf_render_one.py 2>&1 | tail -5
  ls -la "$OUTPATH"
done
echo "$TS" > data/uf/wip_ts.txt
echo DONE renders TS=$TS
