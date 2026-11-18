"""wt: create/check 4 WIP cams (occlusion + inside-geometry test via scene.ray_cast), save, then render sequentially.
ONLY env: comma list of cam names to (re)render; CAMSPEC env JSON overrides."""
import bpy, os, json, math
from mathutils import Vector
from datetime import datetime
R='/workspace/nj-scenes/montclair-state'
sc=bpy.context.scene; vl=bpy.context.view_layer; dg=bpy.context.evaluated_depsgraph_get()
GROUND=('Context_skirt','Terrain_LiDAR','RZ2_','QW_DTM','WF_east','WT_rich')
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
 'WT_CAM_oblique_tileA_from_NW':[[[12,352,'+34'],[62,288,'+0'],32],[[5,345,'+40'],[62,288,'+0'],32]],
 'WT_CAM_eye_tileA_from_N':[[[64,331,'+1.7'],[58,292,'+1.2'],30],[[60,327,'+1.7'],[58,292,'+1.2'],30],[[70,325,'+1.7'],[58,292,'+1.2'],30]],
 'WT_CAM_eye_tileA_from_E':[[[90,312,'+1.7'],[50,300,'+0.8'],30],[[88,308,'+1.7'],[50,300,'+0.8'],30],[[92,316,'+1.7'],[50,300,'+0.8'],30]],
 'WT_CAM_closeup_apron_seam':[[[69,304,'+3.2'],[59,293,'+0.3'],35],[[67,306,'+3.2'],[59,293,'+0.3'],35],[[72,302,'+3.5'],[60,292,'+0.3'],35]],
}
def z_of(x,y,s):
    g=gz(x,y); return g+float(s)
chk={}
for name,cands in SPEC.items():
    chosen=None; tried=[]
    for (p,t,lens) in cands:
        P=Vector((p[0],p[1],z_of(p[0],p[1],p[2]))); T=Vector((t[0],t[1],z_of(t[0],t[1],t[2])))
        d=(T-P); dist=d.length; d.normalize()
        fh,fo=first(P,d)
        dirs=[Vector(v) for v in ((1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1))]
        near=[first(P,v,2.0)[0] for v in dirs]; inside=sum(1 for n in near if n is not None and n<0.4)
        up=first(P,Vector((0,0,1)),25.0) if 'eye' in name or 'close' in name else (None,None)
        ok=(fh is None or fh>0.8*dist) and inside==0 and up[0] is None
        tried.append({'P':[round(c,2) for c in P],'T':[round(c,2) for c in T],'first_hit':[round(fh,2) if fh else None,fo],'dist':round(dist,1),'inside_dirs':inside,'up':up,'ok':ok})
        if ok: chosen=(P,T,lens); break
    if chosen is None: chosen=(Vector(tried[0]['P']),Vector(tried[0]['T']),cands[0][2]); tried.append('NONE_OK_used_first')
    P,T,lens=chosen
    cam=bpy.data.objects.get(name)
    if not cam:
        cd=bpy.data.cameras.new(name); cam=bpy.data.objects.new(name,cd)
        col=bpy.data.collections.get('WT_richardson_west_LiDAR_UNVERIFIED'); col.objects.link(cam)
    cam['wt_obj']=1; cam.location=P; cam.data.lens=lens; cam.data.clip_start=0.1; cam.data.clip_end=5000
    cam.rotation_euler=(T-P).to_track_quat('-Z','Y').to_euler()
    chk[name]=tried
json.dump(chk,open(f'{R}/data/wt/cam_check.json','w'),indent=1,default=str)
for k,v in chk.items(): print('CAM',k,json.dumps(v,default=str)[:600],flush=True)
bpy.ops.wm.save_mainfile(); print('SAVED',flush=True)
ONLY=[c for c in os.environ.get('ONLY','').split(',') if c] or list(SPEC.keys())
ts=datetime.now().strftime('%Y%m%d-%H%M')
sc.render.engine='CYCLES'; sc.cycles.device='CPU'; sc.cycles.samples=24; sc.cycles.use_denoising=True
sc.render.resolution_x=1280; sc.render.resolution_y=720; sc.render.resolution_percentage=80
sc.render.image_settings.file_format='JPEG'; sc.render.image_settings.quality=90
sc.render.threads_mode='FIXED'; sc.render.threads=4
if os.environ.get('NORENDER'): raise SystemExit(0)
for name in ONLY:
    sc.camera=bpy.data.objects[name]; fp=f'{R}/renders/wip/{ts}_{name}_wt.jpg'; sc.render.filepath=fp
    bpy.ops.render.render(write_still=True); print('DONE',name,fp,datetime.now().strftime('%H:%M:%S'),flush=True)
