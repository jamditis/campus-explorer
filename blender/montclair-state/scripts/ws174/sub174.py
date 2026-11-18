# ws174 SUBSET test (main cannot load: 7.7 GB avail, load peaks > 6.3 GB): Normal Ave W S-side objects from main + fix174/fix174b, then WIP renders
import bpy, os, math, numpy as np
from mathutils import Vector
p=os.environ.get('SRC','/workspace/nj-scenes/montclair-state/montclair_state.blend')
PRE=('WS163','WS110','WS172','WS173','WS166','WS170','WS113_paving_tops_proxy','UTIL170')
with bpy.data.libraries.load(p) as (a,b):
    b.objects=[n for n in a.objects if n.startswith(PRE) and 'skirt' not in n.lower() and 'CAM' not in n and 'hidden' not in n]
sc=bpy.context.scene
for o in b.objects:
    if o is None: continue
    if o.type in ('MESH','CURVE','EMPTY'): sc.collection.objects.link(o)
print('LOADED',len([o for o in b.objects if o]),flush=True)
if os.environ.get('NOFIX')!='1':
    exec(open('/workspace/nj-scenes/montclair-state/scripts/ws174/fix174.py').read())
    exec(open('/workspace/nj-scenes/montclair-state/scripts/ws174/fix174b.py').read())
if os.environ.get('SAVE'): bpy.ops.wm.save_as_mainfile(filepath=os.environ['SAVE'],compress=True); print('SAVED',flush=True)
if os.environ.get('NORENDER')=='1': raise SystemExit
D2=np.load('/workspace/nj-scenes/montclair-state/prep/ws163_lot3S/dtm163.npy')[0]
def gz2(x,y):
    i=int((x+350)/0.5); j=int((y+290)/0.5); s=D2[max(j-3,0):j+4,max(i-3,0):i+4]; return float(np.nanmedian(s))
bpy.ops.mesh.primitive_plane_add(size=400,location=(-310,-240,113.0)); g=bpy.context.object; g.name='SUB174_underlay'
m=bpy.data.materials.new('SUB174_under'); m.use_nodes=True; m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(0.10,0.14,0.06,1); g.data.materials.append(m)
w=bpy.data.worlds.new('W'); sc.world=w; w.use_nodes=True; bg=w.node_tree.nodes['Background']
sky=w.node_tree.nodes.new('ShaderNodeTexSky'); w.node_tree.links.new(sky.outputs[0],bg.inputs[0]); bg.inputs[1].default_value=0.35
sun=bpy.data.objects.new('SUN',bpy.data.lights.new('SUN','SUN')); sc.collection.objects.link(sun); sun.data.energy=3.5; sun.rotation_euler=(math.radians(50),0,math.radians(200))
sc.render.engine='CYCLES'; sc.cycles.device='CPU'; sc.cycles.samples=int(os.environ.get('SAMP','20')); sc.cycles.use_denoising=True
sc.render.resolution_x=1280; sc.render.resolution_y=720; sc.render.resolution_percentage=70
sc.render.image_settings.file_format='JPEG'; sc.render.image_settings.quality=88
sc.view_settings.view_transform='AgX'
CAMS=[('oblique_NormalAve_W_S_curb_moved_from_N_high',(-312,-236),30.0,(-322,-266),0.0,24),
      ('eye_NormalAve_W_S_walk_from_E_taper',(-271.0,-275.6),1.7,(-322,-264.0),1.0,26),
      ('eye_NormalAve_W_from_W_end_N_walk',(-344.0,-254.0),1.7,(-300,-266.5),1.0,26),
      ('closeup_S_curb_walk_D2_mouth_new_line',(-318.0,-257.5),1.6,(-326.0,-264.2),0.2,30)]
OUTD='/workspace/nj-scenes/montclair-state/renders/wip/'; STAMP=os.environ.get('STAMP','20261115-2350'); TAG=os.environ.get('TAG','ws174subset')
only=os.environ.get('ONLY')
for k,(lab,(cx,cy),ch,(tx,ty),th,fl) in enumerate(CAMS):
    if only and str(k) not in only.split(','): continue
    cz=gz2(cx,cy)+ch; tz=gz2(tx,ty)+th
    cam=bpy.data.objects.new('C',bpy.data.cameras.new('C')); sc.collection.objects.link(cam); cam.data.lens=fl; cam.data.clip_end=2000
    cam.location=(cx,cy,cz); d=Vector((tx,ty,tz))-Vector((cx,cy,cz)); cam.rotation_euler=d.to_track_quat('-Z','Y').to_euler()
    sc.camera=cam; sc.render.filepath=OUTD+'%s_%s_%s.jpg'%(STAMP,lab,TAG)
    bpy.ops.render.render(write_still=True); print('WROTE',sc.render.filepath,flush=True)
