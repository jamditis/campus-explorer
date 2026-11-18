# Session iv: the "diagonal facets" on the amphitheater seat tops were not geometry (clay test: smooth, no facets)
# but the Brick Texture's built-in per-brick colour (Color1 white vs Color2 ~0.75) multiplied into the stone,
# i.e. ~25% contrast between neighbouring blocks on top of iq/ir tone variation. This keeps each material's
# mean brick multiplier but cuts the per-brick contrast to ~±3.5% (seats/aisle) and ~±10% (coursed risers).
# Run after ip/iq/ir/is/it/iu. Original colours stored on the node as custom props (iv_c1/iv_c2); REVERT=1 restores. SAVE=1 saves.
import bpy, os
NEW={'hn_amphi_seat_stone_blocks':((0.92,0.90,0.88),(0.86,0.84,0.82)),
     'io_amphi_aisle_stone':((0.96,0.945,0.925),(0.92,0.905,0.885)),
     'hn_amphi_riser_coursed_stone':((0.88,0.85,0.82),(0.72,0.67,0.64))}
for mn,(c1,c2) in NEW.items():
    nt=bpy.data.materials[mn].node_tree
    for q in nt.nodes:
        if q.bl_idname!='ShaderNodeTexBrick': continue
        if 'iv_c1' not in q: q['iv_c1']=list(q.inputs['Color1'].default_value); q['iv_c2']=list(q.inputs['Color2'].default_value)
        if os.environ.get('REVERT'):
            q.inputs['Color1'].default_value=q['iv_c1']; q.inputs['Color2'].default_value=q['iv_c2']
        else:
            q.inputs['Color1'].default_value=(*c1,1); q.inputs['Color2'].default_value=(*c2,1)
        q.label='iv_brick'; print('IV',mn,tuple(round(x,3) for x in q.inputs['Color1'].default_value),tuple(round(x,3) for x in q.inputs['Color2'].default_value))
if os.environ.get('OUTB'): bpy.ops.wm.save_as_mainfile(filepath=os.environ['OUTB'],copy=True); print('IV WROTE')
elif os.environ.get('SAVE'): bpy.ops.wm.save_mainfile(); print('IV SAVED')
