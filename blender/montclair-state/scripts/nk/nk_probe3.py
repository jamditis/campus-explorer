import bpy, mathutils
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
for x,y,dy in ((0.5,12.0,1),(1.5,12.0,1),(5.5,12.0,1),(1.0,9.0,-1),(6.5,9.0,-1)):
    p=mathutils.Vector((x,y,139.0)); d=mathutils.Vector((0,dy,0)); seq=[]
    for k in range(8):
        r=sc.ray_cast(dg,p,d,distance=8)
        if not r[0]: break
        seq.append((r[4].name[:40],round(r[1].y,3))); p=r[1]+d*0.002
    print('RAY',x,y,seq)
for n in ('NG hallway N maroon doors 0 frosted glass','NG 1F hallway N wall'):
    o=bpy.data.objects[n]; e=o.evaluated_get(dg)
    print('OBJ',n,[ (s.link,s.material.name if s.material else None) for s in o.material_slots],[m.name for m in o.modifiers],len(e.data.polygons) if e.data else None)
