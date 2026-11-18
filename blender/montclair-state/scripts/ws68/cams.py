import bpy, os, bmesh
from datetime import datetime
from mathutils import Vector
from mathutils.bvhtree import BVHTree
sc=bpy.context.scene; R='/workspace/nj-scenes/montclair-state'
dg=bpy.context.evaluated_depsgraph_get()
def bvh(n):
    o=bpy.data.objects[n]; e=o.evaluated_get(dg); m=e.to_mesh(); bm=bmesh.new(); bm.from_mesh(m); bm.transform(o.matrix_world); t=BVHTree.FromBMesh(bm); bm.free(); e.to_mesh_clear(); return t
TT=[bvh(n) for n in ('Terrain_LiDAR_DTM_1m','Context_skirt_3DEP_ortho_4km',[o.name for o in bpy.data.objects if o.name.startswith('WS68_RHD_ground')][0])]
def gz(x,y): return max([t.ray_cast(Vector((x,y,200)),Vector((0,0,-1)))[0].z for t in TT if t.ray_cast(Vector((x,y,200)),Vector((0,0,-1)))[0] is not None]+[0])
def cam(n,loc,tgt,lens,eye=None):
    if eye is not None: loc=(loc[0],loc[1],gz(loc[0],loc[1])+eye)
    c=bpy.data.objects.get(n)
    if not c: c=bpy.data.objects.new(n,bpy.data.cameras.new(n)); sc.collection.objects.link(c)
    c.location=loc; c.data.lens=lens; c.data.clip_start=0.1; c.data.clip_end=3000
    c.rotation_euler=(Vector(tgt)-Vector(loc)).to_track_quat('-Z','Y').to_euler()
def camz(n,loc,tgt,lens,eye=None,th=1.0):
    tgt=(tgt[0],tgt[1],gz(tgt[0],tgt[1])+th); cam(n,loc,tgt,lens,eye)
camz('WS49_CAM_oblique_band_trees_SE_from_campus',(0,-20,235),(330,-430),30,None,0.0)
camz('WS49_CAM_eye_band_from_Kasser_frontage',(-205,-125,0),(-480,-330),35,1.6,6.0)
camz('WS49_CAM_eye_band_from_CCOM_east',(35,-60,0),(380,-320),35,1.6,6.0)
camz('WS67_CAM_oblique_CollegeAve_W_to_RHD',(-175,-150,175),(-250,-55),30,None,0.0)
camz('WS67_CAM_eye_CollegeAve_W_from_Kasser_steps',(-212,-70,0),(-268,-50),28,1.7,2.0)
camz('WS67_CAM_eye_CollegeAve_E_from_RHD_entrance',(-266,-56,0),(-214,-66),28,1.7,1.5)
camz('WS67_CAM_closeup_CollegeAve_gap_bridge',(-262,-61,0),(-246,-56),30,2.2,0.3)
