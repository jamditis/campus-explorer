import bpy
exec(open('scripts/ni/ni_build.py').read())
sc=bpy.context.scene
sc.render.engine='CYCLES'; sc.cycles.samples=12; sc.cycles.use_denoising=True; sc.render.resolution_x=1280; sc.render.resolution_y=720; sc.render.resolution_percentage=50
sc.camera=bpy.data.objects['NH_CAM_closeup_entrance_door_glazing']; sc.render.image_settings.file_format='JPEG'
def r(tag,hide):
    st=[(bpy.data.objects[n],bpy.data.objects[n].hide_render) for n in hide]
    for o,_ in st: o.hide_render=True
    sc.render.filepath='renders/test_ni/sign_%s.jpg'%tag; bpy.ops.render.render(write_still=True); print('R',tag)
    for o,h in st: o.hide_render=h
r('a_rails',['NG stair S glass rail','NG landing S glass rail','NG bridge W glass rail'])
r('b_sign',['NG bridge LED sign MONTCLAIR STATE UNIVERSITY'])
