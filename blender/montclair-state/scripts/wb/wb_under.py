"""wb: lift WT verts that sit UNDER walks 435/436/429 (y 310.5-318.3, y-fade to 0 at 318.3) to slab top -5 cm (raise-only), so the coarse (~1.5 m) WT faces no longer dip from a low under-slab vert to the raised verge -> removes the remaining soil face on the 435 north stretch. Then re-snap QS/QV grass + re-seat strips."""
import bpy,numpy as np,sys
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R='/workspace/nj-scenes/montclair-state'; O=bpy.data.objects; dg=bpy.context.evaluated_depsgraph_get()
def bvh(o):
    e=o.evaluated_get(dg); m=e.to_mesh(); b=BVHTree.FromPolygons([o.matrix_world@v.co for v in m.vertices],[tuple(p.vertices) for p in m.polygons]); e.to_mesh_clear(); return b
WK=['313027435','313027436','313027429']
S=[bvh(O[f'QS_footway_{k}_UNVERIFIED']) for k in WK]
def top(B,x,y):
    z=[h[0].z for b in B for h in [b.ray_cast(Vector((x,y,500)),Vector((0,0,-1)))] if h[0] is not None]; return max(z) if z else None
o=O['WT_richardson_west_LiDAR_patch_UNVERIFIED']; mw=o.matrix_world; mi=mw.inverted()
np.save(f'{R}/data/wb/WT_pre_wb_under.npy',np.array([v.co[:] for v in o.data.vertices]))
k=0;mx=0
for v in o.data.vertices:
    c=mw@v.co
    if not (38<=c.x<=78 and 310.5<=c.y<=318.3): continue
    s=None
    for dx,dy in ((0,0),(0.3,0),(-0.3,0),(0,0.3),(0,-0.3)):
        t=top(S,c.x+dx,c.y+dy)
        if t is not None: s=t if s is None else max(s,t)
    if s is None: continue
    fy=1.0 if c.y<=316.5 else max(0.0,(318.3-c.y)/1.8); fy=fy*fy*(3-2*fy)
    tgt=c.z+max(0.0,(s-0.05)-c.z)*fy
    if tgt>c.z+0.002: mx=max(mx,tgt-c.z); c.z=tgt; v.co=mi@c; k+=1
o.data.update(); print('UNDER',k,round(mx,3)); bpy.context.view_layer.update(); dg=bpy.context.evaluated_depsgraph_get()
G=[bvh(O[n]) for n in O.keys() if O[n].type=='MESH' and n.startswith(('WT_richardson_west_LiDAR','RZ2_','WF_east_dorm_LiDAR','WU_richardson_reid','QW_DTM'))]
SL=[bvh(O[n]) for n in O.keys() if O[n].type=='MESH' and n.startswith(('QS_footway_','QW_footway_','QS_service_','TR_footway','SG_'))]
# pokes
pk=0
for x in np.arange(38,78,0.25):
    for y in np.arange(310,319,0.25):
        s=top(SL,x,y)
        if s is None: continue
        g=top(G,x,y)
        if g is not None and g>s-0.005: pk+=1
print('POKES',pk)
for name in [n for n in O.keys() if 'grass_points' in n and n[:2] in ('QS','QV')]:
    g=O[name]; m=g.matrix_world; mi2=m.inverted(); n=0; dn=0
    for v in g.data.vertices:
        c=m@v.co
        if not (38<=c.x<=78 and 309.5<=c.y<=318.8): continue
        z=top(G,c.x,c.y)
        if z is None: continue
        if top(SL,c.x,c.y) is not None:
            if c.z>z-0.15: c.z=z-0.2; v.co=mi2@c; dn+=1
            continue
        if abs(c.z-z)>0.005: c.z=z; v.co=mi2@c; n+=1
    g.data.update(); print('GRASS',name,n,dn)
for sn in WK:
    t=O[f'QT_soil_edge_{sn}_UNVERIFIED']; Sb=bvh(O[f'QS_footway_{sn}_UNVERIFIED']); tw=t.matrix_world; inv=tw.inverted(); n=0
    for p in t.data.polygons:
        vi=list(p.vertices); ws=[tw@t.data.vertices[i].co for i in vi]; d=[Sb.find_nearest(v)[3] for v in ws]
        for j in np.argsort(d)[2:]:
            v=ws[j]
            if not (309.5<=v.y<=318.8): continue
            z=top(G,v.x,v.y)
            if z is not None and abs(v.z-(z+0.01))>0.003: t.data.vertices[vi[j]].co=inv@Vector((v.x,v.y,z+0.01)); n+=1
    t.data.update(); print('RESEAT',sn,n)
if '--save' in sys.argv: bpy.ops.wm.save_mainfile(); print('SAVED',len(O))
