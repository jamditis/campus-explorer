import bpy, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
def bvh(o):
    M=o.matrix_world; return BVHTree.FromPolygons([M@v.co for v in o.data.vertices],[p.vertices[:] for p in o.data.polygons])
st=[o for o in bpy.data.objects if o.name.startswith('WS170b_Lot3_S_end_curb_concrete_strip')][0]
M=st.matrix_world; V=np.array([tuple(M@v.co) for v in st.data.vertices])
print('P192 strip',st.name,len(V),'x',V[:,0].min(),V[:,0].max(),'y',V[:,1].min(),V[:,1].max(),'z',V[:,2].min(),V[:,2].max(),'mat',[m.name for m in st.data.materials])
# vertices near E end
e=V[V[:,0]>V[:,0].max()-0.6]; print('P192 Eend verts',np.round(e,3).tolist()[:40])
others=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(('WS163_ground','WS191b_','WS191c_','WS190b_','WS110_ground','WS162_Lot3_asphalt','WS190_','WS186','WS170'))]
T=[(o.name[:40],bvh(o)) for o in others]
for x in [V[:,0].max()-0.3, V[:,0].max()+0.05, V[:,0].max()+0.3, V[:,0].max()+1.0]:
  for y in np.arange(V[:,1].max()+0.3, V[:,1].min()-0.5, -0.2):
    hs=[]
    for n,t in T:
        h=t.ray_cast(Vector((x,y,300)),Vector((0,0,-1)))
        if h[0]: hs.append((n[:22],round(h[0].z,3)))
    print('P192 x%.2f y%.2f'%(x,y),sorted(hs,key=lambda a:-a[1])[:3])
