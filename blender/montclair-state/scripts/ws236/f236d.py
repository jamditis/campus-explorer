# ws236 Codex #49 fix: f236c copied each source vertex's UV onto its extruded duplicate, collapsing the seam strips in UV space
# (smeared band). These grounds use position-based planar ortho mappings (ws60/uv.py, ws68/apply68.py), so fit the affine
# u,v = a*x + b*y + c per object and UV layer by least squares on the ORIGINAL faces' loops and evaluate it at each strip
# loop's world XY. Strip faces = the f236c faces (all four verts within 4 m of an M3b boundary vert, created on the seam).
import bpy, bmesh, numpy as np
from mathutils.kdtree import KDTree
M=bpy.data.objects['M3b_north_LiDAR_DTM_1m_west_rail_corridor_UNVERIFIED_seam']
mb=bmesh.new(); mb.from_mesh(M.data); mb.transform(M.matrix_world)
mbd=[v.co.copy() for v in mb.verts if v.is_boundary]
K=KDTree(len(mbd))
for i,c in enumerate(mbd): K.insert((c.x,c.y,0),i)
K.balance()
names=['PK_Feliciano_west_DTM_fill_UNVERIFIED','WS60_terrain_edge_apron_LiDAR_to_skirt']+[o.name for o in bpy.data.objects if o.name.startswith('WS68_RHD_ground_northDTM')]
NF={'PK_Feliciano_west_DTM_fill_UNVERIFIED':290,'WS60_terrain_edge_apron_LiDAR_to_skirt':26}
for n in names:
    o=bpy.data.objects[n]; mw=o.matrix_world
    bm=bmesh.new(); bm.from_mesh(o.data); bm.faces.ensure_lookup_table()
    k=NF.get(n,135)
    strip=list(bm.faces)[-k:]   # extrude_edge_only appends its faces at the end of the face list
    ok=all(len(f.verts)==4 and min(K.find(((mw@v.co).x,(mw@v.co).y,0))[2] for v in f.verts)<4 for f in strip)
    sset=set(strip)
    for li,uv in enumerate(bm.loops.layers.uv.values()):
        X=[];U=[]
        for f in bm.faces:
            if f in sset: continue
            for l in f.loops:
                w=mw@l.vert.co; X.append((w.x,w.y,1.0)); U.append(tuple(l[uv].uv))
        X=np.array(X); U=np.array(U)
        A,res,_,_=np.linalg.lstsq(X,U,rcond=None)
        err=np.abs(X@A-U).max()
        for f in strip:
            for l in f.loops:
                w=mw@l.vert.co; l[uv].uv=tuple(np.array((w.x,w.y,1.0))@A)
        print('F236D',n[:30],'layer',uv.name,'fit max err',round(float(err),5),'strip faces',len(strip),'strip ok',ok,flush=True)
    bm.to_mesh(o.data); o.data.update()
