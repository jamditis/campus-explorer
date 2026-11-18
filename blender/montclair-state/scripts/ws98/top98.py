import bpy,os
p='/workspace/nj-scenes/montclair-state/montclair_state.blend'
names=['Terrain_LiDAR_DTM_1m','WS76_accessible_lot_asphalt_ortho2020_UNVERIFIED_edges','WS79_lot_E_patch_asphalt_ortho2020_UNVERIFIED_edges','WS75_sprague_lot_asphalt_ortho2020_UNVERIFIED_edges','WS80_sprague_lot_fill_asphalt_ortho2020_UNVERIFIED_edges','WS94_lot_slit_filler_asphalt_UNVERIFIED','WS96_lot_E_edge_gap_filler_asphalt_UNVERIFIED','WS77_lot_median_island_MULCH_JOEphoto20261112_curb_ortho2020','WS27_CollegeAve_carriageway_2020ortho','WS27_CollegeAve_curb_right_UNVERIFIED','WS27_CollegeAve_curb_left_UNVERIFIED','Footpaths_OSM','WS73_curb_back_lawn_verge_UNVERIFIED']+os.environ.get('EXTRA','').split(',')
with bpy.data.libraries.load(p) as (s,d): d.objects=[n for n in names if n in s.objects]
sc=bpy.context.scene
for o in d.objects: sc.collection.objects.link(o)
for o in list(bpy.data.objects):
    if o.name in ('Cube','Light','Camera'): bpy.data.objects.remove(o)
sc.render.engine='BLENDER_WORKBENCH'
sh=sc.display.shading; sh.light='FLAT'; sh.color_type='OBJECT'
C={'Terrain':(0.3,0.5,0.25,1),'WS79_lot':(0.1,0.3,1,1),'WS76':(0.9,0.9,0.2,1),'WS75':(0.6,0.6,0.6,1),'WS80':(1,0.5,0,1),'WS94':(1,0,1,1),'WS96':(0,1,1,1),'WS77':(0.4,0.25,0.1,1),'WS27_CollegeAve_carr':(0.15,0.15,0.15,1),'WS27_CollegeAve_curb':(1,1,1,1),'Footpaths':(0.9,0.75,0.6,1),'WS73':(0.2,0.8,0.2,1),'WS98':(1,0.2,0.2,1)}
for o in d.objects:
    for k,c in C.items():
        if o.name.startswith(k): o.color=c
cd=bpy.data.cameras.new('c'); cam=bpy.data.objects.new('c',cd); sc.collection.objects.link(cam); sc.camera=cam
cd.type='ORTHO'; cd.ortho_scale=34; cam.location=(-213,-85,200); cam.rotation_euler=(0,0,0)
sc.render.resolution_x=680; sc.render.resolution_y=680
sc.render.filepath=os.environ.get('OUT','/workspace/nj-scenes/montclair-state/scripts/ws98/top_before.png'); bpy.ops.render.render(write_still=True); print("WROTE")
