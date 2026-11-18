"""wu: create/check 4 WIP cams, save, render sequentially."""
import bpy, os, json
from mathutils import Vector
from datetime import datetime
R='/workspace/nj-scenes/montclair-state'
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
GROUND=('Context_skirt','Terrain_LiDAR','RZ2_','QW_DTM','WF_east','WT_rich','WU_richardson')
def gz(x,y):
    o=Vector((x,y,300.0))
    for _ in range(30):
        h,loc,nrm,idx,ob,mat=sc.ray_cast(dg,o,Vector((0,0,-1)))
        if not h: return None
        if ob.name.startswith(GROUND): return loc.z
        o=loc-Vector((0,0,0.01))
    return None
def first(o,d,dist=1e4):
    h,loc,nrm,idx,ob,mat=sc.ray_cast(dg,o,d,distance=dist)
    return ((loc-o).length,ob.name) if h else (None,None)
SPEC=json.loads(os.environ.get('CAMSPEC','null')) or {
 'WU_CAM_oblique_tileB_from_NE':[[[145,355,'+40'],[100,285,'+0'],32],[[150,345,'+45'],[100,285,'+0'],32],[[130,350,'+38'],[100,280,'+0'],32]],
 'WU_CAM_eye_tileB_from_N':[[[100,314,'+1.7'],[98,292,'+1.0'],30],[[102,316,'+1.7'],[98,292,'+1.0'],30],[[96,315,'+1.7'],[100,295,'+1.0'],30]],
 'WU_CAM_eye_tileB_from_E':[[[128,278,'+1.7'],[96,275,'+0.8'],30],[[126,290,'+1.7'],[95,280,'+0.8'],30],[[130,265,'+1.8'],[100,270,'+0.6'],30]],
 'WU_CAM_closeup_richardson_NE_apron':[[[84,300,'+3.0'],[92,289,'+0.3'],35],[[86,302,'+3.2'],[94,290,'+0.3'],35],[[80,298,'+3.0'],[90,288,'+0.3'],35]],
}
def z_of(x,y,s):
    g=gz(x,y); 
    if g is None: g=137.5
    return g+float(s)
chk={}
col=bpy.data.collections.get('WU_richardson_reid_LiDAR_UNVERIFIED')
for name,cands in SPEC.items():
    chosen=None; tried=[]
    for (p,t,lens) in cands:
        P=Vector((p[0],p[1],z_of(p[0],p[1],p[2]))); T=Vector((t[0],t[1],z_of(t[0],t[1],t[2])))
        d=(T-P); dist=d.length; d.normalize()
        fh,fo=first(P,d)
        dirs=[Vector(v) for v in ((1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1))]
        near=[first(P,v,2.0)[0] for v in dirs]; inside=sum(1 for n in near if n is not None and n<0.4)
        up=first(P,Vector((0,0,1)),25.0) if ('eye' in name or 'close' in name) else (None,None)
        ok=(fh is None or fh>0.8*dist) and inside==0 and up[0] is None
        tried.append({'P':[round(c,2) for c in P],'T':[round(c,2) for c in T],'first_hit':[round(fh,2) if fh else None,fo],'dist':round(dist,1),'inside_dirs':inside,'up':up,'ok':ok})
        if ok: chosen=(P,T,lens); break
    if chosen is None: chosen=(Vector(tried[0]['P']),Vector(tried[0]['T']),cands[0][2]); tried.append('NONE_OK_used_first')
    P,T,lens=chosen
    cam=bpy.data.objects.get(name)
    if not cam:
        cd=bpy.data.cameras.new(name); cam=bpy.data.objects.new(name,cd); col.objects.link(cam)
    cam['wu_obj']=1; cam.location=P; cam.data.lens=lens; cam.data.clip_start=0.1; cam.data.clip_end=5000
    cam.rotation_euler=(T-P).to_track_quat('-Z','Y').to_euler()
    chk[name]=tried
json.dump(chk,open(f'{R}/data/wu/cam_check.json','w'),indent=1,default=str)
for k,v in chk.items(): print('CAM',k,json.dumps(v,default=str)[:700],flush=True)
bpy.ops.wm.save_mainfile(); print('SAVED',flush=True)
ONLY=[c for c in os.environ.get('ONLY','').split(',') if c] or list(SPEC.keys())
ts=datetime.now().strftime('%Y%m%d-%H%M')
sc.render.engine='CYCLES'; sc.cycles.device='CPU'; sc.cycles.samples=24; sc.cycles.use_denoising=True
sc.render.resolution_x=1280; sc.render.resolution_y=720; sc.render.resolution_percentage=80
sc.render.image_settings.file_format='JPEG'; sc.render.image_settings.quality=90
sc.render.threads_mode='FIXED'; sc.render.threads=4
if os.environ.get('NORENDER'): raise SystemExit(0)
for name in ONLY:
    sc.camera=bpy.data.objects[name]; fp=f'{R}/renders/wip/{ts}_{name}_wu.jpg'; sc.render.filepath=fp
    bpy.ops.render.render(write_still=True); print('DONE',name,fp,datetime.now().strftime('%H:%M:%S'),flush=True)
