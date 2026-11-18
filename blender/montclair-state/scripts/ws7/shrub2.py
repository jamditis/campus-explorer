import bpy, os
src={n:bpy.data.objects[n] for n in ('Shrub_Azalea','Shrub_Boxwood')}
for n,o in src.items():
  print('SRC',n,o.library,[(m.type,getattr(m,'node_group',None) and m.node_group.name, getattr(m,'texture',None) and m.texture.name) for m in o.modifiers])
  for m in o.modifiers:
    if m.type=='NODES':
      for k in m.keys(): print('  IN',k,m[k])
order=['Shrub_Azalea','Shrub_Boxwood','Shrub_Azalea','Shrub_Boxwood']
for k in range(4):
  o=bpy.data.objects[f'WS7_Shrub_in_ws4_sign_bed_{k}_UNVERIFIED']
  s=src[order[k]]
  o.data=s.data
  for m in s.modifiers:
    nmod=o.modifiers.new(m.name,m.type)
    if m.type=='DISPLACE':
      nmod.texture=m.texture; nmod.strength=m.strength; nmod.mid_level=m.mid_level; nmod.texture_coords=m.texture_coords
    elif m.type=='NODES':
      nmod.node_group=m.node_group
      for key in m.keys():
        try: nmod[key]=m[key]
        except Exception as e: print('KEYFAIL',key,e)
  sc=0.82 if 'Azalea' in order[k] else 0.8
  o.scale=(sc,sc,sc)
  o.name=o.name.replace('Shrub_in',order[k].split('_')[1]+'_in')
  print('SET',o.name,o.data.name,[m.type for m in o.modifiers])
dg=bpy.context.evaluated_depsgraph_get()
for o in bpy.data.collections['WS7_Cole_gable_base_and_bed_20261109'].objects:
  if o.type=='MESH' and 'bed' in o.name:
    e=o.evaluated_get(dg); print('EVAL',o.name,len(e.data.polygons), [round(v,2) for v in o.dimensions])
if os.environ.get('SAVE'): bpy.ops.wm.save_mainfile(); print('SAVED')
import sys
if os.environ.get('SAVE'): sys.exit(0)
sc=bpy.context.scene; sc.camera=bpy.data.objects['WS7_CAM_closeup_ws4_bed_from_S']
sc.render.engine='CYCLES'; sc.cycles.samples=12; sc.render.resolution_x=640; sc.render.resolution_y=360; sc.render.resolution_percentage=100
sc.world=bpy.data.worlds['WP2_World_GOLDEN']
sc.render.image_settings.file_format='JPEG'; sc.render.filepath='/workspace/nj-scenes/montclair-state/scripts/ws7/test_bed.jpg'
bpy.ops.render.render(write_still=True); print('TESTWROTE')
