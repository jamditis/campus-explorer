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
CAMS=[('oblique_NormalAve_N_side_from_S_high', (np.float64(-178.36), np.float64(-315.07)), 22.0, (np.float64(-171.7), np.float64(-286.84)), 0.0, 24), ('eye_NormalAve_N_walk_from_W_looking_E', (np.float64(-204.63), np.float64(-278.35)), 1.7, (np.float64(-132.73), np.float64(-295.84)), 1.0, 26), ('eye_NormalAve_N_curb_from_road_E_looking_W', (np.float64(-114.46), np.float64(-305.49)), 1.5, (np.float64(-191.35), np.float64(-283.03)), 0.3, 26), ('closeup_NormalAve_N_curb_verge_walk', (np.float64(-172.97), np.float64(-292.2)), 1.6, (np.float64(-163.92), np.float64(-288.68)), 0.0, 30)]
OUTD='/workspace/nj-scenes/montclair-state/renders/wip/'; STAMP=os.environ.get('STAMP',__import__('time').strftime('%Y%m%d-%H%M')); TAG=os.environ.get('TAG','ws175subset')
only=os.environ.get('ONLY')
for k,(lab,(cx,cy),ch,(tx,ty),th,fl) in enumerate(CAMS):
    if only and str(k) not in only.split(','): continue
    cz=gz2(cx,cy)+ch; tz=gz2(tx,ty)+th
    cam=bpy.data.objects.new('C',bpy.data.cameras.new('C')); sc.collection.objects.link(cam); cam.data.lens=fl; cam.data.clip_end=2000
    cam.location=(cx,cy,cz); d=Vector((tx,ty,tz))-Vector((cx,cy,cz)); cam.rotation_euler=d.to_track_quat('-Z','Y').to_euler()
    sc.camera=cam; sc.render.filepath=OUTD+'%s_%s_%s.jpg'%(STAMP,lab,TAG)
    bpy.ops.render.render(write_still=True); print('WROTE',sc.render.filepath,flush=True)
