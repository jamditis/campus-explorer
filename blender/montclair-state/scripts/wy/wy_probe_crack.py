"""wy: pixel-ray the remaining south-eye crack. No save."""
import bpy, json, os
from mathutils import Vector
R='/workspace/nj-scenes/montclair-state'
os.chdir(R)
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
cam=bpy.data.objects['WY_CAM_eye_reid_hole_from_S']
def pixel_ray(px,py,resx=1280,resy=720):
    nx=(px+0.5)/resx; ny=1.0-(py+0.5)/resy
    tr,br,bl,tl=cam.data.view_frame(scene=sc)
    top=tl.lerp(tr,nx); bot=bl.lerp(br,nx); p=bot.lerp(top,ny)
    origin=cam.matrix_world.translation
    target=cam.matrix_world@p
    return origin,(target-origin).normalized()
def hit(origin,direction,dist=400):
    ok,loc,nrm,idx,obj,mat=sc.ray_cast(dg,origin,direction,distance=dist)
    if not ok: return None
    rec=dict(obj=obj.name if obj else None,
             xyz=[round(loc.x,3),round(loc.y,3),round(loc.z,4)],
             nrm=[round(nrm.x,3),round(nrm.y,3),round(nrm.z,3)],
             dist=round((loc-origin).length,3))
    o2=loc+direction*0.02
    ok2,loc2,nrm2,idx2,obj2,mat2=sc.ray_cast(dg,o2,direction,distance=3.0)
    if ok2:
        rec['behind']=dict(obj=obj2.name if obj2 else None,
                           xyz=[round(loc2.x,3),round(loc2.y,3),round(loc2.z,4)],
                           gap=round((loc2-loc).length,4))
    return rec
out={'rows':[]}
for py in (380,400,420,440,460,480,500):
    row=[]
    for px in range(80,1200,40):
        o,d=pixel_ray(px,py)
        rec=hit(o,d) or {'obj':None}
        rec['px']=px; rec['py']=py
        row.append(rec)
    objs=sorted({r.get('obj') for r in row})
    print(f'py={py} objs={objs} n={len(row)}', flush=True)
    out['rows'].append(row)
# dense mid crack estimate py=430
dense=[]
prev=None
for px in range(60,1220,4):
    o,d=pixel_ray(px,430)
    rec=hit(o,d)
    if not rec: rec={'obj':None,'xyz':None}
    rec['px']=px
    if prev and rec.get('obj')!=prev.get('obj'):
        rec['trans']=f"{prev.get('obj')}->{rec.get('obj')}"
        print('TRANS px',px,'py430',rec.get('trans'), 'xyz',rec.get('xyz'), 'prev',prev.get('xyz'), flush=True)
    dense.append(rec); prev=rec
out['dense_py430']=[{k:r.get(k) for k in ('px','obj','xyz','behind','trans')} for r in dense]
json.dump(out, open('data/wy/probe_crack.json','w'), indent=1)
print('WROTE probe_crack.json', flush=True)
