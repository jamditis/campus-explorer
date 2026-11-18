# ws125c: smooth-shade the 3 shrub core meshes; widen groundcover mats ×1.5 so they overlap into a carpet (z ×0.85).
import bpy
ms={o.data for o in bpy.data.objects if o.name.startswith('WS125_bed_')}
for m in ms:
    for p in m.polygons: p.use_smooth=True
n=0
for o in bpy.data.objects:
    if o.name.startswith('WS125_bed_groundcover_'):
        o.scale=(o.scale.x*1.5,o.scale.y*1.5,o.scale.z*0.85); o.location.z-=0.005; n+=1
print('M125c groundcover scaled',n,'meshes smoothed',len(ms))
bpy.ops.wm.save_mainfile(); print('M125c SAVED')
