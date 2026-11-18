import bpy, mathutils
def bb(o):
    cs=[o.matrix_world@mathutils.Vector(c) for c in o.bound_box]; return [round(min(c[i] for c in cs),2) for i in range(3)],[round(max(c[i] for c in cs),2) for i in range(3)]
out=open('data/np/probe.txt','w')
for o in sorted(bpy.data.objects,key=lambda o:o.name):
    if o.type!='MESH': continue
    n=o.name
    if n.startswith(('NG ','NH ','NI ','NJ ','NK ','NO ')) or 'grid' in n.lower() or 'studio' in n.lower() and 'pipe' in n.lower():
        lo,hi=bb(o); out.write(f"{n}|{o.users_collection[0].name if o.users_collection else ''}|{lo}|{hi}|{o.hide_render}\n")
out.close()
