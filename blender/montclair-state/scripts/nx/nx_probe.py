import bpy, mathutils
for o in bpy.data.objects:
    n=o.name.lower()
    if any(k in n for k in ('classroom','whiteboard','room shell','marker')) and o.type in('MESH','CAMERA'):
        cs=[o.matrix_world@mathutils.Vector(c) for c in o.bound_box]
        lo=[round(min(c[i] for c in cs),2) for i in range(3)]; hi=[round(max(c[i] for c in cs),2) for i in range(3)]
        print('OBJ',o.name,o.type,o.hide_render,lo,hi,[s.material.name if s.material else None for s in o.material_slots][:3], o.users_collection[0].name)
# green patch probe: cells x -17..-13, y 24..27.5 : roof hits and what's at 1F
dg=bpy.context.evaluated_depsgraph_get()
from mathutils.bvhtree import BVHTree
roofs=[o for o in bpy.data.objects if o.type=='MESH' and not o.hide_render and (o.name.startswith(('School of Communication and Media roof','School of Communication and Media hip')) or (o.name.startswith('CCOM') and 'roof' in o.name.lower()))]
print('ROOFS',[o.name for o in roofs][:20])
def bvh(o):
    me=o.data; M=o.matrix_world; return BVHTree.FromPolygons([M@v.co for v in me.vertices],[p.vertices for p in me.polygons])
rb=[(o.name,bvh(o)) for o in roofs]
dn=mathutils.Vector((0,0,-1))
for y in [23.75,24.25,24.75,25.25,25.75,26.25,26.75,27.25,27.75,28.25]:
    row=[]
    for x in [-18.25,-17.75,-17.25,-16.75,-16.25,-15.75,-15.25,-14.75,-14.25,-13.75,-13.25,-12.75,-12.25,-11.75]:
        h=None
        for nm,b in rb:
            l=b.ray_cast(mathutils.Vector((x,y,190)),dn)[0]
            if l: h=round(l.z,1); break
        row.append('R' if h else '.')
    print('ROOFROW y=%.2f'%y,''.join(row))
# walls near patch
for o in bpy.data.objects:
    if o.type!='MESH' or o.hide_render: continue
    cs=[o.matrix_world@mathutils.Vector(c) for c in o.bound_box]
    lo=[min(c[i] for c in cs) for i in range(3)]; hi=[max(c[i] for c in cs) for i in range(3)]
    if hi[0]>-19 and lo[0]<-11 and hi[1]>22.5 and lo[1]<29 and lo[2]<140 and hi[2]>137.5 and (hi[0]-lo[0])*(hi[1]-lo[1])<400:
        print('NEAR',o.name,[round(v,2) for v in lo],[round(v,2) for v in hi])
