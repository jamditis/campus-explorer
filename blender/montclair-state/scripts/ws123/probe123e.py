import bpy
c=bpy.data.collections['Tree_HoneyLocust_LOD1_Oct_turning']
for o in c.all_objects: print('O',o.name,o.hide_render,o.hide_viewport,tuple(round(x,2) for x in o.location),[m.type for m in o.modifiers],c.hide_render)
print('CH',[ (ch.name,ch.hide_render) for ch in c.children])
f=next(o for o in bpy.data.objects if o.name.startswith('WS117_Chapin_W_entrance_frame_canopy'))
import bmesh
bm=bmesh.new(); bm.from_mesh(f.data); bm.transform(f.matrix_world)
parts=[]
seen=set()
for v in bm.verts:
    if v in seen: continue
    st=[v]; comp=[]
    while st:
        x=st.pop()
        if x in seen: continue
        seen.add(x); comp.append(x); st+=[e.other_vert(x) for e in x.link_edges]
    print('PART',[round(min(p.co[i] for p in comp),2) for i in range(3)],[round(max(p.co[i] for p in comp),2) for i in range(3)])
# what's near door floor right
for o in bpy.data.objects:
    if o.type!='MESH' or o.hide_render: continue
    bb=[o.matrix_world@__import__('mathutils').Vector(b) for b in o.bound_box]
    if min(v.x for v in bb)<-209.5 and max(v.x for v in bb)>-211.5 and min(v.y for v in bb)<-196.5 and max(v.y for v in bb)>-197.8 and min(v.z for v in bb)<125.2 and max(v.z for v in bb)>124.5: print('NEAR',o.name)
