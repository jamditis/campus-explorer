import bpy, bmesh
from mathutils import Vector
fp=bpy.data.objects['Footpaths_OSM']; me=fp.data
print('verts',len(me.vertices),'faces',len(me.polygons),'mods',[m.type+':'+m.name for m in fp.modifiers],'mw_id',fp.matrix_world==fp.matrix_world.Identity(4), 'users',me.users, 'lib',fp.library, me.library)
bm=bmesh.new(); bm.from_mesh(me)
nb=sum(1 for e in bm.edges if e.is_boundary); print('boundary edges',nb, 'manifold?', all(e.is_manifold for e in bm.edges))
up=sum(1 for f in bm.faces if f.normal.z>0.5); dn=sum(1 for f in bm.faces if f.normal.z<-0.5); print('up',up,'down',dn,'side',len(bm.faces)-up-dn)
import statistics
L=[e.calc_length() for e in bm.edges]; print('edge len med',statistics.median(L),'max',max(L))
# objects near error region
C=Vector((10.6,141.1))
ter=bpy.data.objects['Terrain_LiDAR_DTM_1m']
from mathutils.bvhtree import BVHTree
dg=bpy.context.evaluated_depsgraph_get(); te=ter.evaluated_get(dg); bt=bmesh.new(); bt.from_mesh(te.to_mesh()); bt.transform(ter.matrix_world); tree=BVHTree.FromBMesh(bt)
def tz(x,y):
    h=tree.ray_cast(Vector((x,y,400)),Vector((0,0,-1))); return h[0].z if h[0] else None
n=0
for o in bpy.data.objects:
    if o.type not in ('MESH','EMPTY') or o.parent: continue
    p=o.matrix_world.translation
    d=(p.xy-C).length
    if d<24 or d>110 or p.y<150 and p.x<20: continue
    t=tz(p.x,p.y)
    if t is None: continue
    if 1.0 < p.z-t < 10 and len(o.users_collection) and o.name!='Footpaths_OSM':
        n+=1
        if n<60: print('FLOATOBJ',o.name,round(p.x,1),round(p.y,1),round(p.z-t,2),o.users_collection[0].name)
print('n float objs',n)
for c in bpy.data.objects:
    if c.type=='MESH' and c.modifiers and any(m.type=='NODES' for m in c.modifiers) and 'Foot' in c.name: print('GN',c.name)
