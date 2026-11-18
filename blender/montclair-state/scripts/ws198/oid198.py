# ws198: object-ID render (workbench, flat, unique object colours) of the CE camera, same cull/framing as cutrend189
import bpy, os, json, colorsys
from mathutils import Vector
S='/workspace/nj-scenes/montclair-state/scripts/'
exec(open(S+'ws189/alloff189.py').read())
bpy.ops.wm.open_mainfile(filepath=os.environ['FILE'])
for f in os.environ.get('CHAIN','').split(): exec(open(S+f).read())
sc=bpy.context.scene
cx0,cx1,cy0,cy1=map(float,os.environ['CULL'].split(','))
HIDE=['Context_skirt','BD_farfield']
vis=[]
for o in sc.objects:
    if o.type in ('CAMERA','LIGHT'): continue
    if any(o.name.startswith(h) for h in HIDE): o.hide_render=True; continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]; xs=[v.x for v in bb]; ys=[v.y for v in bb]
    if max(xs)<cx0 or min(xs)>cx1 or max(ys)<cy0 or min(ys)>cy1: o.hide_render=True
    if not o.hide_render: vis.append(o)
M={}
for i,o in enumerate(vis):
    r,g,b=((i*37)%256,(i*91+40)%256,(i*173+80)%256)
    o.color=(r/255,g/255,b/255,1); M['%d,%d,%d'%(r,g,b)]=o.name
json.dump(M,open(os.environ['OUTF']+'.json','w'))
cx,cy,cz,tx,ty,tz,fl=[float(a) for a in os.environ['CAM'].split(',')]
c=bpy.data.objects.new('C198',bpy.data.cameras.new('C198')); sc.collection.objects.link(c)
c.location=(cx,cy,cz); c.data.lens=fl; c.data.clip_start=0.1; c.data.clip_end=3000
c.rotation_euler=(Vector((tx,ty,tz))-Vector((cx,cy,cz))).to_track_quat('-Z','Y').to_euler(); sc.camera=c
mt=bpy.data.materials.new('OID198'); mt.use_nodes=True; nt=mt.node_tree; nt.nodes.clear()
oi=nt.nodes.new('ShaderNodeObjectInfo'); em=nt.nodes.new('ShaderNodeEmission'); out=nt.nodes.new('ShaderNodeOutputMaterial')
nt.links.new(oi.outputs['Color'],em.inputs['Color']); nt.links.new(em.outputs[0],out.inputs[0])
bpy.context.view_layer.material_override=mt
sc.render.engine='CYCLES'; sc.cycles.device='CPU'; sc.cycles.samples=1; sc.cycles.use_denoising=False; sc.cycles.max_bounces=0
sc.cycles.filter_width=0.01; sc.view_settings.view_transform='Standard'; sc.view_settings.look='None'; sc.render.film_transparent=True
sc.render.threads_mode='FIXED'; sc.render.threads=4; sc.render.use_simplify=True
for o in vis:
    for ps in getattr(o,'particle_systems',[]): pass
sc.render.resolution_x=1280; sc.render.resolution_y=720; sc.render.resolution_percentage=int(os.environ.get('PCT','55'))
sc.render.image_settings.file_format='PNG'; sc.render.filepath=os.environ['OUTF']; bpy.ops.render.render(write_still=True); print('WROTE',os.environ['OUTF'],flush=True)
