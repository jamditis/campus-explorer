# partial-scene before/after of limb149 on 3 trees in the day-18 area (eye level 1.7 m), side view + walker scale bar
import bpy, os, json, resource
from mathutils import Vector
P='/workspace/nj-scenes/montclair-state/montclair_state.blend'
MODE=os.environ.get('MODE','before'); TN=os.environ.get('TN','T_PinOak_L1_0060')
idx=[json.loads(l) for l in open('/workspace/nj-scenes/montclair-state/scripts/ws147/bboxes.jsonl')]
with bpy.data.libraries.load(P, link=False) as (src,dst): dst.objects=[TN]
t=dst.objects[0]; sc=bpy.context.scene; sc.collection.objects.link(t)
for n in ('Cube',):
    if n in bpy.data.objects: bpy.data.objects.remove(bpy.data.objects[n])
bpy.context.view_layer.update()
p=t.matrix_world.translation.copy()
# load paving objects whose bbox covers the tree
near=[d['n'] for d in idx if d['t']=='MESH' and not d['n'].startswith('T_') and d['bb'][0]<p.x+8 and d['bb'][1]>p.x-8 and d['bb'][2]<p.y+8 and d['bb'][3]>p.y-8 and (d['bb'][1]-d['bb'][0])<120 and any(k in m.lower() for m in d['mats'] for k in ('concrete','asphalt','walk','lawn','grass'))]
with bpy.data.libraries.load(P, link=False) as (src,dst): dst.objects=near
for o in dst.objects:
    for m in list(o.modifiers): o.modifiers.remove(m)
    sc.collection.objects.link(o)
print("NEAR",near)
if MODE=='after':
    exec(open('/workspace/nj-scenes/montclair-state/scripts/ws149/limb149.py').read())
# 1.8 m human-scale post
bpy.ops.mesh.primitive_cylinder_add(radius=0.15,depth=1.8,location=(p.x+3,p.y-1,p.z+0.9))
cam=bpy.data.objects.new('C',bpy.data.cameras.new('C')); sc.collection.objects.link(cam)
loc=Vector((p.x,p.y-16,p.z+1.7)); tgt=Vector((p.x,p.y,p.z+3)); cam.location=loc; cam.data.lens=30
cam.rotation_euler=(tgt-loc).to_track_quat('-Z','Y').to_euler(); sc.camera=cam
sun=bpy.data.objects.new('S',bpy.data.lights.new('S','SUN')); sun.data.energy=3; sun.rotation_euler=(0.8,0.2,2.4); sc.collection.objects.link(sun)
sc.world=bpy.data.worlds.new('W'); sc.world.color=(0.6,0.7,0.85)
sc.render.engine='CYCLES'; sc.cycles.device='CPU'; sc.cycles.samples=8; sc.render.resolution_x=640; sc.render.resolution_y=400
sc.render.image_settings.file_format='JPEG'
sc.render.filepath='/workspace/nj-scenes/montclair-state/scripts/ws149/prevlimb149_%s_%s.jpg'%(TN,MODE)
bpy.ops.render.render(write_still=True); print("RSS",resource.getrusage(resource.RUSAGE_SELF).ru_maxrss//1024)
