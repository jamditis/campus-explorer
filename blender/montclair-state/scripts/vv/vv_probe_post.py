import bpy, json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import bmesh
dg = bpy.context.evaluated_depsgraph_get()
log = {'links': [], 'gaps': []}
for k in range(3):
    link = bpy.data.objects.get('VV_Blanton_entrance_%d_path_link_UNVERIFIED' % k)
    L = bpy.data.objects.get('TU_Blanton_entrance_%d_landing_UNVERIFIED' % k)
    walks = [o for o in bpy.data.objects if o.name.startswith('TJ_walk_313029')]
    print('door', k, 'link', bool(link), 'landing', bool(L))
    if not link or not L:
        continue
    # landing outer vs link
    lv = [L.matrix_world @ v.co for v in L.data.vertices]
    zhi = max(p.z for p in lv)
    top = [p for p in lv if p.z > zhi - 0.1]
    # link bvh
    bm = bmesh.new(); bm.from_object(link, dg); bm.transform(link.matrix_world)
    bvh = BVHTree.FromBMesh(bm); bm.free()
    gaps = []
    for p in top:
        loc, nrm, idx, d = bvh.find_nearest(p)
        if loc is not None:
            xy = ((loc.x-p.x)**2+(loc.y-p.y)**2)**0.5
            gaps.append(xy)
    gaps.sort()
    # also link end vs TJ walks
    lv2 = [link.matrix_world @ v.co for v in link.data.vertices]
    end_gaps = []
    for w in walks:
        bm = bmesh.new(); bm.from_object(w, dg); bm.transform(w.matrix_world)
        verts = [v.co.copy() for v in bm.verts]; bm.free()
        for p in lv2:
            nv = min(verts, key=lambda q: (q.x-p.x)**2+(q.y-p.y)**2)
            end_gaps.append((((nv.x-p.x)**2+(nv.y-p.y)**2)**0.5, w.name))
    end_gaps.sort(key=lambda t: t[0])
    entry = dict(k=k, landing_to_link_min=round(gaps[0],3) if gaps else None,
                 landing_to_link_med=round(gaps[len(gaps)//2],3) if gaps else None,
                 link_to_walk_min=round(end_gaps[0][0],3) if end_gaps else None,
                 link_to_walk=end_gaps[0][1] if end_gaps else None,
                 n_link_verts=len(link.data.vertices))
    log['gaps'].append(entry)
    print('POST', entry)
json.dump(log, open('data/vv/probe_post.json','w'), indent=1)
print('OBJS', len(bpy.data.objects))
