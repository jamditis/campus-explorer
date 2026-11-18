import bpy, mathutils
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
for (y,z) in [(10.1,139.0),(11.0,141.5),(12.6,139.0),(11.8,144.5),(13.3,138.2)]:
    o=mathutils.Vector((-26.0,y,z)); d=mathutils.Vector((1,0,0)); t=0
    hits=[]
    for k in range(8):
        h=sc.ray_cast(dg,o,d)
        if not h[0]: break
        ob=h[4]; mn=ob.material_slots[h[3] if False else 0].material.name if ob.material_slots else ''
        hits.append((ob.name[:60],round(h[1].x,3),mn[:30])); o=h[1]+d*0.002
    print('RAY',y,z,hits)
