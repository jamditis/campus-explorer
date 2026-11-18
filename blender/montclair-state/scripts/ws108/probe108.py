import bpy, math
for o in sorted([o for o in bpy.data.objects if o.name.startswith('WS107_Chapin_')],key=lambda o:o.name):
    me=o.data; sl=0; fl=0; zs=[]
    for p in me.polygons:
        nz=p.normal.z
        if 0.3<nz<0.99: sl+=1; zs.append(min(me.vertices[v].co.z for v in p.vertices))
        elif nz>0.99: fl+=1
    print('P108',o.name,len(me.vertices),len(me.polygons),'slope',sl,'flat',fl,'eaveZ',round(min(zs),2) if zs else None,[s.material.name if s.material else None for s in o.material_slots], tuple(round(x,2) for x in o.matrix_world.translation))
