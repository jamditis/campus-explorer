# ws129 UNIFY #34: E walk + planting strip N of the Chapin S drive curb. 2020 ortho: pale walk dy +1.75..+4.25 from the curb line, dark strip
# dy +0.25..+1.5, lawn beyond +4.5. 2023 LiDAR intensity agrees once read as NIR (grass/groundcover high ~105-133, concrete ~65-75, mulch/asphalt low):
# planted strip dy 0.4-1.9, concrete dy 2.2-4.3. -> walk 2.5 m (dy 1.85..4.35), mulch bed dy 0.15..1.85 (curb back), x -234 .. -205.5.
import bpy, bmesh, os, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
SAVE=os.environ.get('SAVE','0')=='1'
D='/workspace/nj-scenes/montclair-state/scripts/'
A=np.vstack([np.load(D+'ws128/las_E.npy'),np.load(D+'ws129/las129.npy')]); G=A[A[:,3]==2][:,:3]
def lz(x,y,r=0.8):
    d2=(G[:,0]-x)**2+(G[:,1]-y)**2; m=d2<r*r
    if m.sum()<3: m=d2<(2.5*r)**2
    w=1/(d2[m]+0.05); return float((G[m,2]*w).sum()/w.sum())
yN=lambda x:-239.0-0.233*(x+232.0)
nrm=Vector((0.233,1)).normalized()   # perpendicular-ish offset direction: use plain +y offsets (dy) as measured
for o in [o for o in bpy.data.objects if o.name.startswith('WS129b_')]: bpy.data.objects.remove(o)
col=bpy.data.collections.get('WS129_Chapin_S_lot')
covers=[o for o in bpy.data.objects if o.name.startswith(('WS112_CollegeAve_S_E_walk_N_brick','WS115_E_walk_N_concrete'))]
TC=[BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[p.vertices for p in o.data.polygons if p.normal.z>0.5]) for o in covers]
cN=[o for o in bpy.data.objects if o.name.startswith(('WS128_Chapin_S_drive_N_curb','WS129_Chapin_S_lot_N_curb'))]
def band(name,d0,d1,x0,x1,nu,nv,mat,dz):
    bm=bmesh.new(); Z=np.zeros((nv+1,nu+1)); XY=[]
    for j in range(nv+1):
        row=[]
        for i in range(nu+1):
            x=x0+(x1-x0)*i/nu; y=yN(x)+d0+(d1-d0)*j/nv; row.append((x,y)); Z[j,i]=lz(x,y)
        XY.append(row)
    for _ in range(4): Z[1:-1,1:-1]=(Z[1:-1,1:-1]*2+Z[:-2,1:-1]+Z[2:,1:-1]+Z[1:-1,:-2]+Z[1:-1,2:])/6
    # straighten the cross-fall: fit each column to a line across the band (clean plane, no ripples)
    for i in range(nu+1):
        c=np.polyfit(np.arange(nv+1),Z[:,i],1); Z[:,i]=np.polyval(c,np.arange(nv+1))
    vv=[]
    for j in range(nv+1):
        r=[]
        for i in range(nu+1):
            x,y=XY[j][i]; z=Z[j,i]+dz
            for T in TC:
                h=T.ray_cast(Vector((x,y,200)),Vector((0,0,-1)))[0]
                if h is not None: z=min(z,h.z-0.012)
            r.append(bm.verts.new((x,y,z)))
        vv.append(r)
    for j in range(nv):
        for i in range(nu): bm.faces.new((vv[j][i],vv[j][i+1],vv[j+1][i+1],vv[j+1][i]))
    bm.normal_update()
    for f in bm.faces:
        if f.normal.z<0: f.normal_flip()
    for e in [e for e in bm.edges if e.is_boundary]:
        a,b=e.verts; a2=bm.verts.new(a.co-Vector((0,0,0.12))); b2=bm.verts.new(b.co-Vector((0,0,0.12))); bm.faces.new((a,b,b2,a2))
    me=bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); me.materials.append(bpy.data.materials.get(mat))
    o=bpy.data.objects.new(name,me); col.objects.link(o); return o
wk=band('WS129b_Chapin_S_drive_N_walk_concrete_2p5m_ortho2020_LiDARint_UNVERIFIEDends',1.85,4.35,-234.0,-205.5,57,5,'SC_walk_concrete_joints_UNVERIFIED',0.02)
mb=band('WS129b_Chapin_S_drive_N_planting_strip_mulch_ortho2020_LiDARint_UNVERIFIEDplanting',0.16,1.87,-234.0,-205.5,57,4,'WS3_Mulch_bark_dark_brown',-0.02)
print('M129b walk',len(wk.data.polygons),'mulch',len(mb.data.polygons))
TT=[BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[p.vertices for p in o.data.polygons if p.normal.z>0.5]) for o in (wk,mb)]
nl=0
for g in [o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(('Terrain_LiDAR_DTM_1m','WS113_terrain_fan_fill','WS110_ground_patch'))]:
    mw=g.matrix_world; mi=mw.inverted()
    for v in g.data.vertices:
        p=mw@v.co
        if not (-235<p.x<-204.5 and yN(p.x)-0.2<p.y<yN(p.x)+5.0): continue
        best=None
        for dx,dy in ((0,0),(0.3,0),(-0.3,0),(0,0.3),(0,-0.3)):
            for T in TT:
                h=T.ray_cast(Vector((p.x+dx,p.y+dy,200)),Vector((0,0,-1)))[0]
                if h is not None: best=h.z if best is None else min(best,h.z)
        if best is not None and p.z>best-0.10: p.z=best-0.10; v.co=mi@p; nl+=1
print('M129b ground lowered',nl)
px=bpy.data.objects.get('WS113_paving_tops_proxy')
if px and not px.get('ws129b'):
    px['ws129b']=1; pbm=bmesh.new(); pbm.from_mesh(px.data); pmi=px.matrix_world.inverted(); n0=len(pbm.faces)
    for o in (wk,mb):
        for p in o.data.polygons:
            if p.normal.z>0.5: pbm.faces.new([pbm.verts.new(pmi@(o.matrix_world@o.data.vertices[i].co)) for i in p.vertices])
    pbm.to_mesh(px.data); pbm.free(); print('M129b proxy',n0,'->',len(px.data.polygons))
if SAVE: bpy.ops.wm.save_mainfile(); print('M129b SAVED')
