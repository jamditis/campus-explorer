import bpy, json, bmesh
from mathutils.bvhtree import BVHTree
p='/workspace/nj-scenes/montclair-state/montclair_state.blend'
names=['Terrain_LiDAR_DTM_1m','WS80_sprague_lot_fill_asphalt_ortho2020_UNVERIFIED_edges','WS77_lot_median_island_MULCH_JOEphoto20261112_curb_ortho2020','WS75_sprague_lot_asphalt_ortho2020_UNVERIFIED_edges','WS81_lot_seam_underlay_asphalt']
with bpy.data.libraries.load(p) as (s,d): d.objects=[n for n in names if n in s.objects]
out={}
def wv(o):
    dg=bpy.context.evaluated_depsgraph_get(); bpy.context.scene.collection.objects.link(o)
    dg.update(); e=o.evaluated_get(dg); m=e.to_mesh(); mw=o.matrix_world
    return [mw@v.co for v in m.vertices],[list(f.vertices) for f in m.polygons]
X0,X1,Y0,Y1=-224,-210,-97,-86
for o in d.objects:
    V,F=wv(o)
    fs=[]
    for i,f in enumerate(F):
        c=sum((V[j] for j in f),V[0]*0)/len(f)
        if X0<c.x<X1 and Y0<c.y<Y1: fs.append([i,round(c.x,2),round(c.y,2),round(c.z,3),[[round(V[j].x,2),round(V[j].y,2),round(V[j].z,3)] for j in f]])
    out[o.name]={'n_faces':len(F),'region':fs,'mods':[m.type for m in o.modifiers]}
    print('P99',o.name,len(F),len(fs),[m.type for m in o.modifiers])
json.dump(out,open('/workspace/nj-scenes/montclair-state/scripts/ws99/probe99.json','w'))
