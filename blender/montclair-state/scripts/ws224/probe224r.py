import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
o=bpy.data.objects['T_SugarMaple_L1_0281']; M=o.matrix_world
G=[]
for nm in ('Terrain_LiDAR_DTM_1m','Footpaths_OSM','WS209_CCOM_walk_apron_crossi','CCOM_dock_apron_20261014jf3'):
    for g in bpy.data.objects:
        if g.name.startswith(nm) and g.type=='MESH':
            Mg=g.matrix_world; G.append(BVHTree.FromPolygons([Mg@v.co for v in g.data.vertices],[p.vertices[:] for p in g.data.polygons]))
def ground(x,y):
    zs=[h[0].z for T in G for h in [T.ray_cast(Vector((x,y,200)),Vector((0,0,-1)))] if h[0]]
    return max(zs) if zs else None
ax=Vector((10.32,-43.39)); low=[]
for v in o.data.vertices:
    w=M@v.co; r=(w.xy-ax).length
    if r<1.0: continue
    g=ground(w.x,w.y)
    if g is not None and w.z-g<3.0: low.append((round(w.z-g,2),round(r,1),round(w.x,1),round(w.y,1)))
low.sort(); print('P224',o.data.name,len(o.data.vertices),'verts <3 m clearance:',len(low),low[:8])
