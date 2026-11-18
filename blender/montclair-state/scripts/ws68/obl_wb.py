import bpy,os
import bpy,os
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws68/cams.py').read())
sc=bpy.context.scene
sc.camera=bpy.data.objects[os.environ['CAM']]
for o in bpy.data.objects:
    if o.name.startswith('BD_') or o.name=='Context_ground_beyond_data': o.hide_render=True
hide=[h for h in os.environ.get('HIDE','').split(',') if h]
hl=[h for h in os.environ.get('HL','').split(',') if h]
for o in bpy.data.objects:
    if any(o.name.startswith(h) for h in hide): o.hide_render=True
sc.render.engine='BLENDER_WORKBENCH'
sh=sc.display.shading; sh.light='STUDIO'; sh.color_type=os.environ.get('CT','MATERIAL')
if hl:
    sh.color_type='OBJECT'
    import colorsys
    for i,o in enumerate(bpy.data.objects):
        o.color=(0.6,0.6,0.6,1)
        for j,h in enumerate(hl):
            if o.name.startswith(h): o.color=colorsys.hsv_to_rgb(j/len(hl),1,1)+(1,)
    print('LEGEND',[(h,[round(c,2) for c in colorsys.hsv_to_rgb(j/len(hl),1,1)]) for j,h in enumerate(hl)])
sc.render.resolution_x=1280;sc.render.resolution_y=720;sc.render.resolution_percentage=100
sc.render.filepath=os.environ['OUT'];sc.render.image_settings.file_format='PNG'
bpy.ops.render.render(write_still=True);print('WROTE',os.environ['OUT'])
