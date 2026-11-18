# Session jb part 2: chamfer faces (face attr 'jb_chamfer'=1, set by jb_nosing_chamfer.py) on the seat stone and the aisle
# nosing material get a slightly lighter, noise-broken worn tone: Base Color x (1 + (GAIN-1) * jb_chamfer * noise),
# noise scale 6 mapped 0.35..1.0 (default GAIN_JB 1.08; 1.14 tested, a bit strong), plus roughness unchanged. Frame label 'jb' (idempotent).
# Env GAIN, SAVE=1, OUTB=copy, REVERT=1 (removes jb nodes).
import bpy, os
GAIN=float(os.environ.get('GAIN_JB',1.08))
for mn in ['hn_amphi_seat_stone_blocks','ip_amphi_aisle_nosing_worn']:
    nt=bpy.data.materials[mn].node_tree; N=nt.nodes; Lk=nt.links
    bs=next(n for n in N if n.type=='BSDF_PRINCIPLED')
    old=[n for n in N if n.get('jb')]
    if old:
        src=N[old[0]['jb_src']]; out=src.outputs[old[0]['jb_srcsock']]
        for n in old: N.remove(n)
        Lk.new(out,bs.inputs['Base Color'])
    if os.environ.get('REVERT'): print('JB shade reverted',mn); continue
    bl=bs.inputs['Base Color'].links
    if bl: src=bl[0].from_node; sock=bl[0].from_socket
    else:
        rgb=N.new('ShaderNodeRGB'); rgb.outputs[0].default_value=bs.inputs['Base Color'].default_value; src=rgb; sock=rgb.outputs[0]
    at=N.new('ShaderNodeAttribute'); at.attribute_type='GEOMETRY'; at.attribute_name='jb_chamfer'
    nz=N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value=6.0; nz.inputs['Detail'].default_value=3.0
    mr=N.new('ShaderNodeMapRange'); mr.inputs['From Min'].default_value=0.35; mr.inputs['From Max'].default_value=0.65
    mr.inputs['To Min'].default_value=0.35; mr.inputs['To Max'].default_value=1.0
    m1=N.new('ShaderNodeMath'); m1.operation='MULTIPLY'
    m2=N.new('ShaderNodeMath'); m2.operation='MULTIPLY_ADD'; m2.inputs[1].default_value=GAIN-1.0; m2.inputs[2].default_value=1.0
    vm=N.new('ShaderNodeVectorMath'); vm.operation='MULTIPLY'
    Lk.new(nz.outputs['Fac'],mr.inputs['Value']); Lk.new(at.outputs['Fac'],m1.inputs[0]); Lk.new(mr.outputs['Result'],m1.inputs[1])
    Lk.new(m1.outputs['Value'],m2.inputs[0]); Lk.new(sock,vm.inputs[0]); Lk.new(m2.outputs['Value'],vm.inputs[1]); Lk.new(vm.outputs['Vector'],bs.inputs['Base Color'])
    fr=N.new('NodeFrame'); fr.label='jb'
    nodes=[at,nz,mr,m1,m2,vm,fr]+([src] if src.name.startswith('RGB') and not bl else [])
    for i,n in enumerate(nodes):
        n['jb']=1; n['jb_src']=src.name; n['jb_srcsock']=list(src.outputs).index(sock)
        if n is not fr: n.parent=fr; n.location=(bs.location.x-700+i*150,bs.location.y-900)
    print('JB shade',mn,'gain',GAIN,'src',src.name)
if os.environ.get('OUTB'): bpy.ops.wm.save_as_mainfile(filepath=os.environ['OUTB'],copy=True); print('JB WROTE')
elif os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('JB SAVED')
