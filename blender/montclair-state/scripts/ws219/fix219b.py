# ws219 W38b: College Ave asphalt seam at the RHD SE crosswalk. WS67 (gap asphalt bridging main's WS27 carriageway to the
# north-file KY carriageway) uses the darker WS27 asphalt and crosses KY's lighter asphalt surface -> a jagged two-tone
# boundary running diagonally across the lane (z-crossing of two surfaces). Give WS67's asphalt faces KY's material so
# the overlap reads as one surface; the tone change then sits on WS67's straight east edge, a transverse paving joint
# (real resurfacing joints look like this). Material-only change; no geometry moved.
import bpy
o=bpy.data.objects['WS67_CollegeAve_gap_asphalt (bridges WS27 to north-file KY carr'] if 'WS67_CollegeAve_gap_asphalt (bridges WS27 to north-file KY carr' in bpy.data.objects else next(x for x in bpy.data.objects if x.name.startswith('WS67_CollegeAve_gap_asphalt'))
from collections import Counter
print('F219B faces per slot',Counter(p.material_index for p in o.data.polygons),flush=True)
ky=bpy.data.materials['KY_college_ave_asphalt_UNVERIFIED']
if o.material_slots[0].link=='OBJECT': o.material_slots[0].material=ky
else: o.data.materials[0]=ky
print('F219B slot0 ->',o.material_slots[0].material.name,'mesh users',o.data.users,flush=True)
