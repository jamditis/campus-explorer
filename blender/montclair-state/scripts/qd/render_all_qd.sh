#!/bin/bash
# one camera per Blender process (qc_render_lowmem radius cull), sequential, each under guard.sh
cd /workspace/nj-scenes/montclair-state
for spec in PE_CAM_oblique_dickson_from_SW:900 PE_CAM_eye_calcia_west:400 QA_CAM_eye_feliciano_sw_slope:400 QC_CAM_closeup_calcia_west_cornerbay:250; do
  c=${spec%%:*}; r=${spec##*:}
  echo "== $c RAD $r $(date +%H:%M:%S)"; CAMS=$c RAD=$r TEXLIM=1024 scripts/qd/guard.sh scripts/qd/render_qd.sh 2>&1 | tail -3
done
echo ALL_DONE $(date +%H:%M:%S)
