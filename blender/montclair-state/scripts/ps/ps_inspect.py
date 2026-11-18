import bpy,bmesh
w=bpy.data.objects['Calcia Hall walls']; me=w.data
print('V',len(me.vertices),'F',len(me.polygons),'mods',[m.type for m in w.modifiers],'mats',[m.name for m in me.materials])
bm=bmesh.new(); bm.from_mesh(me)
print('nonmanifold',sum(1 for e in bm.edges if not e.is_manifold),'boundary',sum(1 for e in bm.edges if e.is_boundary))
print('dims',w.dimensions[:], 'loc', w.location[:], 'win_top', w.get('win_top'))
s=bpy.data.objects['PR_Calcia_slot_surrounds_UNVERIFIED']; print('surr V',len(s.data.vertices))
for n in bpy.data.objects.keys():
    if 'Calcia' in n or 'Dickson' in n or 'CAM' in n and ('calcia' in n.lower() or 'dickson' in n.lower()): print('OBJ',n, bpy.data.objects[n].type)
