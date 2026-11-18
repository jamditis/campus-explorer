# ws134j: Balance Kitchen massing had no UVs -> the Freeman cream-brick texture smeared into vertical stripes. Box-project UVs in metres.
import bpy, os
SAVE=os.environ.get('SAVE','0')=='1'
o=[o for o in bpy.data.objects if o.name.startswith('WS134_Balance_Kitchen')][0]; me=o.data
f=[x for x in bpy.data.objects if x.name.startswith('UY_Freeman_S_cream_brick_skin')]
print('FREEMAN uv layers',[l.name for l in f[0].data.uv_layers] if f else None)
uvl=me.uv_layers.get('UVMap') or me.uv_layers.new(name='UVMap')
for p in me.polygons:
    n=p.normal
    for li in p.loop_indices:
        c=me.vertices[me.loops[li].vertex_index].co
        if abs(n.z)>0.7: uv=(c.x,c.y)
        elif abs(n.x)>abs(n.y): uv=(c.y,c.z)
        else: uv=(c.x,c.z)
        uvl.data[li].uv=uv
print('UV done',len(me.polygons))
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
