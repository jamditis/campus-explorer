#!/bin/bash
# qo: one camera per Blender process, sequential (copy of qn's render_qn.sh with qo names)
cd /workspace/nj-scenes/montclair-state; B=/workspace/opt/blender/blender; O=${ODIR:-renders/wip}; mkdir -p $O
for C in ${CAMS//,/ }; do
  T=$(date +%Y%m%d-%H%M); free -m | awk '/Mem:/{print "avail",$7}'
  CAMS=$C EXR=1 OUT=$O/${T}_CAM_qo.jpg RES=${RES:-80} SPP=${SPP:-40} RAD=${RAD:-450} bash scripts/pw/guard.sh $B -b ${BLEND:-montclair_state.blend} ${PRE:+--python $PRE} --python scripts/qe/qe_render_lowmem.py > data/qo/r_${T}_$C.log 2>&1
  tail -1 data/qo/r_${T}_$C.log
  for e in $O/${T}_*_qo.exr; do [ -f "$e" ] || continue; j=${e%.exr}.jpg; $B -b --factory-startup --python scripts/denoise_exr.py -- $e $j AgX "AgX - Base Contrast" -1.0 1024 576 > /dev/null 2>&1; ls -la $j; rm -f $e; done
done
echo RENDER_DONE
