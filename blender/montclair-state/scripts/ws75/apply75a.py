# ws75a: lawn override for the WS68 ground S/SW of the cogen plant (x<-251, y<-89): the 2020 ortho there shows Sprague Field's
# track + east grandstand roof stripes, which rendered as dark bars on the modeled lawn hill. Insert Mix(ortho, sunlit lawn, mask)
# right after the ortho Image Texture so the rest of the shader treats it as lawn. Mask: data/ws75_sprague_lawn_mask.png (world x -350..-240, y -165..-55).
import bpy
m=bpy.data.materials['WS68_Ground_ortho_grass_north2020']; nt=m.node_tree; N=nt.nodes
if 'WS75_lawn_mix' not in N:
    o=N['Image Texture.003']
    outs=[(l.to_node,l.to_socket) for l in nt.links if l.from_node==o and l.from_socket.name=='Color']
    g=N.new('ShaderNodeNewGeometry'); g.name='WS75_geo'
    mp=N.new('ShaderNodeMapping'); mp.name='WS75_map'; mp.inputs['Scale'].default_value=(1/110,1/110,1); mp.inputs['Location'].default_value=(350/110,165/110,0)
    tx=N.new('ShaderNodeTexImage'); tx.name='WS75_mask'; tx.image=bpy.data.images.load('//data/ws75_sprague_lawn_mask.png',check_existing=True)
    tx.image.colorspace_settings.name='Non-Color'; tx.extension='CLIP'; tx.interpolation='Linear'
    mx=N.new('ShaderNodeMix'); mx.name='WS75_lawn_mix'; mx.data_type='RGBA'
    mx.inputs[7].default_value=(0.184,0.227,0.170,1.0)  # B = sunlit lawn from ortho (srgb .463,.510,.447), linear
    nt.links.new(g.outputs['Position'],mp.inputs['Vector']); nt.links.new(mp.outputs['Vector'],tx.inputs['Vector'])
    nt.links.new(tx.outputs['Color'],mx.inputs['Factor']); nt.links.new(o.outputs['Color'],mx.inputs[6])
    for n,s in outs: nt.links.new(mx.outputs[2],s)
    for n in (g,mp,tx,mx): n.location=(o.location.x+250,o.location.y-400)
    print('WS75a mix inserted, rewired',len(outs),[n.name for n,s in outs],flush=True)
