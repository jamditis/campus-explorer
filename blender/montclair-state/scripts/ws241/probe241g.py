# m2c241 check: does ground (evaluated M3a / skirt) poke through the merged Ice Arena / Lot 28S paving? sample paving faces
import bpy, os, json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
def ev(o):
    for m in o.modifiers: m.show_viewport=m.show_render
    dg=bpy.context.evaluated_depsgraph_get(); e=o.evaluated_get(dg); me=e.to_mesh(); M=o.matrix_world
    t=BVHTree.FromPolygons([M@v.co for v in me.vertices],[p.vertices[:] for p in me.polygons]); e.to_mesh_clear(); return t
NAMES=[o.name for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(('M3a_','Context_skirt','M3b_','Terrain','WS'))]
NAMES=[n for n in NAMES if (lambda cs:(min(c.x for c in cs)<-150 and max(c.x for c in cs)>-215 and min(c.y for c in cs)<715 and max(c.y for c in cs)>610))([bpy.data.objects[n].matrix_world@Vector(c) for c in bpy.data.objects[n].bound_box])]
print('P241G grounds',NAMES,flush=True)
GR=[ev(bpy.data.objects[n]) for n in NAMES]
out=[]
for o in bpy.data.objects:
    if not o.name.startswith(('KP IceArena','KQ Lot 28S','KR Lot 28S','KV Lot28S','Ice Arena L0','KU IceArena','KO IceArena')) or o.type!='MESH': continue
    M=o.matrix_world; n=0; bad=0; mx=0; worst=None
    for p in o.data.polygons:
        if (M.to_3x3()@p.normal).normalized().z<0.7: continue
        c=M@p.center; n+=1
        hh=[(t.ray_cast(Vector((c.x,c.y,c.z+20)),Vector((0,0,-1)),60)[0],nm) for t,nm in zip(GR,NAMES)]; hh=[(h.z,nm) for h,nm in hh if h is not None]; g,gn=max(hh,default=(-1e9,''))
        if g>c.z+0.01:
            bad+=1
            if g-c.z>mx: mx=g-c.z; worst=(round(c.x,1),round(c.y,1),round(c.z,2),gn[:30])
    out.append((o.name[:40],n,bad,round(mx,2),worst))
    print('P241G',o.name[:40],'up-faces',n,'ground above',bad,'max',round(mx,2),worst,flush=True)
os._exit(0)
