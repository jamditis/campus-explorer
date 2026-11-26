import bpy,os,sys
for im in bpy.data.images:
    fp=bpy.path.abspath(im.filepath) if im.filepath else ''
    sz=os.path.getsize(fp) if fp and os.path.exists(fp) else -1
    print('IMG248',im.name,'|',fp,'|',sz,'packed',bool(im.packed_file),im.packed_file.size if im.packed_file else 0,flush=True)
sys.stdout.flush(); os._exit(0)
