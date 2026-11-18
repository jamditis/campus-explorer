# Session jd (2026-10-26 ~1:25 AM ET): make jc's joint chips a bit more legible without looking like damage.
# (1) re-runs jc_joint_chips.py with DARK (default 0.46, was 0.35) and MORT (default 0.05, was 0.045);
# (2) adds a small inward bump driven by the same chip mask: new Bump node (Invert, Strength STR default 0.3,
#     Distance 2 mm) chained in front of each material's existing Normal input (seat stone: Bump.001; nosing: Bump).
# Nodes tagged 'jd' (idempotent; REVERT=1 removes the bump and restores jc DARK=0.35/MORT=0.045). SAVE=1 / OUTB=copy.
import bpy, os, runpy
REV=os.environ.get('REVERT')=='1'
sv={k:os.environ.pop(k,None) for k in ('SAVE','OUTB','REVERT')}
os.environ['DARK']='0.35' if REV else os.environ.get('JD_DARK','0.46'); os.environ['MORT']='0.045' if REV else os.environ.get('JD_MORT','0.05')
runpy.run_path('/workspace/nj-scenes/montclair-state/scripts/jc/jc_joint_chips.py',run_name='__main__')
for k,v in sv.items():
    if v is not None: os.environ[k]=v
STR=float(os.environ.get('STR',0.3))
for mn in ['hn_amphi_seat_stone_blocks','ip_amphi_aisle_nosing_worn']:
    nt=bpy.data.materials[mn].node_tree; N=nt.nodes; Lk=nt.links
    bs=next(n for n in N if n.type=='BSDF_PRINCIPLED')
    for n in [n for n in N if n.get('jd')]:
        if n.type=='BUMP' and n.inputs['Normal'].links:
            src=n.inputs['Normal'].links[0].from_socket; N.remove(n); Lk.new(src,bs.inputs['Normal'])
        else: N.remove(n)
    if REV: print('JDC reverted',mn); continue
    d=next(n for n in N if n.get('jc') and n.type=='MATH' and n.operation=='MULTIPLY_ADD')
    mask=d.inputs[0].links[0].from_socket
    prev=bs.inputs['Normal'].links[0].from_socket
    b=N.new('ShaderNodeBump'); b['jd']=1; b.label='jd chip bump'; b.invert=True
    b.inputs['Strength'].default_value=STR; b.inputs['Distance'].default_value=0.002
    Lk.new(mask,b.inputs['Height']); Lk.new(prev,b.inputs['Normal']); Lk.new(b.outputs['Normal'],bs.inputs['Normal'])
    b.location=(bs.location.x-250,bs.location.y-600)
    print('JDC',mn,'DARK',os.environ['DARK'],'MORT',os.environ['MORT'],'bump',STR,'prev',prev.node.name)
if os.environ.get('OUTB'): bpy.ops.wm.save_as_mainfile(filepath=os.environ['OUTB'],copy=True); print('JDC WROTE')
elif os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('JDC SAVED')
