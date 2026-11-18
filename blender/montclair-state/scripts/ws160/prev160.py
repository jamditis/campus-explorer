# partial preview (balloon fallback): append only objects around Panzer from the given .blend and render the 4 WIP cams
import bpy, json, os, resource
from mathutils import Vector
from datetime import datetime
M='/workspace/nj-scenes/montclair-state/'; P=M+os.environ.get('SRC','montclair_state.blend'); TAG=os.environ.get('TAG','ws160a')
R=[json.loads(l) for l in open(M+'scripts/ws147/bboxes.jsonl')]
X0,X1,Y0,Y1=[float(v) for v in os.environ.get('BOX','-310,-205,-255,-130').split(',')]
def ov(b): return b[0]<X1 and b[1]>X0 and b[2]<Y1 and b[3]>Y0
idx={r['n']:r for r in R}
with bpy.data.libraries.load(P, link=False) as (src,dst):
    want=[]
    for n in src.objects:
        r=idx.get(n)
        if n.startswith(('WS159','WS160')) or n.startswith('WS158_Panzer'): want.append(n); continue
        if r and r['t']=='MESH' and not r['hr'] and 'bb' in r and ov(r['bb']) and '_RETIRED' not in n:
            if n.startswith('Context_skirt') : continue
            want.append(n)
    dst.objects=want; dst.worlds=[w for w in src.worlds if w=='WP2_World_GOLDEN'][:1]
sc=bpy.context.scene
for n in ('Cube','Light'):
    if n in bpy.data.objects: bpy.data.objects.remove(bpy.data.objects[n])
for o in dst.objects:
    if o is None: continue
    if '_RETIRED' in o.name or o.hide_render: continue
    if os.environ.get('LITE','1')=='1':
        for m in list(o.modifiers):
            if m.type in ('NODES','PARTICLE_SYSTEM') and not o.name.startswith(('WS105_bank_shrub','WS160b')): o.modifiers.remove(m)
    if o.name not in sc.collection.objects: sc.collection.objects.link(o)
for o in bpy.data.objects:
    if o.type=='MESH' and o.name not in sc.collection.objects.keys(): o.hide_render=True
if dst.worlds and dst.worlds[0]: sc.world=dst.worlds[0]
sun=bpy.data.objects.new('S',bpy.data.lights.new('S','SUN')); sun.data.energy=3.5; sun.data.angle=0.02; sun.rotation_euler=(0.85,0.1,3.6); sc.collection.objects.link(sun)
print('PREV160 appended',len(want),'RSS',resource.getrusage(resource.RUSAGE_SELF).ru_maxrss//1024,flush=True)
T=bpy.data.objects.get('Terrain_LiDAR_DTM_1m'); Ti=T.matrix_world.inverted()
def gz(x,y):
    ok,loc,n,i=T.ray_cast(Ti@Vector((x,y,400)),Vector((0,0,-1)))
    return (T.matrix_world@loc).z if ok else 122.3
cams=[('oblique_Panzer_gym_roof_from_SE',(-222,-246),(-268,-192),24,46.0,0.0),
      ('eye_PanzerE_from_College_Ave_S',(-227.5,-204),(-238,-171),26,1.7,5.0),
      ('eye_Panzer_N_walk_spur_from_College_Ave',(-226.5,-160),(-236,-170.5),28,1.7,0.5),
      ('closeup_PanzerE_lobby_arches',(-227.0,-178.5),(-236.3,-171.0),28,1.7,4.5)]
only=os.environ.get('ONLY','')
cd=bpy.data.cameras.new('C'); cam=bpy.data.objects.new('C',cd); sc.collection.objects.link(cam); sc.camera=cam
sc.render.use_simplify=True; sc.render.simplify_child_particles_render=0.3; sc.cycles.texture_limit_render='512'; sc.render.simplify_subdivision_render=1
sc.render.engine='CYCLES'; sc.cycles.device='CPU'; sc.cycles.samples=int(os.environ.get('SAMP','24')); sc.cycles.use_denoising=True
sc.render.resolution_x=1280; sc.render.resolution_y=720; sc.render.resolution_percentage=60
sc.render.image_settings.file_format='JPEG'; sc.render.image_settings.quality=90
sc.view_settings.view_transform='AgX' if 'AgX' in [i.identifier for i in sc.view_settings.bl_rna.properties['view_transform'].enum_items] else 'Filmic'
for nm,l,t,lens,eye,th in cams:
    if only and only not in nm: continue
    loc=Vector((l[0],l[1],gz(*l)+eye)); tg=Vector((t[0],t[1],gz(*t)+th))
    cam.location=loc; cd.lens=lens; cd.clip_start=0.1; cd.clip_end=3000
    cam.rotation_euler=(tg-loc).to_track_quat('-Z','Y').to_euler()
    out=M+'renders/wip/%s_%s_%s_partial.jpg'%(datetime.now().strftime('%Y%m%d-%H%M'),nm,TAG)
    sc.render.filepath=out; bpy.ops.render.render(write_still=True)
    print('WROTE',out,'RSS',resource.getrusage(resource.RUSAGE_SELF).ru_maxrss//1024,flush=True)
