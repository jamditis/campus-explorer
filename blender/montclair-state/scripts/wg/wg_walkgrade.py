import bpy, numpy as np, math, json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
X0,X1,Y0,Y1=213.9,216.15,403.1,408.1; PADZ=134.45
P=bpy.data.objects['WF_east_dorm_LiDAR_terrain_patch_UNVERIFIED']; pmw=P.matrix_world; pinv=pmw.inverted()
W=bpy.data.objects['WD_walk_1132693523_UNVERIFIED']; wm=W.matrix_world; wi=wm.inverted()
# 1) walk rows: median of 5 cross samples on current patch +0.04 (pad rows clamp to pad+0.04)
def bvh_eval(o):
    dg=bpy.context.evaluated_depsgraph_get(); e=o.evaluated_get(dg); m=e.to_mesh()
    t=BVHTree.FromPolygons([o.matrix_world@v.co for v in m.vertices],[tuple(p.vertices) for p in m.polygons]); e.to_mesh_clear(); return t
g=lambda t,x,y:(lambda h:h[0].z if h[0] else None)(t.ray_cast(Vector((x,y,400)),Vector((0,0,-1))))
bp=bvh_eval(P)
V=[wm@v.co for v in W.data.vertices]; rows={}
for i,p in enumerate(V): rows.setdefault(round(p.x,1),[]).append(i)
for k,idx in rows.items():
    pts=[V[i] for i in idx]; ys=[p.y for p in pts]; x=sum(p.x for p in pts)/len(pts)
    s=[g(bp,x,y) for y in np.linspace(min(ys),max(ys),5)]; s=[a for a in s if a is not None]
    if not s: continue
    z=float(np.median(s))+0.04
    if x>=X0-0.1: z=PADZ+0.04
    for i in idx: W.data.vertices[i].co=wi@Vector((V[i].x,V[i].y,z))
W.data.update(); W.modifiers['WG_solid'].thickness=0.25
# smooth walk z along x (3-tap) to avoid kinks
keys=sorted(rows); zs=[(wm@W.data.vertices[rows[k][0]].co).z for k in keys]
zs2=[zs[0]]+[ (zs[i-1]+2*zs[i]+zs[i+1])/4 for i in range(1,len(zs)-1)]+[zs[-1]]
for k,z in zip(keys,zs2):
    for i in rows[k]:
        p=wm@W.data.vertices[i].co; W.data.vertices[i].co=wi@Vector((p.x,p.y,z))
W.data.update(); bpy.context.view_layer.update()
# 2) grade patch to walk: inside strip+0.15 -> walkz-0.03; blend to 1.5 m
wme=W.data
flat=BVHTree.FromPolygons([Vector(((wm@v.co).x,(wm@v.co).y,0)) for v in wme.vertices],[tuple(p.vertices) for p in wme.polygons])
real=BVHTree.FromPolygons([wm@v.co for v in wme.vertices],[tuple(p.vertices) for p in wme.polygons])
bak=[];n=0
for v in P.data.vertices:
    p=pmw@v.co
    if not (206<p.x<X0+0.2 and 400<p.y<411): continue
    loc,nor,fi,d=flat.find_nearest(Vector((p.x,p.y,0)))
    if loc is None or d>1.6: continue
    wz=g(real,loc.x,loc.y)
    if wz is None: continue
    tgt=wz-0.03
    w=1.0 if d<=0.15 else max(0.0,1-(d-0.15)/1.45); w=w*w*(3-2*w)
    nz=p.z*(1-w)+tgt*w
    if abs(nz-p.z)>1e-4: bak.append((v.index,p.z)); v.co=pinv@Vector((p.x,p.y,nz)); n+=1
P.data.update(); json.dump(bak,open('data/wg/patch_walkgrade_bak.json','w'))
print('walkgrade verts',n,'walk z range',round(min(zs2),2),round(max(zs2),2))
c=bpy.data.objects['WG_cut_skirt_W_door_feather']; c.location=(211.75,405.5,135.0); c.scale=(6.5,15.0,10.0)
bpy.context.view_layer.update()
bp=bvh_eval(P); bs=bvh_eval(bpy.data.objects['Context_skirt_3DEP_ortho_4km'])
out=[];miss=0
for x in np.arange(206,216.2,0.25):
    for y in np.arange(398,413,0.25):
        a=g(bp,x,y); b=g(bs,x,y)
        if a is None and b is None and x<215.9: miss+=1
        if 213.85<=x<=216.15 and 402.85<=y<=408.35: continue
        if a and b and b-a>0.05: out.append((round(b-a,3),x,y))
out.sort(reverse=True); print('POKES>5cm',len(out),out[:6],'HOLES',miss)
bpy.ops.wm.save_mainfile(); print('SAVED',len(bpy.data.objects))
