"""Pack MAIN-only 20261107a: relative libs + pack_all + save_as copy into export stage."""
import bpy, os, shutil
STAGE = "/workspace/export_20261107a/montclair_state_scene/nj-scenes/montclair-state"
os.makedirs(STAGE, exist_ok=True)
OUT = os.path.join(STAGE, "montclair_state.blend")
print("FILE", bpy.data.filepath)
print("OBJECTS", len(bpy.data.objects), "LIBS", len(bpy.data.libraries), "IMAGES", len(bpy.data.images))
miss=0
for img in bpy.data.images:
    if img.packed_file: continue
    if img.source in ('FILE','SEQUENCE','TILED') and img.filepath:
        ap = bpy.path.abspath(img.filepath)
        if not os.path.exists(ap):
            print("MISS", img.name, img.filepath); miss += 1
print("MISS_COUNT", miss)
try:
    bpy.ops.file.pack_all(); print("pack_all OK")
except Exception as e:
    print("pack_all FAIL", e)
for lib in bpy.data.libraries:
    if lib.parent is not None: continue
    ap = os.path.normpath(bpy.path.abspath(lib.filepath)).replace('\\','/')
    name = os.path.basename(ap)
    if '/assets/' in ap:
        new = '//../assets/' + name
        if lib.filepath != new:
            print('LIBREL', lib.filepath, '->', new); lib.filepath = new
    elif name == 'sprague_cafe_src.blend':
        new = '//north/sprague_cafe_src.blend'
        if lib.filepath != new:
            print('LIBREL', lib.filepath, '->', new); lib.filepath = new
COMPRESS = True
live = bpy.data.filepath
try:
    COMPRESS = open(live,'rb').read(4) == bytes.fromhex('28b52ffd')
except Exception:
    pass
print('COMPRESS', COMPRESS)
bpy.ops.wm.save_as_mainfile(filepath=OUT, compress=COMPRESS, copy=True)
print("SAVED", OUT, os.path.getsize(OUT))
print("OBJECTS_FINAL", len(bpy.data.objects))
print("PACKED", sum(1 for i in bpy.data.images if i.packed_file))
# write sha of live
import hashlib
h=hashlib.sha256()
with open(live,'rb') as f:
    for chunk in iter(lambda: f.read(1<<20), b''): h.update(chunk)
open('/workspace/nj-scenes/montclair-state/data/vu/post_sha256.txt','w').write(h.hexdigest()+'  '+live+'\n')
open('/workspace/nj-scenes/montclair-state/data/vu/obj_count_final.txt','w').write(str(len(bpy.data.objects))+'\n')
print('LIVE_SHA', h.hexdigest())
