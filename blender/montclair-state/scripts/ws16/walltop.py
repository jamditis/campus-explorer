import bpy
o=bpy.data.objects['TZ_Cole_north_addition_UNVERIFIED']; mw=o.matrix_world; mi=mw.inverted(); me=o.data
roofv=set(v for p in me.polygons if p.material_index==1 for v in p.vertices)
cand=set(v for p in me.polygons if p.material_index!=1 for v in p.vertices)
n=0; sh=0
for v in cand:
    w=mw@me.vertices[v].co
    if 142.95<w.z<143.4:
        if v in roofv: sh+=1; continue
        w.z=142.88; me.vertices[v].co=mi@w; n+=1
me.update(); print('LOWERED',n,'shared_skipped',sh)
bpy.ops.wm.save_mainfile(); print('SAVED')
