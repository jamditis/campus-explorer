import bpy, os
from mathutils import Vector
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
# vertical multi-hit probe: list every surface under each point (top first)
pts=[tuple(float(c) for c in p.split(':')) for p in os.environ['PXY'].split()]
for (x,y) in pts:
    o=Vector((x,y,160.0)); hits=[]
    for i in range(8):
        h,loc,nor,fi,ob,_=sc.ray_cast(dg,o,Vector((0,0,-1)))
        if not h: break
        mat=''
        try:
            me=ob.data; mi=me.polygons[fi].material_index if fi < len(me.polygons) else -1
            mat=me.materials[mi].name[:30] if mi>=0 and me.materials else ''
        except Exception: pass
        hits.append((ob.name[:40],round(loc.z,3),round(nor.z,2),mat)); o=loc-Vector((0,0,0.002))
    print('P188',(x,y),hits,flush=True)
