import bpy, os, sys
from mathutils import Vector
REV=os.environ.get('REVERT')=='1'; CN='PL_CAM_closeup_feliciano_roof_hips'; CO='PL_cams_20261101pl'
if CN in bpy.data.objects:
    d=bpy.data.objects[CN].data; bpy.data.objects.remove(bpy.data.objects[CN]); bpy.data.cameras.remove(d)
if CO in bpy.data.collections: bpy.data.collections.remove(bpy.data.collections[CO])
if not REV:
    col=bpy.data.collections.new(CO); bpy.context.scene.collection.children.link(col)
    cd=bpy.data.cameras.new(CN); cd.lens=float(os.environ.get('LENS','40')); o=bpy.data.objects.new(CN,cd); col.objects.link(o)
    o.location=Vector(tuple(float(x) for x in os.environ.get('LOC','-272,236,186').split(',')))
    t=Vector(tuple(float(x) for x in os.environ.get('TGT','-232,196,156').split(',')))
    o.rotation_euler=(t-o.location).to_track_quat('-Z','Y').to_euler(); o['UNVERIFIED_pl']='roof hip close-up cam'
    print('PL_CAM',o.location[:],'->',t[:])
if os.environ.get('SAVEAS'): bpy.ops.wm.save_as_mainfile(filepath=os.environ['SAVEAS'],copy=True)
if '--save' in sys.argv: bpy.ops.wm.save_mainfile(); print('SAVED')
