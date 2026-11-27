# ws263 M5 pre-release check (NO SAVE; open main directly, base meshes, no depsgraph eval): reusable before the 8 PM release.
# Reports libraries + where they live, any image/library path outside montclair-state/ or assets/, absolute paths, missing files,
# packed images, objects with NaN/inf verts, empty meshes in the scene, University Hall objects (must be none / untouched).
import bpy, os, math, numpy as np
TAG='M5C264'; root=os.path.dirname(bpy.data.filepath); ok_roots=(root+'/', os.path.normpath(root+'/../assets')+'/')
print(TAG,'file',bpy.data.filepath,flush=True)
print(TAG,'libs',[(l.name,l.filepath,os.path.exists(bpy.path.abspath(l.filepath))) for l in bpy.data.libraries],flush=True)
bad=[];absP=[];miss=[];pk=[]
for coll in ('images','libraries'):
    for i in getattr(bpy.data,coll):
        fp=getattr(i,'filepath','')
        if coll=='images' and i.packed_file: pk.append(i.name); continue
        if not fp or (coll=='images' and i.source not in ('FILE','SEQUENCE','TILED')): continue
        ab=os.path.normpath(bpy.path.abspath(fp, library=getattr(i,'library',None)))
        if not fp.startswith('//'): absP.append((i.name,fp))
        if not ab.startswith(ok_roots) or '/north/' in ab: bad.append((i.name,ab))
        if not os.path.exists(ab): miss.append((i.name,ab))
print(TAG,'paths outside montclair-state/ or assets/ or under north/',len(bad),bad[:10],flush=True)
print(TAG,'absolute paths',len(absP),absP[:10],flush=True)
print(TAG,'missing files',len(miss),miss[:10],flush=True)
print(TAG,'packed images',len(pk),pk[:10],flush=True)
nan=[];empty=[]
for o in bpy.context.scene.objects:
    if o.type!='MESH' or o.library: continue
    me=o.data; n=len(me.vertices)
    if n==0: empty.append(o.name[:60]); continue
    a=np.empty(n*3,np.float32); me.vertices.foreach_get('co',a)
    if not np.isfinite(a).all(): nan.append(o.name[:60])
print(TAG,'NaN/inf meshes',len(nan),nan[:10],flush=True)
print(TAG,'empty meshes in scene',len(empty),empty[:10],flush=True)
uh=[o.name for o in bpy.data.objects if 'university hall' in o.name.lower() or o.name.lower().startswith(('uh_','univhall'))]
print(TAG,'University Hall named objects',len(uh),uh[:10],flush=True)
print(TAG,'objects',len(bpy.data.objects),'scene',len(bpy.context.scene.objects),flush=True)

# ws264 additions: library-internal absolute paths (not fixable from main), and an evaluated compare hook for the
# WS113_paving_edge_grade users (proxy NaN fix must not change them): EVAL=1 evaluates only those objects.
libabs=[(i.name,i.library.name,i.filepath) for i in bpy.data.images if i.library and i.filepath and not i.filepath.startswith('//')]
print(TAG,'absolute paths inside linked libraries (not main-owned)',len(libabs),libabs,flush=True)
locabs=[(i.name,i.filepath) for i in list(bpy.data.images)+list(bpy.data.libraries) if not getattr(i,'library',None) and i.filepath and not i.filepath.startswith('//') and not (isinstance(i,bpy.types.Image) and i.packed_file)]
print(TAG,'main-owned absolute paths',len(locabs),locabs,flush=True)
print(TAG,'unresolved libs',[l.name for l in bpy.data.libraries if not os.path.exists(bpy.path.abspath(l.filepath))],flush=True)
if os.environ.get('EVAL'):
    users=[]
    for ob in bpy.context.scene.objects:
        for m in ob.modifiers:
            if m.type=='NODES' and m.node_group and (m.node_group.name=='WS113_paving_edge_grade' or any(n.type=='GROUP' and n.node_tree and n.node_tree.name=='WS113_paving_edge_grade' for n in m.node_group.nodes)):
                users.append(ob); break
    keep=set(users)
    for ob in bpy.data.objects:
        if ob not in keep:
            for m in ob.modifiers: m.show_viewport=False
    dg=bpy.context.evaluated_depsgraph_get()
    import hashlib
    for ob in users:
        e=ob.evaluated_get(dg); me=e.to_mesh(); n=len(me.vertices); a=np.empty(n*3,np.float32); me.vertices.foreach_get('co',a)
        a=np.round(a,3); print(TAG,'EVAL',ob.name,n,hashlib.sha1(a.tobytes()).hexdigest()[:12],'finite',bool(np.isfinite(a).all()),flush=True); np.save('/workspace/nj-scenes/montclair-state/scripts/ws264/tmp_eval_'+os.path.basename(bpy.data.filepath)[15:-6]+'_'+ob.name[:12]+'.npy',a.reshape(-1,3)); e.to_mesh_clear()
os._exit(0)
