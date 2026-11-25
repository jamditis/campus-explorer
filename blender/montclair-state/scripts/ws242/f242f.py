# ws242: verts added this session to M3a/M3b (f242b/f242c/f242d flaps + gap fill) carry default (zero/white) values in the
# tiles' generic attributes (ortho tone / colour-feather layers) -> pale faces in the test render. Copy every POINT and
# CORNER attribute value for new verts/corners from the nearest pre-ws242 vertex (xy KD-tree against the ws241h meshes).
import bpy
from mathutils import Vector
from mathutils.kdtree import KDTree
PRE='/workspace/nj-scenes/montclair-state/montclair_state_pre_20261125ws242.blend'
T242F=[x for x in bpy.data.objects if x.name.startswith(('M3a_north_LiDAR_DTM_1m','M3b_north_LiDAR_DTM_1m')) and not x.library]
for tgt in T242F:
    with bpy.data.libraries.load(PRE) as (a,b): b.meshes=[]; b.objects=[tgt.name]
    o=tgt; me=o.data; old=b.objects[0].data; n=tgt.name
    kd=KDTree(len(old.vertices))
    for i,v in enumerate(old.vertices): kd.insert(Vector((v.co.x,v.co.y,0)),i)
    kd.balance()
    near=[kd.find(Vector((v.co.x,v.co.y,0))) for v in me.vertices]
    new=[i for i,(c,j,d) in enumerate(near) if d>1e-3]
    # nearest old vertex -> one of its corners in the old mesh
    oc={}
    for l in old.loops: oc.setdefault(l.vertex_index,l.index)
    rep=[]
    for at in me.attributes:
        if at.name.startswith('.') or at.name in ('position',) or at.domain not in ('POINT','CORNER'): continue
        oa=old.attributes.get(at.name)
        if oa is None or oa.domain!=at.domain: continue
        key='vector' if hasattr(at.data[0],'vector') else ('color' if hasattr(at.data[0],'color') else 'value')
        if at.domain=='POINT':
            for i in new: setattr(at.data[i],key,getattr(oa.data[near[i][1]],key))
            rep.append((at.name,'P',len(new)))
        else:
            k=0
            for l in me.loops:
                if l.vertex_index<len(near) and (near[l.vertex_index][2]>1e-3 or l.index>=len(old.loops)):
                    j=near[l.vertex_index][1]; setattr(at.data[l.index],key,getattr(oa.data[oc[j]],key)); k+=1
            rep.append((at.name,'C',k))
    me.update()
    bpy.data.objects.remove(b.objects[0])
    print('F242F',n[:12],'old mesh',old.name,'new verts',len(new),'attrs',rep,flush=True)
