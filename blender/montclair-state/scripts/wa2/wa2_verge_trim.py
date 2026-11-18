"""wa2 verge trim: undo the verge raise on WT verts at y>311 (WT north fade / WF seam) because it opened thin black cracks in the N eye view; re-snap grass and re-seat the 3 strips there."""
import bpy, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R='/workspace/nj-scenes/montclair-state'; O=bpy.data.objects; dg=bpy.context.evaluated_depsgraph_get()
Y0=float(__import__('os').environ.get('Y0','311'))
o=O['WT_richardson_west_LiDAR_patch_UNVERIFIED']; pre=np.load(f'{R}/data/wa2/WT_richardso_pre_wa2.npy'); mw=o.matrix_world; k=0
for v in o.data.vertices:
    c=mw@v.co
    if c.y>Y0 and abs(v.co.z-pre[v.index][2])>1e-5: v.co=Vector(pre[v.index]); k+=1
o.data.update(); print('RESTORED',k); bpy.context.view_layer.update(); dg=bpy.context.evaluated_depsgraph_get()
def bvh(o):
    e=o.evaluated_get(dg); m=e.to_mesh(); b=BVHTree.FromPolygons([o.matrix_world@v.co for v in m.vertices],[tuple(p.vertices) for p in m.polygons]); e.to_mesh_clear(); return b
G=[bvh(O[n]) for n in O.keys() if O[n].type=='MESH' and n.startswith(('WT_richardson_west_LiDAR','RZ2_','WF_east_dorm_LiDAR','WU_richardson_reid','QW_DTM'))]
SL=[bvh(O[n]) for n in O.keys() if O[n].type=='MESH' and n.startswith(('QS_footway_','QW_footway_','QS_service_','TR_footway','SG_'))]
def top(B,x,y):
    z=[h[0].z for b in B for h in [b.ray_cast(Vector((x,y,500)),Vector((0,0,-1)))] if h[0] is not None]; return max(z) if z else None
for name in [n for n in O.keys() if 'grass_points' in n and n[:2] in ('QS','QV')]:
    g=O[name]; m=g.matrix_world; mi=m.inverted(); n=0
    for v in g.data.vertices:
        c=m@v.co
        if not (38<=c.x<=78 and Y0-1<=c.y<=322): continue
        z=top(G,c.x,c.y)
        if z is None or top(SL,c.x,c.y) is not None: continue
        if abs(c.z-z)>0.005: c.z=z; v.co=mi@c; n+=1
    g.data.update(); print('GRASS',name,n)
for sn in ['313027436','313027429','313027435']:
    t=O[f'QT_soil_edge_{sn}_UNVERIFIED']; S=bvh(O[f'QS_footway_{sn}_UNVERIFIED']); mw=t.matrix_world; inv=mw.inverted(); n=0
    for p in t.data.polygons:
        vi=list(p.vertices); ws=[mw@t.data.vertices[i].co for i in vi]; d=[S.find_nearest(v)[3] for v in ws]
        for j in np.argsort(d)[2:]:
            v=ws[j]
            if v.y<=Y0-0.5: continue
            z=top(G,v.x,v.y)
            if z is not None and abs(v.z-(z+0.01))>0.003: t.data.vertices[vi[j]].co=inv@Vector((v.x,v.y,z+0.01)); n+=1
    t.data.update(); print('RESEAT',sn,n)
bpy.ops.wm.save_mainfile(); print('SAVED',len(O))
