# ws108: Chapin Hall eave overhang + dark-brown soffit/fascia, tile ridge caps, window grid.
# Evidence: Wikimedia Commons MSU_Chapin_Hall.jpg (2007, PD) — red-tile hip roof, ~0.6-0.8 m overhang,
# dark-brown underside/fascia, white stucco, regular grid of dark-framed rectangular windows (~3 storeys).
import bpy, bmesh, math, os
from mathutils import Vector
D=0.70; FT=0.22; CAP_R=0.14
SAVE=os.environ.get('SAVE')=='1'
for o in [o for o in bpy.data.objects if o.name.startswith('WS108_Chapin_')]: bpy.data.objects.remove(o)
def mat(name,rgb,rough,spec=0.5):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name); m.use_nodes=True
    b=m.node_tree.nodes.get('Principled BSDF'); b.inputs['Base Color'].default_value=(*rgb,1); b.inputs['Roughness'].default_value=rough
    m.diffuse_color=(*rgb,1); return m
M_wood=mat('WS108_Chapin_eave_soffit_fascia_dark_brown_wood',(0.085,0.05,0.03),0.7)
M_glass=mat('WS108_Chapin_window_glass_dark',(0.025,0.03,0.035),0.12)
M_frame=mat('WS108_Chapin_window_frame_dark_bronze',(0.06,0.045,0.035),0.5)
src=[o for o in bpy.data.objects if o.name.startswith('WS107_Chapin_') and o.type=='MESH']
tile=None
for o in src:
    for s in o.material_slots:
        if s.material and ('tile' in s.material.name.lower()): tile=s.material
col=bpy.data.collections.get('WS108_Chapin_eaves_windows_UNVERIFIED') or bpy.data.collections.new('WS108_Chapin_eaves_windows_UNVERIFIED')
if col.name not in bpy.context.scene.collection.children: bpy.context.scene.collection.children.link(col)
skipnames=('WS107_','WS108_','T_','Tree','tree','CAM')
from mathutils.bvhtree import BVHTree
_T=bpy.data.objects.get('Terrain_LiDAR_DTM_1m')
_TB=None
if _T is not None:
    _bm=bmesh.new(); _bm.from_mesh(_T.data); _bm.transform(_T.matrix_world); _TB=BVHTree.FromBMesh(_bm); _bm.free()
def ground(x,y):
    if _TB is None: return None
    h=_TB.ray_cast(Vector((x,y,250.0)),Vector((0,0,-1)))[0]
    return None if h is None else h.z
def newobj(name,bm,mats):
    me=bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for m in mats: me.materials.append(m)
    ob=bpy.data.objects.new(name,me); col.objects.link(ob); return ob
eb=bmesh.new(); cb=bmesh.new(); wb=bmesh.new()
n_eave=n_cap=n_win=0
for o in src:
    bm=bmesh.new(); bm.from_mesh(o.data); bm.transform(o.matrix_world); bmesh.ops.recalc_face_normals(bm,faces=bm.faces[:])
    bm.normal_update()
    sl=lambda f: 0.25<f.normal.z<0.99
    vert=lambda f: abs(f.normal.z)<0.08
    # per-vertex outward offsets accumulated from outer eave edges (miter at corners)
    offs={}; edges=[]
    for e in bm.edges:
        fs=e.link_faces
        if len(fs)!=2: continue
        a,b=fs
        if sl(a) and sl(b):
            # ridge/hip cap
            p0,p1=e.verts[0].co.copy(),e.verts[1].co.copy(); ax=(p1-p0)
            if ax.length<0.3: continue
            nrm=(a.normal+b.normal).normalized(); u=ax.normalized(); w=u.cross(nrm).normalized()
            ring=[]
            for p in (p0,p1):
                r=[cb.verts.new(p+nrm*0.03+(nrm*math.cos(t)+w*math.sin(t))*CAP_R) for t in [math.radians(-90+30*k) for k in range(7)]]
                ring.append(r)
            for k in range(6): cb.faces.new((ring[0][k],ring[0][k+1],ring[1][k+1],ring[1][k]))
            n_cap+=1; continue
        s,v=(a,b) if sl(a) and vert(b) else ((b,a) if sl(b) and vert(a) else (None,None))
        if s is None: continue
        if v.calc_center_median().z > sum(x.co.z for x in e.verts)/2: continue  # wall goes up: no eave
        nh=Vector((v.normal.x,v.normal.y,0)).normalized()
        edges.append((e,s,nh))
        for x in e.verts: offs.setdefault(x.index,[]).append(nh)
    def offvec(vi):
        ns=offs[vi]; 
        if len(ns)==1: return ns[0]*D
        m=(ns[0]+ns[1]); 
        if m.length<1e-3: return ns[0]*D
        m.normalize(); c=max(0.5,m.dot(ns[0])); return m*(D/c)
    def planez(f,p):
        n=f.normal; c=f.verts[0].co
        return c.z-(n.x*(p.x-c.x)+n.y*(p.y-c.y))/n.z
    for e,s,nh in edges:
        P=[x.co.copy() for x in e.verts]
        Q=[]
        for x in e.verts:
            q=x.co+offvec(x.index); q.z=planez(s,q); Q.append(q)
        tv=[eb.verts.new(p) for p in (P[0],P[1],Q[1],Q[0])]
        bv=[eb.verts.new(p-Vector((0,0,FT))) for p in (P[0],P[1],Q[1],Q[0])]
        ft=eb.faces.new(tv); ft.material_index=0
        for f in (eb.faces.new((bv[3],bv[2],bv[1],bv[0])),eb.faces.new((tv[3],tv[2],bv[2],bv[3])),
                  eb.faces.new((tv[0],tv[3],bv[3],bv[0])),eb.faces.new((tv[2],tv[1],bv[1],bv[2]))): f.material_index=1
        n_eave+=1
    # windows on vertical walls
    for f in bm.faces:
        if not vert(f) or f.calc_area()<12: continue
        vs=[x.co for x in f.verts]; nh=Vector((f.normal.x,f.normal.y,0)).normalized(); u=Vector((-nh.y,nh.x,0))
        c0=vs[0]; ts=[(p-c0).dot(u) for p in vs]; t0,t1=min(ts),max(ts); W=t1-t0
        if W<4: continue
        top=min(p.z for p in vs if p.z>min(q.z for q in vs)+2) if any(p.z>min(q.z for q in vs)+2 for p in vs) else None
        if top is None: continue
        ncol=max(1,int((W-2.4)/3.2)+1); sp=(W-2.4)/max(1,ncol-1) if ncol>1 else 0
        for k in range(ncol):
            t=t0+1.2+k*sp if ncol>1 else t0+W/2
            base=c0+u*(t-(c0-c0).dot(u)); bx,by=base.x,base.y
            g=ground(bx+nh.x*1.2,by+nh.y*1.2)
            g=123.0 if g is None else g
            z=g+0.95
            while z+1.6<top-0.9:
                for (hw,hh,off,mi,z0) in ((0.6,0.9,0.025,0,z-0.1),(0.5,0.8,0.04,1,z)):
                    cx=Vector((bx,by,0))+nh*off; 
                    zc=z0+0.8 if mi==1 else z+0.8
                    pts=[cx+u*-hw+Vector((0,0,zc-hh)),cx+u*hw+Vector((0,0,zc-hh)),cx+u*hw+Vector((0,0,zc+hh)),cx+u*-hw+Vector((0,0,zc+hh))]
                    ff=wb.faces.new([wb.verts.new(p) for p in pts]); ff.material_index=mi
                n_win+=1; z+=3.5
    bm.free()
e=newobj('WS108_Chapin_eave_overhang_0.7m_fascia_UNVERIFIED',eb,[tile,M_wood])
c=newobj('WS108_Chapin_tile_ridge_hip_caps',cb,[tile])
w=newobj('WS108_Chapin_windows_grid_UNVERIFIED',wb,[M_frame,M_glass])
for ob in (c,w):
    for p in ob.data.polygons: p.use_smooth=(ob is c)
print('E108 eave edges',n_eave,'caps',n_cap,'windows',n_win)
if SAVE: bpy.ops.wm.save_mainfile(); print('E108 SAVED')
