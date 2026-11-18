import bpy, bmesh, collections
from mathutils import Vector
from mathutils.bvhtree import BVHTree
fp=bpy.data.objects['Footpaths_OSM']; ter=bpy.data.objects['Terrain_LiDAR_DTM_1m']
dg=bpy.context.evaluated_depsgraph_get(); te=ter.evaluated_get(dg); bt=bmesh.new(); bt.from_mesh(te.to_mesh()); bt.transform(ter.matrix_world); tree=BVHTree.FromBMesh(bt)
print('terrain bbox', [round(min(v.co[i] for v in bt.verts),1) for i in range(3)], [round(max(v.co[i] for v in bt.verts),1) for i in range(3)])
cells=collections.defaultdict(list); miss=0
for v in fp.data.vertices:
    h=tree.ray_cast(Vector((v.co.x,v.co.y,400)),Vector((0,0,-1)))
    if h[0] is None: miss+=1; continue
    cells[(int(v.co.x//16),int(v.co.y//16))].append(v.co.z-h[0].z)
print('miss',miss)
import statistics
rows=[]
for k,L in cells.items():
    m=statistics.median(L); rows.append((k,m,min(L),max(L),len(L)))
for k,m,a,b,n in sorted(rows,key=lambda r:(r[0][1],r[0][0])):
    if abs(m)>0.25 or b>0.6: print('CELL x%4d y%4d med %5.2f min %5.2f max %5.2f n %d'%(k[0]*16,k[1]*16,m,a,b,n))
print('cells',len(rows),'bad',sum(1 for r in rows if r[1]>0.25))
