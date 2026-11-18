# ws170 light SUBSET render (main cannot load under the memory balloon): Normal Ave W / Lot 3 S objects from main + fix170 utility line.
import bpy, os, math, numpy as np
from mathutils import Vector
p='/workspace/nj-scenes/montclair-state/montclair_state.blend'
PRE=('WS163','WS110','WS162','WS164','WS165','WS166','WS167','WS169')
with bpy.data.libraries.load(p) as (a,b):
    b.objects=[n for n in a.objects if n.startswith(PRE) and 'skirt' not in n and 'CAM' not in n and 'hidden' not in n]
sc=bpy.context.scene
for o in b.objects:
    if o is None: continue
    if o.type in ('MESH','CURVE'): sc.collection.objects.link(o)
print('LOADED',len([o for o in b.objects if o]),flush=True)
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws170/fix170.py').read())
D2=np.load('/workspace/nj-scenes/montclair-state/prep/ws163_lot3S/dtm163.npy')[0]
def gz2(x,y):
    i=int((x+350)/0.5); j=int((y+290)/0.5); s=D2[max(j-3,0):j+4,max(i-3,0):i+4]; return float(np.nanmedian(s))
# ground underlay so nothing floats over void (dark lawn plane at DTM min-0.3)
bpy.ops.mesh.primitive_plane_add(size=400,location=(-310,-240,113.5)); g=bpy.context.object; g.name='SUB170_underlay'
m=bpy.data.materials.new('SUB170_under'); m.diffuse_color=(0.10,0.14,0.06,1); m.use_nodes=True; m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(0.10,0.14,0.06,1); g.data.materials.append(m)
w=bpy.data.worlds.new('W'); sc.world=w; w.use_nodes=True; bg=w.node_tree.nodes['Background']
sky=w.node_tree.nodes.new('ShaderNodeTexSky'); w.node_tree.links.new(sky.outputs[0],bg.inputs[0]); bg.inputs[1].default_value=0.35
sun=bpy.data.objects.new('SUN',bpy.data.lights.new('SUN','SUN')); sc.collection.objects.link(sun); sun.data.energy=3.5; sun.rotation_euler=(math.radians(50),0,math.radians(200))
sc.render.engine='CYCLES'; sc.cycles.device='CPU'; sc.cycles.samples=24; sc.cycles.use_denoising=True
sc.render.resolution_x=1280; sc.render.resolution_y=720; sc.render.resolution_percentage=70
sc.render.image_settings.file_format='JPEG'; sc.render.image_settings.quality=88
sc.view_settings.view_transform='AgX'
CAMS=[('oblique_NormalAve_W_utility_line_from_SW_high',(-346,-289),34.0,(-310,-262),0.0,24),
      ('eye_NormalAve_W_S_walk_poles_from_E',(-276.5,-274.0),1.7,(-322,-262.5),6.0,26),
      ('eye_NormalAve_W_from_W_end_N_walk',(-344.0,-254.0),1.7,(-300,-266.5),7.0,26),
      ('closeup_pole_crossarm_x-317_from_NW',(-331.0,-251.0),1.6,(-317.5,-263.5),6.5,24)]
OUTD='/workspace/nj-scenes/montclair-state/renders/wip/'; STAMP=os.environ.get('STAMP','20261115-2000')
only=os.environ.get('ONLY')
for k,(lab,(cx,cy),ch,(tx,ty),th,fl) in enumerate(CAMS):
    if only and str(k)!=only: continue
    cz=gz2(cx,cy)+ch; tz=gz2(tx,ty)+th
    cam=bpy.data.objects.new('C',bpy.data.cameras.new('C')); sc.collection.objects.link(cam); cam.data.lens=fl; cam.data.clip_end=2000
    cam.location=(cx,cy,cz); d=Vector((tx,ty,tz))-Vector((cx,cy,cz)); cam.rotation_euler=d.to_track_quat('-Z','Y').to_euler()
    sc.camera=cam; sc.render.filepath=OUTD+'%s_%s_ws170subset.jpg'%(STAMP,lab)
    bpy.ops.render.render(write_still=True); print('WROTE',sc.render.filepath,flush=True)
