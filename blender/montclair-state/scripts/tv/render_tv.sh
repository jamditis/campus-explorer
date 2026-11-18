#!/bin/bash
cd /workspace/nj-scenes/montclair-state
B=/workspace/opt/blender/blender
O=${ODIR:-renders/wip}
TAG=${TAG:-tv}
RES=${RES:-80}
SPP=${SPP:-36}
RAD=${RAD:-320}
for C in ${CAMS//,/ }; do
  T=$(date +%Y%m%d-%H%M)
  free -m | awk '/Mem:/{print "avail",$7}'
  echo "RENDER $C @ $T"
  CAMS=$C EXR=1 OUT=$O/${T}_CAM_${TAG}.jpg RES=$RES SPP=$SPP RAD=$RAD \
    bash scripts/pw/guard.sh $B -b ${BLEND:-montclair_state.blend} ${PRE:+--python $PRE} \
    --python scripts/qe/qe_render_lowmem.py > data/tv/r_${T}_$C.log 2>&1
  tail -3 data/tv/r_${T}_$C.log | grep -E 'Saved|Error|Traceback' || true
  ls -lt $O/${T}_*${TAG}.jpg 2>/dev/null | head -2
done
