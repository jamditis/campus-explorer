import bpy
from mathutils import Vector
w=bpy.data.objects['Feliciano School of Business walls']; me=w.data; fa=me.attributes['facade'].data; mw=w.matrix_world
for p in me.polygons[:200]:
    if abs(p.normal.z)>0.2: continue
    cs=[(tuple(round(c,2) for c in mw@me.vertices[me.loops[li].vertex_index].co), tuple(round(c,2) for c in fa[li].vector)) for li in p.loop_indices]
    print('F',p.index,p.material_index,len(cs),cs)
