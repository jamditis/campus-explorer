import bpy
from mathutils import Vector
dg=bpy.context.evaluated_depsgraph_get()
sk=bpy.data.objects['Context_skirt_3DEP_ortho_4km'].evaluated_get(dg)
def gz(x,y):
    r=sk.ray_cast(Vector((x,y,400)),Vector((0,0,-1))); return r[1].z if r[0] else None
for n in ['TL_tree_095_UNVERIFIED','TL_tree_096_UNVERIFIED','TL_tree_099_UNVERIFIED','TL_tree_100_UNVERIFIED','TL_tree_101_UNVERIFIED','TL_tree_104_UNVERIFIED','TL_tree_107_UNVERIFIED']:
    o=bpy.data.objects[n]; mw=o.matrix_world
    P=[mw@v.co for v in o.data.vertices]
    zmin=min(p.z for p in P); low=[p for p in P if p.z<zmin+0.3]
    c=sum(low,Vector())/len(low)
    print('TB',n,'origin',[round(x,2) for x in mw.translation],'scale',[round(x,2) for x in o.scale],'zmin',round(zmin,2),'lowc',round(c.x,2),round(c.y,2),'g_low',round(gz(c.x,c.y),2),'mods',[m.type for m in o.modifiers],'parent',o.parent.name if o.parent else None)
