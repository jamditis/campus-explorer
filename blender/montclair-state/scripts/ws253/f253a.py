# ws253 (CHAIN via ws208/merge208.py on main ws252f): UNIFY W63d — walk + stairs along Feliciano's east face and the wide
# diagonal walk on the grass plot's NE side (to Dickson's NW corner), plus the acorn lamp seen as a dark dot in the 2020 ortho.
# Evidence: 2023 LiDAR 1 m profiles (scripts/ws252/prep252_next.txt): x -191.5 / -190.5 climb 134.0 -> 136.7 m over y 163-172
# (two steep runs 0.37-0.39 m/m with a gentler 0.12-0.14 m/m stretch at y 166-168), flat 136.7-136.9 to y 176, then 1.0 m over
# y 176.5-179.5; diagonal NE edge of the grass plot flat 136.7-136.9. 2020 ortho crop (crop253.py, box only): light N-S strip
# x -192 .. -189.5 (y 160 -> 184+), light ~5 m-wide diagonal band from the strip at y 172.6-178.5 SE to Dickson's NW corner
# (x -184 .. -177.5, y 160-166), grass plot SW of it, dark dot at (-189.75, 172.4).
# Stairs vs ramps, riser counts, landing extents and the cheek walls are UNVERIFIED (no photo; LiDAR slope too steep for a walk).
import bpy, bmesh, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
TAG='F253A'
P1=bpy.data.objects['WS251_W63b_passage_LiDAR2023_ground_patch_1m']; P2=bpy.data.objects['WS250_W63_lawn_LiDAR2023_ground_patch_1m']
COL=P1.users_collection[0]
def mat(n):
    m=bpy.data.materials.get(n); print(TAG,'mat',n,bool(m),flush=True); return m
M_STEP=mat('WS35_concrete_steps'); M_WALL=mat('OH_cheek_wall_concrete_UNVERIFIED'); M_WALK=mat('WS159_concrete_walk_broomed')
O=np.load('/workspace/nj-scenes/montclair-state/scripts/ws251/d251a.npy')[0]
def oz(x,y):
    fx=x-(-204)-0.5; fy=y-128-0.5; i=min(max(int(np.floor(fx)),0),O.shape[1]-2); j=min(max(int(np.floor(fy)),0),O.shape[0]-2); tx=min(max(fx-i,0),1); ty=min(max(fy-j,0),1)
    q=O[j:j+2,i:i+2]; return float(q[0,0]*(1-tx)*(1-ty)+q[0,1]*tx*(1-ty)+q[1,0]*(1-tx)*ty+q[1,1]*tx*ty)
XW,XE,XC=-194.95,-189.5,-189.25   # ws253d: walk/stairs W edge widened to x -194.95 (modelled Feliciano E wall is at x -197.5 for y<172, -194.5 for y>=172; the WS251 patch ends at x -195)
XW_LAST=-191.98  # last stretch (y>=179.2) stays on the ortho strip x -192..-189.5
Z0=134.03
# profile: list of segments (y0,y1,kind,z0,z1,nr)
SEG=[(163.8,166.6,'st',Z0,135.27,8),(166.6,168.6,'wk',135.27,135.30,0),(168.6,171.6,'st',135.30,136.70,9),
     (171.6,176.4,'wk',136.70,136.87,0),(176.4,179.2,'st',136.87,137.87,6),(179.2,183.5,'wk',137.87,None,0)]
def top_at(y):
    for (a,b,k,za,zb,nr) in SEG:
        if a-1e-6<=y<=b+1e-6:
            if k=='wk':
                if zb is None:  # ws253b: last stretch drapes on the ground + 6 cm, blended from the flight top over 1.5 m
                    g=lambda yy: max(oz(-191.9,yy),oz(-190.7,yy),oz(-189.6,yy))  # ws253c: highest of W edge / centre / E edge
                    return g(y)+0.06+(za-g(a)-0.06)*max(0.0,1-(y-a)/1.5),k
                return za+(zb-za)*(y-a)/(b-a),k
            r=(zb-za)/nr; t=(b-a)/nr; kk=min(nr-1,int((y-a)/t)); return za+(kk+1)*r,k
    return None,None
def box(bm,x0,x1,y0,y1,z0,z1):
    vs=[bm.verts.new((x,y,z)) for z in (z0,z1) for y in (y0,y1) for x in (x0,x1)]
    for q in ((0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)): bm.faces.new([vs[i] for i in q])
def obj(name,bm,mats):
    bmesh.ops.recalc_face_normals(bm,faces=bm.faces[:])
    me=bpy.data.meshes.new(name); bm.normal_update(); bm.to_mesh(me); bm.free()
    for m in mats: me.materials.append(m)
    uv=me.uv_layers.new(name='UVMap')
    for p in me.polygons:
        n=p.normal
        for li in p.loop_indices:
            co=me.vertices[me.loops[li].vertex_index].co
            uv.data[li].uv=(co.x,co.y) if abs(n.z)>0.5 else ((co.y if abs(n.x)>abs(n.y) else co.x),co.z)
    o=bpy.data.objects.new(name,me); COL.objects.link(o); print(TAG,'obj',name,len(me.vertices),len(me.polygons),flush=True); return o
if 'WS253_W63d_Feliciano_E_walk_and_stairs_UNVERIFIED' not in bpy.data.objects:
    # (1) N-S walk + stairs (stairs/landings as boxes; walk stretches as sloped slabs)
    bm=bmesh.new(); bmw=bmesh.new()
    for (a,b,k,za,zb,nr) in SEG:
        if k=='st':
            r=(zb-za)/nr; t=(b-a)/nr
            for kk in range(nr): box(bm,XW,XE,a+kk*t,(b if kk==nr-1 else a+(kk+1)*t+0.02),133.70,za+(kk+1)*r)
        else:
            n=max(1,int(round((b-a)/0.5))); ys=[a+(b-a)*i/n for i in range(n+1)]; xw=XW_LAST if zb is None else XW
            T=[(bmw.verts.new((xw,y,top_at(y)[0])),bmw.verts.new((XE,y,top_at(y)[0]))) for y in ys]
            B=[(bmw.verts.new((xw,y,top_at(y)[0]-0.35)),bmw.verts.new((XE,y,top_at(y)[0]-0.35))) for y in ys]
            for i in range(n):
                bmw.faces.new([T[i][0],T[i][1],T[i+1][1],T[i+1][0]]); bmw.faces.new([B[i][0],B[i+1][0],B[i+1][1],B[i][1]])
                bmw.faces.new([T[i][0],T[i+1][0],B[i+1][0],B[i][0]]); bmw.faces.new([T[i][1],B[i][1],B[i+1][1],T[i+1][1]])
            bmw.faces.new([T[0][0],B[0][0],B[0][1],T[0][1]]); bmw.faces.new([T[n][0],T[n][1],B[n][1],B[n][0]])
    obj('WS253_W63d_Feliciano_E_walk_and_stairs_UNVERIFIED',bm,[M_STEP])
    obj('WS253_W63d_Feliciano_E_walk_slabs',bmw,[M_WALK])
    # (2) E cheek walls along the three flights (sloped prism, top = nosing line + 0.15, flat 0.6 m past each end)
    bm=bmesh.new()
    for (a,b,k,za,zb,nr) in SEG:
        if k!='st': continue
        r=(zb-za)/nr; t=(b-a)/nr
        # ws253f: straight cap parallel to the nosing line; offset = max(0.15, what the ground just east needs + 0.10) (ws253e's sampled max read as a wavy cap)
        zn=lambda y: za+r*min(nr,max(1.0,1+(y-a)/t))
        need=max(oz(-188.8,a+(b-a)*i/20)+0.10-zn(a+(b-a)*i/20) for i in range(21)); off=max(0.15,need)
        prof=[(a,zn(a)+off),(a+t,zn(a+t)+off),(b,zn(b)+off)]
        A=[bm.verts.new((XE,y,z)) for y,z in prof]; C=[bm.verts.new((XC,y,z)) for y,z in prof]
        A0=[bm.verts.new((XE,y,133.70)) for y,z in prof]; C0=[bm.verts.new((XC,y,133.70)) for y,z in prof]
        for i in range(len(prof)-1):
            bm.faces.new([A[i],A[i+1],C[i+1],C[i]]); bm.faces.new([A0[i],A[i],A[i+1],A0[i+1]]); bm.faces.new([C0[i],C0[i+1],C[i+1],C[i]]); bm.faces.new([A0[i],A0[i+1],C0[i+1],C0[i]])
        bm.faces.new([A0[0],C0[0],C[0],A[0]]); bm.faces.new([A0[-1],A[-1],C[-1],C0[-1]])
    # ws253d: W cheek (x -195.2..-194.95) for y 163.8..172 where the wall is recessed to x -197.5; top = max(nosing + 0.15, apron top)
    XWC=-195.2; prof=[]
    # ws253f: one straight cap per segment (flight A, landing, flight B), offset = max(0.15, apron + 0.08 - line)
    def gw(y): return max(oz(xx,yy) for xx in (-195.7,-195.2,-194.9) for yy in (max(163.8,y-0.5),y,min(172.0,y+0.5)))+0.08
    for (sa,sb,k,za,zb,nr) in SEG[:3]:
        if k=='st':
            r=(zb-za)/nr; t=(sb-sa)/nr; ln=lambda y,sa=sa,za=za,r=r,t=t,nr=nr: za+r*min(nr,max(1.0,1+(y-sa)/t))
            pts=[sa,sa+t,sb]
        else:
            ln=lambda y,sa=sa,sb=sb,za=za,zb=zb: za+(zb-za)*(y-sa)/(sb-sa); pts=[sa,sb]
        off=max(0.15,max(gw(sa+(sb-sa)*i/20)-ln(sa+(sb-sa)*i/20) for i in range(21)))
        prof+=[(y,ln(y)+off) for y in pts]
    A=[bm.verts.new((XWC,y,z)) for y,z in prof]; C=[bm.verts.new((XW,y,z)) for y,z in prof]
    A0=[bm.verts.new((XWC,y,133.70)) for y,z in prof]; C0=[bm.verts.new((XW,y,133.70)) for y,z in prof]
    for i in range(len(prof)-1):
        bm.faces.new([A[i],A[i+1],C[i+1],C[i]]); bm.faces.new([A0[i],A[i],A[i+1],A0[i+1]]); bm.faces.new([C0[i],C0[i+1],C[i+1],C[i]]); bm.faces.new([A0[i],A0[i+1],C0[i+1],C0[i]])
    bm.faces.new([A0[0],C0[0],C[0],A[0]]); bm.faces.new([A0[-1],A[-1],C[-1],C0[-1]])
    obj('WS253_W63d_Feliciano_E_stair_cheek_walls_UNVERIFIED',bm,[M_WALL])
    # ws253d: raise-only apron x -197.6..-195.2, y 163.8..172 draped on the evaluated ground + 6 cm (base terrain under Feliciano's eave,
    # re-snapped by GN, can't be lowered) -> UNIFY W63e
    bm=bmesh.new(); S=0.5; xa,xb,ya,yb=-197.6,XWC,163.8,172.0
    nx=int(round((xb-xa)/S)); ny=int(round((yb-ya)/S)); xs=[xa+(xb-xa)*i/nx for i in range(nx+1)]; ys=[ya+(yb-ya)*j/ny for j in range(ny+1)]
    top={}; bot={}
    for i,x in enumerate(xs):
        for j,y in enumerate(ys):
            z=max(oz(xx,yy) for xx in (max(x-0.5,xa),x,min(x+0.5,xb)) for yy in (max(y-0.5,ya),y,min(y+0.5,yb)))+0.06;  # ws253e: 3x3 max (chord pokes at the N edge)
            top[i,j]=bm.verts.new((x,y,z)); bot[i,j]=bm.verts.new((x,y,z-0.4))
    for i in range(nx):
        for j in range(ny): bm.faces.new([top[i,j],top[i+1,j],top[i+1,j+1],top[i,j+1]])
    for i in range(nx):
        bm.faces.new([top[i,0],bot[i,0],bot[i+1,0],top[i+1,0]]); bm.faces.new([top[i+1,ny],bot[i+1,ny],bot[i,ny],top[i,ny]])
    for j in range(ny):
        bm.faces.new([top[0,j+1],bot[0,j+1],bot[0,j],top[0,j]]); bm.faces.new([top[nx,j],bot[nx,j],bot[nx,j+1],top[nx,j+1]])
    obj('WS253_W63d_Feliciano_E_recess_apron_raise_only_UNVERIFIED',bm,[M_WALK])
    # (3) wide diagonal walk (draped on the evaluated ground + 6 cm, 0.5 m bisect grid, 0.3 m skirt)
    POLY=[(XC,172.85),(-183.9,166.6),(-184.0,158.75),(-182.5,158.75),(-182.5,160.0),(-177.5,160.0),(-177.5,166.0),(XC,178.25)]
    bm=bmesh.new(); vs=[bm.verts.new((x,y,0)) for x,y in POLY]; f=bm.faces.new(vs)
    for gx in np.arange(-189.0,-177.5,0.5):
        g=bm.verts[:]+bm.edges[:]+bm.faces[:]; r=bmesh.ops.bisect_plane(bm,geom=g,plane_co=(gx,0,0),plane_no=(1,0,0))
    for gy in np.arange(159.0,178.5,0.5):
        g=bm.verts[:]+bm.edges[:]+bm.faces[:]; r=bmesh.ops.bisect_plane(bm,geom=g,plane_co=(0,gy,0),plane_no=(0,1,0))
    for v in bm.verts: v.co.z=oz(v.co.x,v.co.y)+0.06
    bnd=[e for e in bm.edges if e.is_boundary]
    ex=bmesh.ops.extrude_edge_only(bm,edges=bnd)
    for v in [g for g in ex['geom'] if isinstance(g,bmesh.types.BMVert)]: v.co.z-=0.36
    print(TAG,'diag faces',len(bm.faces),'z %.2f..%.2f'%(min(v.co.z for v in bm.verts),max(v.co.z for v in bm.verts)),flush=True)
    obj('WS253_W63d_diagonal_walk_grass_plot_NE_to_Dickson_NW',bm,[M_WALK])
    # (4) ground patch verts under the N-S walk/stairs lowered (stairs -0.30, walk -0.10 below the top)
    for P in (P1,P2):
        me=P.data; Mw=P.matrix_world; Mi=Mw.inverted(); n=0
        for v in me.vertices:
            w=Mw@v.co
            if (XW-0.1 if w.y<179.2 else XW_LAST-0.1)<=w.x<=XC+0.05 and 163.8<=w.y<=183.5:
                z,k=top_at(w.y)
                if z is None: continue
                zt=z-(0.30 if k=='st' else 0.10)
                if w.z>zt: w.z=zt; v.co=Mi@w; n+=1
            elif XC+0.05<w.x<=-188.9 and 163.8<=w.y<=179.2:  # ws253c: x -189 column beside the cheek: no higher than the tread - 5 cm
                z,k=top_at(w.y)
                if z is not None and w.z>z+0.10: w.z=z+0.10; v.co=Mi@w; n+=1  # ws253d: +0.10 (at -0.05 it dug a trench beside the cheek)
        me.update(); print(TAG,'patch',P.name,'verts lowered',n,flush=True)
    # (5) lamp at the ortho dot (linked acorn mesh copy), base on the walk top
    src=bpy.data.objects.get('Lamp_acorn_031')
    if src:
        z,_=top_at(172.4); ln=src.copy(); ln.name='WS253_W63d_Lamp_acorn_ortho2020_UNVERIFIED'
        ln.location=(-189.75,172.4,z-0.02+(src.location.z-src.matrix_world.translation.z))
        for c in src.users_collection: c.objects.link(ln); break
        print(TAG,'lamp z',round(z,2),flush=True)
for y in (163.9,165,166.7,168,169,170.5,171.7,174,176.5,178,179.3,181,183.4): print(TAG,'prof y',y,'top %.2f'%top_at(y)[0],top_at(y)[1],'eval %.2f'%oz(-190.7,y),flush=True)
