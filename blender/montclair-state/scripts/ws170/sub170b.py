import bpy, os
os.environ['ONLY']='9'
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws170/sub170.py').read())
if os.environ.get('FIXB')=='1': exec(open('/workspace/nj-scenes/montclair-state/scripts/ws170/fix170b.py').read())
CAMS=[('closeup_Lot3_S_end_curb_strip_from_SW',(-312.5,-243.5),1.6,(-301.5,-234.5),0.3,28),
      ('closeup_bank_S_end_from_SW',(-317.5,-239.0),1.7,(-306.0,-224.0),0.3,28)]
for lab,(cx,cy),ch,(tx,ty),th,fl in CAMS:
    cz=gz2(cx,cy)+ch; tz=gz2(tx,ty)+th
    cam=bpy.data.objects.new('C',bpy.data.cameras.new('C')); sc.collection.objects.link(cam); cam.data.lens=fl
    cam.location=(cx,cy,cz); d=Vector((tx,ty,tz))-Vector((cx,cy,cz)); cam.rotation_euler=d.to_track_quat('-Z','Y').to_euler()
    sc.camera=cam; sc.render.filepath='/workspace/nj-scenes/montclair-state/scripts/ws170/t_%s_%s.jpg'%(os.environ.get('TAG','x'),lab)
    bpy.ops.render.render(write_still=True); print('WROTE',sc.render.filepath,flush=True)
