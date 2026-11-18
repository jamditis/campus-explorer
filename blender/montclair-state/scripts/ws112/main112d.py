import bpy, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
BK='/workspace/nj-scenes/montclair-state/montclair_state_pre_20261113ws112_c.blend'
O=lambda p: next(o for o in bpy.data.objects if o.name.startswith(p))
# (a) restore Terrain_LiDAR from _c (undo ws112c lift)
with bpy.data.libraries.load(BK) as (src,dst): dst.objects=[n for n in src.objects if n.startswith('Terrain_LiDAR_DTM_1m')]
b=dst.objects[0]; cur=O('Terrain_LiDAR_DTM_1m'); nr=0
for vc,vb in zip(cur.data.vertices,b.data.vertices):
    if (vc.co-vb.co).length>1e-6: vc.co=vb.co.copy(); nr+=1
cur.data.update(); bpy.data.objects.remove(b,do_unlink=True); print('E112d restored terrain',nr)
# (b) find what pokes through the brick link
st=O('WS112_CollegeAve_S_E_walk_N_brick'); mw=st.matrix_world
top=[p for p in st.data.polygons if p.normal.z>0.5]
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
cnt={}; pts=[]
for p in top:
    for f in (0.2,0.5,0.8):
        vs=[mw@st.data.vertices[i].co for i in p.vertices]; c=vs[0].lerp(vs[2],f)
        h=sc.ray_cast(dg,Vector((c.x,c.y,c.z+20)),Vector((0,0,-1)))
        if h[0] and h[4].name!=st.name: cnt[h[4].name]=cnt.get(h[4].name,0)+1; pts.append((h[4].name,c.copy()))
print('E112d pokers',cnt)
for name in cnt:
    o=bpy.data.objects[name]
    if o.type!='MESH' or name.startswith(('T_','WS111_','WS110_CollegeAve','WS102_','Footpaths')): continue
    print('E112d mods',name,[m.type for m in o.modifiers])
    if any(m.type=='NODES' for m in o.modifiers): continue
    me=o.data; m2=o.matrix_world; mi=m2.inverted()
    bst=BVHTree.FromPolygons([tuple(mw@v.co) for v in st.data.vertices],[tuple(p.vertices) for p in top]); n=0
    for v in me.vertices:
        p=m2@v.co
        for dx,dy in ((0,0),(0.6,0),(-0.6,0),(0,0.6),(0,-0.6)):
            h=bst.ray_cast(Vector((p.x+dx,p.y+dy,p.z+20)),Vector((0,0,-1)),40)
            if h[0] is not None and p.z>h[0].z-0.08: p.z=h[0].z-0.08; v.co=mi@p; n+=1; break
    me.update(); print('E112d capped',name,n)
bpy.ops.wm.save_mainfile(); print('E112 SAVED')
