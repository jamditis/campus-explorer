import numpy as np, math, bpy, os
from mathutils import Vector
p='/workspace/nj-scenes/montclair-state/montclair_state.blend'
PRE=('Context_ground_beyond','WS16','WS17','WS163','WS110','WS13','UTIL170','WS86','WS179','WS113_paving_tops_proxy')
with bpy.data.libraries.load(p) as (a,b):
    b.objects=[n for n in a.objects if n.startswith(PRE) and 'skirt_target' not in n and 'CAM' not in n and 'hidden' not in n]
sc=bpy.context.scene
for o in b.objects:
    if o is None: continue
    if o.type in ('MESH','CURVE','EMPTY') and o.name not in sc.collection.objects: sc.collection.objects.link(o)
print('LOADED',len([o for o in b.objects if o]),flush=True)
S='/workspace/nj-scenes/montclair-state/scripts/'
exec(open(S+'ws181/fix181.py').read())
for f in os.environ.get('FIXES','').split():
    exec(open(S+f).read())
if os.environ.get('MAP')=='1': exec(open(S+'ws182/map182.py').read())
if os.environ.get('NORENDER')=='1': raise SystemExit
exec(compile(open(S+os.environ.get('TAIL','ws182/tail182.py')).read(),'tail','exec'))
