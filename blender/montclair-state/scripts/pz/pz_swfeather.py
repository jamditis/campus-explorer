# pz: SW terrace step west of Feliciano. The MAIN Terrain_LiDAR_DTM_1m ends in a straight cut at x~-246; south of y~128 the ground
# west of the cut (Context_skirt / PK west-fill south feather) sits 1.0-1.8 m lower -> a visible 'terrace step' line in the
# Feliciano NW oblique. PZ_Feliciano_SW_DTM_edge_feather_UNVERIFIED: 1 m grid from the DTM edge (3 cm under it) easing
# (smoothstep) down over FW m west to 5 cm under whatever ground lies below (skirt / PK fill), rows y 30..132; where the step
# is <8 cm the row is skipped. Same Ground_ortho_grass + 'ortho' UV (least-squares fit on the PK fill). REVERT=1 deletes. UNVERIFIED.
import bpy, bmesh, os
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
REV=os.environ.get('REVERT')=='1'; ON='PZ_Feliciano_SW_DTM_edge_feather_UNVERIFIED'; FW=float(os.environ.get('FW','22'))
if ON in bpy.data.objects:
    o=bpy.data.objects[ON]; m=o.data; bpy.data.objects.remove(o); bpy.data.meshes.remove(m); print('REVERTED',ON)
if not REV:
    def bvh(name):
        o=bpy.data.objects[name]; bm=bmesh.new(); bm.from_mesh(o.data); bm.transform(o.matrix_world); t=BVHTree.FromBMesh(bm); bm.free(); return t
    D=bvh('Terrain_LiDAR_DTM_1m'); S=bvh('Context_skirt_3DEP_ortho_4km'); F=bvh('PK_Feliciano_west_DTM_fill_UNVERIFIED')
    def hz(t,x,y):
        h=t.ray_cast(Vector((x,y,300)),Vector((0,0,-1)),400); return h[0].z if h[0] else None
    def under(x,y):
        a=hz(F,x,y); b=hz(S,x,y)
        if a is None: return b
        if b is None: return a
        return max(a,b)
    P=bpy.data.objects['PK_Feliciano_west_DTM_fill_UNVERIFIED']; pm=P.data; pw=P.matrix_world; puv=pm.uv_layers['ortho'].data
    A=[];U=[]
    for li in range(0,len(pm.loops),7):
        l=pm.loops[li]
        c=pw@pm.vertices[l.vertex_index].co; A.append((c.x,c.y,1.0)); U.append(tuple(puv[l.index].uv))
    A=np.array(A); U=np.array(U); coef,res,rk,sv=np.linalg.lstsq(A,U,rcond=None); resid=np.abs(A@coef-U).max()
    rows={}; 
    for y in range(30,133):
        xe=None; x=-236.0
        while x>-262:
            if hz(D,x,y) is None: xe=x+0.5; break
            x-=0.5
        if xe is None: continue
        ze=hz(D,xe+0.3,y)
        if ze is None: continue
        u0=under(xe-1.0,y)
        if u0 is None or ze-u0<0.08: continue
        rows[y]=(xe,ze)
    print('PZ_SW rows',len(rows),min(rows) if rows else None,max(rows) if rows else None,'uv resid %.4f'%resid)
    bm=bmesh.new(); L=bm.loops.layers.uv.new('ortho'); grid={}
    for y,(xe,ze) in rows.items():
        xs=[xe+0.6]+[float(x) for x in range(int(np.floor(xe)),int(np.floor(xe-FW))-2,-1)]
        for i,x in enumerate(xs):
            u=under(x,y)
            if u is None: continue
            d=min(1.0,max(0.0,(xe-x)/FW)); w=1-(3*d*d-2*d*d*d)
            z=(ze-0.03)*w+(u-0.05)*(1-w) if x<xe else ze-0.03
            grid[(y,i)]=bm.verts.new((x,y,z))
    nf=0
    for (y,i),v in list(grid.items()):
        k=[(y,i),(y,i+1),(y+1,i+1),(y+1,i)]
        if all(kk in grid for kk in k):
            vs=[grid[kk] for kk in k]
            try:
                f=bm.faces.new(vs)
            except ValueError: continue
            if f.normal.z<0: f.normal_flip()
            for lp in f.loops: c=lp.vert.co; lp[L].uv=tuple(np.array((c.x,c.y,1.0))@coef)
            nf+=1
    me=bpy.data.meshes.new(ON); bm.to_mesh(me); bm.free(); me.materials.append(pm.materials[0])
    o=bpy.data.objects.new(ON,me); o['source_note']='UNVERIFIED (pz, Nov 2 2026): feather from the LiDAR DTM west cut (x~-246) down to the skirt/PK fill, y 30..132, smoothstep over %.0f m; replaces a 1-1.8 m terrace step that is a data seam, not a real landform (unconfirmed)'%FW
    P.users_collection[0].objects.link(o); print('PZ_SW verts',len(me.vertices),'faces',nf)
