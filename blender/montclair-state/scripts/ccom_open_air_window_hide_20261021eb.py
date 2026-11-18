# Session eb: Joe 3:43 PM "dark vertical slot beside the white glazed stair block" (ea aerial) = CCOM_Win_Wing_A
# window instances generated ABOVE the SCM wall top (143.0) next to Life Hall (x 27-35, y 4-7): their dark room
# boxes stand in open air above the lower roof. Hide every visible Wing_A instance whose room-box interior has NO
# roof/eave/soffit anywhere above it (open air) -> prop 'eb_hidden'. Idempotent; SAVE=1 saves; REVERT=1 unhides.
import bpy, os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
SAVE=os.environ.get('SAVE')=='1'; REVERT=os.environ.get('REVERT')=='1'
for o in bpy.data.objects:
    if o.get('eb_hidden'): o.hide_render=False; o.hide_viewport=False; del o['eb_hidden']
if not REVERT:
    dg=bpy.context.evaluated_depsgraph_get(); vs=[]; fs=[]
    for ob in bpy.data.objects:
        if ob.type!='MESH' or ob.hide_render: continue
        if not any(k in ob.name.lower() for k in ('roof','soffit','eave')): continue
        e=ob.evaluated_get(dg); m=e.to_mesh(); M=ob.matrix_world; off=len(vs)
        vs+=[M@v.co for v in m.vertices]; fs+=[[off+i for i in p.vertices] for p in m.polygons]; e.to_mesh_clear()
    B=BVHTree.FromPolygons(vs,fs); hid=[]
    for o in bpy.data.objects:
        if o.instance_type!='COLLECTION' or not o.instance_collection or o.hide_render: continue
        if not o.instance_collection.name.startswith('CCOM_Win_Wing_A'): continue
        M=o.matrix_world; c=M@Vector((0,-1.2,1.2))
        if B.ray_cast(c,Vector((0,0,1)),30.0)[0] is None:
            o['eb_hidden']=1; o.hide_render=True; o.hide_viewport=True
            hid.append((o.name,tuple(round(x,2) for x in o.location)))
    print('HIDDEN',len(hid)); [print('  H',h) for h in hid]
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
