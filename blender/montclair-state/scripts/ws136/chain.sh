cd /workspace/nj-scenes/montclair-state
NEED=6000 MAXW=1080 bash scripts/ws136/waitmem.sh bash -c '
WD_MIN=1500 SAVE=1 bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b --factory-startup montclair_state.blend --python scripts/ws136/main136a.py > scripts/ws136/main136a.log 2>&1
echo MAINDONE $(date +%T) >> scripts/ws136/main136a.log'
