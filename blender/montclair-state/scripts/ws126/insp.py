import bpy
with bpy.data.libraries.load('/workspace/nj-scenes/assets/campus_assets.blend') as (df,dt):
    print('LIBOBJ',[n for n in df.objects if 'Shrub' in n or 'Bush' in n or 'Leaf' in n or 'Pachy' in n or 'Ground' in n])
for o in bpy.data.objects:
    if o.name.startswith(('WS116_Chapin_W_bed','ShrubLeaf')) or (o.name.startswith('WS125_bed_shrub_') and o.name.endswith(('00_Boxwood_UNVERIFIEDspecies',))):
        print('OBJ',o.name,o.type,tuple(round(v,2) for v in o.location),tuple(round(v,2) for v in o.dimensions),len(o.data.polygons) if o.type=='MESH' else '',[m.type+':'+(m.node_group.name if m.type=='NODES' and m.node_group else '') for m in o.modifiers],[m.name for m in o.data.materials] if o.type=='MESH' else '')
import collections
print('CNT',collections.Counter(o.name.split('_')[-2] for o in bpy.data.objects if o.name.startswith('WS125_bed_shrub_')))
print('GC',sum(1 for o in bpy.data.objects if o.name.startswith('WS125_bed_groundcover_')))
