"""ws: (1) read-only inventory of band x40-155,y245-320 (bbox + evaluated mesh, no ray_cast) -> data/ws/inventory_raw.json
(2) MAIN-only pack export 20261108a into stage via save_as_mainfile(copy=True). Live file never overwritten."""
import bpy, os, json, numpy as np, time, re, hashlib
from mathutils import Vector
R='/workspace/nj-scenes/montclair-state'; t0=time.time()
LIVE=bpy.data.filepath
assert LIVE.endswith('montclair-state/montclair_state.blend')
X0,X1,Y0,Y1=40,155,245,320
g=np.load(R+'/data/wo/chm_grid_sw_1m.npz'); dtm=g[[k for k in g.files if k.endswith('dtm')][0]]
def D(x,y):
    ix=int(np.floor(x-40)); iy=int(np.floor(y-140))
    if 0<=iy<dtm.shape[0] and 0<=ix<dtm.shape[1]:
        v=dtm[iy,ix]; return None if np.isnan(v) else float(v)
    return None
OSM=['313027428','313027436','313027437','546643369','552441882','546643370','313028549']
KEY=re.compile(r'(walk|road|street|path|apron|skirt|terrain|lidar|patch|curb|stair|step|plaza|lawn|ground|context|'+'|'.join(OSM)+')',re.I)
deps=bpy.context.evaluated_depsgraph_get()
inv=[]
for o in bpy.data.objects:
    if o.type not in ('MESH','CURVE','EMPTY') : continue
    try: bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    except Exception: continue
    xs=[v.x for v in bb]; ys=[v.y for v in bb]; zs=[v.z for v in bb]
    if max(xs)<X0 or min(xs)>X1 or max(ys)<Y0 or min(ys)>Y1: continue
    big = (max(xs)-min(xs))>400 or (max(ys)-min(ys))>400
    cx=(min(xs)+max(xs))/2; cy=(min(ys)+max(ys))/2
    r={'name':o.name,'type':o.type,'colls':[c.name for c in o.users_collection],
       'bbox':[round(min(xs),2),round(max(xs),2),round(min(ys),2),round(max(ys),2),round(min(zs),2),round(max(zs),2)],
       'lib':o.library.filepath if o.library else None,'inst':o.instance_collection.name if o.instance_collection else None,
       'parent':o.parent.name if o.parent else None,'mods':[m.type for m in getattr(o,'modifiers',[])][:8],
       'dtm_at_center':D(cx,cy)}
    if o.type=='MESH' and KEY.search(o.name):
        try:
            ev=o.evaluated_get(deps); me=ev.to_mesh()
            n=len(me.vertices)
            if n<2_000_000:
                co=np.empty(n*3,dtype=np.float32); me.vertices.foreach_get('co',co); co=co.reshape(-1,3)
                M=np.array(o.matrix_world); co=co@M[:3,:3].T+M[:3,3]
                m=(co[:,0]>=X0)&(co[:,0]<X1)&(co[:,1]>=Y0)&(co[:,1]<Y1)
                c=co[m]
                if len(c):
                    ix=np.floor(c[:,0]-40).astype(int); iy=np.floor(c[:,1]-140).astype(int)
                    ok=(ix>=0)&(ix<dtm.shape[1])&(iy>=0)&(iy<dtm.shape[0])
                    dz=np.full(len(c),np.nan); dz[ok]=c[ok,2]-dtm[iy[ok],ix[ok]]
                    f=np.isfinite(dz)
                    r['band_verts']=int(len(c)); r['eval_verts']=n
                    if f.any():
                        d=dz[f]; r['dz_obj_minus_dtm']={'med':round(float(np.median(d)),2),'p5':round(float(np.percentile(d,5)),2),'p95':round(float(np.percentile(d,95)),2),'min':round(float(d.min()),2),'max':round(float(d.max()),2)}
                    r['band_xy_extent']=[round(float(c[:,0].min()),1),round(float(c[:,0].max()),1),round(float(c[:,1].min()),1),round(float(c[:,1].max()),1)]
            ev.to_mesh_clear()
        except Exception as e: r['eval_err']=str(e)[:100]
    elif not big:
        d=D(cx,cy)
        if d is not None: r['bbox_minz_minus_dtm']=round(min(zs)-d,2)
    inv.append(r)
os.makedirs(R+'/data/ws',exist_ok=True)
json.dump({'band':[X0,X1,Y0,Y1],'n':len(inv),'objs':len(bpy.data.objects),'items':inv},open(R+'/data/ws/inventory_raw.json','w'),indent=0)
print('INVENTORY_DONE',len(inv),round(time.time()-t0,1),flush=True)
# ---- pack export ----
STAGE="/workspace/export_20261108a/montclair_state_scene/nj-scenes/montclair-state"
os.makedirs(STAGE,exist_ok=True); OUT=os.path.join(STAGE,"montclair_state.blend")
libs=[]
for lib in bpy.data.libraries:
    libs.append([lib.filepath, os.path.normpath(bpy.path.abspath(lib.filepath)), lib.parent.filepath if lib.parent else None])
json.dump(libs,open(R+'/data/ws/libs.json','w'),indent=0)
miss=0
for img in bpy.data.images:
    if img.packed_file: continue
    if img.source in ('FILE','SEQUENCE','TILED') and img.filepath and not os.path.exists(bpy.path.abspath(img.filepath)): miss+=1
print('MISS_COUNT',miss)
try: bpy.ops.file.pack_all(); print('pack_all OK')
except Exception as e: print('pack_all FAIL',e)
for lib in bpy.data.libraries:
    if lib.parent is not None: continue
    ap=os.path.normpath(bpy.path.abspath(lib.filepath)).replace('\\','/'); name=os.path.basename(ap)
    if '/assets/' in ap:
        new='//../assets/'+name
        if lib.filepath!=new: print('LIBREL',lib.filepath,'->',new); lib.filepath=new
    elif name=='sprague_cafe_src.blend':
        new='//north/sprague_cafe_src.blend'
        if lib.filepath!=new: print('LIBREL',lib.filepath,'->',new); lib.filepath=new
COMPRESS=open(LIVE,'rb').read(4)==bytes.fromhex('28b52ffd'); print('COMPRESS',COMPRESS)
assert os.path.abspath(OUT)!=os.path.abspath(LIVE)
bpy.ops.wm.save_as_mainfile(filepath=OUT,compress=COMPRESS,copy=True)
print('SAVED',OUT,os.path.getsize(OUT)); print('OBJECTS_FINAL',len(bpy.data.objects)); print('PACKED',sum(1 for i in bpy.data.images if i.packed_file))
h=hashlib.sha256()
with open(LIVE,'rb') as f:
    for ch in iter(lambda:f.read(1<<20),b''): h.update(ch)
open(R+'/data/ws/live_sha256.txt','w').write(h.hexdigest()+'  '+LIVE+'\n'); print('LIVE_SHA',h.hexdigest(),'T',round(time.time()-t0,1))
