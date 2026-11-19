# read-only: which surface is on top along the close-up camera's view (evaluated, skirt GN on)
import bpy, mathutils, os
F=os.environ.get('F','/workspace/nj-scenes/montclair-state/montclair_state_ws236c.blend')
with bpy.data.libraries.load(F) as (a,b): b.objects=[n for n in a.objects if n.startswith(('M3b_','PK_Feliciano','WS60_terrain','WS68_RHD_ground','Context_skirt_3DEP_ortho_4km'))]
for o in b.objects: bpy.context.scene.collection.objects.link(o)
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
for x,y in [(-330,213),(-327,211),(-324,209),(-321,208),(-318,206),(-315,205),(-312,203),(-325,200),(-322,190),(-310,215)]:
    r=sc.ray_cast(dg,mathutils.Vector((x,y,300)),mathutils.Vector((0,0,-1)))
    print('P236E',x,y,r[4].name[:20] if r[0] else None,round(r[1].z,2) if r[0] else None,flush=True)
