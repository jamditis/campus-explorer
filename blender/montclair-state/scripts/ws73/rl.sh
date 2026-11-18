#!/bin/bash
# lite render runner with MemAvailable watchdog (floor WD_MIN, default 1500 MB)
cd /workspace/nj-scenes/montclair-state
CULL=${CULL:--275,-225,-75,-35} MAXSPAN=3000 ALWAYS=Terrain_LiDAR_DTM_1m SKIP="${SKIP:-band_street,tuft,ev_rhd,ew_rhd,fi_rhd,ex_rhd}" TEXLIM=${TEXLIM:-512} SAMP=${SAMP:-12} PCT=${PCT:-45} DIR=${DIR:-test} WD_MIN=${WD_MIN:-1500} timeout 900 bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b --factory-startup --python scripts/ws73/render73L.py 2>&1 | grep -E "^(LR|W72 (c|t|j))|WROTE|WATCHDOG|Error|rror"
