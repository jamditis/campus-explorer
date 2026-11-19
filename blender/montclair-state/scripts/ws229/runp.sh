#!/bin/bash
# probe runner: open main with all modifiers off at load_post (no full-scene eval), run PY
cd /workspace/nj-scenes/montclair-state
cat > /tmp/ws229_off.py <<'P'
import bpy,os
from bpy.app.handlers import persistent
@persistent
def _off(*a):
    for o in bpy.data.objects:
        for m in o.modifiers: m.show_viewport=False
bpy.app.handlers.load_post.append(_off)
bpy.ops.wm.open_mainfile(filepath=os.environ.get('INF','/workspace/nj-scenes/montclair-state/montclair_state.blend'))
exec(open(os.environ['PY']).read())
P
PY=${PYF:-$PWD/scripts/ws229/$1} WD_MIN=1200 bash scripts/ws33/wd.sh /workspace/opt/blender/blender -b --factory-startup --python /tmp/ws229_off.py 2>&1 | grep -E "${2:-P229}|rror|Trace|WATCH"
