import bpy
@bpy.app.handlers.persistent
def _off(*a):
    for o in bpy.data.objects:
        for m in o.modifiers: m.show_viewport=False
bpy.app.handlers.load_post.append(_off)
bpy.ops.wm.open_mainfile(filepath='/workspace/nj-scenes/montclair-state/montclair_state.blend')
AP=next(o for o in bpy.data.objects if o.name.startswith('KX_drive_apron'))
M=AP.matrix_world
for p in AP.data.polygons:
    if p.material_index==1:
        c=M@p.center; print('YEL',p.index,list(p.vertices),round(c.x,2),round(c.y,2),round(c.z,3),round(p.normal.z,2))
for p in AP.data.polygons:
    c=M@p.center
    if c.x>-268 and p.normal.z>0.7: print('ETOP',p.index,p.material_index,list(p.vertices),round(c.x,2),round(c.y,2))
SL=next(o for o in bpy.data.objects if o.name.startswith('WS215_RHD'))
print('SLmats',[m.name for m in SL.data.materials])
