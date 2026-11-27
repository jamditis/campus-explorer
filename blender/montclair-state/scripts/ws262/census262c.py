# ws262 M4b census (merge208 CHAIN, base meshes, NO SAVE): every library main links from, ID counts per type, overrides, and
# whether any linked ID is indirectly-linked (needed by another linked ID). Exits before save.
import bpy, os, collections
TAG='C262C'
for lib in bpy.data.libraries:
    c=collections.Counter(); ind=0; ov=0; ex=[]
    for attr in dir(bpy.data):
        coll=getattr(bpy.data,attr,None)
        if not isinstance(coll,bpy.types.bpy_prop_collection) or attr in ('libraries','window_managers','workspaces','screens'): continue
        try: it=list(coll)
        except Exception: continue
        for i in it:
            if getattr(i,'library',None)==lib:
                c[attr]+=1; ind+=bool(getattr(i,'is_library_indirect',False))
                if len(ex)<8: ex.append(i.name[:40])
    print(TAG,lib.name,lib.filepath,'exists',os.path.exists(bpy.path.abspath(lib.filepath)),dict(c),'indirect',ind,'ex',ex,flush=True)
n_ov=sum(1 for o in bpy.data.objects if o.override_library); print(TAG,'objects with overrides',n_ov,flush=True)
lo=[o for o in bpy.data.objects if o.library]; inscene=[o.name for o in lo if bpy.context.scene.objects.get(o.name)]
print(TAG,'linked objects',len(lo),'in scene',len(inscene),flush=True)
print(TAG,'collections linked',[c.name for c in bpy.data.collections if c.library][:20],flush=True)
os._exit(0)
