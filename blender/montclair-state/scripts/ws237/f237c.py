# ws237 W53p tone (try): M3b (north 2020 LEAF-OFF ortho, dormant-brown grass) meets the campus fills (PK / WS60 / WS68), whose
# materials tint a grass texture green, along a hard brown/green line. Feather M3b's colour toward the campus lawn tone over
# 10 m from those grounds: POINT attribute w237_seamfade = smoothstep(1 - d/10) (d = 2D distance to the nearest PK/WS60/WS68
# vertex), and in North_ground_ortho2020.001 (M3b only) the final base colour mixes toward a green-shifted copy of itself.
import bpy, mathutils
from mathutils.kdtree import KDTree
M=bpy.data.objects['M3b_north_LiDAR_DTM_1m_west_rail_corridor_UNVERIFIED_seam']
src=['PK_Feliciano_west_DTM_fill_UNVERIFIED','WS60_terrain_edge_apron_LiDAR_to_skirt']+[o.name for o in bpy.data.objects if o.name.startswith('WS68_RHD_ground_northDTM')]
pts=[]
for n in src:
    o=bpy.data.objects[n]; mw=o.matrix_world
    pts+=[(mw@v.co) for v in o.data.vertices]
kd=KDTree(len(pts))
for i,p in enumerate(pts): kd.insert((p.x,p.y,0),i)
kd.balance()
FD=10.0; me=M.data; mw=M.matrix_world
a=me.attributes.get('w237_seamfade') or me.attributes.new('w237_seamfade','FLOAT','POINT')
vals=[0.0]*len(me.vertices); n1=0
for v in me.vertices:
    w=mw@v.co; _,_,d=kd.find((w.x,w.y,0)); t=max(0.0,1-d/FD); s=t*t*(3-2*t); vals[v.index]=s; n1+=s>0
a.data.foreach_set('value',vals)
mat=bpy.data.materials['North_ground_ortho2020.001']; nt=mat.node_tree; N=nt.nodes
bs=N['Principled BSDF']; lk=bs.inputs['Base Color'].links[0]; srcs=lk.from_socket
at=N.new('ShaderNodeAttribute'); at.attribute_name='w237_seamfade'; at.attribute_type='GEOMETRY'; at.name='w237_fade_attr'
hs=N.new('ShaderNodeHueSaturation'); hs.name='w237_green_hsv'; hs.inputs['Hue'].default_value=0.56; hs.inputs['Saturation'].default_value=1.25; hs.inputs['Value'].default_value=0.95
gm=N.new('ShaderNodeMix'); gm.data_type='RGBA'; gm.blend_type='MIX'; gm.name='w237_green_grass_mix'; gm.inputs['Factor'].default_value=0.45; gm.inputs[7].default_value=(0.16,0.25,0.08,1)
mx=N.new('ShaderNodeMix'); mx.data_type='RGBA'; mx.name='w237_seam_tone_mix'
mf=N.new('ShaderNodeMath'); mf.operation='MULTIPLY'; mf.inputs[1].default_value=0.9; mf.name='w237_fade_strength'
nt.links.new(srcs,hs.inputs['Color']); nt.links.new(hs.outputs[0],gm.inputs[6])
nt.links.new(at.outputs['Fac'],mf.inputs[0]); nt.links.new(mf.outputs[0],mx.inputs['Factor'])
nt.links.new(srcs,mx.inputs[6]); nt.links.new(gm.outputs[2],mx.inputs[7]); nt.links.new(mx.outputs[2],bs.inputs['Base Color'])
print('F237C M3b verts faded',n1,'of',len(me.vertices),'source pts',len(pts),flush=True)
