#!/bin/bash
cd /workspace/nj-scenes/montclair-state
CULL=${CULL:--360,-210,-180,-40} MAXSPAN=3000 ALWAYS=Terrain_LiDAR_DTM_1m SKIP="${SKIP:-band_street,tuft,ev_rhd,ew_rhd,fi_rhd,ex_rhd}" TEXLIM=${TEXLIM:-512} SAMP=${SAMP:-12} PCT=${PCT:-45} DIR=${DIR:-test} WD_MIN=${WD_MIN:-1500} timeout 900 bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b --factory-startup --python scripts/ws75/render75L.py 2>&1 | grep -E "^(LR|WS75)|WROTE|WATCHDOG|Error|rror"
