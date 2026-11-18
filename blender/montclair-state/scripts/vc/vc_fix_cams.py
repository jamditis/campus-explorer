import bpy, json
from mathutils import Vector
OSM=json.load(open('/workspace/nj-scenes/montclair-state/data/uv/freeman_osm_probe.json'))
GR=float(json.load(open('/workspace/nj-scenes/montclair-state/data/uv/uv_main.json')).get('GR',129.053))
OUT=0.08
e1=[e for e in OSM['edges'] if e['i']==1][0]
U1=Vector((e1['u'][0],e1['u'][1],0)).normalized()
N1=Vector((e1['n'][0],e1['n'][1],0)).normalized()
A1=Vector((e1['a'][0],e1['a'][1],0))
L1=e1['len']
print('W edge L', round(L1,2), 'GR', GR)
for name in ['UY_CAM_eye_Freeman_W_side','VC_CAM_closeup_Freeman_W_glass_backplane','VB_CAM_closeup_Freeman_W_glass_cream']:
    o=bpy.data.objects.get(name)
    if not o:
        print('MISSING', name); continue
    loc=Vector(o.location)
    t=(loc-A1).dot(U1); n=(loc-A1).dot(N1)
    lens = o.data.lens if o.type=='CAMERA' else None
    print(name, 'loc', [round(x,2) for x in loc], 't', round(t,2), 'n_out', round(n,2), 'lens', lens)
w=bpy.data.objects.get('UY_Freeman_W_recessed_vertical_windows_UNVERIFIED')
if w:
    pts=[w.matrix_world@Vector(v) for v in w.bound_box]
    print('W win t', round(min((p-A1).dot(U1) for p in pts),2), round(max((p-A1).dot(U1) for p in pts),2))
    print('W win n', round(min((p-A1).dot(N1) for p in pts),2), round(max((p-A1).dot(N1) for p in pts),2))
bp=bpy.data.objects.get('VC_Freeman_W_glass_backplanes_UNVERIFIED')
if bp:
    pts=[bp.matrix_world@Vector(v) for v in bp.bound_box]
    print('BP n', round(min((p-A1).dot(N1) for p in pts),3), round(max((p-A1).dot(N1) for p in pts),3))
    print('BP faces', len(bp.data.polygons))
# list first few materials on W win
if w:
    print('W mats', [s.material.name if s.material else None for s in w.material_slots])
g=bpy.data.materials.get('VB_Freeman_glass_cool_clear_UNVERIFIED')
if g:
    b=g.node_tree.nodes.get('Principled BSDF')
    print('glass alpha', b.inputs['Alpha'].default_value, 'trans', b.inputs['Transmission Weight'].default_value if 'Transmission Weight' in b.inputs else None)
