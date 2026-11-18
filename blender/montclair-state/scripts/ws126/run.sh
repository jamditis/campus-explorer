cd /workspace/nj-scenes/montclair-state
WD_MIN=1300 bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b --factory-startup montclair_state.blend --python scripts/ws126/main126.py 2>&1 | grep -E "M126|rror|Trace|WATCH|line"
