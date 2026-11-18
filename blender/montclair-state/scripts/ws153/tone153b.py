# ws153b: Freeman façade tones vs Commons 2007 + Montclarion 2019 (piers near-neutral grey-beige, white-ish frames)
import bpy, resource
M='/workspace/nj-scenes/montclair-state/'
for m in bpy.data.materials:
    if m.name.startswith('WS152_Freeman_cream_brick'):
        bt=[n for n in m.node_tree.nodes if n.type=='TEX_BRICK'][0]
        bt.inputs['Color1'].default_value=(0.46,0.42,0.35,1); bt.inputs['Color2'].default_value=(0.52,0.48,0.40,1); bt.inputs['Mortar'].default_value=(0.56,0.55,0.52,1)
        print('TONE153 brick',m.name)
    if m.name.startswith('WS152_Freeman_mullion_alu'):
        m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(0.74,0.75,0.76,1); print('TONE153 alu',m.name)
bpy.ops.wm.save_as_mainfile(filepath=M+'montclair_state_ws153b.blend',copy=True)
print('SAVED_WS153B RSS',resource.getrusage(resource.RUSAGE_SELF).ru_maxrss//1024)
