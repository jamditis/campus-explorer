# ws264 M5 pre-release cleanup (merge208 CHAIN). (1) Relativise the absolute paths main itself stores: 2 local images
# (data/ts/naip_*) + 6 library paths (assets/*.blend) -> '//' relative. The 4 linked-image paths (SweetgumStar/TulipPoplar)
# live inside assets/campus_assets.blend and are NOT changeable from main (library data) -> left, logged.
# (2) WS113_paving_tops_proxy (hidden; ray/proximity target of GN WS113_paving_edge_grade): delete its 188 NaN verts
# (74 faces touching them) so the target BVH has only finite geometry. (3) 113 empty mesh stubs: unlink+remove the 110 with
# no modifiers, no children and no references (probe264a); keep the 3 with modifiers (GN generates their geometry).
import bpy, os, bmesh, numpy as np
TAG='F264B'
root=os.path.dirname(bpy.data.filepath)
n=0
for i in list(bpy.data.images)+list(bpy.data.libraries):
    if getattr(i,'library',None) or (isinstance(i,bpy.types.Image) and i.packed_file): continue
    fp=i.filepath
    if not fp or fp.startswith('//'): continue
    ab=os.path.normpath(fp)
    if not os.path.exists(ab): print(TAG,'skip missing',i.name,fp,flush=True); continue
    rel='//'+os.path.relpath(ab,root)
    i.filepath=rel; n+=1; print(TAG,'rel',type(i).__name__,i.name,fp,'->',rel,flush=True)
left=[(x.name,x.filepath) for x in list(bpy.data.images)+list(bpy.data.libraries) if not getattr(x,'library',None) and x.filepath and not x.filepath.startswith('//') and not (isinstance(x,bpy.types.Image) and x.packed_file)]
print(TAG,'relativised',n,'left local-absolute',left,flush=True)
if left: raise SystemExit('F264A paths left')
o=bpy.data.objects['WS113_paving_tops_proxy']; me=o.data
bm=bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table()
# f264a v1 deleted the NaN verts + 74 faces: the evaluated WS113 grade then dropped 37 ground verts by up to 0.48 m at the
# Chapin W plaza edge / S of Chapin (those faces carried real paving tops). v2 REPAIRS instead: each NaN vert gets the mean
# of its finite edge-neighbours (iterated for clusters); faces stay.
bad=[v for v in bm.verts if not all(np.isfinite(v.co))]
todo=set(bad); it=0
while todo and it<50:
    it+=1; done=[]
    for v in todo:
        nb=[e.other_vert(v).co for e in v.link_edges if e.other_vert(v) not in todo]
        if nb: v.co=sum(nb,v.co*0)/len(nb) if False else (sum((c for c in nb),__import__('mathutils').Vector((0,0,0)))/len(nb)); done.append(v)
    for v in done: todo.discard(v)
iso=[v for v in todo]
if iso: bmesh.ops.delete(bm,geom=iso,context='VERTS')
nf=len(bad)
bm.to_mesh(me); bm.free(); me.update()
a=np.empty(len(me.vertices)*3,np.float32); me.vertices.foreach_get('co',a)
print(TAG,'proxy nan repaired',nf-len(iso),'iters',it,'isolated deleted',len(iso),'now v',len(me.vertices),'f',len(me.polygons),'finite',bool(np.isfinite(a).all()),flush=True)
if not np.isfinite(a).all(): raise SystemExit('F264A nan left')
# refs (same as probe264a)
ref=set()
for ob in bpy.data.objects:
    if ob.parent: ref.add(ob.parent.name)
    for m in ob.modifiers:
        for p in dir(m):
            if p.startswith('_'): continue
            try: v=getattr(m,p)
            except Exception: continue
            if isinstance(v,bpy.types.Object): ref.add(v.name)
        if m.type=='NODES':
            for k in m.keys():
                if isinstance(m[k],bpy.types.Object): ref.add(m[k].name)
    for c in ob.constraints:
        t=getattr(c,'target',None)
        if isinstance(t,bpy.types.Object): ref.add(t.name)
for ng in bpy.data.node_groups:
    for nd in ng.nodes:
        for s in nd.inputs:
            v=getattr(s,'default_value',None)
            if isinstance(v,bpy.types.Object): ref.add(v.name)
        v=getattr(nd,'object',None)
        if isinstance(v,bpy.types.Object): ref.add(v.name)
kill=[ob for ob in bpy.context.scene.objects if ob.type=='MESH' and not ob.library and len(ob.data.vertices)==0
      and len(ob.modifiers)==0 and len(ob.children)==0 and ob.name not in ref]
kept=[ob.name for ob in bpy.context.scene.objects if ob.type=='MESH' and not ob.library and len(ob.data.vertices)==0 and ob not in kill]
names=[ob.name for ob in kill]
for ob in kill:
    me=ob.data; bpy.data.objects.remove(ob,do_unlink=True)
    if me.users==0: bpy.data.meshes.remove(me)
print(TAG,'empty stubs removed',len(names),'kept',kept,flush=True)
open('/workspace/nj-scenes/montclair-state/scripts/ws264/f264b_removed_stubs.txt','w').write('\n'.join(names)+'\n')
