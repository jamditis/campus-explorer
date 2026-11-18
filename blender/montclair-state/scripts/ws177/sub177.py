import numpy as np, math
from mathutils import Vector
import bpy, os, sys
p='/workspace/nj-scenes/montclair-state/montclair_state.blend'
PRE=('WS138b_ground_fill','WS134_ground_patch','WS133b_ground_patch','WS163','WS110','WS172','WS173','WS174','WS175','WS166','WS170','WS113_paving_tops_proxy','UTIL170')
with bpy.data.libraries.load(p) as (a,b):
    b.objects=[n for n in a.objects if n.startswith(PRE) and 'skirt' not in n.lower() and 'CAM' not in n and 'hidden' not in n]
sc=bpy.context.scene
for o in b.objects:
    if o is None: continue
    if o.type in ('MESH','CURVE','EMPTY') and o.name not in sc.collection.objects: sc.collection.objects.link(o)
print('LOADED',len([o for o in b.objects if o]),flush=True)
if os.environ.get('NOFIX')!='1':
    exec(open('/workspace/nj-scenes/montclair-state/scripts/ws177/fix177.py').read())
    if os.environ.get('FIXB','1')=='1': exec(open('/workspace/nj-scenes/montclair-state/scripts/ws177/fix177b.py').read())
    if os.environ.get('FIXC')=='1': exec(open('/workspace/nj-scenes/montclair-state/scripts/ws177/fix177c.py').read())
exec(compile(open('/workspace/nj-scenes/montclair-state/scripts/ws177/sub177tail.py').read(),'tail','exec'))
