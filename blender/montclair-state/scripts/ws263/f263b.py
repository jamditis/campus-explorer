# ws263 W66 residual (merge208 CHAIN): replace ws262's band-only lawn skin with the widened skin263b.json (prep263b.py: whole
# lawn component(s) between the WS115 walk and Chapin that touch the terrain band; edge 0.1 m off walks/walls/beds and on the
# axis-aligned eval-box edge y -224 / x -230). ws262's skin W edge was a diagonal 0.1 m staircase mid-lawn where single 5 cm
# cells of WS113 showed through (probe262g: 77) = the faint dotted marks in the eye-from-N view. Same material, smooth shading.
import bpy, json
TAG='F263B'; OLD='WS262_W66_lawn_skin_over_WS113_terrain_band'; SN='WS263_W66_lawn_skin_whole_strip_WS115_walk_to_Chapin'
if SN in bpy.data.objects: raise SystemExit('F263B already')
old=bpy.data.objects.get(OLD)
if not old: raise SystemExit('F263B no ws262 skin')
mat=old.data.materials[0]; coll=old.users_collection[0]
d=json.load(open('/workspace/nj-scenes/montclair-state/scripts/ws263/skin263b.json'))
me=bpy.data.meshes.new(SN); me.from_pydata([tuple(v) for v in d['v']],[],[tuple(f) for f in d['f']]); me.shade_smooth(); me.materials.append(mat)
ob=bpy.data.objects.new(SN,me); coll.objects.link(ob)
om=old.data; bpy.data.objects.remove(old); bpy.data.meshes.remove(om)
print(TAG,'replaced',OLD,'->',SN,'v',len(me.vertices),'f',len(me.polygons),'mat',mat.name,'coll',coll.name,flush=True)
