import bpy
from mathutils import Vector
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
for x in (-226,-232,-238):
  for y in [-71+0.75*k for k in range(14)]:
    ok,loc,n,i,o,_=sc.ray_cast(dg,Vector((x,y,150)),Vector((0,0,-1)))
    mn=''
    if ok and o.type=='MESH':
        e=o.evaluated_get(dg); me=e.data
        if i<len(me.polygons):
            mi=me.polygons[i].material_index; mn=me.materials[mi].name if mi<len(me.materials) and me.materials[mi] else ''
    print('P89C',x,y,round(loc.z,2) if ok else None,o.name[:45] if ok else '',mn[:30])
c=bpy.data.objects['WS89_CAM_eye_median_from_CollegeAve_E']; print('P89C cam',tuple(round(v,2) for v in c.location))
