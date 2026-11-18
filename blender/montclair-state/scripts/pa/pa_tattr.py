import bpy
T=bpy.data.objects['Terrain_LiDAR_DTM_1m']; me=T.data
print('TA attrs',[(a.name,a.domain,a.data_type) for a in me.attributes])
print('TA uv',[u.name for u in me.uv_layers], me.uv_layers.active.name if me.uv_layers.active else None)
from mathutils import Vector
for p in ((128,172),(126,168),(140,190),(100,200)):
    ok,loc,n,i=T.ray_cast(Vector((p[0],p[1],400)),Vector((0,0,-1)))
    if ok: print('TA hit',p,i,me.polygons[i].material_index,round(me.polygons[i].area,1))
for m in me.materials:
    print('TA mat',m.name,[ (n.type,getattr(n,'attribute_name',getattr(n,'uv_map',''))) for n in m.node_tree.nodes if n.type in ('ATTRIBUTE','UVMAP','TEX_COORD','TEX_IMAGE','NORMAL_MAP')])
