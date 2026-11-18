import bpy
for o in bpy.data.collections['OG_Schmitt_Hall_mansard_cap_entrance_20261031og'].all_objects:
    print('OG',o.name,o.type,[ (s.material.name if s.material else None) for s in o.material_slots], tuple(round(v,1) for v in o.dimensions))
