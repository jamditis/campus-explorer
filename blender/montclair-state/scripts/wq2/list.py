import bpy,re
for o in bpy.data.objects:
  n=o.name
  if re.search(r'(?i)canopy|forest|backdrop|woods|tree.?card|impostor|far.?tree|distant|horizon|treeline|tree_line',n):
    bb=[o.matrix_world@__import__('mathutils').Vector(c) for c in o.bound_box]
    xs=[v.x for v in bb]; ys=[v.y for v in bb]
    print('OBJ',n,o.type,o.hide_render,round(min(xs)),round(max(xs)),round(min(ys)),round(max(ys)), len(o.modifiers), [m.type for m in o.modifiers][:3])
c=bpy.data.objects['CAM_oblique_cole_hall_nnw_br']; print('CAM',[round(v,1) for v in c.matrix_world.translation],[round(v,2) for v in c.matrix_world.to_euler()],c.data.lens)
