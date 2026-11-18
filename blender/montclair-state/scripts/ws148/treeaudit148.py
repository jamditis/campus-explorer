import bpy
for me in bpy.data.meshes:
    ln=[i for i,m in enumerate(me.materials) if m and 'Leaf' in m.name]
    if not ln: continue
    zs=sorted(p.center.z for p in me.polygons if p.material_index in ln)
    if zs: print("TREE",me.name,"users",me.users,"leafcards",len(zs),"minz",round(zs[0],2),"below2.4",sum(z<2.4 for z in zs),"top",round(zs[-1],1))
