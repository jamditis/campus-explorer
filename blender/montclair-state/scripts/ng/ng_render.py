import bpy, os, sys
sc=bpy.context.scene
import os as _o
if _o.environ.get('EXPO'): sc.view_settings.exposure=float(_o.environ['EXPO'])
cams=os.environ['CAMS'].split(','); out=os.environ['OUT']; res=int(os.environ.get('RES','50')); spp=int(os.environ.get('SPP','16'))
sc.render.engine='CYCLES'; sc.cycles.device='CPU'; sc.cycles.samples=spp; sc.cycles.use_denoising=True
sc.render.resolution_x=1280; sc.render.resolution_y=720; sc.render.resolution_percentage=res
sc.render.image_settings.file_format='JPEG'; sc.render.image_settings.quality=90
sc.render.use_persistent_data=True; sc.render.use_stamp=False
roof=[o for o in bpy.data.objects if o.name.startswith(('School of Communication and Media roof','School of Communication and Media barrel','School of Communication and Media eave','School of Communication and Media hip','ek coping caps School','el coping strips School'))]
cut=[o for o in bpy.data.objects if o.name.startswith(('CCOM newsroom studio ceiling','CCOM tower 4a shaft','CCOM_lounge_ceil_','dd_EAST0_ceiling','dd_SOUTH0_ceiling')) or o.name in ('NG double-height ceiling','NG 2F hallway ceiling','NG 2F back hallway ceiling','CCOM_int_lounge_ceil_20261014v','NG connector ceiling','NG link ceiling','dc_ceiling_tiles','CCOM_lounge_east_ceil_20261014jf')]
for c in cams:
    st=[(o,o.hide_render) for o in roof+cut]
    if 'aerial' in c:
        for o in roof+cut: o.hide_render=True
    sc.camera=bpy.data.objects[c]; sc.render.filepath=out.replace('CAM',c); bpy.ops.render.render(write_still=True)
    for o,h in st: o.hide_render=h
    print('RENDERED',sc.render.filepath)
