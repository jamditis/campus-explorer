# ws224k (viewer round-7 W-R7a): T_SugarMaple_L1_0281 (Tree_TulipPoplar_LOD1 mesh, shared by 58 trees) stands correctly at
# the foot of the CCOM courtyard bank (trunk base 133.75 on ground 133.76-133.82; NOT sunk - the courtyard 4-6 m away is
# ~1.7 m higher), so its lowest limb, which reaches up-slope over the courtyard, passes 1.2-1.5 m above the paving.
# Campus trees over walks are limbed up (~2.4 m clearance). This ONE object gets its own mesh copy (the other 57 untouched)
# and every vertex more than 1.0 m from the trunk axis that lies under local ground + 2.4 m is removed (pruned limb ends).
import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
o=bpy.data.objects['T_SugarMaple_L1_0281']; M=o.matrix_world
o.data=o.data.copy(); o.data.name='Tree_TulipPoplar_LOD1_T0281_limbed_up'
G=[]
for nm in ('Terrain_LiDAR_DTM_1m','Footpaths_OSM','WS209_CCOM_walk_apron_crossi','CCOM_dock_apron_20261014jf3'):
    for g in bpy.data.objects:
        if g.name.startswith(nm) and g.type=='MESH':
            Mg=g.matrix_world; G.append(BVHTree.FromPolygons([Mg@v.co for v in g.data.vertices],[p.vertices[:] for p in g.data.polygons]))
def ground(x,y):
    zs=[h[0].z for T in G for h in [T.ray_cast(Vector((x,y,200)),Vector((0,0,-1)))] if h[0]]
    return max(zs) if zs else None
vs=sorted((M@v.co for v in o.data.vertices),key=lambda w:w.z)[:20]
ax=Vector((sum(w.x for w in vs)/20,sum(w.y for w in vs)/20))
bm=bmesh.new(); bm.from_mesh(o.data)
kill=[]
for v in bm.verts:
    w=M@v.co
    if (w.xy-ax).length<1.0: continue
    g=ground(w.x,w.y)
    if g is not None and w.z<g+2.4: kill.append(v)
print('F224K trunk axis (%.2f,%.2f); removing %d of %d verts'%(ax.x,ax.y,len(kill),len(bm.verts)),flush=True)
assert len(kill)<0.08*len(bm.verts)
bmesh.ops.delete(bm,geom=kill,context='VERTS'); bm.to_mesh(o.data); bm.free(); o.data.update()
