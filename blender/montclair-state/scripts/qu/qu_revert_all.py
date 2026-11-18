import os,bpy
os.environ['REVERT']='1'
for f in ['scripts/qu/qu_side.py','scripts/qu/qu_main.py']:
    try: exec(open(f).read(),{'__name__':'__main__'})
    except SystemExit: pass
exec(open('scripts/qu/qu_sig.py').read())
m=bpy.data.materials['OV_Paving_concrete_walk_tone_UNVERIFIED']; print('OV nodes',len(m.node_tree.nodes),'bc from',m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].links[0].from_node.name)
