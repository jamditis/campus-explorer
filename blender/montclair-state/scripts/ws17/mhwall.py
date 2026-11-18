"""ws17: pale lens at Morehead's west eave = wall tops (z up to 144.3) reaching the roof surface (coplanar/poking,
roof material has alpha at the eave). Clamp Morehead Hall walls verts to <= roof_z - CL under the LiDAR roof
(BVH down-rays). APPLY=1 saves; else crop render."""
import bpy,os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
CL=float(os.environ.get('CL','0.12'))
dg=bpy.context.evaluated_depsgraph_get()
r=bpy.data.objects['Morehead Hall roof (LiDAR)']; re=r.evaluated_get(dg)
bvh=BVHTree.FromObject(re,dg)  # roof local == world? check
print('roofMW identity',r.matrix_world.is_identity)
w=bpy.data.objects['Morehead Hall walls']; me=w.data; print('wallMW identity',w.matrix_world.is_identity,'mods',[m.type for m in w.modifiers])
ch=0; maxd=0
for v in me.vertices:
    if v.co.z<143.0: continue
    hit=bvh.ray_cast(Vector((v.co.x,v.co.y,160.0)),Vector((0,0,-1)))
    if hit[0] is None: continue
    lim=hit[0].z-CL
    if v.co.z>lim:
        maxd=max(maxd,v.co.z-lim); v.co.z=lim; ch+=1
me.update(); print('CLAMPED',ch,'max drop',round(maxd,3))
w['ws17_walltop_clamp']=f'clamped {ch} verts to roof-{CL}'
if os.environ.get('APPLY')=='1':
    bpy.ops.wm.save_mainfile(); print('SAVED')
else:
    exec(open('/workspace/nj-scenes/montclair-state/scripts/ws17/crop_render.py').read().replace('0145_ws17_probe_morehead_eavetop_tile','0152_ws17_probe_morehead_wallclamp'))
