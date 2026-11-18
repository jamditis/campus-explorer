# ws75f: lawn override on Terrain_LiDAR ground materials over the (unmodelled) Sprague Field east grandstand roof footprint (x -262..-231, y -131..roof N edge): its dark roof stripes in ortho2020 read as a dark slab on the lawn.
# rises above the WS68 ground near the field). World-space mask data/ws75_grandstand_roof_lawn_mask.png (x -350..-240, y -165..-55; x<-232, -150<y<-89, minus the new lot box).
import bpy
mats=set()
for n in ('Terrain_LiDAR_DTM_1m',):
    o=bpy.data.objects.get(n)
    if o: mats|={s.material for s in o.material_slots if s.material and s.material.name in ('Ground_ortho_grass','Lawn_Varied_Oct_local_fade','COLE_lawn_post2020_bs')}
for m in mats:
    nt=m.node_tree; N=nt.nodes
    if 'WS75_lawn_mix' in N: continue
    print('WS75f all',[(n.name,n.image.name,tuple(n.image.size)) for n in N if n.type=='TEX_IMAGE' and n.image],flush=True); imgs=[n for n in N if n.type=='TEX_IMAGE' and n.image and n.image.size[0]>=1500 and not any(k in n.image.name for k in ('Grass','Leaves','Normal','Rough'))]
    print('WS75f',m.name,[ (n.name,n.image.name) for n in imgs],flush=True)
    for o in imgs:
        outs=[(l.to_node,l.to_socket) for l in nt.links if l.from_node==o and l.from_socket.name=='Color']
        g=N.new('ShaderNodeNewGeometry'); mp=N.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value=(1/110,1/110,1); mp.inputs['Location'].default_value=(350/110,165/110,0)
        tx=N.new('ShaderNodeTexImage'); tx.name='WS75_mask'; tx.image=bpy.data.images.load('//data/ws75_grandstand_roof_lawn_mask.png',check_existing=True)
        tx.image.colorspace_settings.name='Non-Color'; tx.extension='CLIP'
        mx=N.new('ShaderNodeMix'); mx.name='WS75_lawn_mix'; mx.data_type='RGBA'; mx.inputs[7].default_value=(0.184,0.227,0.170,1.0)
        nt.links.new(g.outputs['Position'],mp.inputs['Vector']); nt.links.new(mp.outputs['Vector'],tx.inputs['Vector'])
        nt.links.new(tx.outputs['Color'],mx.inputs['Factor']); nt.links.new(o.outputs['Color'],mx.inputs[6])
        for n,s in outs: nt.links.new(mx.outputs[2],s)
        print('WS75f rewired',m.name,o.name,len(outs),flush=True)
