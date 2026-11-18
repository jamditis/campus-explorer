# mw self-review fixes: brighter studio light panels (interior read too dark vs ccom_njpbs_newsroom_21);
# inset mezzanine slab/fascia/upper band 1 cm from the side walls (rule 4a: no coincident end faces against wall faces)
import bpy, math
from mathutils import Vector
L=math.hypot(0.238,0.9713); d=Vector((0.238/L,0.9713/L,0))
m=bpy.data.materials['MW_studio_light_panel_emit_UNVERIFIED']; m.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value=14.0
UA=-18.04+0.35; UB=1.8
for nm in ['CCOM newsroom back mezzanine slab + fascia (mw)','CCOM newsroom upper white band (mw)']:
    o=bpy.data.objects[nm]; k=0
    for v in o.data.vertices:
        u=d.dot(v.co)
        if abs(u-UA)<1e-3: v.co+=d*0.01; k+=1
        elif abs(u-UB)<1e-3: v.co-=d*0.01; k+=1
    print("INSET",nm,k)
bpy.ops.wm.save_mainfile(); print("SAVED",len(bpy.data.objects))
