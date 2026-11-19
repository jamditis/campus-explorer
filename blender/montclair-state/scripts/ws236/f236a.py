# ws236 W53q: feather the SYNTHETIC main-native ground edges (PK Feliciano west fill, WS60 edge apron) into the M3b 1 m LiDAR
# corridor patch. Evidence call: M3b is 1 m LiDAR DTM; PK fill (UNVERIFIED synthetic) and WS60 apron (LiDAR-to-skirt feather) are
# interpolated edges, so the synthetic side moves. Ground only: any vertex with another object's geometry within 1.5 m (2D) and
# -1..+3 m vertically is left alone (never lift/drop ground under paving, walls, fences). Base meshes (merge208 convention).
import bpy, bmesh, mathutils, os
from mathutils.kdtree import KDTree
M=bpy.data.objects['M3b_north_LiDAR_DTM_1m_west_rail_corridor_UNVERIFIED_seam']
D=float(os.environ.get('FD','12'))
mb=bmesh.new(); mb.from_mesh(M.data); mb.transform(M.matrix_world)
mbd=[v.co.copy() for v in mb.verts if v.is_boundary]
K=KDTree(len(mbd))
for i,c in enumerate(mbd): K.insert((c.x,c.y,0),i)
K.balance()
TERR=('Terrain','M3','PK_Feliciano','WS60_terrain','WS68_RHD_ground','Skirt','skirt','BD_','DTM','Lawn','lawn','Grass_','grass')
targets=os.environ.get('FT','PK_Feliciano_west_DTM_fill_UNVERIFIED|WS60_terrain_edge_apron_LiDAR_to_skirt').split('|')
targets=[n if n in bpy.data.objects else [o.name for o in bpy.data.objects if o.name.startswith(n)][0] for n in targets]
# region bbox
xs=[];ys=[]
for n in targets:
    o=bpy.data.objects[n]
    for c in o.bound_box:
        w=o.matrix_world@mathutils.Vector(c); xs.append(w.x); ys.append(w.y)
X0,X1,Y0,Y1=min(xs)-2,max(xs)+2,min(ys)-2,max(ys)+2
obs=[];own={}
for o in bpy.data.objects:
    if o.type!='MESH' or o.name in targets or o.name==M.name or any(t in o.name for t in TERR): continue
    if o.hide_render: continue
    bb=[o.matrix_world@mathutils.Vector(c) for c in o.bound_box]
    if max(b.x for b in bb)<X0 or min(b.x for b in bb)>X1 or max(b.y for b in bb)<Y0 or min(b.y for b in bb)>Y1: continue
    mw=o.matrix_world
    for v in o.data.vertices:
        w=mw@v.co
        if X0<=w.x<=X1 and Y0<=w.y<=Y1: obs.append(w.copy()); own[len(obs)-1]=o.name
KO=KDTree(max(1,len(obs)))
for i,c in enumerate(obs): KO.insert((c.x,c.y,0),i)
KO.balance()
print('F236A obstacles verts',len(obs),'objs',len(set(own.values())),flush=True)
for n in targets:
    o=bpy.data.objects[n]; me=o.data
    bm=bmesh.new(); bm.from_mesh(me)
    seam=[];dl=[]
    for v in bm.verts:
        if not v.is_boundary: continue
        c=o.matrix_world@v.co
        near=K.find_n((c.x,c.y,0),3)
        if not near or near[0][2]>3: continue
        ws=[1/max(0.2,d) for _,_,d in near]; z=sum(mbd[i].z*w for (_,i,_),w in zip(near,ws))/sum(ws)
        seam.append((c.x,c.y,0)); dl.append(z-c.z)
    if not seam: print('F236A',n,'no seam',flush=True); continue
    KS=KDTree(len(seam))
    for i,c in enumerate(seam): KS.insert(c,i)
    KS.balance()
    moved=0;blocked=0;mx=0;hits={}
    for v in bm.verts:
        c=o.matrix_world@v.co
        near=KS.find_n((c.x,c.y,0),4)
        d0=near[0][2]
        if d0>=D: continue
        ws=[1/max(0.3,d) for _,_,d in near]; dz=sum(dl[i]*w for (_,i,_),w in zip(near,ws))/sum(ws)
        if abs(dz)<0.03: continue
        t=1-d0/D; w=t*t*(3-2*t); nz=c.z+w*dz
        bad=False
        for (p,i,d) in KO.find_range((c.x,c.y,0),1.5):
            if min(c.z,nz)-1<=obs[i].z<=max(c.z,nz)+3: bad=True; hits[own[i]]=hits.get(own[i],0)+1; break
        if bad: blocked+=1; continue
        v.co.z+=w*dz; moved+=1; mx=max(mx,abs(w*dz))
    bm.to_mesh(me); me.update()
    s=sorted(dl); print('F236A',n,'seam',len(seam),'step med',round(s[len(s)//2],2),'min',round(s[0],2),'max',round(s[-1],2),'moved',moved,'blocked',blocked,'maxdz',round(mx,2),flush=True)
    print('F236A blockers',sorted(hits.items(),key=lambda x:-x[1])[:12],flush=True)
