# ws240 self-review fix: the KY clearance bar read brownish in the ws239 close-up; Joe's/Street View photo shows a DARK bar
# (dark grey/black steel, yellow-black ends not visible in the photo). Give the bar + hangers a single-user dark steel material.
import bpy
objs=[o for o in bpy.data.objects if o.name.startswith('KY_rhd_clearance_bar (')]
print('F240A objs',[(o.name[:50],[m.name for m in o.data.materials if m]) for o in objs],flush=True)
mat=bpy.data.materials.get('WS240_clearance_bar_dark_steel') or bpy.data.materials.new('WS240_clearance_bar_dark_steel')
mat.use_nodes=True
b=mat.node_tree.nodes.get('Principled BSDF')
b.inputs['Base Color'].default_value=(0.028,0.029,0.031,1); b.inputs['Metallic'].default_value=0.35; b.inputs['Roughness'].default_value=0.55
mat.diffuse_color=(0.028,0.029,0.031,1)
for o in objs:
    if o.data.users>1: o.data=o.data.copy()
    for i,s in enumerate(o.material_slots):
        print('F240A slot',o.name[:40],i,s.material.name if s.material else None,flush=True)
        s.material=mat
print('F240A done',len(objs),flush=True)
