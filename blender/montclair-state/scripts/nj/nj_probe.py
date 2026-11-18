import bpy, mathutils
sc=bpy.context.scene
print('VIEW',sc.view_settings.view_transform,sc.view_settings.look,sc.view_settings.exposure,sc.view_settings.gamma)
def bb(o):
    cs=[o.matrix_world@mathutils.Vector(c) for c in o.bound_box]
    return [min(c[i] for c in cs) for i in range(3)],[max(c[i] for c in cs) for i in range(3)]
# objects near the bin region
for o in bpy.data.objects:
    if o.type not in ('MESH','CURVE') or o.hide_render: continue
    lo,hi=bb(o)
    if lo[0]>-21.5 and hi[0]<-17 and lo[1]>8 and hi[1]<11 and lo[2]>136.5 and hi[2]<139.5:
        print('BIN?|%s|%s|%s|%s|%s'%(o.name,[round(v,2) for v in lo],[round(v,2) for v in hi],[s.material.name if s.material else None for s in o.material_slots],[c.name for c in o.users_collection]))
# materials of key interior objects
for o in bpy.data.objects:
    if o.type=='MESH' and not o.hide_render and (o.name.startswith('NG ') or 'atrium' in o.name.lower() or 'lounge' in o.name.lower() or 'red wall' in o.name.lower()):
        print('INT|%s|%s'%(o.name,[s.material.name if s.material else None for s in o.material_slots]))
