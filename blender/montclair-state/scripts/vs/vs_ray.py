import bpy
from mathutils import Vector
sc=bpy.context.scene; cam=bpy.data.objects['UV_CAM_eye_Freeman_N_entrance']
dg=bpy.context.evaluated_depsgraph_get()
fr=cam.data.view_frame(scene=sc)  # tr, br, bl, tl
mw=cam.matrix_world; o=mw.translation
print('CAMLOC',tuple(round(x,2) for x in o),'clip',cam.data.clip_start)
def pt(u,v):
    tl,tr,br,bl=fr[3],fr[0],fr[1],fr[2]
    top=tl.lerp(tr,u); bot=bl.lerp(br,u); return mw@top.lerp(bot,v)
for u,v in [(0.05,0.95),(0.2,0.9),(0.1,0.85),(0.4,0.97),(0.6,0.97),(0.9,0.97)]:
    p=pt(u,v); d=(p-o).normalized()
    hit,loc,n,i,ob,_=sc.ray_cast(dg,o,d)
    print('RAY',u,v,hit, ob.name if ob else None, round((loc-o).length,2) if hit else None, [s.material.name for s in ob.material_slots if s.material][:2] if ob else None)
