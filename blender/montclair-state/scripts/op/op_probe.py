import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ter=bpy.data.objects['Terrain_LiDAR_DTM_1m']; rd=bpy.data.objects['Roads_OSM']
dg=bpy.context.evaluated_depsgraph_get()
def tree(o):
    e=o.evaluated_get(dg); b=bmesh.new(); b.from_mesh(e.to_mesh()); b.transform(o.matrix_world); return BVHTree.FromBMesh(b),b
tt,_=tree(ter)
print('roads mods',[m.name for m in rd.modifiers],'verts',len(rd.data.vertices),'mats',[s.material.name if s.material else None for s in rd.material_slots])
mw=rd.matrix_world
cells={}
for v in rd.data.vertices:
    p=mw@v.co; h=tt.ray_cast(Vector((p.x,p.y,400)),Vector((0,0,-1)))
    if not h[0]: continue
    f=p.z-h[0].z; k=(int(p.x//16),int(p.y//16)); cells.setdefault(k,[]).append(f)
import statistics
bad=0
rows=[]
for k,l in sorted(cells.items()):
    m=statistics.median(l)
    if abs(m)>0.25: bad+=1
    rows.append((k[0]*16,k[1]*16,len(l),round(m,2)))
print('cells',len(cells),'bad',bad)
open('data/op/roads_float.txt','w').write('\n'.join(map(str,rows)))
# summary by y band
for y0 in range(-400,600,40):
    l=[r[3] for r in rows if y0<=r[1]<y0+40]
    if l: print('y',y0,len(l),'med',round(statistics.median(l),2),'min',min(l),'max',max(l))
# other road-like objects
for o in bpy.data.objects:
    n=o.name.lower()
    if o.type=='MESH' and any(s in n for s in ('road','street','asphalt','plaza','drive','lot')) and not o.library:
        print('OBJ',o.name,o.hide_render,[c.name for c in o.users_collection][:2],[round(x,1) for x in o.dimensions])
