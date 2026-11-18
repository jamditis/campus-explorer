#!/bin/bash
# tl (copy of tk render)
cd /workspace/nj-scenes/montclair-state; B=/workspace/opt/blender/blender; O=${ODIR:-renders/wip}
for C in ${CAMS//,/ }; do
  T=$(date +%Y%m%d-%H%M); free -m | awk '/Mem:/{print "avail",$7}'
  CAMS=$C EXR=1 OUT=$O/${T}_CAM_tl.jpg RES=${RES:-80} SPP=${SPP:-40} RAD=${RAD:-450} bash scripts/pw/guard.sh $B -b ${BLEND:-montclair_state.blend} ${PRE:+--python $PRE} --python scripts/qe/qe_render_lowmem.py > data/tl/r_${T}_$C.log 2>&1
  tail -1 data/tl/r_${T}_$C.log
  for e in $O/${T}_*_tl.exr; do [ -f "$e" ] || continue; j=${e%.exr}.jpg; $B -b --factory-startup --python scripts/denoise_exr.py -- $e $j AgX "AgX - Base Contrast" -1.0 1024 576 > /dev/null 2>&1; ls -la $j; rm -f $e; done
done
echo RENDER_DONE
