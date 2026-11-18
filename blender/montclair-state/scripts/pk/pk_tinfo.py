import bpy
T=bpy.data.objects['Terrain_LiDAR_DTM_1m']; me=T.data
print('TI mats',[s.material.name if s.material else None for s in T.material_slots])
print('TI uv',[u.name for u in me.uv_layers],'attrs',[(a.name,a.domain,a.data_type) for a in me.attributes][:20])
mat=T.material_slots[0].material
for n in mat.node_tree.nodes:
    if n.type in ('TEX_COORD','UVMAP','ATTRIBUTE','TEX_IMAGE','MAPPING'): print('TI node',n.type,n.name,getattr(n,'uv_map',''),getattr(n,'attribute_name',''), n.image.name if getattr(n,'image',None) else '')
import collections
mi=collections.Counter(p.material_index for p in me.polygons); print('TI mi',mi)
# west edge
tm=T.matrix_world; e={}
for v in me.vertices:
    w=tm@v.co
    if 140<=w.y<=240 and -260<w.x<-235:
        k=round(w.y); e[k]=min(e.get(k,1e9),w.x)
print('TI edge',sorted(e.items())[::10])
