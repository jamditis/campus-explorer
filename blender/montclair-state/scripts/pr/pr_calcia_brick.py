# pr: Calcia brick + skirt brick shaders course size: pe ported 0.40 x 0.20 m bricks (read twice too large, per pl/pm notes) ->
# US modular brick 203 x 57 mm + ~10 mm joints (0.213 x 0.067 m pitch), joint 1 cm. Slot pattern untouched.
# Previous values in material prop pr_prev; REVERT=1 restores. UNVERIFIED (brick module from refs calcia_web_05/07 look, not measured).
import bpy, os, json
REV=os.environ.get('REVERT')=='1'
K=('Brick Width','Row Height','Mortar Size')
for mn in ('PE_Calcia_brick_slot_windows_UNVERIFIED','PE_Calcia_skirt_brick_UNVERIFIED'):
    m=bpy.data.materials.get(mn)
    if m is None: continue
    b=m.node_tree.nodes['Brick Texture']
    if REV:
        if 'pr_prev' in m:
            for k,v in json.loads(m['pr_prev']).items(): b.inputs[k].default_value=v
            del m['pr_prev']
        print('PR_BRICK reverted')
    else:
        if 'pr_prev' not in m: m['pr_prev']=json.dumps({k:b.inputs[k].default_value for k in K})
        b.inputs['Brick Width'].default_value=0.213; b.inputs['Row Height'].default_value=0.067; b.inputs['Mortar Size'].default_value=0.01
        print('PR_BRICK set',json.loads(m['pr_prev']))
