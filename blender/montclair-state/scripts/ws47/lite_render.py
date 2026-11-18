# ws47: LITE render (memory balloon blocks full-file renders): terrain (with all modifiers) + golden sun/world only, from main.
import bpy, os
from datetime import datetime
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import bmesh
F='/workspace/nj-scenes/montclair-state/montclair_state.blend'; R='/workspace/nj-scenes/montclair-state'
want=['Terrain_LiDAR_DTM_1m','Context_ground_beyond_data','WP2_Sun_GOLDEN']
with bpy.data.libraries.load(F,link=False) as (src,dst):
    dst.objects=[n for n in want if n in src.objects]; dst.worlds=['WP2_World_GOLDEN'] if 'WP2_World_GOLDEN' in src.worlds else []
sc=bpy.context.scene
for o in list(sc.objects): bpy.data.objects.remove(o)
for o in bpy.data.objects:
    if o.name in want: sc.collection.objects.link(o)
if bpy.data.worlds.get('WP2_World_GOLDEN'): sc.world=bpy.data.worlds['WP2_World_GOLDEN']
dg=bpy.context.evaluated_depsgraph_get()
o=bpy.data.objects['Terrain_LiDAR_DTM_1m']; e=o.evaluated_get(dg); m=e.to_mesh(); bm=bmesh.new(); bm.from_mesh(m); bm.transform(o.matrix_world); T=BVHTree.FromBMesh(bm)
def gz(x,y):
    h=T.ray_cast(Vector((x,y,300)),Vector((0,0,-1)))[0]; return h.z if h else 115
def cam(n,loc,tgt,lens,eye=None,th=1.0):
    if eye is not None: loc=(loc[0],loc[1],gz(loc[0],loc[1])+eye)
    tgt=(tgt[0],tgt[1],gz(tgt[0],tgt[1])+th)
    c=bpy.data.objects.new(n,bpy.data.cameras.new(n)); sc.collection.objects.link(c)
    c.location=loc; c.data.lens=lens; c.data.clip_start=0.1; c.data.clip_end=3000
    c.rotation_euler=(Vector(tgt)-Vector(loc)).to_track_quat('-Z','Y').to_euler(); return c
C=[(cam('a',(55,-150,180),(117,-66),26),'oblique_SE_QI_patch_from_SW'),(cam('b',(116,-96,0),(116,-62),24,1.6),'eye_QI_patch_from_S'),
   (cam('c',(84,-48,0),(122,-70),24,1.6),'eye_QI_patch_from_NW'),(cam('d',(108,-80,0),(112,-64),28,3.0,0.0),'closeup_QI_patch_seam')]
ts=datetime.now().strftime('%Y%m%d-%H%M')
sc.render.engine='CYCLES'; sc.cycles.device='CPU'; sc.cycles.samples=16; sc.cycles.use_denoising=True
sc.render.resolution_x=1280; sc.render.resolution_y=720; sc.render.resolution_percentage=60
sc.render.image_settings.file_format='JPEG'; sc.render.image_settings.quality=90; sc.render.threads_mode='FIXED'; sc.render.threads=4
for c,l in C:
    sc.camera=c; fp=f'{R}/renders/wip/{ts}_{l}_LITE_terrain_only_ws47_goldenhour.jpg'; sc.render.filepath=fp
    bpy.ops.render.render(write_still=True); print('WROTE',fp,flush=True)
# hole check: rays down over the old hole area must hit terrain near z~115, not Context_ground at ~0.5
miss=0;tot=0
for x in range(93,141,1):
    for y in range(-73,-59,1):
        tot+=1; h=T.ray_cast(Vector((x+.5,y+.5,300)),Vector((0,0,-1)))[0]
        if h is None or h.z<50: miss+=1
print('L47 hole check misses',miss,'of',tot)
