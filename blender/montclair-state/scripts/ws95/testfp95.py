import bpy
from mathutils import Vector
p='/workspace/nj-scenes/montclair-state/montclair_state.blend'
names=['Terrain_LiDAR_DTM_1m','Footpaths_OSM','WS76_accessible_lot_asphalt_ortho2020_UNVERIFIED_edges','WS79_lot_E_patch_asphalt_ortho2020_UNVERIFIED_edges','WS75_sprague_lot_asphalt_ortho2020_UNVERIFIED_edges','WS80_sprague_lot_fill_asphalt_ortho2020_UNVERIFIED_edges','WS82_sprague_lane_onesurface_asphalt_ortho2020_UNVERIFIED_edges','WS27_CollegeAve_carriageway_2020ortho']
with bpy.data.libraries.load(p) as (s,d): d.objects=names
sc=bpy.context.scene
for o in d.objects: sc.collection.objects.link(o)
for o in list(bpy.data.objects):
    if o.name.startswith(('Cube','Light')): bpy.data.objects.remove(o)
sc.render.engine='BLENDER_WORKBENCH'
sh=sc.display.shading; sh.light='STUDIO'; sh.color_type='OBJECT'; sh.show_cavity=True; sh.cavity_type='BOTH'
cols={'Footpaths_OSM':(0.95,0.95,0.95,1),'Terrain_LiDAR_DTM_1m':(0.3,0.5,0.25,1)}
for o in d.objects: o.color=cols.get(o.name,(0.3,0.3,0.35,1))
cam=bpy.data.objects['Camera']; sc.camera=cam
sc.render.resolution_x=1000; sc.render.resolution_y=800
import sys; tag=sys.argv[-1]
if tag=='after': exec(open('/workspace/nj-scenes/montclair-state/scripts/ws95/fixfp95.py').read())
def shot(n,loc,tgt,lens=30):
    cam.location=loc; dd=Vector(tgt)-Vector(loc); cam.rotation_euler=dd.to_track_quat('-Z','Y').to_euler(); cam.data.lens=lens
    sc.render.filepath='/workspace/nj-scenes/montclair-state/scripts/ws95/look_'+n+'_'+tag+'.png'; bpy.ops.render.render(write_still=True); print("WROTE",n)
shot('hook',(-196,-104,134),(-210,-90,127),30)
shot('top',(-210,-92,175),(-210,-91.9,125),30)
