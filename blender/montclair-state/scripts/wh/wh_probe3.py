"""wh probe3: transforms, UV continuity, normals at edges, ou_edge Mix details."""
import bpy, json, math, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT='/workspace/nj-scenes/montclair-state'
PN='WF_east_dorm_LiDAR_terrain_patch_UNVERIFIED'
SK='Context_skirt_3DEP_ortho_4km'
P=bpy.data.objects[PN]; sk=bpy.data.objects[SK]
out={}
out['patch_loc']=list(P.location); out['patch_scale']=list(P.scale); out['patch_rot']=list(P.rotation_euler)
out['skirt_loc']=list(sk.location); out['skirt_scale']=list(sk.scale); out['skirt_rot']=list(sk.rotation_euler)
print('PATCH loc/scale/rot', out['patch_loc'], out['patch_scale'], out['patch_rot'])
print('SKIRT loc/scale/rot', out['skirt_loc'], out['skirt_scale'], out['skirt_rot'])

mat=P.data.materials[0]; nt=mat.node_tree
for nm in ['Math','Mix','Math.001','Mix.001','Map Range','Map Range.001','Noise Texture']:
    n=nt.nodes[nm]
    extra={}
    if hasattr(n,'operation'): extra['op']=n.operation
    if hasattr(n,'data_type'): extra['dtype']=n.data_type
    if hasattr(n,'blend_type'): extra['blend']=n.blend_type
    if n.type=='MIX':
        extra['blend_type']=n.blend_type
        extra['data_type']=n.data_type
    ins={}
    for i in n.inputs:
        if i.is_linked:
            ins[i.identifier if hasattr(i,'identifier') else i.name] = f"LINKED {i.links[0].from_node.name}.{i.links[0].from_socket.name}"
        else:
            try:
                v=i.default_value
                ins[i.name]= [round(float(x),4) for x in list(v)[:4]] if hasattr(v,'__len__') and not isinstance(v,str) else (round(float(v),4) if isinstance(v,(int,float)) else str(v))
            except Exception as e:
                ins[i.name]=str(e)
    print(nm, n.type, extra, ins)
    out[nm]=dict(extra=extra, inputs=ins)

# UV compare: patch loop UV vs skirt loop UV via lstsq? Better: pick patch boundary verts and
# find skirt loops near same XY
puv=P.data.uv_layers['ortho']
suv=sk.data.uv_layers['ortho']

# sample some patch faces near each edge and compare UV predicted from a skirt-nearby face
# Build skirt XY->UV from a subset of loops
sxy=[]; su=[]; sv=[]
mw=sk.matrix_world
for p in sk.data.polygons:
    c=mw@p.center
    if not (0<=c.x<=350 and 250<=c.y<=560): continue
    for li in p.loop_indices:
        v=mw@sk.data.vertices[sk.data.loops[li].vertex_index].co
        uv=suv.data[li].uv
        sxy.append((v.x,v.y)); su.append(uv[0]); sv.append(uv[1])
print('skirt uv samples in region', len(sxy))
sxy=np.array(sxy); su=np.array(su); sv=np.array(sv)

def nearest_uv(x,y):
    d=(sxy[:,0]-x)**2+(sxy[:,1]-y)**2
    j=int(d.argmin())
    return float(su[j]), float(sv[j]), float(d[j]**0.5)

# patch UVs at edge vs interior
pmw=P.matrix_world
samples=[]
for p in P.data.polygons:
    c=pmw@p.center
    # pick faces near edges or interior
    tag=None
    if abs(c.x-300)<1.5 and 360<c.y<480: tag='east'
    elif abs(c.x-50)<1.5 and 360<c.y<480: tag='west'
    elif abs(c.y-320)<1.5 and 80<c.x<280: tag='south'
    elif abs(c.y-509)<1.5 and 80<c.x<280: tag='north'
    elif 170<c.x<180 and 415<c.y<425: tag='interior'
    if not tag: continue
    # average UV of face
    uvs=[puv.data[li].uv for li in p.loop_indices]
    um=sum(u[0] for u in uvs)/len(uvs); vm=sum(u[1] for u in uvs)/len(uvs)
    su_,sv_,dist=nearest_uv(c.x,c.y)
    samples.append(dict(tag=tag,x=round(c.x,2),y=round(c.y,2),z=round(c.z,2),
                        puv=(round(um,5),round(vm,5)), suv=(round(su_,5),round(sv_,5)),
                        du=round(um-su_,5), dv=round(vm-sv_,5), skirt_xy_dist=round(dist,2)))

from collections import defaultdict
by=defaultdict(list)
for s in samples: by[s['tag']].append(s)
uv_sum={}
for tag,lst in by.items():
    dus=[abs(s['du']) for s in lst]; dvs=[abs(s['dv']) for s in lst]
    uv_sum[tag]=dict(n=len(lst), max_du=max(dus), max_dv=max(dvs),
                     mean_du=round(sum(dus)/len(dus),5), mean_dv=round(sum(dvs)/len(dvs),5),
                     sample=lst[:3])
    print('UV', tag, uv_sum[tag])
out['uv']=uv_sum

# normals: patch vs evaluated skirt at east/south/interior
dg=bpy.context.evaluated_depsgraph_get()
ske=sk.evaluated_get(dg); sme=ske.to_mesh()
svs=[sk.matrix_world@v.co for v in sme.vertices]
sfs=[tuple(p.vertices) for p in sme.polygons]
bs=BVHTree.FromPolygons(svs,sfs)
# also need face normals
snorms=[(sk.matrix_world.to_3x3()@p.normal).normalized() for p in sme.polygons]

def skirt_hit(x,y):
    h=bs.ray_cast(Vector((x,y,400)), Vector((0,0,-1)))
    if h[0] is None: return None
    # h = (loc, nrm, index, dist)
    return dict(z=round(h[0].z,3), n=(round(h[1].x,3),round(h[1].y,3),round(h[1].z,3)),
                face_n=None if h[2] is None else (round(snorms[h[2]].x,3),round(snorms[h[2]].y,3),round(snorms[h[2]].z,3)))

ncomp=[]
for tag,pts in {
    'east':[(298,y) for y in range(360,481,20)],
    'west':[(52,y) for y in range(360,481,20)],
    'south':[(x,322) for x in range(80,281,40)],
    'interior':[(175,420),(220,400),(250,430)],
}.items():
    recs=[]
    for x,y in pts:
        # patch face normal: find polygon whose center is near
        best=None; bd=1e9
        for p in P.data.polygons:
            c=pmw@p.center
            d=(c.x-x)**2+(c.y-y)**2
            if d<bd: bd=d; best=p
        pn=(pmw.to_3x3()@best.normal).normalized() if best else None
        sh=skirt_hit(x,y)
        recs.append(dict(x=x,y=y, bd=round(bd**0.5,2),
                         pn=None if pn is None else (round(pn.x,3),round(pn.y,3),round(pn.z,3)),
                         skirt=sh))
    # mean |pn - sn|
    diffs=[]
    for r in recs:
        if r['pn'] and r['skirt'] and r['skirt']['n']:
            diffs.append(sum((r['pn'][i]-r['skirt']['n'][i])**2 for i in range(3))**0.5)
    print(tag, 'n', len(recs), 'mean_ndiff', round(sum(diffs)/len(diffs),3) if diffs else None, 'max', round(max(diffs),3) if diffs else None)
    print('  sample', recs[:2])
    ncomp.append(dict(tag=tag, mean_ndiff=round(sum(diffs)/len(diffs),3) if diffs else None,
                      max_ndiff=round(max(diffs),3) if diffs else None, sample=recs[:3]))
out['normals']=ncomp
ske.to_mesh_clear()

# skirt face size in east dorm vs patch
areas=[]
for p in sk.data.polygons:
    c=mw@p.center
    if 50<=c.x<=300 and 320<=c.y<=509:
        areas.append(p.area)
print('skirt faces in box', len(areas), 'median area', float(np.median(areas)) if areas else None, 'mean', float(np.mean(areas)) if areas else None)
out['skirt_face_area_in_box']=dict(n=len(areas), median=float(np.median(areas)) if areas else None, mean=float(np.mean(areas)) if areas else None)
print('patch face area median ~1.0 (1m grid)')

json.dump(out, open(f'{ROOT}/data/wh/probe3.json','w'), indent=2)
print('WROTE probe3')
