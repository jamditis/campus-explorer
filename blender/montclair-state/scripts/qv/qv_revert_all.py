import os,bpy
os.environ['REVERT']='1'; os.environ.pop('QVSAVE',None)
for f in ['scripts/qv/qv_ceil.py','scripts/qv/qv_grass.py','scripts/qv/qv_lawn.py','scripts/qv/qv_cams.py']:
    try: exec(open(f).read(),{'__name__':'__main__'})
    except SystemExit: pass
exec(open('scripts/qv/qv_sig.py').read())
m=bpy.data.materials['OW2_Context_skirt_ortho_strip_tone_UNVERIFIED']; print('OW2 nodes',len(m.node_tree.nodes),'bc from',m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].links[0].from_node.name)
c=bpy.data.materials['QU_int_ceiling_panels_UNVERIFIED']; print('CEIL nodes',len(c.node_tree.nodes))
