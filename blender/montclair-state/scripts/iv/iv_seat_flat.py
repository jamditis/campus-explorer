# Session iv: seat tops / aisle treads flat-shaded (exact vertical normals) on the Kasser amphitheater bowl.
# Run after ip/iq/ir/is/it/iu. SAVE=1 saves; REVERT=1 restores smooth on all faces. CLAY=1 (test only) grey diffuse override on the bowl.
import bpy, os
o=bpy.data.objects['Kasser_amphitheater_bowl_hl']; me=o.data
mats=[m.name if m else '' for m in me.materials]
flatm={mats.index(n) for n in ('hn_amphi_seat_stone_blocks','io_amphi_aisle_stone','ir_amphi_seat_arris','io_amphi_stage_concrete') if n in mats}
n=0
for p in me.polygons:
    if os.environ.get('REVERT'): p.use_smooth=True; continue
    if p.material_index in flatm and p.normal.z>0.9995:
        if p.use_smooth: n+=1
        p.use_smooth=False
me.update()
print('IV flat faces set',n)
if os.environ.get('CLAY'):
    cm=bpy.data.materials.new('iv_clay'); cm.use_nodes=True
    cm.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(0.4,0.4,0.4,1)
    for i in range(len(me.materials)): me.materials[i]=cm
if os.environ.get('SAVE'):
    bpy.ops.wm.save_mainfile(); print('IV SAVED')
