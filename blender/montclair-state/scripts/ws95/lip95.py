import bpy
p='/workspace/nj-scenes/montclair-state/montclair_state.blend'
names=['Terrain_LiDAR_DTM_1m','WS76_accessible_lot_asphalt_ortho2020_UNVERIFIED_edges','WS79_lot_E_patch_asphalt_ortho2020_UNVERIFIED_edges','WS75_sprague_lot_asphalt_ortho2020_UNVERIFIED_edges','WS80_sprague_lot_fill_asphalt_ortho2020_UNVERIFIED_edges','WS81_lot_seam_underlay_asphalt','WS94_lot_slit_filler_asphalt_UNVERIFIED','WS77_lot_median_island_MULCH_JOEphoto20261112_curb_ortho2020']
with bpy.data.libraries.load(p) as (s,d): d.objects=[n for n in names if n in s.objects]
sc=bpy.context.scene
for o in d.objects: sc.collection.objects.link(o)
for o in list(bpy.data.objects):
    if o.name.startswith(('Cube','Light','Camera')) and o.name!='WS79_CAM_closeup_island_E_end_patch': bpy.data.objects.remove(o)
sc.render.engine='BLENDER_WORKBENCH'
sh=sc.display.shading; sh.light='STUDIO'; sh.color_type='OBJECT'; sh.show_cavity=True
C={'Terrain':(0.3,0.5,0.25,1),'WS81':(1,0.1,0.1,1),'WS79_lot':(0.1,0.3,1,1),'WS76':(0.9,0.9,0.2,1),'WS75':(0.6,0.6,0.6,1),'WS80':(1,0.5,0,1),'WS94':(1,0,1,1),'WS77':(0.4,0.25,0.1,1)}
for o in d.objects:
    for k,c in C.items():
        if o.name.startswith(k): o.color=c
from mathutils import Vector
cd=bpy.data.cameras.new('c'); cam=bpy.data.objects.new('c',cd); sc.collection.objects.link(cam); sc.camera=cam
cam.location=(-210.5,-91.5,129.9); dd=Vector((-218.5,-85,127.0))-cam.location; cam.rotation_euler=dd.to_track_quat('-Z','Y').to_euler(); cd.lens=28
sc.render.resolution_x=1000; sc.render.resolution_y=560
sc.render.filepath='/workspace/nj-scenes/montclair-state/scripts/ws95/lip_probe.png'; bpy.ops.render.render(write_still=True); print("WROTE")
