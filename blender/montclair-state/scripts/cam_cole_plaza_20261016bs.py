import bpy, math, os
from mathutils import Vector
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
nm="CAM_closeup_cole_hall_plaza_bs"
o=bpy.data.objects.get(nm)
if o is None:
    cd=bpy.data.cameras.new(nm); o=bpy.data.objects.new(nm,cd)
    ref=bpy.data.objects["CAM_closeup_cole_hall_portico_br"]; ref.users_collection[0].objects.link(o)
    cd.clip_start=ref.data.clip_start; cd.clip_end=ref.data.clip_end
o.data.lens=24
deck=bpy.data.objects["COLE_plaza_deck_bs"]
from mathutils.bvhtree import BVHTree
bv=BVHTree.FromObject(deck,dg)
x,y=-197.0,-97.0
h=bv.ray_cast(Vector((x,y,200)),Vector((0,0,-1)))
gz=h[0].z if h[0] else 129.0
o.location=(x,y,gz+2.2)
tgt=Vector((-172.0,-74.0,gz+2.6))
dirv=(tgt-o.location).normalized()
o.rotation_euler=dirv.to_track_quat('-Z','Y').to_euler()
print("CAMSET",nm,tuple(round(a,2) for a in o.location), "ground", round(gz,2))
if os.environ.get("SAVE")=="1": bpy.ops.wm.save_mainfile(); print("SAVED")
