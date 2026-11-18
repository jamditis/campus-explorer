# pl (session pl, Nov 1 2026). ALL UNVERIFIED, reversible; REVERT=1 undoes.
# Feliciano LiDAR roof: vertical 'step' faces (slot 5 plain stucco, LiDAR jumps between roof levels) that stand
# INSIDE the footprint (> D m in plan from every outer wall segment) read as white shards across the red hips.
# A real hipped tile roof has no such walls -> those faces get the forced-tile slot 4. Outer-line steps stay stucco.
import bpy, os, sys, json
from mathutils import Vector
from mathutils.geometry import intersect_point_line
REV=os.environ.get('REVERT')=='1'; SAVE='--save' in sys.argv; OUT=os.environ.get('SAVEAS'); D=float(os.environ.get('D','1.2'))
r=bpy.data.objects['Feliciano School of Business roof (LiDAR)']; w=bpy.data.objects['Feliciano School of Business walls']
if 'pl_prev_mi' in r:
    for i,mi in json.loads(r['pl_prev_mi']): r.data.polygons[i].material_index=mi
    del r['pl_prev_mi']
if 'UNVERIFIED_pl_steps' in r: del r['UNVERIFIED_pl_steps']
if not REV:
    mw=w.matrix_world; segs=[]
    for p in w.data.polygons:
        vs=[mw@w.data.vertices[i].co for i in p.vertices]
        lo=sorted(vs,key=lambda v:v.z)[:2]; segs.append((Vector((lo[0].x,lo[0].y,0)),Vector((lo[1].x,lo[1].y,0))))
    def dist(c):
        best=1e9
        for a,b in segs:
            q,t=intersect_point_line(c,a,b); t=min(max(t,0),1); q=a+(b-a)*t; best=min(best,(c-q).length)
        return best
    rm=r.matrix_world; R=rm.to_3x3(); prev=[]
    for p in r.data.polygons:
        if p.material_index!=5: continue
        if abs((R@p.normal).normalized().z)>0.15: continue
        c=rm@p.center; c=Vector((c.x,c.y,0))
        if dist(c)>D: prev.append((p.index,5)); p.material_index=4
    r['pl_prev_mi']=json.dumps(prev); r['UNVERIFIED_pl_steps']='interior LiDAR step faces (>%.1f m from outer walls) -> forced tile'%D
    print('PL_STEPS retoned',len(prev),'of',sum(1 for p in r.data.polygons if p.material_index in (4,5)))
else: print('REVERTED_PL_STEPS')
if OUT: bpy.ops.wm.save_as_mainfile(filepath=OUT,copy=True); print('SAVED_AS',OUT)
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
