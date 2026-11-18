#!/bin/bash
cd /workspace/nj-scenes/montclair-state
for i in $(seq 1 120); do a=$(awk '/MemAvailable/{print int($2/1024)}' /proc/meminfo); [ $a -gt 6000 ] && break; sleep 5; done
echo "start avail=$a $(date)"
cp montclair_state.blend montclair_state_pre_20261110ws36.blend
cp montclair_state_pre_20261110ws35.blend /tmp/ws36_src.blend
cp /tmp/ws36_src.blend montclair_state.blend
FOFF=2.0 SX=-175 SY=-112 SAVE=1 WD_MIN=900 bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b montclair_state.blend --python scripts/ws36/build.py 2>&1 | grep -E "SAVED|rror:|Traceback|line [0-9]"
grep -q . /dev/null
sha256sum montclair_state.blend
SX=-175 SY=-112 OUT_TAG=GOLDEN_ws36_goldenhour CAMS="WS35_CAM_closeup_RedHawk_statue=closeup_RedHawk_statue_pass2,WS35_CAM_eye_RedHawk_statue_match4_from_W=eye_RedHawk_statue_match4_from_W_pass2" WD_MIN=1200 bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b montclair_state.blend --python scripts/ws35/render35.py 2>&1 | grep -E "WROTE|rror:|WATCHDOG"
echo done $(date)
