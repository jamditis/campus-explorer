# pf (C): Feliciano LiDAR roof read as patchy red/white (roofc alpha 0.33, 71 % pitched, ov prep). Reuse OW_ccis_roof_tile_ring_GN (already in MAIN) as a
# removable modifier PF_feliciano_roof_tile_ring: pitched verts -> tile, flat -> membrane. Mesh/material unedited. REVERT=1 removes. UNVERIFIED (ref feliciano_commons_08 shows red tile hips).
import bpy,os,sys
R=[o for o in bpy.data.objects if o.name.startswith('Feliciano') and o.name.endswith('roof (LiDAR)')]
print('ROOFOBJ',[o.name for o in R]); r=R[0]; MOD='PF_feliciano_roof_tile_ring'
if MOD in r.modifiers: r.modifiers.remove(r.modifiers[MOD])
if 'UNVERIFIED_pf_tile_ring' in r: del r['UNVERIFIED_pf_tile_ring']
if os.environ.get('REVERT')!='1':
    m=r.modifiers.new(MOD,'NODES'); m.node_group=bpy.data.node_groups['OW_ccis_roof_tile_ring_GN']
    r['UNVERIFIED_pf_tile_ring']='roofc override reused from ow (CCIS): pitched tile, flat membrane'
    print('MODS',[x.name for x in r.modifiers])
if '--save' in sys.argv: bpy.ops.wm.save_mainfile()
print('PF_ROOF_DONE',os.environ.get('REVERT'))
