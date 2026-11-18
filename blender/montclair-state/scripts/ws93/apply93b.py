# ws91b: apply union-outline lot edge displacements (lots_disp91.json); interior falloff 1.2 m; fold check; raise-only z (terrain+2cm, cap 4cm)
import bpy,json,math,os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree
OB=bpy.data.objects; R=1.2; ZCAP=0.04
DD=json.load(open('/workspace/nj-scenes/montclair-state/scripts/ws93/lots_disp93.json'))
T=OB['Terrain_LiDAR_DTM_1m']; e=T.evaluated_get(bpy.context.evaluated_depsgraph_get()); me=e.to_mesh()
TB=BVHTree.FromPolygons([e.matrix_world@v.co for v in me.vertices],[tuple(p.vertices) for p in me.polygons]); e.to_mesh_clear()
def tz(x,y):
    h=TB.ray_cast(Vector((x,y,300)),Vector((0,0,-1))); return h[0].z if h[0] else -1e9
for n,d in DD.items():
    o=OB[n]; mw=o.matrix_world; inv=mw.inverted(); me=o.data
    W=[mw@v.co for v in me.vertices]; new=[w.copy() for w in W]; nz0=[p.normal.z for p in me.polygons]
    d={int(k):v for k,v in d.items()}
    for i,(dx,dy) in d.items():
        x,y=W[i].x+dx,W[i].y+dy; z=W[i].z; t=tz(x,y)
        if t>z-0.02: z=max(z,min(t+0.02,W[i].z+ZCAP))
        new[i]=Vector((x,y,z))
    if d:
        bl=list(d); kd=KDTree(len(bl))
        for k,i in enumerate(bl): kd.insert(Vector((W[i].x,W[i].y,0)),k)
        kd.balance()
        # boundary verts not in d (covered) must not be dragged: collect boundary set from edges
        import collections
        ec=collections.Counter()
        for p in me.polygons:
            vs=list(p.vertices)
            for a in range(len(vs)): ec[tuple(sorted((vs[a],vs[(a+1)%len(vs)])))]+=1
        bset={v for e_,c in ec.items() if c==1 for v in e_}
        for i in range(len(W)):
            if i in d or i in bset: continue
            co,k,dist=kd.find(Vector((W[i].x,W[i].y,0)))
            if dist>R: continue
            f=1.0 if dist<0.05 else max(0.0,1-(dist-0.05)/(R-0.05)); dx,dy=d[bl[k]]
            new[i]=Vector((W[i].x+dx*f,W[i].y+dy*f,W[i].z))
    for v,p in zip(me.vertices,new): v.co=inv@p
    me.update(); bad=0
    for it in range(3):
        fl=[p for p,z0 in zip(me.polygons,nz0) if abs(z0)>0.5 and p.normal.z*z0<0.2*abs(z0)]
        if not fl: break
        for p in fl:
            for vi in p.vertices: me.vertices[vi].co=inv@W[vi]; bad+=1
        me.update()
    print('B91',n[:50],'moved_bnd',len(d),'revert',bad)
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('B91 SAVED')
