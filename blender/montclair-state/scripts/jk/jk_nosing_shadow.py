# Session jk (2026-10-26 ~6:35 AM ET): subtle contact shadow line under each seat nosing / in the riser-tread inner corners.
# Shader only (no geometry): Ambient Occlusion node (only_local, distance DIST default 0.05 m) -> Base Color *= mix(1, AO, AMT default 0.35)
# in the amphitheater seat/riser stone + aisle nosing materials. Nodes tagged 'jk' (idempotent; REVERT=1 removes them). SAVE=1 / OUTB=copy.
# Does not touch geometry, UVs or normals, so no jc/jd/je/jf/jg/jh rerun-order constraints are affected.
import bpy, os
REV=os.environ.get('REVERT')=='1'; DIST=float(os.environ.get('DIST',0.05)); AMT=float(os.environ.get('AMT',0.35))
MATS=os.environ.get('MATS','hn_amphi_seat_stone_blocks,hn_amphi_riser_coursed_stone,io_amphi_aisle_stone,ip_amphi_aisle_nosing_worn').split(',')
for mn in MATS:
    m=bpy.data.materials.get(mn)
    if not m: print('JKN missing',mn); continue
    nt=m.node_tree; N=nt.nodes; L=nt.links
    bs=next(n for n in N if n.type=='BSDF_PRINCIPLED'); bc=bs.inputs['Base Color']
    old=[n for n in N if n.get('jk')]
    if old:
        mul=next(n for n in old if n.get('jk')=='mul')
        src=mul.inputs['A'].links[0].from_socket if mul.inputs['A'].links else None
        for n in old: N.remove(n)
        if src: L.new(src,bc)
    if REV: print('JKN reverted',mn); continue
    src=bc.links[0].from_socket if bc.links else None
    ao=N.new('ShaderNodeAmbientOcclusion'); ao['jk']='ao'; ao.only_local=True; ao.samples=8; ao.inputs['Distance'].default_value=DIST
    mx=N.new('ShaderNodeMix'); mx['jk']='mix'; mx.data_type='FLOAT'; mx.inputs['Factor'].default_value=AMT
    mx.inputs[2].default_value=1.0; L.new(ao.outputs['AO'],mx.inputs[3])
    mul=N.new('ShaderNodeMix'); mul['jk']='mul'; mul.data_type='RGBA'; mul.blend_type='MULTIPLY'; mul.inputs['Factor'].default_value=1.0
    if src: L.new(src,mul.inputs['A'])
    else: mul.inputs['A'].default_value=bc.default_value[:]
    L.new(mx.outputs[0],mul.inputs['B']); L.new(mul.outputs['Result'],bc)
    for i,n in enumerate((ao,mx,mul)): n.location=(bs.location.x-600+200*i,bs.location.y+400)
    print('JKN',mn,'DIST',DIST,'AMT',AMT,'src',src.node.name if src else None, 'users',m.users)
if os.environ.get('OUTB'): bpy.ops.wm.save_as_mainfile(filepath=os.environ['OUTB'],copy=True); print('JKN WROTE')
elif os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('JKN SAVED')
