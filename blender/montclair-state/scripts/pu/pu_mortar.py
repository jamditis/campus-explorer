# pu: mortar relief on Calcia brick -- shader-only bump from the existing Brick Texture's mortar mask (Fac) so joints read
# recessed at grazing light (strength 0.35, distance 6 mm), on the Calcia wall + skirt brick and the Dickson facade brick.
# Joint depth UNVERIFIED (typical concave/raked joint). Only added where the BSDF Normal input is free; REVERT=1 removes
# the PU_ nodes/links exactly.
import bpy, os
REV=os.environ.get('REVERT')=='1'
for mn in ('PE_Calcia_brick_slot_windows_UNVERIFIED','PE_Calcia_skirt_brick_UNVERIFIED','PE_Dickson_brick_buff_no_red_spandrel_UNVERIFIED'):
    m=bpy.data.materials.get(mn)
    if not m: print('PU_MORTAR missing',mn); continue
    nt=m.node_tree
    for n in [n for n in nt.nodes if n.name.startswith('PU_mortar')]: nt.nodes.remove(n); print('REVERTED_PU_MORTAR',mn)
    if REV: continue
    bt=[n for n in nt.nodes if n.type=='TEX_BRICK']
    bs=[n for n in nt.nodes if n.type=='BSDF_PRINCIPLED']
    print('PU_MORTAR',mn,'brick',[n.name for n in bt],'bsdf',[(n.name,n.inputs['Normal'].is_linked) for n in bs])
    if not bt or not bs: continue
    b=nt.nodes.new('ShaderNodeBump'); b.name='PU_mortar_bump'; b.inputs['Strength'].default_value=0.35; b.inputs['Distance'].default_value=0.006; b.invert=True
    nt.links.new(bt[0].outputs['Fac'],b.inputs['Height'])
    k=0
    for s in bs:
        if not s.inputs['Normal'].is_linked: nt.links.new(b.outputs['Normal'],s.inputs['Normal']); k+=1
    if k==0: nt.nodes.remove(b); print('PU_MORTAR no free normal',mn)
    else: print('PU_MORTAR added',mn,k)
