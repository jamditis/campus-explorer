import bpy
for nm in ['Center for Computing and Information Science walls','Calcia Hall walls','Speech Building walls','Center for Environmental and Life Sciences walls']:
    w=bpy.data.objects[nm]; me=w.data
    print(nm,{k:round(w[k],3) for k in w.keys() if isinstance(w[k],float) or isinstance(w[k],int)})
    fa=me.attributes['facade'].data
    for p in list(me.polygons)[:4]:
        print(' P',p.index,[(tuple(round(c,2) for c in (w.matrix_world@me.vertices[me.loops[li].vertex_index].co)),tuple(round(c,2) for c in fa[li].vector)) for li in p.loop_indices])
