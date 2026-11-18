# ws180 subset: sub178 objects + WS86/WS179, ws177/178 fixes (as the pending merge), optional probe179 / fix179, then renders (tail180)
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
for f in ('ws177/fix177.py','ws177/fix177b.py','ws177/fix177c.py','ws178/fix178.py'): exec(open(S+f).read())
if os.environ.get('PROBE')=='1': exec(open(S+'ws179/probe179.py').read())
if os.environ.get('FIX179')=='1':
    try: exec(open(S+'ws179/fix179.py').read())
    except SystemExit: print('FIX179 dry exit',flush=True)
if os.environ.get('FIX180')=='1': exec(open(S+'ws180/fix180.py').read())
if os.environ.get('FIX180B')=='1': exec(open(S+'ws180/fix180b.py').read())
exec(open(S+'ws181/fix181.py').read()); exec(open(S+'ws182/fix182.py').read())
exec(open(S+'ws179/probe179.py').read())
if os.environ.get('NORENDER')=='1': raise SystemExit
exec(compile(open(S+'ws180/tail180.py').read(),'tail','exec'))
