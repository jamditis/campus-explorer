import bpy
from mathutils import Vector
SKIPP=('T_','Lamp_','Bench_','PC_fillet_grass','PL_feliciano_lawn_grass','cx_','Tree','tree')
def ground(x,y,dg,sc,top=400.0):
    z=top
    for _ in range(25):
        r=sc.ray_cast(dg,Vector((x,y,z)),Vector((0,0,-1)))
        if not r[0]: return None,None
        o=r[4]
        if o.name.startswith(SKIPP) or 'grass' in o.name.lower() or o.type!='MESH' and o.type!='CURVES':
            z=r[1].z-0.01; continue
        if o.name.startswith(('Context_ground_beyond','BD_','Context_skirt')) : return r[1].z,o.name
        return r[1].z,o.name
    return None,None
