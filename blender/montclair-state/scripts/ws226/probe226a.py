# W53 probe: terrain modifier stack + east grid: base vs evaluated top vs dtm_1m.npy; building/tree bases in east
import bpy, sys, os, json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import numpy as np
A=np.load('/workspace/nj-scenes/montclair-state/data/dtm_1m.npy')
def dtm(x,y):
    i,j=int(y+250),int(x+250)
    return float(A[i,j]) if 0<=i<500 and 0<=j<500 else None
t=bpy.data.objects['Terrain_LiDAR_DTM_1m']; M=t.matrix_world
print('P226 mw',[list(r) for r in M], 'mesh',t.data.name,len(t.data.vertices),len(t.data.polygons),flush=True)
mods=list(t.modifiers)
for m in mods:
    d={'n':m.name,'t':m.type,'r':m.show_render}
    if m.type=='NODES' and m.node_group:
        d['ng']=m.node_group.name
        d['nodes']=[ (n.bl_idname, n.name) for n in m.node_group.nodes][:40]
        ins={}
        for k in m.keys():
            v=m[k]
            ins[k]= v.name if hasattr(v,'name') else (str(v)[:40])
        d['in']=ins
    print('P226 MOD',json.dumps(d),flush=True)
def bvh(onlybase=False):
    for i,m in enumerate(mods): m.show_viewport = (False if onlybase else m.show_render)
    dg=bpy.context.evaluated_depsgraph_get(); e=t.evaluated_get(dg); me=e.to_mesh()
    B=BVHTree.FromPolygons([M@v.co for v in me.vertices],[p.vertices[:] for p in me.polygons]); e.to_mesh_clear(); return B
def allz(B,x,y):
    z=400; hs=[]
    while len(hs)<5:
        h=B.ray_cast(Vector((x,y,z)),Vector((0,0,-1)))
        if not h[0]: break
        hs.append(round(h[0].z,2)); z=h[0].z-0.02
    return hs
Bb=bvh(True); Be=bvh(False)
grid=[]
for x in range(-240,250,10):
    for y in range(-240,250,10):
        d=dtm(x+0.5,y+0.5)
        b=allz(Bb,x+0.5,y+0.5); e=allz(Be,x+0.5,y+0.5)
        grid.append((x,y,d,b,e))
json.dump(grid,open('/workspace/nj-scenes/montclair-state/scripts/ws226/probe226a_grid.json','w'))
# buildings in east: lowest vertex vs dtm under bbox centre
out=[]
for o in bpy.data.objects:
    if o.type!='MESH' or o.hide_render: continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    cx=sum(v.x for v in bb)/8; cy=sum(v.y for v in bb)/8; zmin=min(v.z for v in bb)
    if cx<60 or cx>245 or abs(cy)>245: continue
    d=dtm(cx,cy); e=allz(Be,cx,cy)
    out.append((o.name,round(cx,1),round(cy,1),round(zmin,2),d and round(d,2),e[:3]))
json.dump(out,open('/workspace/nj-scenes/montclair-state/scripts/ws226/probe226a_obj.json','w'))
print('P226 done grid',len(grid),'obj',len(out),flush=True)
sys.stdout.flush(); os._exit(0)
