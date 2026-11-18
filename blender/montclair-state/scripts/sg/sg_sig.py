import bpy
g=sum(len(o.data.vertices) for o in bpy.data.objects if o.type=='MESH' and 'grass_points' in o.name)
fw=sum(len(o.data.polygons) for o in bpy.data.objects if o.name.startswith('SF_footway'))
lot=bpy.data.objects['SF_Lot38_asphalt_313028558_UNVERIFIED'].data
print('SGSIG',len(bpy.data.objects),len(bpy.data.materials),g,fw,len(lot.polygons),lot.name,bpy.data.objects['SF_QuadRoad_313028549_UNVERIFIED'].hide_render,bpy.data.objects['SF_Lot38_stall_stripes_UNVERIFIED'].material_slots[0].material.name)
