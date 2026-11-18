# ws174 SUBSET test (main cannot load: 7.7 GB avail, load peaks > 6.3 GB): Normal Ave W S-side objects from main + fix174/fix174b, then WIP renders
import bpy, os, math, numpy as np
from mathutils import Vector
p=os.environ.get('SRC','/workspace/nj-scenes/montclair-state/montclair_state.blend')
PRE=('WS163','WS110','WS172','WS173','WS174','WS166','WS170','WS113_paving_tops_proxy','UTIL170')
with bpy.data.libraries.load(p) as (a,b):
    b.objects=[n for n in a.objects if n.startswith(PRE) and 'skirt' not in n.lower() and 'CAM' not in n and 'hidden' not in n]
sc=bpy.context.scene
for o in b.objects:
    if o is None: continue
    if o.type in ('MESH','CURVE','EMPTY') and o.name not in sc.collection.objects: sc.collection.objects.link(o)
print('LOADED',len([o for o in b.objects if o]),flush=True)
if os.environ.get('NOFIX')!='1':
    exec(open('/workspace/nj-scenes/montclair-state/scripts/ws175/fix175.py').read())
    exec(open('/workspace/nj-scenes/montclair-state/scripts/ws175/fix175b.py').read())
    exec(open('/workspace/nj-scenes/montclair-state/scripts/ws175/fix175c.py').read())
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
CAMS=[('oblique_WS110_S_curb_from_N_high',(-255.6,-250.6),25.0,(-232.7,-283.8),0.0,24),
      ('eye_WS110_S_walk_from_E_toward_junction',(-213.2,-288.4),1.7,(-281.1,-271.3),1.0,26),
      ('eye_NormalAve_S_curb_from_road_W_looking_E',(-289.9,-265.1),1.5,(-212.9,-287.4),0.3,26),
      ('closeup_junction_S_curb_straightened',(-274.5,-269.8),1.6,(-267.6,-275.0),0.1,30),
      ('oblique_NormalAve_W_frontyards_from_N_high',(-312,-236),30.0,(-322,-266),0.0,24)]
OUTD='/workspace/nj-scenes/montclair-state/renders/wip/'; STAMP=os.environ.get('STAMP','20261116-0045'); TAG=os.environ.get('TAG','ws175subset')
only=os.environ.get('ONLY')
for k,(lab,(cx,cy),ch,(tx,ty),th,fl) in enumerate(CAMS):
    if only and str(k) not in only.split(','): continue
    cz=gz2(cx,cy)+ch; tz=gz2(tx,ty)+th
    cam=bpy.data.objects.new('C',bpy.data.cameras.new('C')); sc.collection.objects.link(cam); cam.data.lens=fl; cam.data.clip_end=2000
    cam.location=(cx,cy,cz); d=Vector((tx,ty,tz))-Vector((cx,cy,cz)); cam.rotation_euler=d.to_track_quat('-Z','Y').to_euler()
    sc.camera=cam; sc.render.filepath=OUTD+'%s_%s_%s.jpg'%(STAMP,lab,TAG)
    bpy.ops.render.render(write_still=True); print('WROTE',sc.render.filepath,flush=True)
