"""Probe Blanton doors vs base/spandrel bands — what still crosses glass."""
import bpy, bmesh, json
from mathutils import Vector
from mathutils.bvhtree import BVHTree

out = {'doors': [], 'candidates': []}
# candidate band-like objects
cands = []
for o in bpy.data.objects:
    if o.type != 'MESH':
        continue
    n = o.name
    if any(k in n for k in ('Blanton', 'blanton')):
        if any(k in n.lower() for k in ('band', 'base', 'spandrel', 'plinth', 'mid', 'skirt', 'surround', 'pier')):
            cands.append(o.name)
        elif n.startswith('TI_Blanton') or n.startswith('TN_Blanton') or n.startswith('TU_Blanton'):
            cands.append(o.name)
out['cand_names'] = sorted(set(cands))

def world_verts(o):
    mw = o.matrix_world
    return [mw @ v.co for v in o.data.vertices]

def bbox(vs):
    xs=[v.x for v in vs]; ys=[v.y for v in vs]; zs=[v.z for v in vs]
    return dict(xmin=min(xs),xmax=max(xs),ymin=min(ys),ymax=max(ys),zmin=min(zs),zmax=max(zs))

def bvh_of(o):
    bm = bmesh.new(); bm.from_mesh(o.data); bm.transform(o.matrix_world); bm.faces.ensure_lookup_table()
    t = BVHTree.FromBMesh(bm); bm.free(); return t

for k in range(3):
    G = bpy.data.objects.get('TJ_Blanton_entrance_%d_glass_UNVERIFIED'%k)
    F = bpy.data.objects.get('TJ_Blanton_entrance_%d_frame_UNVERIFIED'%k)
    if not G: continue
    gv = world_verts(G)
    gc = sum(gv, Vector())/len(gv)
    gb = bbox(gv)
    # horizontal axis
    best=None
    for i in range(len(gv)):
        for j in range(i+1,len(gv)):
            d=gv[j]-gv[i]; d.z=0
            if best is None or d.length>best.length: best=d
    u=best.normalized(); n=Vector((-u.y,u.x,0))
    # ensure n points outward-ish (away from Blanton center ~141.6,450.4)
    BC=Vector((141.6,450.4,0))
    if (gc-BC).to_2d().dot(n.to_2d())<0: n=-n
    half_w = max(abs((v-gc).dot(u)) for v in gv) + 0.05
    half_d = max(abs((v-gc).dot(n)) for v in gv) + 0.15
    zlo,zhi = gb['zmin']-0.05, gb['zmax']+0.05
    door = dict(k=k, c=[round(x,3) for x in gc], u=[round(x,3) for x in u], n=[round(x,3) for x in n],
                half_w=round(half_w,3), half_d=round(half_d,3), z=[round(zlo,3),round(zhi,3)],
                glass_bbox=gb, frame_loc=list(F.location) if F else None,
                hits=[])
    g_bvh = bvh_of(G)
    for nm in out['cand_names']:
        o = bpy.data.objects[nm]
        if o == G or o == F: continue
        # quick AABB reject in door local
        vs = world_verts(o)
        if not vs: continue
        in_span=0; z_in=0; samples=[]
        for v in vs:
            d=v-gc; d2=Vector((d.x,d.y,0))
            if abs(d2.dot(u))<=half_w+0.3 and abs(d2.dot(n))<=half_d+0.8:
                in_span += 1
                if zlo-0.5 <= v.z <= zhi+0.5:
                    z_in += 1
                    if len(samples)<6:
                        samples.append([round(v.x,2),round(v.y,2),round(v.z,2)])
        if in_span < 2: continue
        # BVH overlap
        try:
            o_bvh = bvh_of(o)
            ov = g_bvh.overlap(o_bvh)
            n_ov = len(ov)
        except Exception as e:
            n_ov = -1
        # also count verts that project into glass AABB and are near glass plane
        near_glass=0
        for v in vs:
            d=v-gc
            if abs(d.dot(u))<=half_w and abs(d.dot(n))<=0.25 and zlo<=v.z<=zhi:
                near_glass += 1
        if n_ov>0 or near_glass>4 or z_in>8:
            ob = bbox(vs)
            door['hits'].append(dict(name=nm, verts=len(vs), in_span=in_span, z_in=z_in,
                                     near_glass=near_glass, overlap_pairs=n_ov,
                                     zrange=[round(ob['zmin'],2),round(ob['zmax'],2)],
                                     samples=samples))
    out['doors'].append(door)

# also describe spandrel + block_base briefly
for nm in ('TN_Blanton_spandrel_bands_UNVERIFIED','TN_Blanton_block_base_UNVERIFIED','TN_Blanton_piers_UNVERIFIED'):
    o=bpy.data.objects.get(nm)
    if not o: continue
    vs=world_verts(o); b=bbox(vs)
    out['candidates'].append(dict(name=nm, nverts=len(vs), bbox=b,
        mats=[m.name if m else None for m in o.data.materials]))

# TI mid band / milky?
for o in bpy.data.objects:
    if 'Blanton' in o.name and o.type=='MESH':
        mats=[m.name if m else None for m in (o.data.materials or [])]
        if any(m and ('milk' in m.lower() or 'mid' in m.lower() or 'band' in m.lower() or 'white' in m.lower()) for m in mats):
            out.setdefault('mat_hits',[]).append((o.name, mats))

json.dump(out, open('/workspace/nj-scenes/montclair-state/data/vu/probe_doors.json','w'), indent=1)
print('WROTE probe_doors.json doors', len(out['doors']))
for d in out['doors']:
    print('DOOR', d['k'], 'hits', [(h['name'], h['near_glass'], h['overlap_pairs'], h['z_in']) for h in d['hits']])
