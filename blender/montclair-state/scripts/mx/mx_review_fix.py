# mx review fixes (t5 close-up test): softbox shell read light grey (metallic black reflecting the floor) -> matte black;
# front light stand sat right behind the west glazing -> moved 0.6 m further in (t -2.6 -> -3.2).
import bpy, math
from mathutils import Vector
L=math.hypot(0.238,0.9713); n=Vector((-0.9713/L,0.238/L,0)); C0=20.36; T0=0.012
b=bpy.data.materials['MX_light_stand_black_UNVERIFIED'].node_tree.nodes['Principled BSDF']
b.inputs['Metallic'].default_value=0.0; b.inputs['Roughness'].default_value=0.85; b.inputs['Base Color'].default_value=(0.008,0.008,0.008,1)
k=0
for nm in ['CCOM newsroom light stands + softbox shells (mx)','CCOM newsroom softbox diffusers (mx, emissive)']:
    o=bpy.data.objects[nm]
    for v in o.data.vertices:
        if n.dot(v.co)-C0-T0>-4.5: v.co+=n*(-0.6); k+=1
    o.data.update()
print("MOVED",k)
bpy.ops.wm.save_mainfile(); print("SAVED",len(bpy.data.objects))
