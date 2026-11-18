import bpy,numpy as np
from mathutils import Vector
for o in bpy.data.objects:
    if 'accessible_symbol' in o.name or o.name.startswith('WS76'):
        mw=o.matrix_world; V=[mw@v.co for v in o.data.vertices] if o.type=='MESH' else []
        if V:
            xs=[v.x for v in V];ys=[v.y for v in V];zs=[v.z for v in V]
            print('P196',o.name,o.type,len(V),len(o.data.polygons),'x %.2f %.2f y %.2f %.2f z %.3f %.3f'%(min(xs),max(xs),min(ys),max(ys),min(zs),max(zs)),[m.name for m in o.data.materials],[m.type for m in o.modifiers],o.hide_render,flush=True)
