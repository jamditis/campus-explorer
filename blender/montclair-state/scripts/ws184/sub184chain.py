# ws184 chain subset test (loader from ws182/sub182chain.py; runs scripts/ws184/chain.txt in order). Orig: ws180 subset: sub178 objects + WS86/WS179, ws177/178 fixes (as the pending merge), optional probe179 / fix179, then renders (tail180)
import numpy as np, math
from mathutils import Vector
import bpy, os, sys
p='/workspace/nj-scenes/montclair-state/montclair_state.blend'
PRE=('WS167','WS169','WS162','Context_ground_beyond','WS138b_ground_fill','WS134_ground_patch','WS133b_ground_patch','WS163','WS110','WS172','WS173','WS174','WS175','WS166','WS170','WS113_paving_tops_proxy','UTIL170','WS86','WS179')
with bpy.data.libraries.load(p) as (a,b):
    b.objects=[n for n in a.objects if n.startswith(PRE) and 'skirt' not in n.lower() and 'CAM' not in n and 'hidden' not in n]
sc=bpy.context.scene
for o in b.objects:
    if o is None: continue
    if o.type in ('MESH','CURVE','EMPTY') and o.name not in sc.collection.objects: sc.collection.objects.link(o)
print('LOADED',len([o for o in b.objects if o]),flush=True)
S='/workspace/nj-scenes/montclair-state/scripts/'
for f in [l.strip() for l in open(S+'ws184/chain.txt') if l.strip() and not l.startswith('#')]:
    exec(open(S+f).read())
print('CHAIN DONE',flush=True)
