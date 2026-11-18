# ws214b W35: Red Hawk Deck College Ave vehicle entrance. Evidence: Joe's Sep 2021 Street View (entrance at street/sidewalk level,
# 'RED HAWK DECK' sign over the opening) + model deck levels (eu ground slab 121.5 = lower level, et level-2 wearing surface 124.98).
# The College Ave entrance enters LEVEL 2 (124.98), not the 121.5 ground slab; the LiDAR 121.4 under the opening is bare-earth/under-deck.
# -> KX_drive_apron regraded linearly from the College Ave edge (KY top 1 m S of the apron S edge) to 124.970 at its N edge;
#    threshold slab bridges apron N edge -> et S edge (+0.3 m under et) at 124.975; side-walk fills = apron edge +1.5 cm;
#    LH gutter fill in x -277.5..-263.5 = KY edge z -0.5 cm.
import bpy, bmesh, math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
def ob(p): return next((o for o in bpy.data.objects if o.name.startswith(p)),None)
AP=ob('KX_drive_apron'); KY=ob('KY_college_ave_carriageway_asphalt'); SW=ob('KY_rhd_drive_side_walk_fill'); LH=ob('LH_college_ave_gutter_asphalt_fill')
if not all([AP,KY,SW,LH]) or ob('WS214_rhd_entry_threshold'): print('F214 b skip',flush=True)
else:
    def bvh(o): M=o.matrix_world; return BVHTree.FromPolygons([M@v.co for v in o.data.vertices],[p.vertices[:] for p in o.data.polygons])
    tk=bvh(KY)
    def kyz(x,y):
        h=tk.ray_cast(Vector((x,y,200)),Vector((0,0,-1)),300); return h[0].z if h[0] is not None else None
    fd=Vector((1,-0.242)).normalized(); nd=Vector((-fd.y,fd.x))
    if nd.y<0: nd=-nd
    yF=lambda x:-39.61-0.242*(x+278)
    Z2=124.970
    me=AP.data; M=AP.matrix_world; Mi=M.inverted(); W=[M@v.co for v in me.vertices]
    U=[Vector((w.x,w.y)).dot(fd) for w in W]; V=[Vector((w.x,w.y)).dot(nd) for w in W]
    def band(u,lst):
        s=[i for i in range(len(W)) if abs(U[i]-u)<0.6]
        return s
    zs={}
    for i,w in enumerate(W):
        s=band(U[i],None); vS=min(V[j] for j in s); vN=max(V[j] for j in s)
        jS=min(s,key=lambda j:V[j]); p=Vector((W[jS].x,W[jS].y))-nd*1.0
        z0=None
        for k in range(6):
            z0=kyz(p.x,p.y)
            if z0 is not None: break
            p=p-nd*0.5
        if z0 is None: z0=124.75
        f=(V[i]-vS)/max(vN-vS,0.5); f=min(max(f,0),1)
        zs[i]=z0+(Z2-z0)*f
    for i,w in enumerate(W): me.vertices[i].co=Mi@Vector((w.x,w.y,zs[i]))
    me.update()
    zmin=min(zs.values()); zmax=max(zs.values())
    # threshold: along the apron N edge
    ta=bvh(AP)
    u0=min(U); u1=max(U); n=12; bm=bmesh.new(); A=[]; B=[]
    for k in range(n+1):
        u=u0+(u1-u0)*k/n
        s=[i for i in range(len(W)) if abs(U[i]-u)<0.6]; vN=max(V[j] for j in s)
        p=fd*u+nd*(vN-0.4)
        # go north to the et edge + 0.3
        q=Vector(p)
        while q.y<yF(q.x)+0.3: q=q+nd*0.1
        A.append(bm.verts.new((p.x,p.y,Z2+0.005))); B.append(bm.verts.new((q.x,q.y,Z2+0.005)))
    for k in range(n): bm.faces.new((A[k],A[k+1],B[k+1],B[k]))
    for f in bm.faces:
        if f.normal.z<0: f.normal_flip()
    tm=bpy.data.meshes.new('WS214_thr'); bm.to_mesh(tm); bm.free()
    to=bpy.data.objects.new('WS214_rhd_entry_threshold_level2_streetview2021_UNVERIFIED',tm); tm.materials.append(AP.data.materials[0])
    for c in AP.users_collection: c.objects.link(to)
    # side-walk fills: apron edge + 1.5 cm (nearest apron point along the face direction)
    ta=bvh(AP); me=SW.data; M=SW.matrix_world; Mi=M.inverted(); ns=0
    for v in me.vertices:
        w=M@v.co; h=ta.find_nearest(w.to_2d().to_3d()+Vector((0,0,w.z)))
        loc=ta.find_nearest(Vector((w.x,w.y,Z2)))[0]
        if loc is None: continue
        z=loc.z+0.015; v.co=Mi@Vector((w.x,w.y,z)); ns+=1
    me.update()
    # LH gutter: KY edge z - 0.5 cm in the entrance x range
    me=LH.data; M=LH.matrix_world; Mi=M.inverted(); nl=0
    for v in me.vertices:
        w=M@v.co
        if not (-277.5<w.x<-263.5): continue
        p=Vector((w.x,w.y)); z0=None
        for k in range(12):
            z0=kyz(p.x,p.y)
            if z0 is not None: break
            p=p-nd*0.25
        if z0 is None: continue
        v.co=Mi@Vector((w.x,w.y,z0-0.005)); nl+=1
    me.update()
    print('F214 b apron z',round(zmin,3),round(zmax,3),'threshold',n,'walk verts',ns,'LH verts',nl,flush=True)
