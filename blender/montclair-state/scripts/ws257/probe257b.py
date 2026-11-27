# ws257 read-only M2c review: (a) are the queued NE Children's Center downpipes / valley flashing / ridge caps already in main
# (ws246 found the gutters were, queue stale)? (b) north-file Maintenance Building massing: bbox, mats, and main objects in its box.
import sys; sys.stdout.reconfigure(line_buffering=True)
import bpy, os, json, numpy as np
MS='/workspace/nj-scenes/montclair-state/'
Q=[q['name'] for q in json.load(open(MS+'scripts/ws256/m2c_next256.json'))['queue'] if q['status']=='review']
with bpy.data.libraries.load(MS+'montclair_state.blend') as (a,b): mn=list(a.objects)
with bpy.data.libraries.load(MS+'north/montclair_north.blend') as (a,b): nn=list(a.objects)
for q in Q:
    inm=[n for n in mn if n.startswith(q)]; inn=[n for n in nn if n.startswith(q)]
    print('P257B',q[:60],'| main:',inm[:3],'| north:',inn[:3])
want=[n for n in nn if n.startswith('MSU Maintenance Building')]
with bpy.data.libraries.load(MS+'north/montclair_north.blend') as (a,b): b.objects=want
for o in b.objects:
    M=o.matrix_world; co=np.array([M@v.co for v in o.data.vertices])
    x0,x1,y0,y1,z0,z1=co[:,0].min(),co[:,0].max(),co[:,1].min(),co[:,1].max(),co[:,2].min(),co[:,2].max()
    print('P257B north',o.name,'v',len(co),'x %.1f..%.1f y %.1f..%.1f z %.1f..%.1f'%(x0,x1,y0,y1,z0,z1),'mats',[m.name for m in o.data.materials if m])
    BB=json.load(open(MS+'scripts/ws205/bbox205.json'))
    hits=[(n,v[2:8]) for n,v in BB.items() if v[0]=='MESH' and not (v[3]<x0 or v[2]>x1 or v[5]<y0 or v[4]>y1) and v[7]>z0+1 and (v[3]-v[2])<200]
    for n,v in hits: print('P257B   main in box:',n[:70],[round(t,1) for t in v])
os._exit(0)
