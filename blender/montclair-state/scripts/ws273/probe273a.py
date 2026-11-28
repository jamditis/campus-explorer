# ws273 probe A (merge208 CHAIN, NO SAVE): what makes the dark rectangle at the Sprague lot S edge (#4b) and the x~-249 tone line (#4a).
import bpy, os, collections, numpy as np
from mathutils import Vector
TAG='P273A'; BX=(-262.0,-226.0,-122.0,-104.0)
def meets(o,m=0.0):
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    return not (max(v.x for v in bb)<BX[0]-m or min(v.x for v in bb)>BX[1]+m or max(v.y for v in bb)<BX[2]-m or min(v.y for v in bb)>BX[3]+m)
for o in bpy.context.scene.objects:
    if o.type!='MESH' or not meets(o) or o.name.startswith(('T_','TREE','gd_grass','BD_farfield','Context_skirt')): continue
    me=o.data; mw=o.matrix_world
    cnt=collections.Counter(); zs=[]
    for p in me.polygons:
        c=mw@p.center
        if BX[0]<c.x<BX[1] and BX[2]<c.y<BX[3]:
            mn=o.material_slots[p.material_index].material.name if o.material_slots and o.material_slots[p.material_index].material else None
            cnt[mn]+=1; zs.append(c.z)
    if not cnt: continue
    print(TAG,'OBJ',o.name[:70],'hide_render',o.hide_render,'faces_in',sum(cnt.values()),'z',round(min(zs),2),round(max(zs),2),'mats',dict(cnt),'mods',[(m.name,m.type,m.show_viewport,m.show_render) for m in o.modifiers],flush=True)
# per 1 m cell: highest base-mesh face centre per object (cheap first-hit proxy) at y -104..-122, x -252..-234
for y in np.arange(-104.5,-122,-1.0):
    row=[]
    for x in np.arange(-252.5,-232,1.0):
        row.append('.')
    pass
os._exit(0)
