import bpy,re
from mathutils import Vector
M='/workspace/nj-scenes/montclair-state/montclair_state.blend'
with bpy.data.libraries.load(M) as (src,dst):
    allnames=list(src.objects)
pat=re.compile(r'^(WS110_(?!.*CAM)|WS102_CollegeAve|WS103_CollegeAve|WS104_|Footpaths_OSM|WS105_)')
want=[n for n in allnames if pat.search(n)]
with bpy.data.libraries.load(M) as (src,dst):
    dst.objects=want
for o in dst.objects:
    if o is None: continue
    bpy.context.scene.collection.objects.link(o)
    if o.type!='MESH': continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]; xs=[v.x for v in bb]; ys=[v.y for v in bb]; zs=[v.z for v in bb]
    print('B111',o.name,len(o.data.vertices),'x',round(min(xs),1),round(max(xs),1),'y',round(min(ys),1),round(max(ys),1),'z',round(min(zs),2),round(max(zs),2),'hide',o.hide_render,[m.name for m in o.material_slots])
bpy.ops.wm.save_as_mainfile(filepath='/workspace/nj-scenes/montclair-state/prep/ws111_CollegeAve_S_walks_aprons/work111_src.blend')
