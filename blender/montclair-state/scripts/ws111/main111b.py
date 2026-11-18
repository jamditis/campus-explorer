# ws111b: smooth the brick corner aprons (plane fit + boundary-residual IDW, no DTM noise), re-cap terrain
import bpy, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
A=np.array([-244.8,-239.3]);B=np.array([-256.1,-271.6]);d=(B-A)/np.linalg.norm(B-A);n=np.array([d[1],-d[0]])
def st(x,y): return (x-A[0])*d[0]+(y-A[1])*d[1],(x-A[0])*n[0]+(y-A[1])*n[1]
O=lambda p: next(o for o in bpy.data.objects if o.name.startswith(p))
def bvh_of(o):
    mw=o.matrix_world; return BVHTree.FromPolygons([tuple(mw@v.co) for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons])
bw=bvh_of(O('WS110_NormalAve_sidewalk'))
for side in ('W','E'):
    cu=O('WS110_CollegeAve_S_end_curb_'+side); mw=cu.matrix_world; me=cu.data
    bk=np.array([tuple(mw@me.vertices[k+2].co) for k in range(0,len(me.vertices),4)]); sb,_=st(bk[:,0],bk[:,1]); bk=bk[np.argmax(sb>=16.0):]
    wk=O('WS111_CollegeAve_S_%s_walk'%side); wm=wk.matrix_world; wc=np.array([tuple(wm@v.co) for v in wk.data.vertices]); ws,_=st(wc[:,0],wc[:,1])
    we=wc[(ws>ws.max()-0.05)]; we=we[we[:,2]>we[:,2].min()+0.1] if len(we)>3 else we
    ap=O('WS111_CollegeAve_%s_corner_apron'%side); am=ap.matrix_world; ami=am.inverted(); av=ap.data.vertices
    co=np.array([tuple(am@v.co) for v in av])
    key=np.round(co[:,:2],3); uniq={}
    for i,k in enumerate(map(tuple,key)): uniq.setdefault(k,[]).append(i)
    anc=list(map(tuple,bk))+list(map(tuple,we))
    for k,ids in uniq.items():
        h=bw.ray_cast(Vector((k[0],k[1],140)),Vector((0,0,-1)),60)
        if h[0] is not None and len(ids)>1: anc.append((k[0],k[1],h[0].z+0.006))
    an=np.array(anc)
    G=np.c_[an[:,0],an[:,1],np.ones(len(an))]; cf,*_=np.linalg.lstsq(G,an[:,2],rcond=None); res=an[:,2]-G@cf
    print('F111',side,'anchors',len(an),'plane slope %.3f %.3f'%(cf[0],cf[1]),'res rms %.3f'%np.sqrt((res**2).mean()))
    nset=0
    for k,ids in uniq.items():
        x,y=k; dd=np.hypot(an[:,0]-x,an[:,1]-y)
        if dd.min()<0.02: zt=float(an[np.argmin(dd),2])
        else: w=1/(dd+0.3)**2; zt=float(cf[0]*x+cf[1]*y+cf[2]+(w*res).sum()/w.sum())
        zs=sorted(ids,key=lambda i:-co[i,2])
        top=zs[0]; p=Vector(co[top]); p.z=zt; av[top].co=ami@p
        for i in zs[1:]: p=Vector(co[i]); p.z=zt-0.35; av[i].co=ami@p
        nset+=1
    ap.data.update(); print('F111 set',side,nset)
pav=[o for o in bpy.data.objects if o.name.startswith('WS111_') and ('walk' in o.name or 'apron' in o.name or 'bridge' in o.name)]
bv=[bvh_of(o) for o in pav]
for tn in ('Terrain_LiDAR_DTM_1m','WS110_ground_patch'):
    to=O(tn); me=to.data; mw=to.matrix_world; mi=mw.inverted(); ncap=0
    for v in me.vertices:
        p=mw@v.co
        if not (-268<p.x<-236 and -270<p.y<-238): continue
        zmin=None
        for dx,dy in ((0,0),(0.4,0),(-0.4,0),(0,0.4),(0,-0.4)):
            for b in bv:
                h=b.ray_cast(Vector((p.x+dx,p.y+dy,150)),Vector((0,0,-1)),80)
                if h[0] is not None and h[0].z>p.z-2.0:
                    zmin=h[0].z if zmin is None else min(zmin,h[0].z)
        if zmin is not None and p.z>zmin-0.05: p.z=zmin-0.05; v.co=mi@p; ncap+=1
    me.update(); print('F111 cap',tn,ncap)
bpy.ops.wm.save_mainfile(); print('F111 SAVED')
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws111/cut111.py').read())
