# ws263 M5 (NO SAVE): every image/library/sound/font/cachefile path in main that resolves into north/
import bpy, os
TAG='C263A'
root=os.path.dirname(bpy.data.filepath)
n=0
for coll in ('images','libraries','sounds','fonts','movieclips','cache_files','volumes'):
    for i in getattr(bpy.data,coll):
        fp=getattr(i,'filepath','')
        if not fp: continue
        ab=os.path.normpath(bpy.path.abspath(fp))
        pk=bool(getattr(i,'packed_file',None))
        if '/north/' in ab or 'north/' in fp:
            n+=1
            print(TAG,coll,repr(i.name),fp,'exists',os.path.exists(ab),'packed',pk,'users',i.users,'lib',i.library.name if getattr(i,'library',None) else None,flush=True)
print(TAG,'total',n,flush=True)
# also any modifiers/GN/text referencing north paths (string props)
for o in bpy.data.objects:
    for m in o.modifiers:
        for p in dir(m):
            try: v=getattr(m,p)
            except: continue
            if isinstance(v,str) and 'north/' in v: print(TAG,'MODSTR',o.name,m.name,p,v,flush=True)
os._exit(0)
