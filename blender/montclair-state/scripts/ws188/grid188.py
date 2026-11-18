import bpy, os, bmesh, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from collections import defaultdict
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
x0,x1,y0,y1,st=[float(a) for a in os.environ['GRID'].split(',')]
TR=[]
for o in sc.objects:
    if o.type!='MESH' or o.hide_render or o.name.startswith('Context_skirt'): continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]; xs=[v.x for v in bb]; ys=[v.y for v in bb]
    if max(xs)<x0 or min(xs)>x1 or max(ys)<y0 or min(ys)>y1: continue
    if (max(xs)-min(xs))*(max(ys)-min(ys))>4e5: big=True
    e=o.evaluated_get(dg); m=e.to_mesh(); bm=bmesh.new(); bm.from_mesh(m); bm.transform(o.matrix_world)
    # crop faces to region (+2 m) to keep it light
    kill=[f for f in bm.faces if not any(x0-2<v.co.x<x1+2 and y0-2<v.co.y<y1+2 for v in f.verts)]
    bmesh.ops.delete(bm,geom=kill,context='FACES')
    if bm.faces:
        mats=[(f.material_index) for f in bm.faces]; bm.faces.ensure_lookup_table()
        TR.append((o.name[:46],BVHTree.FromBMesh(bm),[m.materials[f.material_index].name[:26] if m.materials else '' for f in bm.faces]))
    bm.free(); e.to_mesh_clear()
print('G188 objects',len(TR),flush=True)
tops=defaultdict(list)
for x in np.arange(x0,x1+1e-6,st):
    for y in np.arange(y0,y1+1e-6,st):
        hs=[]
        for n,t,ms in TR:
            h=t.ray_cast(Vector((x,y,160)),Vector((0,0,-1)))
            if h[0] is not None: hs.append((h[0].z,n,ms[h[2]],round(h[1].z,2)))
        hs.sort(reverse=True)
        if hs:
            z,n,mn,nz=hs[0]; sec=hs[1] if len(hs)>1 else None
            tops[(n,mn)].append((round(x,2),round(y,2),round(z,2),nz,(sec[1][:20],round(z-sec[0],3)) if sec else None))
for k,v in sorted(tops.items(),key=lambda kv:-len(kv[1])):
    print('G188',k,len(v),v[:5],flush=True)
