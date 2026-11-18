cd /workspace/nj-scenes/montclair-state
WD_MIN=1500 bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b --factory-startup montclair_state_ws171b.blend --python scripts/ws171/probe171c.py 2>&1 | grep -E "PROBE|rror|Trace|WATCH"; echo END
