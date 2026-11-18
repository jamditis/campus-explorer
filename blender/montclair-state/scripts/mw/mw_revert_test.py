import bpy, os
sc=bpy.context.scene
for nm in sc.get('mw_hidden',[]):
    o=bpy.data.objects.get(nm)
    if o: o.hide_render=False; o.hide_viewport=False
col=bpy.data.collections['MS_CCOM_newsroom_studio_20261029mw']
for o in list(col.objects): bpy.data.objects.remove(o)
bpy.data.collections.remove(col)
wn='School of Communication and Media walls'
with bpy.data.libraries.load(os.path.abspath('montclair_state_pre_20261029mw.blend')) as (src,dst):
    dst.meshes=[bpy.data.objects[wn].data.name]
w=bpy.data.objects[wn]; w.data=dst.meshes[0]
cur=(len(bpy.data.objects), len(w.data.polygons), sum(1 for o in bpy.data.objects if not o.hide_render))
print("REV_CUR",cur)
bpy.ops.wm.open_mainfile(filepath=os.path.abspath('montclair_state_pre_20261029mw.blend'))
w=bpy.data.objects[wn]
print("REV_BAK",(len(bpy.data.objects), len(w.data.polygons), sum(1 for o in bpy.data.objects if not o.hide_render)))
