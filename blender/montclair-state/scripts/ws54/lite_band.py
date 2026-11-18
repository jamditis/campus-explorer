# LITE fallback WIP: terrain + skirt (plain material) + band trees + MID street trees only. Clearly labelled LITE.
import bpy, os, sys
F='/workspace/nj-scenes/montclair-state/montclair_state.blend'
with bpy.data.libraries.load(F,link=False) as (s,d):
    names=['Terrain_LiDAR_DTM_1m','WS48_band_street_trees_OSM_lowLOD','WP2_Sun_GOLDEN']
    names+=[n for n in s.objects if n.startswith('MID_stree')][:400]
    d.objects=[n for n in names if n in s.objects]; d.worlds=['WP2_World_GOLDEN']
sc=bpy.context.scene
for o in d.objects: sc.collection.objects.link(o); o.hide_render=False
plain=bpy.data.materials.new('LITE_plain_ground'); plain.use_nodes=True
plain.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(0.12,0.11,0.07,1)
b=bpy.data.objects['WS48_band_street_trees_OSM_lowLOD']; me=b.data
sa=me.attributes.get('tree_scale')
pts=[(v.co.x,v.co.y,v.co.z-0.8*(sa.data[i].value if sa else 1.0)) for i,v in enumerate(me.vertices)]
near=sorted(pts,key=lambda p:(p[0]-245.7)**2+(p[1]+246.8)**2)[:12]; G=sorted(p[2] for p in near)[len(near)//2]
print('LITE ground z',round(G,2),'band verts',len(pts))
bpy.ops.mesh.primitive_plane_add(size=3000,location=(0,0,G-0.05)); g=bpy.context.object; g.data.materials.append(plain)
for m in list(bpy.data.images):
    if m.size[0]*m.size[1]>4096*4096: print('big image',m.name)
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws49/render49.py').read().split("base=bpy.data.objects.get('Sun')")[0].replace("'Terrain_LiDAR_DTM_1m','Context_skirt_3DEP_ortho_4km'","'Terrain_LiDAR_DTM_1m',"))
cam('WS49_CAM_closeup_band_crowns',(210.7,-271.8,G+8),(245.7,-246.8,G+4),35)
cam('WS49_CAM_oblique_band_trees_SE_from_campus',(0,-20,235),(330,-430,G),30)
sc.world=bpy.data.worlds['WP2_World_GOLDEN']
from datetime import datetime
ts=datetime.now().strftime('%Y%m%d-%H%M')
for cname,label in [('WS49_CAM_closeup_band_crowns','closeup_band_crowns'),('WS49_CAM_oblique_band_trees_SE_from_campus','oblique_band_trees_SE_from_campus')]:
    sc.camera=bpy.data.objects[cname]; sc.render.engine='CYCLES'; sc.cycles.device='CPU'; sc.cycles.samples=12; sc.cycles.use_denoising=True
    sc.render.resolution_x=1280; sc.render.resolution_y=720; sc.render.resolution_percentage=50; sc.cycles.texture_limit_render='1024'
    sc.render.threads_mode='FIXED'; sc.render.threads=4
    sc.render.image_settings.file_format='JPEG'
    sc.render.filepath=f"/workspace/nj-scenes/montclair-state/renders/wip/{ts}_{label}_LITE_trees_terrain_only_ws54_goldenhour.jpg"
    bpy.ops.render.render(write_still=True); print('WROTE',sc.render.filepath,flush=True)
