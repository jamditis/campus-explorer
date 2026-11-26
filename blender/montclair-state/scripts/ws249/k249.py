# ws249 (standalone, read-only, F=ws249f): the berm-toe crease SE of the east stand = the ws248 patch (3x3-smoothed, up to
# 0.5-0.8 m over the raw toe) cutting through the now LiDAR-snapped dense terrain. For ws248 patch vertices inside
# x -201..-186, y 44..71 that sit over the evaluated terrain (dense faces < 1.5 m2 only), new z = terrain - 0.04 (same
# "sink under the dense terrain" rule as f248g). Writes k249.json {vertex index: new z} (skirt verts move with their top vert).
import bpy, os, sys, json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
F='/workspace/nj-scenes/montclair-state/'+os.environ.get('F','montclair_state_ws249f.blend')
with bpy.data.libraries.load(F) as (a,b): b.objects=['Terrain_LiDAR_DTM_1m','WS248_E_stand_LiDAR2023_ground_patch_1m']
for o in b.objects: bpy.context.scene.collection.objects.link(o)
T,P=b.objects
for m in T.modifiers:
    if 'skirt_under' in m.name.lower(): m.show_viewport=False
dg=bpy.context.evaluated_depsgraph_get(); e=T.evaluated_get(dg); me=e.to_mesh(); M=T.matrix_world
vs=[M@v.co for v in me.vertices]; box=(-203,-184,42,73)
ps=[p for p in me.polygons if any(box[0]<vs[i].x<box[1] and box[2]<vs[i].y<box[3] for i in p.vertices)]
t=BVHTree.FromPolygons(vs,[p.vertices[:] for p in ps]); area=[p.area for p in ps]
PM=P.matrix_world; key={}; out={}
pv=[(i,PM@v.co) for i,v in enumerate(P.data.vertices)]
tops={}
for i,w in pv:
    k=(round(w.x,3),round(w.y,3)); tops.setdefault(k,[]).append((i,w.z))
n=0;mx=0
for k,L in tops.items():
    x,y=k
    if not (-201<x<-186 and 44<y<71): continue
    zt=max(z for _,z in L)
    h=t.ray_cast(Vector((x,y,zt+50)),Vector((0,0,-1)),100)
    if h[0] is None or area[h[2]]>=1.5 or h[0].z>=zt-0.01: continue
    d=(h[0].z-0.04)-zt; mx=min(mx,d); n+=1
    for i,z in L: out[i]=z+d
json.dump(out,open('/workspace/nj-scenes/montclair-state/scripts/ws249/k249.json','w'))
print('K249 top verts sunk',n,'verts moved',len(out),'max drop %.2f'%mx,flush=True)
sys.stdout.flush(); os._exit(0)
