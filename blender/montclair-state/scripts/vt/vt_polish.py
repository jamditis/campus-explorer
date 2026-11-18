import bpy
m=bpy.data.materials['UV_Freeman_step_concrete_UNVERIFIED']
b=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
c=b.inputs['Base Color']
if not c.is_linked:
    m['vt_old_base']=list(c.default_value); c.default_value=tuple(x*0.78 for x in c.default_value[:3])+(1,)
    print('POL base',[round(x,3) for x in c.default_value])
else: print('POL linked')
b.inputs['Roughness'].default_value=0.9
bpy.ops.wm.save_as_mainfile(filepath='/workspace/nj-scenes/montclair-state/montclair_state.blend')
