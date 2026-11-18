import bpy, bmesh, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
sk=bpy.data.objects['Context_skirt_3DEP_ortho_4km']
col=bpy.data.collections['WG_Bohn_W_door_landing_UNVERIFIED']
nm='WG_cut_skirt_W_door_feather'
if nm not in bpy.data.objects:
    me=bpy.data.meshes.new(nm); bm=bmesh.new(); bmesh.ops.create_cube(bm,size=1); bm.to_mesh(me); bm.free()
    c=bpy.data.objects.new(nm,me); col.objects.link(c)
else: c=bpy.data.objects[nm]
c.location=(212.25,405.5,135.0); c.scale=(5.5,15.0,10.0); c.hide_render=True; c.hide_viewport=True; c.display_type='WIRE'; c['wg_obj']=1
m=sk.modifiers.get('WG_cut_W_door') or sk.modifiers.new('WG_cut_W_door','BOOLEAN')
m.object=c; m.operation='DIFFERENCE'; m.solver='EXACT'
# move modifier before WF GN? keep at end (after WF dip) - fine
bpy.context.view_layer.update()
def bvh(o):
    dg=bpy.context.evaluated_depsgraph_get(); e=o.evaluated_get(dg); mm=e.to_mesh()
    t=BVHTree.FromPolygons([o.matrix_world@v.co for v in mm.vertices],[tuple(p.vertices) for p in mm.polygons]); e.to_mesh_clear(); return t
g=lambda t,x,y:(lambda h:h[0].z if h[0] else None)(t.ray_cast(Vector((x,y,400)),Vector((0,0,-1))))
bp=bvh(bpy.data.objects['WF_east_dorm_LiDAR_terrain_patch_UNVERIFIED']); bs=bvh(sk)
miss=[];out=[]
for x in np.arange(208,216.2,0.25):
    for y in np.arange(396,414,0.25):
        a=g(bp,x,y); b=g(bs,x,y)
        if a is None and b is None and x<215.9: miss.append((x,y))
        if 213.85<=x<=216.15 and 402.85<=y<=408.35: continue
        if a and b and b-a>0.02: out.append((round(b-a,3),x,y))
out.sort(reverse=True); print('POKES',len(out),out[:8]); print('HOLES',len(miss),miss[:10])
bpy.ops.wm.save_mainfile(); print('SAVED',len(bpy.data.objects))
