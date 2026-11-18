"""wj: south-gully LiDAR extension of the WF east-dorm patch (x182-258, y292-320) + skirt dip GN + tree reseat.
Source: 2017 B17 J5D6 class-2 ground (same grid as WF). OSM 552281523 culvert stream runs through the gully."""
import bpy, bmesh, numpy as np, json, math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT='/workspace/nj-scenes/montclair-state'
EX0,EX1,EY0,EY1=182,258,292,320
FE=8.0
rep={}
g=np.load(f'{ROOT}/data/wj/south_hollow_grid_1m.npz'); k=[f for f in g.files if 'B17_J5D6' in f and 'dtm' in f][0]; L=g[k].copy()
GX0,GY0=150,290
# fill nans with neighbour mean (iterative)
for _ in range(6):
    n=np.isnan(L)
    if not n.any(): break
    P=np.pad(L,1,constant_values=np.nan)
    nb=np.stack([P[0:-2,1:-1],P[2:,1:-1],P[1:-1,0:-2],P[1:-1,2:],P[0:-2,0:-2],P[2:,2:],P[0:-2,2:],P[2:,0:-2]])
    m=np.nanmean(nb,axis=0); L[n]=m[n]
rep['nan_left']=int(np.isnan(L).sum())
def lv(x,y):  # vertex at integer corner: mean of 4 cells
    i=int(round(x))-GX0; j=int(round(y))-GY0
    zs=[L[jj,ii] for jj in (j-1,j) for ii in (i-1,i) if 0<=jj<L.shape[0] and 0<=ii<L.shape[1] and np.isfinite(L[jj,ii])]
    return float(np.mean(zs))
def ss(t): t=min(max(t,0.0),1.0); return t*t*(3-2*t)
WF=bpy.data.objects['WF_east_dorm_LiDAR_terrain_patch_UNVERIFIED']
sk=bpy.data.objects['Context_skirt_3DEP_ortho_4km']
dg=bpy.context.evaluated_depsgraph_get()
ske=sk.evaluated_get(dg); sme=ske.to_mesh(); sev=[sk.matrix_world@v.co for v in sme.vertices]
bs=BVHTree.FromPolygons(sev,[tuple(p.vertices) for p in sme.polygons]); ske.to_mesh_clear()
def skz(x,y):
    h=bs.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))
    return (h[0].z, h[1]) if h[0] is not None else (None,None)
# union boundary polygon for wh_edge
POLY=[(50,320),(EX0,320),(EX0,EY0),(EX1,EY0),(EX1,320),(300,320),(300,509),(50,509)]
def dseg(px,py,a,b):
    ax,ay=a;bx,by=b;dx,dy=bx-ax,by-ay;t=((px-ax)*dx+(py-ay)*dy)/(dx*dx+dy*dy);t=min(max(t,0),1)
    return math.hypot(px-ax-t*dx,py-ay-t*dy)
def dpoly(x,y): return min(dseg(x,y,POLY[i],POLY[(i+1)%len(POLY)]) for i in range(len(POLY)))
def whf(d): return 1.0-ss(d/12.0)
def wlat(x): return ss(min(x-EX0, EX1-x)/FE)
# ---- 1. WF south rows (y 320..324) in ext x-range: revert toward raw LiDAR by lateral weight
me=WF.data
bak=np.array([v.co[:] for v in me.vertices]); np.save(f'{ROOT}/data/wj/wf_verts_bak.npy',bak)
attr_bak={}
for an in ('wh_edge',):
    a=me.attributes.get(an)
    if a: attr_bak[an]=np.array([d.value for d in a.data]); np.save(f'{ROOT}/data/wj/wf_{an}_bak.npy',attr_bak[an])
mw=WF.matrix_world; changed=0; maxd=0; row320={}
for v in me.vertices:
    co=mw@v.co
    if EX0<=co.x<=EX1 and 319.9<=co.y<=324.1:
        w=wlat(co.x); zr=lv(co.x,co.y); nz=co.z*(1-w)+zr*w
        if abs(nz-co.z)>1e-4: changed+=1; maxd=max(maxd,abs(nz-co.z))
        v.co.z=nz-mw.translation.z if False else nz  # WF at origin/unit scale (wh probe)
    if EX0<=co.x<=EX1 and abs(co.y-320)<0.05: row320[int(round(co.x))]=v.co.z
rep['wf_rows_changed']=changed; rep['wf_rows_maxdz']=round(maxd,2)
# wh_edge on WF: min(old, f(dist union))
a=me.attributes.get('wh_edge'); n_wh=0
if a and a.domain=='POINT':
    for i,v in enumerate(me.vertices):
        co=mw@v.co
        if co.y<334 and EX0-12<=co.x<=EX1+12:
            nv=min(a.data[i].value, whf(dpoly(co.x,co.y)))
            if nv<a.data[i].value-1e-4: n_wh+=1
            a.data[i].value=nv
rep['wf_wh_edge_lowered']=n_wh; rep['wh_domain']=a.domain if a else None
me.update()
# ---- 2. extension mesh
bm=bmesh.new(); vid={}
def vert(x,y):
    if (x,y) in vid: return vid[(x,y)]
    if y==320 and x in row320: z=row320[x]
    else:
        w=min(wlat(x), ss((y-EY0)/FE)); s,_=skz(x,y); zr=lv(x,y)
        z=zr if s is None else s*(1-w)+zr*w
    v=bm.verts.new((x,y,z)); vid[(x,y)]=v; return v
for y in range(EY0,EY1):
    for x in range(EX0,EX1):
        f=bm.faces.new([vert(x,y),vert(x+1,y),vert(x+1,y+1),vert(x,y+1)]); f.smooth=True
# UV fit from WF loops
uvl=me.uv_layers.get('ortho') or me.uv_layers[0]
A=[];U=[];V=[]
for li in range(0,len(me.loops),37):
    c=mw@me.vertices[me.loops[li].vertex_index].co; uv=uvl.data[li].uv; A.append([c.x,c.y,1]);U.append(uv[0]);V.append(uv[1])
A=np.array(A);cu=np.linalg.lstsq(A,np.array(U),rcond=None)[0];cv=np.linalg.lstsq(A,np.array(V),rcond=None)[0]
lay=bm.loops.layers.uv.new(uvl.name)
for f in bm.faces:
    for l in f.loops:
        c=l.vert.co; l[lay].uv=(cu[0]*c.x+cu[1]*c.y+cu[2], cv[0]*c.x+cv[1]*c.y+cv[2])
EN='WJ_south_gully_LiDAR_patch_ext_UNVERIFIED'
em=bpy.data.meshes.new(EN); bm.to_mesh(em); bm.free()
for m in me.materials: em.materials.append(m)
E=bpy.data.objects.new(EN,em); WF.users_collection[0].objects.link(E)
E['wj_obj']=1; E['UNVERIFIED']='wj: south extension of WF patch over the stream gully (OSM 552281523 culvert outfall); 2017 B17 J5D6 class-2 1 m DTM; 8 m W/S/E feather into skirt'
# attributes: ou_edge (linear fit from WF), wh_edge (union dist), wh_sn (skirt normal)
xs=[];ys=[];ous=[]
oa=me.attributes.get('ou_edge')
if oa:
    for i,v in enumerate(me.vertices):
        c=mw@v.co
        if c.y<345 and 170<c.x<270: xs.append([c.x,c.y,1]); ous.append(oa.data[i].value)
    co_=np.linalg.lstsq(np.array(xs),np.array(ous),rcond=None)[0]; rep['ou_fit']=[float(c) for c in co_]
ev=[E.matrix_world@v.co for v in em.vertices]
def addattr(name,src,vals):
    t=src.data_type if src else 'FLOAT'; d=src.domain if src else 'POINT'
    na=em.attributes.new(name,t,'POINT')
    for i,vv in enumerate(vals):
        if t=='FLOAT': na.data[i].value=vv
        else: na.data[i].vector=vv
if oa: addattr('ou_edge',oa,[min(max(float(co_[0]*c.x+co_[1]*c.y+co_[2]),0),1) for c in ev])
if me.attributes.get('wh_edge'): addattr('wh_edge',me.attributes['wh_edge'],[whf(dpoly(c.x,c.y)) for c in ev])
sa=me.attributes.get('wh_sn')
if sa:
    nv=[]
    for c in ev:
        _,n=skz(c.x,c.y); nv.append(tuple(n) if n is not None else (0,0,1))
    addattr('wh_sn',sa,nv)
rep['attrs_wf']={a.name:(a.domain,a.data_type) for a in me.attributes if not a.name.startswith('.')}
rep['ext_faces']=len(em.polygons); rep['ext_zmin']=round(min(c.z for c in ev),2); rep['ext_zmax']=round(max(c.z for c in ev),2)
# ---- 3. skirt GN dip under WF+ext in the gully box
NG='WJ_skirt_under_south_gully'
ng=bpy.data.node_groups.new(NG,'GeometryNodeTree')
ng.interface.new_socket('Geometry',in_out='INPUT',socket_type='NodeSocketGeometry')
ng.interface.new_socket('Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
N=ng.nodes;K=ng.links
gi=N.new('NodeGroupInput');go=N.new('NodeGroupOutput')
pos=N.new('GeometryNodeInputPosition');sx=N.new('ShaderNodeSeparateXYZ');K.new(pos.outputs[0],sx.inputs[0])
def cmp(s,v,op):
    c=N.new('FunctionNodeCompare');c.data_type='FLOAT';c.operation=op;K.new(s,c.inputs[0]);c.inputs[1].default_value=v;return c.outputs[0]
def AND(a,b):
    n=N.new('FunctionNodeBooleanMath');n.operation='AND';K.new(a,n.inputs[0]);K.new(b,n.inputs[1]);return n.outputs[0]
M=20
sel=AND(AND(cmp(sx.outputs[0],EX0-M,'GREATER_THAN'),cmp(sx.outputs[0],EX1+M,'LESS_THAN')),AND(cmp(sx.outputs[1],EY0-M,'GREATER_THAN'),cmp(sx.outputs[1],336+M,'LESS_THAN')))
sep=N.new('GeometryNodeSeparateGeometry');sep.domain='FACE';K.new(gi.outputs[0],sep.inputs[0]);K.new(sel,sep.inputs[1])
sub=N.new('GeometryNodeSubdivideMesh');sub.inputs['Level'].default_value=3;K.new(sep.outputs[0],sub.inputs[0])
o1=N.new('GeometryNodeObjectInfo');o1.transform_space='RELATIVE';o1.inputs['Object'].default_value=WF
o2=N.new('GeometryNodeObjectInfo');o2.transform_space='RELATIVE';o2.inputs['Object'].default_value=E
jt=N.new('GeometryNodeJoinGeometry');K.new(o1.outputs['Geometry'],jt.inputs[0]);K.new(o2.outputs['Geometry'],jt.inputs[0])
rc=N.new('GeometryNodeRaycast');K.new(jt.outputs[0],rc.inputs['Target Geometry'])
p2=N.new('GeometryNodeInputPosition');ad=N.new('ShaderNodeVectorMath');ad.operation='ADD';K.new(p2.outputs[0],ad.inputs[0]);ad.inputs[1].default_value=(0,0,50)
K.new(ad.outputs[0],rc.inputs['Source Position']);rc.inputs['Ray Direction'].default_value=(0,0,-1);rc.inputs['Ray Length'].default_value=200
hz=N.new('ShaderNodeSeparateXYZ');K.new(rc.outputs['Hit Position'],hz.inputs[0])
pz=N.new('ShaderNodeSeparateXYZ');K.new(p2.outputs[0],pz.inputs[0])
d=N.new('ShaderNodeMath');d.operation='SUBTRACT';K.new(pz.outputs[2],d.inputs[0]);K.new(hz.outputs[2],d.inputs[1])
s=AND(AND(cmp(d.outputs[0],-0.5,'GREATER_THAN'),cmp(d.outputs[0],15.0,'LESS_THAN')),rc.outputs['Is Hit'])
tz=N.new('ShaderNodeMath');tz.operation='SUBTRACT';K.new(hz.outputs[2],tz.inputs[0]);tz.inputs[1].default_value=0.08
cx=N.new('ShaderNodeCombineXYZ');K.new(pz.outputs[0],cx.inputs[0]);K.new(pz.outputs[1],cx.inputs[1]);K.new(tz.outputs[0],cx.inputs[2])
sp=N.new('GeometryNodeSetPosition');K.new(sub.outputs[0],sp.inputs['Geometry']);K.new(s,sp.inputs['Selection']);K.new(cx.outputs[0],sp.inputs['Position'])
jo=N.new('GeometryNodeJoinGeometry');K.new(sp.outputs[0],jo.inputs[0]);K.new(sep.outputs[1],jo.inputs[0]);K.new(jo.outputs[0],go.inputs[0])
md=sk.modifiers.new(NG,'NODES');md.node_group=ng
rep['skirt_mods']=[m.name for m in sk.modifiers]
sk['UNVERIFIED_wj']='wj: skirt dipped 8 cm under WF patch + WJ south-gully ext where skirt sits up to 15 m above (GN, mesh unedited)'
bpy.context.view_layer.update()
# ---- 4. reseat trees + check
dg=bpy.context.evaluated_depsgraph_get()
def bvh(o):
    e=o.evaluated_get(dg);m=e.to_mesh();vs=[o.matrix_world@v.co for v in m.vertices];b=BVHTree.FromPolygons(vs,[tuple(p.vertices) for p in m.polygons]);e.to_mesh_clear();return b
bw=bvh(WF);be=bvh(E);bs2=bvh(sk)
def top(x,y):
    hs=[b.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))[0] for b in (bw,be,bs2)]
    hs=[h.z for h in hs if h is not None]; return max(hs) if hs else None
def patchz(x,y):
    hs=[b.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))[0] for b in (bw,be)]
    hs=[h.z for h in hs if h is not None]; return max(hs) if hs else None
trees=[]
for o in bpy.data.objects:
    if not o.name.startswith('TL_tree_'): continue
    t=o.matrix_world.translation
    if EX0-14<=t.x<=EX1+14 and EY0-14<=t.y<=336:
        gz=top(t.x,t.y)
        if gz is None: continue
        dz=(gz-0.25)-t.z
        if abs(dz)>0.1:
            o.location.z+=dz; o['wj_dz']=float(dz); trees.append([o.name,round(t.x,1),round(t.y,1),round(dz,2)])
rep['trees_moved']=trees
# skirt-above-patch residual
cnt=0;mx=0
for y in np.arange(292.5,336,1.0):
    for x in np.arange(182.5,258,1.0):
        p=patchz(x,y); s_=bs2.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))[0]
        if p is not None and s_ is not None and s_.z>p+0.03: cnt+=1; mx=max(mx,s_.z-p)
rep['skirt_above_after']=cnt; rep['skirt_above_max']=round(mx,2)
# TR footway check
tr=bpy.data.objects.get('TR_footway_546643369_S_gap_UNVERIFIED'); bad=0
if tr:
    for v in tr.data.vertices:
        c=tr.matrix_world@v.co
        if c.x>=EX0-2 and EY0-2<=c.y<=322:
            gz=top(c.x,c.y)
            if gz is not None and abs(gz-c.z)>0.3: bad+=1
rep['tr_footway_off']=bad
print('REPORT',json.dumps(rep))
json.dump(rep,open(f'{ROOT}/data/wj/fix_report.json','w'),indent=1)
bpy.ops.wm.save_mainfile()
