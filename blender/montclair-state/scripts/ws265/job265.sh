cd /workspace/nj-scenes/montclair-state
WD_MIN=1200 bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b --factory-startup $PWD/montclair_state.blend --python scripts/ws264/m5check264.py 2>&1 | grep -E "M5C264|rror|WATCH" > scripts/ws265/m5check264_ws265a.out
echo "$(date +%T) M5 done"
bash scripts/ws265/jobwip265.sh
echo "$(date +%T) ALLDONE"
