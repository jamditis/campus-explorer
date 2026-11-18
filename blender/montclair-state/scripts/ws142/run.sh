# usage: run.sh script.py log [OUT]
cd /workspace/nj-scenes/montclair-state
NEED=${NEED:-6500} MAXW=${MAXW:-1500} bash scripts/ws138/waitmem.sh env WD_MIN=${WD_MIN:-1200} bash scripts/ws33/wd.sh timeout ${TO:-900} /workspace/opt/blender/blender -b --factory-startup ${BLEND:-montclair_state.blend} --python $1 > $2 2>&1
echo "EXIT $? $(date +%T)" >> $2
