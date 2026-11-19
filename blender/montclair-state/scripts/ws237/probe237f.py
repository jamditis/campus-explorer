import bpy,os
dg=bpy.context.evaluated_depsgraph_get(); o=bpy.data.objects['Context_skirt_3DEP_ortho_4km']
e=o.evaluated_get(dg); print('P237F skirt eval verts',len(e.data.vertices),'faces',len(e.data.polygons),flush=True)
m=o.modifiers['WS237_skirt_under_W53q_lowered_edges']; m.show_viewport=False; m.show_render=False; dg.update()
e=o.evaluated_get(dg); print('P237F without ws237',len(e.data.vertices),flush=True)
m.show_viewport=True; m.show_render=True; dg.update()
