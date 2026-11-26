# ws252 (CHAIN via ws208/merge208.py on main ws251b): UNIFY W63c — Feliciano SE lower plaza, plaza-edge raised walk
# (retaining edge) and the E-W stairs up to Dickson's west walk, plus the lamp at (-183.8, 161.6).
# Evidence: 2023 LiDAR 1 m (flat 133.9-134.0 m plaza, abrupt +0.6..0.7 m single-cell step at x -191/-190 for y 154-163,
# E-W band y 156-158 rising 0.37 m/m from 134.1 at x -191 to 136.7 at x -183 = stair run), 2020 ortho (tan plaza x -205..-191,
# y 155..165; light strip x -191..-189.6; light E-W band y 156..158; dark dot + pale globe at (-183.8,161.6)).
# Stairs vs ramp and the wall/walk build-up are UNVERIFIED (no photo). Feliciano arcade east (y 165.5..167) is the plaza's N edge.
import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
TAG='F252A'; COL=None
P=bpy.data.objects['WS251_W63b_passage_LiDAR2023_ground_patch_1m']
for c in P.users_collection: COL=c; break
def mat(n):
    m=bpy.data.materials.get(n); print(TAG,'mat',n,bool(m),flush=True); return m
M_PLAZA=mat('North_Feliciano_paving_concrete'); M_STEP=mat('WS35_concrete_steps'); M_WALL=mat('OH_cheek_wall_concrete_UNVERIFIED'); M_WALK=mat('WS159_concrete_walk_broomed')
Z_PL=134.03; Z_WK=134.66; X_W=-191.0; X_WE=-189.6; Y_S0,Y_S1=156.2,158.4; CH=0.25
NR=17; X_TOP=-183.5; Z_TOP=136.56; X_S=-190.3  # ws252d: first riser 0.7 m in from the plaza edge (LiDAR at x -190 is only 134.14)
RISE=(Z_TOP-Z_PL)/NR; TREAD=(X_TOP-X_S)/(NR-1)
def box(bm,x0,x1,y0,y1,z0,z1,mi=0):
    vs=[bm.verts.new((x,y,z)) for z in (z0,z1) for y in (y0,y1) for x in (x0,x1)]
    for q in ((0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)):
        f=bm.faces.new([vs[i] for i in q]); f.material_index=mi
def obj(name,bm,mats):
    me=bpy.data.meshes.new(name); bm.normal_update(); bm.to_mesh(me); bm.free()
    for m in mats: me.materials.append(m)
    uv=me.uv_layers.new(name='UVMap')
    for p in me.polygons:
        n=p.normal
        for li in p.loop_indices:
            co=me.vertices[me.loops[li].vertex_index].co
            uv.data[li].uv=(co.x,co.y) if abs(n.z)>0.5 else ((co.y if abs(n.x)>abs(n.y) else co.x),co.z)
    o=bpy.data.objects.new(name,me); COL.objects.link(o); print(TAG,'obj',name,len(me.vertices),len(me.polygons),flush=True); return o
if 'WS252_W63c_Feliciano_SE_lower_plaza_paving' not in bpy.data.objects:
    # (1) plaza slab: L-shape (NE corner by Feliciano's SE corner rises -> stop at y 163.8 east of x -197.5)
    # top = max(134.03, evaluated ws251b ground + 4 cm) from scripts/ws251/d251a.npy (eval terrain at cell centres x+0.5,y+0.5),
    # so the base terrain west of the patch (x < -195, re-snapped by GN, can't be lowered) never pokes through (raise paving only)
    import numpy as np
    O=np.load('/workspace/nj-scenes/montclair-state/scripts/ws251/d251a.npy')[0]
    def oz(x,y):
        fx=x-(-204)-0.5; fy=y-128-0.5; i=min(max(int(np.floor(fx)),0),O.shape[1]-2); j=min(max(int(np.floor(fy)),0),O.shape[0]-2); tx=min(max(fx-i,0),1); ty=min(max(fy-j,0),1)
        q=O[j:j+2,i:i+2]; return float(q[0,0]*(1-tx)*(1-ty)+q[0,1]*tx*(1-ty)+q[1,0]*(1-tx)*ty+q[1,1]*tx*ty)
    bm=bmesh.new(); S=0.5; zmax=0
    for (xa,xb,ya,yb) in ((-207.4,-197.5,154.6,165.4),(-197.5,X_W,154.6,163.8)):  # ws252e: W edge meets the Feliciano forecourt brick border (x -207.4)
        nx=int(round((xb-xa)/S)); ny=int(round((yb-ya)/S)); xs=[xa+(xb-xa)*i/nx for i in range(nx+1)]; ys=[ya+(yb-ya)*j/ny for j in range(ny+1)]
        top={}; bot={}
        for i,x in enumerate(xs):
            for j,y in enumerate(ys):
                g=oz(x,y) if x<-195.2 else -1e9
                z=max(Z_PL,g+0.04); zmax=max(zmax,z-Z_PL); top[i,j]=bm.verts.new((x,y,z)); bot[i,j]=bm.verts.new((x,y,133.75))
        for i in range(nx):
            for j in range(ny): bm.faces.new([top[i,j],top[i+1,j],top[i+1,j+1],top[i,j+1]])
        for i in range(nx):
            bm.faces.new([top[i,0],bot[i,0],bot[i+1,0],top[i+1,0]]); bm.faces.new([top[i+1,ny],bot[i+1,ny],bot[i,ny],top[i,ny]])
        for j in range(ny):
            bm.faces.new([top[0,j+1],bot[0,j+1],bot[0,j],top[0,j]]); bm.faces.new([top[nx,j],bot[nx,j],bot[nx,j+1],top[nx,j+1]])
    print(TAG,'plaza top raised max %.2f m above 134.03'%zmax,flush=True)
    obj('WS252_W63c_Feliciano_SE_lower_plaza_paving',bm,[M_PLAZA])
    # (2) raised walk along the plaza's E edge (its W face is the 0.63 m retaining edge), split by the stairs
    bm=bmesh.new(); box(bm,X_W,X_WE,154.6,Y_S0-CH,133.80,Z_WK); box(bm,X_W,X_WE,Y_S1+CH,163.8,133.80,Z_WK)
    obj('WS252_W63c_plaza_E_edge_raised_walk_retaining_UNVERIFIED',bm,[M_WALK])
    # (3) stairs: 17 risers from the plaza (134.03) to Dickson's W walk (136.66); last tread = 1 m landing to x -182.5
    bm=bmesh.new(); box(bm,X_W-0.02,X_S+0.02,Y_S0,Y_S1,133.70,Z_PL)  # plaza-level apron between the raised-walk ends
    for k in range(NR):
        xa=X_S+k*TREAD; xb=(X_TOP+1.0) if k==NR-1 else X_S+(k+1)*TREAD+0.02
        box(bm,xa,xb,Y_S0,Y_S1,133.70,Z_PL+(k+1)*RISE)
    obj('WS252_W63c_E_W_stairs_plaza_to_Dickson_W_walk_UNVERIFIED',bm,[M_STEP])
    # (4) cheek walls both sides, sloped top = nosing line + 0.25
    # one straight sloped prism per side (ws252c; per-tread boxes read as a stepped cheek): top = flat at the raised walk
    # height, then the nosing line + 0.2 m, then flat over the landing
    zn=lambda x: Z_PL+RISE*(1+(x-X_S)/TREAD)
    xk=X_S+((Z_WK-0.2-Z_PL)/RISE-1)*TREAD
    prof=[(X_W,Z_WK),(xk,Z_WK),(X_TOP,zn(X_TOP)+0.2),(X_TOP+1.0,zn(X_TOP)+0.2)]
    bm=bmesh.new()
    for y0,y1 in ((Y_S0-CH,Y_S0),(Y_S1,Y_S1+CH)):
        A=[bm.verts.new((x,y0,z)) for x,z in prof]; B=[bm.verts.new((x,y1,z)) for x,z in prof]
        A0=[bm.verts.new((x,y0,133.70)) for x,z in prof]; B0=[bm.verts.new((x,y1,133.70)) for x,z in prof]
        for i in range(len(prof)-1):
            bm.faces.new([A[i],A[i+1],B[i+1],B[i]]); bm.faces.new([A0[i],A[i],A[i+1],A0[i+1]][::-1]); bm.faces.new([B0[i],B0[i+1],B[i+1],B[i]][::-1])
            bm.faces.new([A0[i+1],B0[i+1],B0[i],A0[i]])
        bm.faces.new([A0[0],B0[0],B[0],A[0]][::-1]); bm.faces.new([A0[-1],A[-1],B[-1],B0[-1]][::-1])
    bmesh.ops.recalc_face_normals(bm,faces=bm.faces[:])
    print(TAG,'cheek profile',[(round(x,2),round(z,2)) for x,z in prof],flush=True)
    obj('WS252_W63c_stair_cheek_walls_UNVERIFIED',bm,[M_WALL])
    # (5) ground patch under the new pieces (patch = the ground here; joined by GN)
    me=P.data; Mw=P.matrix_world; Mi=Mw.inverted(); n1=n2=n3=0
    for v in me.vertices:
        w=Mw@v.co
        if -205<=w.x<=X_W+0.01 and 154.6<=w.y<=(165.4 if w.x<=-197.5 else 163.8) and w.z>Z_PL-0.07: w.z=Z_PL-0.07; n1+=1
        elif X_W<w.x<=X_WE+0.45 and 154.6<=w.y<=163.8 and not (Y_S0-0.5<w.y<Y_S1+0.5): w.z=Z_WK-0.06; n2+=1  # x=-190 column under the walk = walk level (no lip E of it)
        elif X_W<w.x<=X_TOP+1.0 and Y_S0-0.3<=w.y<=Y_S1+0.3:
            k=int((w.x-X_S)/TREAD) if w.x>=X_S else -1; k=min(NR-1,k); zt=Z_PL+(k+1)*RISE-(0.30 if Y_S0<w.y<Y_S1 else 0.10)  # ws252f: -0.30 (chords between 1 m patch verts poked up to 0.10 m through treads at -0.10)
            if w.z>zt: w.z=zt; n3+=1
        else: continue
        v.co=Mi@w
    me.update(); print(TAG,'patch verts lowered plaza',n1,'walk',n2,'stairs',n3,flush=True)
    # (6) lamp: linked duplicate of the nearby acorn lamp, base on the patch ground
    src=bpy.data.objects.get('Lamp_acorn_031')
    if src:
        bv=BVHTree.FromObject(P,bpy.context.evaluated_depsgraph_get())
        h=bv.ray_cast(Mi@Vector((-183.8,161.6,200)),Vector((0,0,-1)))
        zg=(Mw@h[0]).z if h[0] else 136.4
        ln=src.copy(); ln.name='WS252_W63c_Lamp_acorn_ortho2020_UNVERIFIED'
        ln.location=(-183.8,161.6,zg-0.05+(src.location.z-src.matrix_world.translation.z))
        for c in src.users_collection: c.objects.link(ln); break
        print(TAG,'lamp from',src.name,'src loc',tuple(round(a,2) for a in src.location),'ground %.2f'%zg,'new loc',tuple(round(a,2) for a in ln.location),'children',len(src.children),flush=True)
    else: print(TAG,'NO Lamp_acorn_031',flush=True)
    # (7) eye-level grass points (PL, Feliciano lawn) that fall on the new plaza / walk / stairs -> removed
    G=bpy.data.objects.get('PL_feliciano_lawn_grass_points_UNVERIFIED')
    if G:
        Mg=G.matrix_world; bm=bmesh.new(); bm.from_mesh(G.data); n0=len(bm.verts)
        def inside(w):
            if -207.5<=w.x<=X_W and 154.5<=w.y<=(165.5 if w.x<=-197.5 else 163.9): return True
            if X_W<=w.x<=X_TOP+1.1 and Y_S0-CH-0.1<=w.y<=Y_S1+CH+0.1: return True
            return X_W<=w.x<=X_WE+0.05 and 154.5<=w.y<=163.9
        dl=[v for v in bm.verts if inside(Mg@v.co)]; bmesh.ops.delete(bm,geom=dl,context='VERTS')
        bm.to_mesh(G.data); bm.free(); G.data.update(); print(TAG,'PL grass points',n0,'removed',len(dl),flush=True)
