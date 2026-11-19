# W52b: tree trunk bases vs EVALUATED terrain (terrain modifiers on only; everything else modifiers off), + W47 dry list
import bpy, json, os, sys
from mathutils import Vector
from mathutils.bvhtree import BVHTree
T=[o for o in bpy.data.objects if o.name.startswith('Terrain_LiDAR_DTM_1m') and o.type=='MESH']
for t in T:
    for m in t.modifiers: m.show_viewport=True
    print('P225C terrain',t.name,[m.name for m in t.modifiers],flush=True)
dg=bpy.context.evaluated_depsgraph_get()
B=[]
for t in T:
    e=t.evaluated_get(dg); me=e.to_mesh(); M=t.matrix_world
    B.append(BVHTree.FromPolygons([M@v.co for v in me.vertices],[p.vertices[:] for p in me.polygons])); e.to_mesh_clear()
R=[]
for o in bpy.data.objects:
    if o.type!='MESH' or not o.data.name.startswith('Tree_') or o.hide_render: continue
    M=o.matrix_world; ws=[M@v.co for v in o.data.vertices]
    vs=sorted(ws,key=lambda w:w.z)[:20]; ax=Vector((sum(w.x for w in vs)/20,sum(w.y for w in vs)/20)); zb=vs[0].z
    raw=[h[0].z for b in B for h in [b.ray_cast(Vector((ax.x,ax.y,300)),Vector((0,0,-1)))] if h[0]]
    allh=[]
    for b in B:
        z=300
        while True:
            h=b.ray_cast(Vector((ax.x,ax.y,z)),Vector((0,0,-1)))
            if not h[0]: break
            allh.append(round(h[0].z,2)); z=h[0].z-0.01
    R.append((o.name,round(ax.x,1),round(ax.y,1),round(zb,2),allh[:4]))
bad=[r for r in R if r[4] and abs(r[3]-r[4][0])>0.5]
print('P225C trees visible',len(R),'base off top-ground by >0.5 m:',len(bad),flush=True)
for r in sorted(bad,key=lambda r:r[3]-r[4][0])[:40]: print('P225C',r,flush=True)
json.dump(R,open('/workspace/nj-scenes/montclair-state/scripts/ws225/probe225c.json','w'))
os.environ['DRY']='1'
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws225/fix225b.py').read())
sys.stdout.flush(); os._exit(0)
