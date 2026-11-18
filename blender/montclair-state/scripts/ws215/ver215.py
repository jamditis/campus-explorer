import bpy
L=[]
for a in dir(bpy.data):
    c=getattr(bpy.data,a,None)
    if isinstance(c,bpy.types.bpy_prop_collection):
        try:
            for i in c:
                if getattr(i,'library',None) or getattr(i,'is_missing',False): L.append((a,i.name,i.library.filepath if i.library else None,getattr(i,'is_missing',None), i.users))
        except Exception: pass
print('VER objects',len(bpy.data.objects),'meshes',len(bpy.data.meshes),'images',len(bpy.data.images),'libs',[l.filepath for l in bpy.data.libraries])
for x in L[:40]: print('VER LINKED',x)
print('VER unpacked',[(i.name,i.filepath) for i in bpy.data.images if i.source=='FILE' and not i.packed_file])
