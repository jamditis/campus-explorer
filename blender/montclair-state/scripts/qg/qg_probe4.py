import bpy
from mathutils import Vector
T=bpy.data.objects['Terrain_LiDAR_DTM_1m']; me=T.data
print('UV',[u.name for u in me.uv_layers],'ATTR',[(a.name,a.domain,a.data_type) for a in me.attributes][:20])
print('MATS',[m.name for m in me.materials])
for m in me.materials:
    if m and m.use_nodes:
        print('M',m.name,[(n.type,getattr(n,'image',None) and n.image.name, getattr(n,'uv_map',None)) for n in m.node_tree.nodes if n.type in('TEX_IMAGE','UVMAP','TEX_COORD','ATTRIBUTE','MAPPING')])
# who references terrain in GN
for o in bpy.data.objects:
    for md in o.modifiers:
        if md.type=='NODES' and md.node_group:
            refs=[n.inputs[0].default_value.name for n in md.node_group.nodes if n.type=='OBJECT_INFO' and n.inputs[0].default_value]
            keys=[k for k in md.keys()]
            vals=[md[k].name for k in keys if hasattr(md[k],'name')]
            if 'Terrain_LiDAR_DTM_1m' in refs+vals: print('REF',o.name,md.name)
# face sizes in north strip
import statistics
big=0;cnt=0
for p in me.polygons:
    c=p.center
    if -60<c.x<100 and 150<c.y<255:
        cnt+=1; big+= p.area>4
print('FACES in strip',cnt,'big',big)
