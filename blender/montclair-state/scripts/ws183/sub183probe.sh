cd /workspace/nj-scenes/montclair-state
FIXES="ws182/fix182.py ws183/probe183.py" NORENDER=1 WD_MIN=1500 bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b --factory-startup --python scripts/ws182/sub182.py
