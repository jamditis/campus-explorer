"""wa1: QT soil-edge outer band -> ease outer edge down onto ground (lower-only), report all footways. DRY=1 no write."""
import bpy, numpy as np, json, os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
O=bpy.data.objects; dg=bpy.context.evaluated_depsgraph_get()
DRY=os.environ.get('DRY')=='1'; SAVE=os.environ.get('SAVE')=='1'
def bvh(o):
    e=o.evaluated_get(dg); m=e.to_mesh(); b=BVHTree.FromPolygons([o.matrix_world@v.co for v in m.vertices],[tuple(p.vertices) for p in m.polygons]); e.to_mesh_clear(); return b
G=[bvh(O[n]) for n in O.keys() if O[n].type=='MESH' and n.startswith(('WV_stone','WN_south','WO_gully','Terrain_LiDAR','QW_DTM','WU_rich','WT_rich','WF_east','RZ2_','WA0_'))]
def gz(x,y):
    z=[h[0].z for b in G for h in [b.ray_cast(Vector((x,y,500)),Vector((0,0,-1)))] if h[0] is not None]
    return max(z) if z else None
TARGET=0.010
rep={}
for t in [o for o in O if o.name.startswith('QT_soil_edge_'+os.environ.get('ONLYT',''))]:
    sn=t.name.replace('QT_soil_edge_','QS_footway_'); S=bvh(O[sn]); mw=t.matrix_world; inv=mw.inverted()
    before=[];after=[];ch=0;moved=[]
    for p in t.data.polygons:
        vi=list(p.vertices); ws=[mw@t.data.vertices[i].co for i in vi]
        d=[S.find_nearest(v)[3] for v in ws]; idx=np.argsort(d)
        for k in idx[2:]:
            v=ws[k]; g=gz(v.x,v.y)
            if g is None: continue
            dz=v.z-g; before.append(dz)
            if dz>TARGET+0.002:
                nz=g+TARGET; moved.append(dz-TARGET)
                if not DRY: t.data.vertices[vi[k]].co=inv@Vector((v.x,v.y,nz))
    rep[t.name]=dict(outer_n=len(before),moved=len(moved),med_before_cm=round(float(np.median(before))*100,1) if before else None,max_drop_cm=round(max(moved)*100,1) if moved else 0,med_drop_cm=round(float(np.median(moved))*100,1) if moved else 0)
    print('REP',t.name,rep[t.name])
    if not DRY: t.data.update()
json.dump(rep,open('data/wa1/fix_report.json','w'),indent=1)
if SAVE: bpy.ops.wm.save_mainfile(compress=True); print('SAVED')
