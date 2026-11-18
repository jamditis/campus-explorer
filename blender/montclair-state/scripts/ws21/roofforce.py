# ws21: Life Hall sloped roof planes read as grey membrane with red blotches: sloped faces with no ortho colour fall through to the flat-membrane branch.
# Force tile (em_ringforce=1) on sloped faces (0.45<nz<0.93, material 0), as Cole ws15.
import bpy,os
o=bpy.data.objects['Life Hall roof (LiDAR)']; me=o.data; M=o.matrix_world
ef=me.attributes['em_ringforce']; rc=me.attributes['roofc']
vals=[0.0]*len(me.polygons); ef.data.foreach_get('value',vals)
n=0;lowa=0;already=0
for p in me.polygons:
    if p.material_index!=0: continue
    nz=(M.to_3x3()@p.normal).normalized().z
    if 0.45<nz<0.93:
        a=min(rc.data[v].color[3] for v in p.vertices)
        if a<0.02: lowa+=1
        if vals[p.index]>0.5: already+=1
        vals[p.index]=1.0; n+=1
print('FORCE',n,'lowalpha',lowa,'already',already)
if os.environ.get('SAVE')=='1':
    ef.data.foreach_set('value',vals); me.update(); o['ws21']='em_ringforce=1 on sloped faces (tile)'
    bpy.ops.wm.save_mainfile(); print('SAVED')
