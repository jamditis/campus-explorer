import bpy
o=bpy.data.objects['Context_skirt_3DEP_ortho_4km']; me=o.data
uv=me.uv_layers['ortho'].data
import itertools
xs=[v.co.x for v in me.vertices]; ys=[v.co.y for v in me.vertices]
print('BB',min(xs),max(xs),min(ys),max(ys), [l.name for l in me.uv_layers])
pts=[]
for p in me.polygons[:3]+[me.polygons[len(me.polygons)//2], me.polygons[-1]]:
    for li in p.loop_indices:
        vi=me.loops[li].vertex_index; c=me.vertices[vi].co; u=uv[li].uv
        print('UV',round(c.x,1),round(c.y,1),round(u.x,5),round(u.y,5))
