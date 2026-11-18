import bpy
m=bpy.data.materials['TR_Stone_brick_detail_UNVERIFIED']
nt=m.node_tree
bt=nt.nodes['Brick Texture']
print('Brick inputs:')
for inp in bt.inputs:
    v=inp.default_value
    if hasattr(v,'__len__') and not isinstance(v,str):
        try: print(f'  {inp.name}={tuple(round(float(x),4) for x in v)} linked={inp.is_linked}')
        except: print(f'  {inp.name}={v} linked={inp.is_linked}')
    else:
        print(f'  {inp.name}={v} linked={inp.is_linked}')
print('offset', getattr(bt,'offset',None), 'squash', getattr(bt,'squash',None))
# Mix.009 blend type / factor
for name in ('Mix.009','Mix','Mix.007','Mix.008','Mix.001','Mix.004'):
    nd=nt.nodes.get(name)
    if not nd: continue
    print(name, 'blend', getattr(nd,'blend_type',None), 'data', getattr(nd,'data_type',None))
    for i,inp in enumerate(nd.inputs):
        if inp.is_linked:
            print(f'  in[{i}]{inp.name} <- {inp.links[0].from_node.name}')
        else:
            v=inp.default_value
            if hasattr(v,'__len__') and not isinstance(v,str):
                try: print(f'  in[{i}]{inp.name}={tuple(round(float(x),4) for x in v)}')
                except: print(f'  in[{i}]{inp.name}={v}')
            else:
                print(f'  in[{i}]{inp.name}={v}')
# who owns TQ_Stone_buff (fake user?)
m2=bpy.data.materials['TQ_Stone_buff_brick_UNVERIFIED']
print('TQ fake_user', m2.use_fake_user, 'users', m2.users)
# glass on stone?
for o in bpy.data.objects:
    if 'Stone' in o.name and o.type=='MESH':
        print('OBJ', o.name, [s.material.name if s.material else None for s in o.material_slots])
# any window mats on stone?
for o in bpy.data.objects:
    if o.type!='MESH': continue
    if 'Stone' in o.name or any(s.material and 'Stone' in s.material.name for s in o.material_slots):
        mats=[s.material.name if s.material else None for s in o.material_slots]
        if any(m and ('glass' in m.lower() or 'Glass' in m or 'window' in m.lower()) for m in mats):
            print('WINISH', o.name, mats)
