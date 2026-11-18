import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
o=bpy.data.objects['Context_skirt_3DEP_ortho_4km']
bm=bmesh.new(); bm.from_mesh(o.data); bm.transform(o.matrix_world); t=BVHTree.FromBMesh(bm)
a=bpy.data.objects['WS181_Lot36_asphalt_LiDAR2023int_ortho2020_nostalls_UNVERIFIEDe']
bm2=bmesh.new(); bm2.from_mesh(a.data); bm2.transform(a.matrix_world); t2=BVHTree.FromBMesh(bm2)
for y in (-229.5,-230.5,-231,-231.5,-232.5):
    row=[]
    for x in (-337,-336,-335,-334,-332,-330):
        h=t.ray_cast(Vector((x,y,300)),Vector((0,0,-1)))[0]; h2=t2.ray_cast(Vector((x,y,300)),Vector((0,0,-1)))[0]
        row.append(f'{x}:{h.z if h else None:.2f}/{h2.z if h2 else float("nan"):.2f}')
    print('RAW189',y,' '.join(row),flush=True)
for m in o.modifiers:
    if m.type=='NODES':
        ins=[]
        for k in m.keys():
            v=m[k]; ins.append((k, v.name if hasattr(v,'name') else v))
        print('MOD189',m.name,m.node_group.name if m.node_group else None,ins,flush=True)
