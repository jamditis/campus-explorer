import bpy, mathutils
def bb(o):
    cs=[o.matrix_world@mathutils.Vector(c) for c in o.bound_box]; return [round(min(c[i] for c in cs),2) for i in range(3)],[round(max(c[i] for c in cs),2) for i in range(3)]
out=open('data/nq/probe.txt','w')
for o in sorted(bpy.data.objects,key=lambda o:o.name):
    if o.type!='MESH': continue
    lo,hi=bb(o)
    if lo[0]>-40 and hi[0]<40 and lo[1]>-30 and hi[1]<45 and hi[2]>135:
        n=o.name.lower()
        if hi[2]>144 or 'east' in n or 'glass' in n or 'window' in n or 'dome' in n or 'vent' in n or 'grass' in n or 'lawn' in n or 'chair' in n or 'vestib' in n:
            out.write(f"{o.name}|{o.users_collection[0].name if o.users_collection else ''}|{lo}|{hi}|{o.hide_render}|{[s.material.name if s.material else None for s in o.material_slots][:3]}\n")
out.close()
