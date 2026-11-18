import bpy
from mathutils import Vector
dg=bpy.context.evaluated_depsgraph_get()
sk=bpy.data.objects['Context_skirt_3DEP_ortho_4km'].evaluated_get(dg)
def gz(x,y):
    r=sk.ray_cast(Vector((x,y,400)),Vector((0,0,-1))); return r[1].z if r[0] else None
for n in ['TL_tree_095_UNVERIFIED','TL_tree_099_UNVERIFIED','TL_tree_100_UNVERIFIED','TL_tree_101_UNVERIFIED','TL_tree_104_UNVERIFIED']:
    o=bpy.data.objects[n]; mw=o.matrix_world; p0=mw.translation
    for rad in (0.3,0.6):
        P=[mw@v.co for v in o.data.vertices if ((mw@v.co).xy-p0.xy).length<rad]
        if P: print('TT',n,rad,'n',len(P),'zmin',round(min(p.z for p in P),2),'zmax',round(max(p.z for p in P),2),'g',round(gz(p0.x,p0.y),2))
    # local data: verts near local origin
    L=[v.co for v in o.data.vertices if v.co.xy.length<0.3]
    print('TL',n,'local zmin',round(min(v.z for v in L),2) if L else None, 'lz of all min',round(min(v.co.z for v in o.data.vertices),2))
