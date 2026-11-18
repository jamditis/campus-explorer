import bpy
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws189/alloff189.py').read())
bpy.ops.wm.open_mainfile(filepath='/workspace/nj-scenes/montclair-state/montclair_state_ws218a.blend',load_ui=False)
im=bpy.data.images.get('ortho2020_north.jpg.003'); print('P218 img',im.filepath,im.packed_file is not None,im.size[:] if im else None)
NB=bpy.data.collections['N_buildings']
for o in NB.objects:
    for s in o.material_slots:
        m=s.material
        if m and m.use_nodes and any(n.type=='TEX_IMAGE' and n.image==im for n in m.node_tree.nodes): print('P218 uses',o.name,m.name)
import collections
print('P218 hidden',sum(o.hide_render for o in NB.objects), 'mats new', len([m for m in bpy.data.materials if m.name.endswith(('.001','.002','.003'))]))
xs=[o.location.x for o in NB.objects]
