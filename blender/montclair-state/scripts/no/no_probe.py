import bpy, mathutils
def bb(o):
    cs=[o.matrix_world@mathutils.Vector(c) for c in o.bound_box]; return [min(c[i] for c in cs) for i in range(3)],[max(c[i] for c in cs) for i in range(3)]
for o in bpy.data.objects:
    if o.type in('MESH','CURVE') and not o.hide_render:
        lo,hi=bb(o)
        if lo[0]>-21.2 and hi[0]<14 and lo[1]>-14 and hi[1]<26 and hi[2]>141.5 and lo[2]<146.2:
            n=o.name.lower()
            if any(k in n for k in ('led','strip','bar','sign','rail','light','beam','bridge','ceil')):
                print('P',o.name,'|',o.users_collection[0].name if o.users_collection else '',[round(v,2) for v in lo],[round(v,2) for v in hi])
