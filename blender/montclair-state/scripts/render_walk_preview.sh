#!/bin/bash
# Walk preview (session 3g): every 2nd frame of the 240-frame / 24 fps CAM_walk_west move at 640x360, 16 spp, fast OIDN; resumable (skips existing frames).
# Checks the two-Blender cap and free memory before starting. Then encodes 12 fps -> 10 s mp4.
cd /workspace/nj-scenes/montclair-state
OUT=renders/anim/frames_20261008_walk; BLEND=${BLEND:-montclair_state_walk3g.blend}
n=$(ps -C blender --no-headers | wc -l); av=$(free -m | awk '/Mem:/{print $7}')
if [ "$n" -ge 2 ] || [ "$av" -lt 1500 ]; then echo "WAIT: $n blender running, $av MB available"; exit 2; fi
timeout 3000 blender -b --factory-startup $BLEND --python scripts/render_walk.py -- $OUT ${F0:-1} ${F1:-240} 2 640 16 fast 2>&1 | grep -E "FRAME|Error"
ffmpeg -y -loglevel error -framerate 12 -pattern_type glob -i "$OUT/walk_*.png" -c:v libx264 -pix_fmt yuv420p -crf 20 renders/anim/20261008_walk_preview.mp4 && echo "MP4 renders/anim/20261008_walk_preview.mp4"
