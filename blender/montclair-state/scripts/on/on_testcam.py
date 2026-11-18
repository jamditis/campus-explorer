import bpy, os
from mathutils import Vector
tx,ty,tz=[float(v) for v in os.environ['TGT'].split(',')]
cx,cy,cz=[float(v) for v in os.environ['POS'].split(',')]
cd=bpy.data.cameras.new('ON_TEST_cam'); cd.lens=float(os.environ.get('LENS','35'))
c=bpy.data.objects.new('ON_TEST_cam',cd); bpy.context.scene.collection.objects.link(c)
c.location=(cx,cy,cz); d=Vector((tx-cx,ty-cy,tz-cz)); c.rotation_euler=d.to_track_quat('-Z','Y').to_euler()
exec(open('scripts/od/od_render.py').read())
