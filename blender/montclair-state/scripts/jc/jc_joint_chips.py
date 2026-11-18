# Session jc (2026-10-26 ~12:45 AM ET): small chips / arris breaks where the block joints meet the bench-front and
# aisle-step nosings of the Kasser amphitheater (shader only; seat stone + aisle nosing materials).
# Mask = edge zone (jb_chamfer faces OR seat front band it_rowpos < ~0.03, seat material only)
#      x near-joint zone (2nd Brick Texture on the same UVMap / offset 0.5 / freq 2, wider mortar MORT -> Fac = 1 near joints)
#      x per-joint selection (object-space noise scale 2.2, ~half of the joints chipped)
#      x ragged edge (object-space noise scale 70).
# Effect: Base Color x (1 - DARK*mask) (shadowed broken arris) and a small negative bump. Frame 'jc' (idempotent; REVERT=1 removes).
# Env DARK (default 0.28), MORT (default 0.045 in UV units, ~8 cm along a ~1.8 m block), SAVE=1, OUTB=copy.
import bpy, os
DARK=float(os.environ.get('DARK',0.28)); MORT=float(os.environ.get('MORT',0.045))
for mn in ['hn_amphi_seat_stone_blocks','ip_amphi_aisle_nosing_worn']:
    nt=bpy.data.materials[mn].node_tree; N=nt.nodes; Lk=nt.links
    bs=next(n for n in N if n.type=='BSDF_PRINCIPLED')
    old=[n for n in N if n.get('jc')]
    if old:
        src=N[old[0]['jc_src']]; out=src.outputs[old[0]['jc_srcsock']]
        for n in old: N.remove(n)
        Lk.new(out,bs.inputs['Base Color'])
    if os.environ.get('REVERT'): print('JCC reverted',mn); continue
    bl=bs.inputs['Base Color'].links[0]; src=bl.from_node; sock=bl.from_socket
    new=[]
    def nn(t,**kw):
        n=N.new(t); new.append(n)
        for k,v in kw.items(): setattr(n,k,v)
        return n
    uv=nn('ShaderNodeUVMap'); uv.uv_map='UVMap'
    br=nn('ShaderNodeTexBrick'); br.offset=0.5; br.offset_frequency=2; br.squash=1.0; br.squash_frequency=2
    br.inputs['Scale'].default_value=1.0; br.inputs['Mortar Size'].default_value=MORT; br.inputs['Mortar Smooth'].default_value=0.3
    br.inputs['Brick Width'].default_value=1.0; br.inputs['Row Height'].default_value=1.0
    Lk.new(uv.outputs['UV'],br.inputs['Vector'])
    ch=nn('ShaderNodeAttribute'); ch.attribute_type='GEOMETRY'; ch.attribute_name='jb_chamfer'
    edge=ch.outputs['Fac']
    if mn=='hn_amphi_seat_stone_blocks':
        rp=nn('ShaderNodeAttribute'); rp.attribute_type='GEOMETRY'; rp.attribute_name='it_rowpos'
        mb=nn('ShaderNodeMapRange'); mb.interpolation_type='SMOOTHSTEP'; mb.inputs['From Min'].default_value=0.0; mb.inputs['From Max'].default_value=0.03
        mb.inputs['To Min'].default_value=1.0; mb.inputs['To Max'].default_value=0.0
        Lk.new(rp.outputs['Fac'],mb.inputs['Value'])
        mx=nn('ShaderNodeMath',operation='MAXIMUM'); Lk.new(ch.outputs['Fac'],mx.inputs[0]); Lk.new(mb.outputs['Result'],mx.inputs[1]); edge=mx.outputs['Value']
    tc=nn('ShaderNodeTexCoord')
    s1=nn('ShaderNodeTexNoise'); s1.inputs['Scale'].default_value=2.2; s1.inputs['Detail'].default_value=1.0; Lk.new(tc.outputs['Object'],s1.inputs['Vector'])
    m1=nn('ShaderNodeMapRange'); m1.inputs['From Min'].default_value=0.50; m1.inputs['From Max'].default_value=0.56; Lk.new(s1.outputs['Fac'],m1.inputs['Value'])
    s2=nn('ShaderNodeTexNoise'); s2.inputs['Scale'].default_value=70.0; s2.inputs['Detail'].default_value=4.0; Lk.new(tc.outputs['Object'],s2.inputs['Vector'])
    m2=nn('ShaderNodeMapRange'); m2.inputs['From Min'].default_value=0.40; m2.inputs['From Max'].default_value=0.55; Lk.new(s2.outputs['Fac'],m2.inputs['Value'])
    a=nn('ShaderNodeMath',operation='MULTIPLY'); Lk.new(edge,a.inputs[0]); Lk.new(br.outputs['Fac'],a.inputs[1])
    b=nn('ShaderNodeMath',operation='MULTIPLY'); Lk.new(a.outputs['Value'],b.inputs[0]); Lk.new(m1.outputs['Result'],b.inputs[1])
    c=nn('ShaderNodeMath',operation='MULTIPLY'); Lk.new(b.outputs['Value'],c.inputs[0]); Lk.new(m2.outputs['Result'],c.inputs[1])
    d=nn('ShaderNodeMath',operation='MULTIPLY_ADD'); d.inputs[1].default_value=-DARK; d.inputs[2].default_value=1.0; Lk.new(c.outputs['Value'],d.inputs[0])
    vm=nn('ShaderNodeVectorMath',operation='MULTIPLY'); Lk.new(sock,vm.inputs[0]); Lk.new(d.outputs['Value'],vm.inputs[1]); Lk.new(vm.outputs['Vector'],bs.inputs['Base Color'])
    fr=nn('NodeFrame'); fr.label='jc'
    for i,n in enumerate(new):
        n['jc']=1; n['jc_src']=src.name; n['jc_srcsock']=list(src.outputs).index(sock)
        if n is not fr: n.parent=fr; n.location=(bs.location.x-900+i*140,bs.location.y-1250)
    print('JCC chips',mn,'dark',DARK,'mort',MORT,'src',src.name)
if os.environ.get('OUTB'): bpy.ops.wm.save_as_mainfile(filepath=os.environ['OUTB'],copy=True); print('JCC WROTE')
elif os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('JCC SAVED')
