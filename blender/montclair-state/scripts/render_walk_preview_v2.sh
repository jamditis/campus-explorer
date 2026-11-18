#!/bin/bash
# Walk preview v2 (session 3h): extended path ending on Morehead pavilion fill. Keep v1 mp4 untouched.
# Every 2nd frame, 640x360, 16 spp, fast OIDN. Output frames_20261008_walk_v2 + 20261008_walk_preview_v2.mp4
cd /workspace/nj-scenes/montclair-state
OUT=renders/anim/frames_20261008_walk_v2; BLEND=${BLEND:-montclair_state.blend}
mkdir -p "$OUT"
n=$(ps -C blender --no-headers | wc -l); av=$(free -m | awk '/Mem:/{print $7}')
if [ "$n" -ge 2 ] || [ "$av" -lt 1500 ]; then echo "WAIT: $n blender running, $av MB available"; exit 2; fi
# discover frame_end from blend via blender one-liner if F1 not set
F1=${F1:-$(blender -b --factory-startup "$BLEND" --python-expr "import bpy; print('FEND', bpy.context.scene.frame_end)" 2>/dev/null | awk '/FEND/{print $2}')}
F1=${F1:-480}
echo "rendering walk v2 frames 1..$F1 step 2"
timeout 4800 blender -b --factory-startup "$BLEND" --python scripts/render_walk.py -- "$OUT" ${F0:-1} "$F1" 2 640 16 fast 2>&1 | grep -E "FRAME|Error|peak"
# fps: half of 24 with step 2 = 12; duration = F1/24 seconds of motion
ffmpeg -y -loglevel error -framerate 12 -pattern_type glob -i "$OUT/walk_*.png" -c:v libx264 -pix_fmt yuv420p -crf 20 renders/anim/20261008_walk_preview_v2.mp4 && echo "MP4 renders/anim/20261008_walk_preview_v2.mp4"
