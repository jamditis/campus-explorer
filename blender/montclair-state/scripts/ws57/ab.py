import bpy,os,sys
from mathutils import Vector
F=os.environ['SRC']; TAG=os.environ['TAG']
N=['Terrain_LiDAR_DTM_1m','Footpaths_OSM','Roads_OSM']
with bpy.data.libraries.load(F,link=False) as (s,d): d.objects=[n for n in N if n in s.objects]
sc=bpy.context.scene
for o in d.objects: sc.collection.objects.link(o)
for o in list(sc.objects):
    if o.name in ('Cube','Camera','Light'): bpy.data.objects.remove(o)
sun=bpy.data.objects.new('S',bpy.data.lights.new('S','SUN')); sun.data.energy=4; sun.rotation_euler=(0.9,0.2,2.2); sc.collection.objects.link(sun)
w=bpy.data.worlds.new('W'); sc.world=w; w.color=(0.4,0.45,0.5)
t=bpy.data.objects['Terrain_LiDAR_DTM_1m']
from mathutils.bvhtree import BVHTree
import bmesh
dg=bpy.context.evaluated_depsgraph_get(); bm=bmesh.new(); bm.from_mesh(t.evaluated_get(dg).to_mesh()); bm.transform(t.matrix_world); T=BVHTree.FromBMesh(bm)
gz=lambda x,y:T.ray_cast(Vector((x,y,300)),Vector((0,0,-1)))[0].z
for nm,loc,tgt,eye,th in [('fpSW',(51,-91),(58,-81),1.6,0.8),('fpTop',(57,-82),(58,-81.9),25,0)]:
    c=bpy.data.objects.new(nm,bpy.data.cameras.new(nm)); sc.collection.objects.link(c)
    L=Vector((loc[0],loc[1],gz(*loc)+eye)); G=Vector((tgt[0],tgt[1],gz(*tgt)+th))
    c.location=L; c.rotation_euler=(G-L).to_track_quat('-Z','Y').to_euler(); c.data.lens=35 if nm=='fpSW' else 24; c.data.clip_start=0.1
    sc.camera=c; sc.render.engine='CYCLES'; sc.cycles.samples=12; sc.render.resolution_x=960; sc.render.resolution_y=540
    sc.render.filepath=f'/workspace/nj-scenes/montclair-state/renders/test/20261111_ws58_{nm}_{TAG}.jpg'; sc.render.image_settings.file_format='JPEG'
    bpy.ops.render.render(write_still=True); print('WROTE',sc.render.filepath)
