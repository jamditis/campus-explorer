# ws217 ONE-SCENE merge, step 1 (read-only): classify every object in north/montclair_north.blend against main (bbox205.json)
# using the same rules as the viewer merge (tools/web-export/make_chunks.py merge mode): same name -> SKIP_SAME; north ground/terrain ->
# CLIP_TERRAIN (keep only cells main's ground doesn't cover); north object whose XY bbox is >=60% inside one main object of the same
# kind (building/detail) -> SKIP_OVERLAP; otherwise -> APPEND. Writes scripts/ws217/north_manifest217.json. Main is NOT opened.
import bpy, json, re
from mathutils import Vector
from collections import Counter
@bpy.app.handlers.persistent
def _off(*a):
    for o in bpy.data.objects:
        for m in o.modifiers: m.show_viewport=False
bpy.app.handlers.load_post.append(_off)
S='/workspace/nj-scenes/montclair-state/'
MB=json.load(open(S+'scripts/ws205/bbox205.json'))
bpy.ops.wm.open_mainfile(filepath=S+'north/montclair_north.blend',load_ui=False)
GROUND=re.compile(r'(terrain|ground|dtm|lidar_dtm|skirt|farfield|context_ground)',re.I)
mainbig=[(n,b) for n,b in MB.items() if b[0]=='MESH' and not GROUND.search(n) and (b[3]-b[2])<400 and (b[5]-b[4])<400]
def ov(a,b):
    ix=max(0,min(a[1],b[3])-max(a[0],b[2])); iy=max(0,min(a[3],b[5])-max(a[2],b[4]))
    ar=max(1e-6,(a[1]-a[0])*(a[3]-a[2])); return ix*iy/ar
out={}; C=Counter()
for o in bpy.data.objects:
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    box=(min(v.x for v in bb),max(v.x for v in bb),min(v.y for v in bb),max(v.y for v in bb),min(v.z for v in bb),max(v.z for v in bb))
    if o.name in MB: k='SKIP_SAME'
    elif o.type!='MESH': k='NONMESH_'+o.type
    elif GROUND.search(o.name): k='CLIP_TERRAIN'
    else:
        best=max(((ov(box,b),n) for n,b in mainbig if abs(b[6]-box[4])<15),default=(0,None))
        k='SKIP_OVERLAP' if best[0]>=0.6 and (box[1]-box[0])*(box[3]-box[2])>4 else 'APPEND'
    C[k]+=1; out[o.name]=[k,o.type,[round(x,1) for x in box],len(o.data.vertices) if o.type=='MESH' else 0,[c.name for c in o.users_collection]]
json.dump(out,open(S+'scripts/ws217/north_manifest217.json','w'),indent=0)
print('NM217 total',len(out),dict(C),flush=True)
pre=Counter(re.split(r'[_ ]',n)[0] for n,v in out.items() if v[0]=='APPEND')
print('NM217 APPEND prefixes',pre.most_common(40),flush=True)
print('NM217 APPEND verts',sum(v[3] for v in out.values() if v[0]=='APPEND'),flush=True)
print('NM217 CLIP',[n for n,v in out.items() if v[0]=='CLIP_TERRAIN'][:20],flush=True)
print('NM217 libs',[l.filepath for l in bpy.data.libraries],'images',len(bpy.data.images),flush=True)
lib=Counter(); lv=Counter(); pv=Counter(); shared=Counter()
for o in bpy.data.objects:
    v=out[o.name]
    L=o.library.filepath if o.library else 'LOCAL'; lib[(v[0],L)]+=1
    if v[0]=='APPEND':
        lv[L]+=v[3]; pv[re.split(r'[_ ]',o.name)[0]]+=v[3]
        if o.type=='MESH' and o.data.users>1: shared['multiuser_mesh_objs']+=1
for k,n in sorted(lib.items(),key=lambda t:-t[1])[:25]: print('NM217 LIB',k,n,flush=True)
print('NM217 APPEND verts by lib',dict(lv),flush=True)
print('NM217 APPEND verts by prefix',pv.most_common(20),dict(shared),flush=True)
