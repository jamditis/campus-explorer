# Session iy part 2: the wedges stay dark with up-facing custom normals alone (probe_iy: they sit in the notch where a
# half-step meets a full row, so the sun is blocked by the adjoining block = a real cast shadow on a jagged triangle).
# Shader fix: the riser + seat materials read the face attribute 'iy_wedge' (set by iy_wedge_normals.py) and lift the
# base colour on those faces only (x GAIN, default 1.9) so the notch reads as a soft shaded cheek instead of a black wedge.
# Node frame label 'iy' (idempotent). Run after iy_wedge_normals.py. Env GAIN, SAVE=1, OUTB=copy, REVERT=1 (removes iy nodes).
import bpy, os
GAIN=float(os.environ.get('GAIN',1.9))
for mn in ['hn_amphi_riser_coursed_stone','hn_amphi_seat_stone_blocks']:
    nt=bpy.data.materials[mn].node_tree; N=nt.nodes; Lk=nt.links
    bs=next(n for n in N if n.type=='BSDF_PRINCIPLED')
    old=[n for n in N if n.get('iy')]
    if old:
        src=N[old[0]['iy_src']] ; out=src.outputs[old[0]['iy_srcsock']]
        for n in old: N.remove(n)
        Lk.new(out,bs.inputs['Base Color'])
    if os.environ.get('REVERT'): print('IY shade reverted',mn); continue
    l=bs.inputs['Base Color'].links[0]; src=l.from_node; sock=l.from_socket
    at=N.new('ShaderNodeAttribute'); at.attribute_type='GEOMETRY'; at.attribute_name='iy_wedge'
    mr=N.new('ShaderNodeMapRange'); mr.inputs['To Min'].default_value=1.0; mr.inputs['To Max'].default_value=GAIN
    vm=N.new('ShaderNodeVectorMath'); vm.operation='MULTIPLY'
    Lk.new(at.outputs['Fac'],mr.inputs['Value']); Lk.new(sock,vm.inputs[0]); Lk.new(mr.outputs['Result'],vm.inputs[1]); Lk.new(vm.outputs['Vector'],bs.inputs['Base Color'])
    fr=N.new('NodeFrame'); fr.label='iy'
    for i,n in enumerate((at,mr,vm,fr)):
        n['iy']=1; n['iy_src']=src.name; n['iy_srcsock']=list(src.outputs).index(sock)
        if n is not fr: n.parent=fr; n.location=(bs.location.x-500+i*160,bs.location.y-700)
    print('IY shade',mn,'gain',GAIN,'src',src.name)
if os.environ.get('OUTB'): bpy.ops.wm.save_as_mainfile(filepath=os.environ['OUTB'],copy=True); print('IY WROTE')
elif os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('IY SAVED')
