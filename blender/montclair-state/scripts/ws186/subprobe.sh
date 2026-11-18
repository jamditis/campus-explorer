cd /workspace/nj-scenes/montclair-state
FIXES="ws182/fix182.py ws183/fix183.py ws184/fix184.py ws185/fix185.py ${EXTRA}" NORENDER=1 WD_MIN=1500 timeout 900 bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b --factory-startup --python scripts/ws182/sub182.py
