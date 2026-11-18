"""wo: MAIN-only pack export 20261109a via save_as_mainfile(copy=True). Live file never overwritten."""
import bpy, os, json, time, hashlib
R='/workspace/nj-scenes/montclair-state'; t0=time.time()
LIVE=bpy.data.filepath
assert LIVE.endswith('montclair-state/montclair_state.blend')
STAGE="/workspace/export_20261109a/montclair_state_scene/nj-scenes/montclair-state"
os.makedirs(STAGE,exist_ok=True); OUT=os.path.join(STAGE,"montclair_state.blend")
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
        if lib.filepath!=new: lib.filepath=new
    elif name=='sprague_cafe_src.blend':
        new='//north/sprague_cafe_src.blend'
        if lib.filepath!=new: lib.filepath=new
COMPRESS=open(LIVE,'rb').read(4)==bytes.fromhex('28b52ffd'); print('COMPRESS',COMPRESS)
assert os.path.abspath(OUT)!=os.path.abspath(LIVE)
bpy.ops.wm.save_as_mainfile(filepath=OUT,compress=COMPRESS,copy=True)
print('SAVED',OUT,os.path.getsize(OUT)); print('OBJECTS_FINAL',len(bpy.data.objects)); print('PACKED',sum(1 for i in bpy.data.images if i.packed_file))
print('T',round(time.time()-t0,1))
