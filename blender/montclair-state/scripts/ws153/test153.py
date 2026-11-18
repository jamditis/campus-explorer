import bpy,os
M='/workspace/nj-scenes/montclair-state/'
for o in list(bpy.data.objects): bpy.data.objects.remove(o)
with bpy.data.libraries.load(M+'montclair_state_ws152f.blend',link=False) as (src,dst):
    dst.objects=[n for n in src.objects if ('freeman' in n.lower() and '_RETIRED' not in n) or n.startswith('WS152_CAM')]
for o in dst.objects:
    if o: bpy.context.scene.collection.objects.link(o)
print('TEST153 loaded',len(dst.objects))
os.environ['OUT153']='/tmp/test153.blend'
exec(open(M+'scripts/ws153/fix153.py').read()); exec(open(M+'scripts/ws153/probe153.py').read())
sc=bpy.context.scene; sc.render.engine='CYCLES'; sc.cycles.samples=8; sc.render.resolution_x=768; sc.render.resolution_y=432
w=bpy.data.worlds.new('w'); w.color=(0.6,0.65,0.7); sc.world=w
sun=bpy.data.objects.new('sun',bpy.data.lights.new('sun','SUN')); sun.rotation_euler=(0.8,0.2,-0.9); sc.collection.objects.link(sun)
for cn,fn in [('WS152_CAM_eye_Freeman_W_facade_2019match','prev153_eye_W.jpg'),('WS152_CAM_closeup_Freeman_W_bay','prev153_closeup_W.jpg')]:
    sc.camera=bpy.data.objects[cn]; sc.render.filepath=M+'scripts/ws153/'+fn; sc.render.image_settings.file_format='JPEG'; bpy.ops.render.render(write_still=True)
print('TEST153 done')
