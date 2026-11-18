if os.environ.get('SAVE'): bpy.ops.wm.save_as_mainfile(filepath=os.environ['SAVE'],compress=True); print('SAVED',flush=True)
if os.environ.get('NORENDER')=='1': raise SystemExit
G=np.vstack([np.load('/workspace/nj-scenes/montclair-state/prep/ws175_scurb/las175_2023.npy'),np.load('/workspace/nj-scenes/montclair-state/prep/ws174_scurb/las174.npy')]); G=G[G[:,3]==2]
def gz2(x,y):
    k=(abs(G[:,0]-x)<2)&(abs(G[:,1]-y)<2); return float(np.median(G[k,2])) if k.any() else 118.0
bpy.ops.mesh.primitive_plane_add(size=400,location=(-310,-240,113.0)); g=bpy.context.object; g.name='SUB174_underlay'
m=bpy.data.materials.new('SUB174_under'); m.use_nodes=True; m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(0.10,0.14,0.06,1); g.data.materials.append(m)
w=bpy.data.worlds.new('W'); sc.world=w; w.use_nodes=True; bg=w.node_tree.nodes['Background']
sky=w.node_tree.nodes.new('ShaderNodeTexSky'); w.node_tree.links.new(sky.outputs[0],bg.inputs[0]); bg.inputs[1].default_value=0.35
sun=bpy.data.objects.new('SUN',bpy.data.lights.new('SUN','SUN')); sc.collection.objects.link(sun); sun.data.energy=3.5; sun.rotation_euler=(math.radians(50),0,math.radians(200))
sc.render.engine='CYCLES'; sc.cycles.device='CPU'; sc.cycles.samples=int(os.environ.get('SAMP','20')); sc.cycles.use_denoising=True
sc.render.resolution_x=1280; sc.render.resolution_y=720; sc.render.resolution_percentage=70
sc.render.image_settings.file_format='JPEG'; sc.render.image_settings.quality=88
sc.view_settings.view_transform='AgX'
CAMS=[('closeup_Lot3_aisle_S_drive_lawn_edge',(-299.5,-246.0),1.6,(-308.0,-236.0),0.0,28),('oblique_Lot3_aisle_S_drive_from_SE_high',(-290.0,-258.0),14.0,(-307.0,-236.5),0.0,26)]
OUTD='/workspace/nj-scenes/montclair-state/renders/wip/'; STAMP=os.environ.get('STAMP',__import__('time').strftime('%Y%m%d-%H%M')); TAG=os.environ.get('TAG','ws175subset')
only=os.environ.get('ONLY')
for k,(lab,(cx,cy),ch,(tx,ty),th,fl) in enumerate(CAMS):
    if only and str(k) not in only.split(','): continue
    cz=gz2(cx,cy)+ch; tz=gz2(tx,ty)+th
    cam=bpy.data.objects.new('C',bpy.data.cameras.new('C')); sc.collection.objects.link(cam); cam.data.lens=fl; cam.data.clip_end=2000
    cam.location=(cx,cy,cz); d=Vector((tx,ty,tz))-Vector((cx,cy,cz)); cam.rotation_euler=d.to_track_quat('-Z','Y').to_euler()
    sc.camera=cam; sc.render.filepath=OUTD+'%s_%s_%s.jpg'%(STAMP,lab,TAG)
    bpy.ops.render.render(write_still=True); print('WROTE',sc.render.filepath,flush=True)
