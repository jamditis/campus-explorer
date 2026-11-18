"""wa0 probe (no save): Richardson east tower-corner dark slot (WU_CAM_eye_tileB_from_E)."""
import bpy, json
from mathutils import Vector
O=bpy.data.objects; sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
cam=O['WU_CAM_eye_tileB_from_E']
print('CAM', tuple(round(v,3) for v in cam.matrix_world.translation), cam.data.lens)
def ray(px,py,resx=1024,resy=576):
    nx=(px+.5)/resx; ny=1-(py+.5)/resy
    tr,br,bl,tl=cam.data.view_frame(scene=sc)
    p=bl.lerp(br,nx).lerp(tl.lerp(tr,nx),ny)
    o=cam.matrix_world.translation.copy(); d=((cam.matrix_world@p)-o).normalized(); return o,d
pts={'hole':[(x,y) for x in range(760,774,2) for y in range(298,312,3)],
     'wedge':[(742,315),(745,322),(748,328),(752,333),(738,318),(744,312)],
     'grass':[(790,300),(820,295),(780,310)],'wall':[(740,290),(760,290)],'apron':[(700,334),(730,334)]}
rep={}
for k,L in pts.items():
    rep[k]=[]
    for px,py in L:
        o,d=ray(px,py)
        r=sc.ray_cast(dg,o,d)
        rec=dict(px=px,py=py)
        if r[0]:
            rec.update(obj=r[4].name,loc=[round(c,3) for c in r[1]],n=[round(c,3) for c in r[2]],bf=d.dot(r[2])>0.05, dist=round((r[1]-o).length,2))
        else: rec['obj']=None
        rep[k].append(rec); print(k,rec)
json.dump(rep,open('data/wa0/probe.json','w'),indent=1)
