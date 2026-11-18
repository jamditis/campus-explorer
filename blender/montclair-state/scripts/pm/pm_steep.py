# pm (session pm, Nov 1 2026). ALL UNVERIFIED, reversible (REVERT=1 restores every changed face's material index).
# Photo feliciano_commons_08: white stucco upper storeys under LOW red hip roofs with deep eaves; no tall tile curtains.
# (1) Steep LiDAR faces (|nz| < NZ) that pi/pl forced to tile (slot 4) are the upper-storey walls between roof levels
#     -> plain stucco slot 5, then a 3-pass majority filter (4<->5, only faces originally 4) removes isolated shards.
# (2) Low hip read from the air: flat deck faces (slot 0) within RING m of the top of those walls -> forced tile slot 4.
import bpy, os, sys, json, numpy as np
from collections import defaultdict
REV=os.environ.get('REVERT')=='1'; SAVE='--save' in sys.argv; OUT=os.environ.get('SAVEAS')
r=bpy.data.objects['Feliciano School of Business roof (LiDAR)']; P='pm_face_prev_mat'
me=r.data
if P in me.keys():
    for i,m in json.loads(me[P]).items(): me.polygons[int(i)].material_index=m
    del me[P]; print('REVERTED_PM_STEEP')
if not REV:
    NZ=float(os.environ.get('NZ','0.5')); RING=float(os.environ.get('RING','2.5'))
    prev={p.index:p.material_index for p in me.polygons}
    orig4=[p.index for p in me.polygons if p.material_index==4]
    for i in orig4:
        if abs(me.polygons[i].normal.z)<NZ: me.polygons[i].material_index=5
    ef=defaultdict(list)
    for p in me.polygons:
        for e in p.edge_keys: ef[e].append(p.index)
    nb=defaultdict(set)
    for fs in ef.values():
        for a in fs:
            for b in fs:
                if a!=b: nb[a].add(b)
    S=set(orig4)
    for it in range(3):
        cur={i:me.polygons[i].material_index for i in S}
        for i in S:
            ns=[cur[j] for j in nb[i] if j in cur]
            if len(ns)<2: continue
            n5=ns.count(5); n4=len(ns)-n5
            if cur[i]==4 and n5>n4 and abs(me.polygons[i].normal.z)<0.85: me.polygons[i].material_index=5
            elif cur[i]==5 and n4>n5: me.polygons[i].material_index=4
    mw=r.matrix_world
    co=np.array([tuple(mw@v.co) for v in me.vertices])
    wall=[i for i in S if me.polygons[i].material_index==5]
    tops=set()
    for i in wall:
        vs=list(me.polygons[i].vertices); zmax=max(co[v,2] for v in vs)
        for v in vs:
            if co[v,2]>zmax-0.3: tops.add(v)
    T=np.array(sorted(tops)); ring=0
    for p in me.polygons:
        if p.material_index!=0 or p.normal.z<0.97: continue
        c=co[list(p.vertices)].mean(0)
        near=T[(np.hypot(co[T,0]-c[0],co[T,1]-c[1])<RING) & (np.abs(co[T,2]-c[2])<0.6)]
        if len(near): p.material_index=4; ring+=1
    ch={str(i):m for i,m in prev.items() if me.polygons[i].material_index!=m}
    me[P]=json.dumps(ch)
    print('PM_STEEP walls',len(wall),'ring faces',ring,'changed',len(ch))
me.update()
if OUT: bpy.ops.wm.save_as_mainfile(filepath=OUT,copy=True); print('SAVED_AS',OUT)
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
