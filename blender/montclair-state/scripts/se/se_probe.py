import bpy
for o in bpy.data.objects:
    n=o.name
    if any(k in n for k in ('RZ_','SA_','StudentCenter','Student Center','Annex')):
        d=o.data
        info=''
        if o.type=='MESH':
            bb=[o.matrix_world@__import__('mathutils').Vector(c) for c in o.bound_box]
            xs=[v.x for v in bb];ys=[v.y for v in bb];zs=[v.z for v in bb]
            info='v%d f%d x%.0f..%.0f y%.0f..%.0f z%.1f..%.1f mats=%s'%(len(d.vertices),len(d.polygons),min(xs),max(xs),min(ys),max(ys),min(zs),max(zs),[m.name for m in d.materials if m][:4])
        print('SE_OBJ',o.type,repr(n),'hide' if o.hide_render else '',info)
