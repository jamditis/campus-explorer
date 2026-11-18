"""wh: patch/skirt tone + normal feather. Attribute/shader only; no vert moves.
Samples skirt ou_edge onto the WF LiDAR patch; stores wh_edge + wh_sn; assigns a
local material copy that mixes shading normals toward the skirt at the outer edge.
"""
import bpy, json, math, time, os
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from collections import defaultdict, deque

t0=time.time()
ROOT='/workspace/nj-scenes/montclair-state'
os.chdir(ROOT)
SAVE=os.environ.get('SAVE')=='1'
PN='WF_east_dorm_LiDAR_terrain_patch_UNVERIFIED'
SK='Context_skirt_3DEP_ortho_4km'
MATN='WH_east_dorm_patch_tone_UNVERIFIED'
CAMN='WH_CAM_closeup_patch_skirt_east_seam'
COLN='WH_east_dorm_seam_UNVERIFIED'
FEATHER=12.0
X0,X1,Y0,Y1=50.,300.,320.,509.

P=bpy.data.objects[PN]
sk=bpy.data.objects[SK]
assert P.data.materials and P.data.materials[0]
orig_mat=P.data.materials[0]
print('ORIG_MAT', orig_mat.name, 'shared_users', orig_mat.users)

# --- evaluate skirt: ou_edge + BVH for normals ---
dg=bpy.context.evaluated_depsgraph_get()
ske=sk.evaluated_get(dg)
sme=ske.to_mesh()
svs=[sk.matrix_world@v.co for v in sme.vertices]
sfs=[tuple(p.vertices) for p in sme.polygons]
bs=BVHTree.FromPolygons(svs, sfs)
ou_attr=sme.attributes.get('ou_edge')
ou_vals=np.zeros(len(sme.vertices), np.float32)
if ou_attr and ou_attr.data_type=='FLOAT':
    ou_attr.data.foreach_get('value', ou_vals)
print('SKIRT_EVAL verts', len(svs), 'faces', len(sfs), 'ou_edge max', float(ou_vals.max()), 'mean', float(ou_vals.mean()))

# --- distance-to-outer-boundary on the patch ---
me=P.data
n=len(me.vertices)
co=np.zeros(n*3, np.float32)
me.vertices.foreach_get('co', co)
co=co.reshape(n,3)
# boundary edges: used by 1 polygon
edge_count=defaultdict(int)
for p in me.polygons:
    vs=list(p.vertices)
    for a,b in zip(vs, vs[1:]+vs[:1]):
        edge_count[(min(a,b), max(a,b))] += 1
boundary=[e for e,c in edge_count.items() if c==1]
# outer = boundary whose midpoint is near the rectangle frame
outer_verts=set()
for a,b in boundary:
    mx=0.5*(co[a,0]+co[b,0]); my=0.5*(co[a,1]+co[b,1])
    if mx<X0+8 or mx>X1-8 or my<Y0+8 or my>Y1-8:
        outer_verts.add(a); outer_verts.add(b)
print('boundary edges', len(boundary), 'outer verts', len(outer_verts))

# BFS on vertex adjacency for distance in hops (~1 m)
adj=defaultdict(list)
for (a,b),c in edge_count.items():
    adj[a].append(b); adj[b].append(a)
dist=np.full(n, 99.0, np.float32)
q=deque()
for i in outer_verts:
    dist[i]=0.0; q.append(i)
while q:
    i=q.popleft()
    di=dist[i]
    if di>=FEATHER+2: continue
    for j in adj[i]:
        # hop length
        step=float(np.linalg.norm(co[j,:2]-co[i,:2]))
        nd=di+max(step, 0.25)
        if nd<dist[j]:
            dist[j]=nd; q.append(j)
# also clamp by AABB inset so a missed outer-vert still feathers
aabb_d=np.minimum(np.minimum(co[:,0]-X0, X1-co[:,0]), np.minimum(co[:,1]-Y0, Y1-co[:,1]))
dist=np.minimum(dist, np.maximum(aabb_d, 0.0).astype(np.float32))
# smoothstep 0..FEATHER → wh_edge 1..0
t=np.clip(dist/FEATHER, 0.0, 1.0)
wh_edge=(1.0 - t*t*(3.0-2.0*t)).astype(np.float32)
print('wh_edge >0.05', int((wh_edge>0.05).sum()), '==1', int((wh_edge>0.99).sum()),
      'mean_edge', float(wh_edge.mean()), 'max_dist_capped', float(dist.min()), float(np.median(dist)))

# --- sample ou_edge + skirt normal per patch vert ---
ou=np.zeros(n, np.float32)
sn=np.zeros((n,3), np.float32)
sn[:,2]=1.0
hit_n=0
ou_sum=0.0
for i in range(n):
    x,y=float(co[i,0]), float(co[i,1])
    h=bs.ray_cast(Vector((x,y,400.0)), Vector((0.0,0.0,-1.0)))
    if h[0] is None:
        continue
    hit_n+=1
    nrm=h[1]
    if nrm is not None and nrm.length>0.2:
        nrm=nrm.normalized()
        # flip if pointing down
        if nrm.z<0: nrm=-nrm
        sn[i]= (nrm.x, nrm.y, nrm.z)
    fi=h[2]
    if fi is not None and 0<=fi<len(sfs):
        vals=[ou_vals[vi] for vi in sfs[fi]]
        ou[i]=float(sum(vals)/len(vals))
        ou_sum+=ou[i]
ske.to_mesh_clear()
print('SAMPLED hits', hit_n, '/', n, 'ou_mean_on_hits', round(ou_sum/max(hit_n,1),4),
      'ou_max', float(ou.max()), 'n_ou>0.05', int((ou>0.05).sum()))

# --- write attributes (replace if rerun) ---
def write_float(mesh, name, arr):
    if name in mesh.attributes:
        mesh.attributes.remove(mesh.attributes[name])
    a=mesh.attributes.new(name, 'FLOAT', 'POINT')
    a.data.foreach_set('value', arr.astype(np.float32))

def write_vec(mesh, name, arr):
    if name in mesh.attributes:
        mesh.attributes.remove(mesh.attributes[name])
    a=mesh.attributes.new(name, 'FLOAT_VECTOR', 'POINT')
    a.data.foreach_set('vector', arr.astype(np.float32).ravel())

write_float(me, 'ou_edge', ou)
write_float(me, 'wh_edge', wh_edge)
write_vec(me, 'wh_sn', sn)
me.update()
print('ATTRS', [a.name for a in me.attributes if not a.name.startswith('.')])

# --- material copy + normal mix ---
# remove a previous copy if we re-run
old=bpy.data.materials.get(MATN)
if old and old!=orig_mat:
    if P.data.materials[0]==old:
        P.data.materials[0]=orig_mat
    if old.users==0:
        bpy.data.materials.remove(old)

mat=orig_mat.copy()
mat.name=MATN
assert len(mat.name)<=63
mat['wh_mat']=1
mat['UNVERIFIED']='wh: copy of skirt ortho shader; mixes Normal toward sampled skirt normal by wh_edge (12 m outer fade). ou_edge painted from evaluated skirt. No vert moves.'
P.data.materials[0]=mat

nt=mat.node_tree
bsdf=nt.nodes.get('Principled BSDF')
assert bsdf
n_in=bsdf.inputs['Normal']

# place nodes to the left of BSDF
bx,by=bsdf.location
attr_e=nt.nodes.new('ShaderNodeAttribute'); attr_e.name='WH_edge'; attr_e.label='WH_edge'
attr_e.attribute_name='wh_edge'; attr_e.location=(bx-520, by-280)
attr_n=nt.nodes.new('ShaderNodeAttribute'); attr_n.name='WH_sn'; attr_n.label='WH_sn'
attr_n.attribute_name='wh_sn'; attr_n.location=(bx-520, by-420)
geo=nt.nodes.new('ShaderNodeNewGeometry'); geo.name='WH_geo'; geo.label='WH_geo'
geo.location=(bx-520, by-140)
mix=nt.nodes.new('ShaderNodeMix'); mix.name='WH_nrmix'; mix.label='WH_nrmix'
mix.data_type='VECTOR'; mix.location=(bx-260, by-280)
print('MIX IN', [(s.identifier, s.name, s.type) for s in mix.inputs])
print('MIX OUT', [(s.identifier, s.name, s.type) for s in mix.outputs])
def by_id(socks, ident):
    for s in socks:
        if s.identifier==ident:
            return s
    raise KeyError(ident)
fac=by_id(mix.inputs, 'Factor_Float')
a_s=by_id(mix.inputs, 'A_Vector')
b_s=by_id(mix.inputs, 'B_Vector')
out_s=by_id(mix.outputs, 'Result_Vector')
print('MIX socks', fac.identifier, a_s.identifier, b_s.identifier, out_s.identifier)

if n_in.is_linked:
    src=n_in.links[0].from_socket
    nt.links.remove(n_in.links[0])
    nt.links.new(src, a_s)
    print('MIX A from existing', src.node.name, src.name)
else:
    nt.links.new(geo.outputs['Normal'], a_s)
    print('MIX A from Geometry Normal (BSDF Normal was free)')
nt.links.new(attr_n.outputs['Vector'], b_s)
nt.links.new(attr_e.outputs['Fac'], fac)
nt.links.new(out_s, n_in)
print('MATERIAL wired', mat.name)

P['wh_obj']=1
P['UNVERIFIED_wh']='wh: ou_edge sampled from skirt; wh_edge 12m outer fade; wh_sn skirt normals; local mat copy '+MATN

# --- collection + closeup cam ---
col=bpy.data.collections.get(COLN)
if col is None:
    col=bpy.data.collections.new(COLN)
    bpy.context.scene.collection.children.link(col)

# pick a seam viewpoint on the east edge, BVH-checked against nearby meshes
# candidate look-ats along x=299.5 (just inside) / camera just west and up
Pe=P.evaluated_get(bpy.context.evaluated_depsgraph_get())
# local occlusion: meshes whose bbox overlaps a padded east-seam box
pad_min=Vector((270, 350, 80)); pad_max=Vector((330, 470, 160))
obs=[]
for o in bpy.data.objects:
    if o.type!='MESH' or o.hide_render: continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    if max(p.x for p in bb)<pad_min.x or min(p.x for p in bb)>pad_max.x: continue
    if max(p.y for p in bb)<pad_min.y or min(p.y for p in bb)>pad_max.y: continue
    obs.append(o)
# build combined BVH of those evaluated meshes (skip the patch itself? include it — we want to see it)
print('CAM occluders', len(obs))
verts=[]; faces=[]; base=0
dg2=bpy.context.evaluated_depsgraph_get()
for o in obs:
    try:
        ev=o.evaluated_get(dg2); em=ev.to_mesh()
    except Exception:
        continue
    vs=[o.matrix_world@v.co for v in em.vertices]
    if not vs:
        ev.to_mesh_clear(); continue
    verts.extend(vs)
    for p in em.polygons:
        faces.append(tuple(i+base for i in p.vertices))
    base+=len(vs)
    ev.to_mesh_clear()
bvh=BVHTree.FromPolygons(verts, faces) if faces else None

def visible(origin, target, eps=0.15):
    if bvh is None: return True, 0
    d=target-origin
    L=d.length
    if L<1e-6: return False, 0
    hit=bvh.ray_cast(origin, d.normalized(), L-eps)
    return hit[0] is None, L

# ground z helper via patch then skirt
def gz(x,y):
    h=bs.ray_cast(Vector((x,y,400)), Vector((0,0,-1))) if False else None
    # rebuild not available (cleared). Use patch verts approx + eval patch.
    return None

# use live patch + original skirt objects via scene ray? Use a fresh patch BVH
pvs=[P.matrix_world@v.co for v in P.data.vertices]
pfs=[tuple(p.vertices) for p in P.data.polygons]
bp=BVHTree.FromPolygons(pvs, pfs)

def ground(x,y):
    h=bp.ray_cast(Vector((x,y,400)), Vector((0,0,-1)))
    if h[0] is not None: return h[0].z, 'patch'
    # no skirt BVH now; estimate from nearby patch
    return None, None

cands=[]
for y in (370, 385, 400, 415, 430, 445):
    zg,src=ground(292.0, float(y))
    if zg is None: continue
    # camera west of seam, above ground, looking at a point on the seam
    for dx,dz,lens in ((14, 6, 35),(18, 8, 40),(22, 11, 32),(12, 4.5, 45)):
        cam=Vector((292.0-dx, float(y), zg+dz))
        tgt=Vector((300.0, float(y)+2.0, zg-1.5))
        # also test a few ground targets along the seam
        ok=0
        tests=[]
        for ty, tzoff in ((y-8, 0.3),(y, 0.3),(y+8, 0.3),(y, 1.5)):
            gt,s=ground(298.5, float(ty))
            if gt is None: continue
            t=Vector((298.5, float(ty), gt+tzoff))
            vis,L=visible(cam, t)
            tests.append(vis)
            if vis: ok+=1
        cands.append(dict(cam=tuple(round(c,3) for c in cam), tgt=tuple(round(c,3) for c in tgt),
                          y=y, dx=dx, dz=dz, lens=lens, ok=ok, n=len(tests), zg=round(zg,3)))

cands.sort(key=lambda r: (-r['ok'], -r['n'], abs(r['y']-400)))
print('CAM cands top', cands[:6])
pick=cands[0] if cands else dict(cam=(278,400,118), tgt=(300,400,104), lens=35, ok=0, y=400)
print('CAM pick', pick)

# create / replace cam
oldc=bpy.data.objects.get(CAMN)
if oldc:
    cd=oldc.data
    bpy.data.objects.remove(oldc, do_unlink=True)
    if cd and cd.users==0: bpy.data.cameras.remove(cd)
cd=bpy.data.cameras.new(CAMN)
cd.lens=float(pick['lens']); cd.clip_end=30000
cam=bpy.data.objects.new(CAMN, cd)
cam.location=pick['cam']
tgt=Vector(pick['tgt']); origin=Vector(pick['cam'])
d=tgt-origin
cam.rotation_euler=(math.pi/2+math.atan2(d.z, math.hypot(d.x,d.y)), 0, math.atan2(d.y,d.x)-math.pi/2)
cam['wh_obj']=1
cam['UNVERIFIED']='wh closeup of east patch/skirt seam; placement UNVERIFIED (BVH-checked)'
col.objects.link(cam)
# also link to scene master if needed — collection is already a child
print('CAM created', CAMN, 'at', pick['cam'], 'lens', pick['lens'], 'ok', pick['ok'])

# --- report ---
rep=dict(
    orig_mat=orig_mat.name, new_mat=mat.name, feather=FEATHER,
    nverts=n, outer_verts=len(outer_verts), boundary_edges=len(boundary),
    wh_edge_gt05=int((wh_edge>0.05).sum()), wh_edge_eq1=int((wh_edge>0.99).sum()),
    ou_hits=hit_n, ou_max=float(ou.max()), ou_mean=float(ou.mean()),
    ou_gt05=int((ou>0.05).sum()),
    cam=pick, elapsed=round(time.time()-t0,2),
    objs=len(bpy.data.objects),
)
# sample a few locations
samples=[]
for x,y,lab in [(175,420,'interior'),(298,400,'east'),(52,400,'west'),
                (200,322,'south'),(180,500,'northish'),(250,400,'east_of_bohn')]:
    # nearest vert
    d=(co[:,0]-x)**2+(co[:,1]-y)**2
    j=int(d.argmin())
    samples.append(dict(lab=lab,x=x,y=y, vx=round(float(co[j,0]),2), vy=round(float(co[j,1]),2),
                        ou=round(float(ou[j]),4), wh=round(float(wh_edge[j]),4),
                        sn=[round(float(s),3) for s in sn[j]], dist=round(float(dist[j]),2)))
rep['samples']=samples
print('SAMPLES', samples)
json.dump(rep, open('data/wh/apply.json','w'), indent=2)
print('APPLY', {k:rep[k] for k in ('new_mat','wh_edge_gt05','ou_gt05','ou_mean','elapsed','objs')})

if SAVE:
    bpy.ops.wm.save_mainfile()
    print('SAVED', len(bpy.data.objects))
print('WH_FIX_DONE', round(time.time()-t0,1), 's')
