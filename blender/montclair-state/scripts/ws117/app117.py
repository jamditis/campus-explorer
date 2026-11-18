import bpy,sys
src='/workspace/nj-scenes/montclair-state/scripts/ws116/cut116.blend'
with bpy.data.libraries.load(src,link=False) as (fr,to):
    names=[n for n in fr.objects if n.startswith(('WS116_','WS115_E_walk','WS102_CollegeAve_S_curb_E','WS111_CollegeAve_S_E_walk_gap','WS105_Chapin_E_bank_planting_bed_MULCH','WS105_Chapin_E_bank_stair_handrails','WS105_Chapin_E_bank_stair_cheek')) or 'Chapin' in n]
    print('APP names',len(names)); to.objects=names
for o in to.objects:
    if o: bpy.context.scene.collection.objects.link(o)
print('APP', [o.name for o in to.objects if o][:80])
bpy.ops.wm.save_as_mainfile(filepath='/workspace/nj-scenes/montclair-state/scripts/ws117/work117.blend')
print('APP SAVED')
