import bpy, math, os
from mathutils import Vector
p='/workspace/nj-scenes/montclair-state/montclair_state.blend'
names=['Terrain_LiDAR_DTM_1m','WS77_lot_median_island_MULCH_JOEphoto20261112_curb_ortho2020','WS94_lot_slit_filler_asphalt_UNVERIFIED','Footpaths_OSM','WS76_accessible_lot_asphalt_ortho2020_UNVERIFIED_edges','WS79_lot_E_patch_asphalt_ortho2020_UNVERIFIED_edges','WS75_sprague_lot_asphalt_ortho2020_UNVERIFIED_edges','WS80_sprague_lot_fill_asphalt_ortho2020_UNVERIFIED_edges','WS81_lot_seam_underlay_asphalt']
with bpy.data.libraries.load(p) as (s,d): d.objects=names
sc=bpy.context.scene
for o in d.objects: sc.collection.objects.link(o)
for o in bpy.data.objects:
    if o.name.startswith(('Cube','Light')): bpy.data.objects.remove(o)
sc.render.engine='BLENDER_WORKBENCH'
sh=sc.display.shading; sh.light='STUDIO'; sh.color_type='OBJECT'; sh.show_cavity=True; sh.cavity_type='BOTH'; sh.show_shadows=False
cols={'Footpaths_OSM':(0.95,0.95,0.95,1),'Terrain_LiDAR_DTM_1m':(0.3,0.5,0.25,1),'WS94_lot_slit_filler_asphalt_UNVERIFIED':(1,0.2,0.2,1)}
for o in d.objects: o.color=cols.get(o.name,(0.3,0.3,0.35,1))
cam=bpy.data.objects['Camera']; sc.camera=cam
sc.render.resolution_x=1000; sc.render.resolution_y=800; sc.render.resolution_percentage=100
def shot(tag,loc,tgt,lens=30):
    cam.location=loc; d=Vector(tgt)-Vector(loc); cam.rotation_euler=d.to_track_quat('-Z','Y').to_euler(); cam.data.lens=lens
    sc.render.filepath='/workspace/nj-scenes/montclair-state/scripts/ws94/look_'+tag+'.png'; bpy.ops.render.render(write_still=True); print("WROTE",tag)
pass
shot('hook',(-196,-104,134),(-210,-90,127),30)
shot('obl2',(-190,-110,150),(-205,-82,127),35)
