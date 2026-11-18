import bpy,bmesh,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
src='/workspace/nj-scenes/montclair-state/montclair_state.blend'
N=['Terrain_LiDAR_DTM_1m','WS60_terrain_edge_apron_LiDAR_to_skirt','Context_skirt_3DEP_ortho_4km','WS27_CollegeAve_carriageway_2020ortho']
with bpy.data.libraries.load(src) as (fr,to): N=[n for n in fr.objects if any(n.startswith(a) for a in N)]
print('N',N)
with bpy.data.libraries.load(src,link=False) as (fr,to): to.objects=N
sc=bpy.context.scene
for o in to.objects: sc.collection.objects.link(o)
dg=bpy.context.evaluated_depsgraph_get()
T={}
for o in to.objects:
    e=o.evaluated_get(dg); m=e.to_mesh(); bm=bmesh.new(); bm.from_mesh(m); bm.transform(o.matrix_world)
    T[o.name]=BVHTree.FromBMesh(bm); print('M',o.name,len(m.polygons),[md.name for md in o.modifiers][-4:]); bm.free(); e.to_mesh_clear()
D=np.load('/workspace/nj-scenes/montclair-state/data/dtm_1m.npy')
def h(name,x,y):
    for k,t in T.items():
        if k.startswith(name):
            r=t.ray_cast(Vector((x,y,400)),Vector((0,0,-1)),1000)[0]
            return round(r.z,1) if r else None
for y in range(-80,40,8):
    row=[]
    for x in range(-300,-196,8):
        tz=h('Terrain',x,y); az=h('WS60',x,y); sz=h('Context',x,y); rz=h('WS27',x,y)
        d=round(float(D[y+250,x+250]),1) if x>=-250 else '-'
        row.append('%d:%s/%s/%s/%s|%s'%(x,tz,az,sz,rz,d))
    print('Y',y,' '.join(row))
