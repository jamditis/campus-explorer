# ws209 W12b: one clean concrete crossing slab where the CCOM walk crosses the dock apron; GN-delete that span of the
# draped Footpaths_OSM (appended last in its stack); 3h joint faces in the span removed; apron/fill tucked under the slab.
import bpy, bmesh, numpy as np, sys
sys.path.insert(0,'/workspace/nj-scenes/montclair-state/scripts/ws209'); from an209 import tri_interp
from mathutils import Vector
D='/workspace/nj-scenes/montclair-state/scripts/'
e=np.load(D+'ws208/walk_eval_ws207a_apron.npz'); WV,WF=e['V'],e['F']
O=np.array([-0.4957*-28.0-13.7014,-28.0]); u=np.array([0.4441391,-0.89595784]); n=np.array([0.89595784,0.4441391])
S0,S1,TW=0.0,14.0,3.0
ap=bpy.data.objects['CCOM_dock_apron_20261014jf3']; fl=bpy.data.objects['WS206_CCOM_walk_E_edge_straight_fill_ortho_LiDAR_UNVERIFIED']
def wz(o): mw=o.matrix_world; return np.array([tuple(mw@v.co) for v in o.data.vertices])
def tris(o):
    V=wz(o); F=[]
    for p in o.data.polygons:
        vs=list(p.vertices); F+=[[vs[0],vs[j],vs[j+1]] for j in range(1,len(vs)-1)]
    return V,np.array(F)
AV,AF=tris(ap)
# targets
ss=np.arange(S0,S1+1e-6,0.25); ts=np.arange(0,TW+1e-6,0.25)
G=np.array([O+u*s+n*t for s in ss for t in ts]); SG=np.repeat(ss,len(ts)); TG=np.tile(ts,len(ss))
A=tri_interp(AV,AF,G); W=tri_interp(WV,WF,G)
tgt=np.where(np.isnan(A),W,A+0.012); w=np.ones(len(G))
endz=(SG<=0.5)|(SG>=S1-0.5); tgt=np.where(endz&~np.isnan(W),W+0.006,tgt); w[endz]=4
m=~np.isnan(tgt)
X=np.stack([np.ones_like(SG),SG,SG**2,SG**3,TG,SG*TG,TG**2],1)
c,*_=np.linalg.lstsq(X[m]*w[m,None],tgt[m]*w[m],rcond=None)
def ztop(s,t): return c@np.array([1,s,s*s,s**3,t,s*t,t*t])
Z=X@c
res=Z-tgt; print('F209 fit rms %.4f min %.4f max %.4f'%(np.sqrt(np.nanmean(res[m]**2)),res[m].min(),res[m].max()),flush=True)
# end-zone guarantee: slab >= walk+6mm where walk faces survive
def ztop2(s,t):
    z=ztop(s,t)
    if s<0.6 or s>S1-0.6:
        q=O+u*s+n*min(max(t,0.05),TW-0.05); wv=tri_interp(WV,WF,q[None])[0]
        if not np.isnan(wv): z=max(z,wv+0.006)
    return z
# --- slab mesh
J=0.010; js=[x for x in np.arange(1.5,S1-0.1,1.5)]; jt=[1.5]
sv=sorted(set(np.round(list(np.arange(S0,S1+1e-6,0.25))+[x+d for x in js for d in(-J/2,J/2)],4))); sv=[x for x in sv if not any(abs(x-j)<J/2-1e-6 for j in js)]
tv=sorted(set(np.round(list(np.arange(0,TW+1e-6,0.25))+[x+d for x in jt for d in(-J/2,J/2)],4))); tv=[x for x in tv if not any(abs(x-j)<J/2-1e-6 for j in jt)]
bm=bmesh.new(); idx={}
for i,s in enumerate(sv):
    for k,t in enumerate(tv):
        q=O+u*s+n*t; idx[i,k]=bm.verts.new((q[0],q[1],ztop2(s,t)))
def injoint(a,b,L): return any(abs((a+b)/2-j)<J for j in L)
for i in range(len(sv)-1):
    for k in range(len(tv)-1):
        f=bm.faces.new((idx[i,k],idx[i,k+1],idx[i+1,k+1],idx[i+1,k]))
        f.material_index=1 if (injoint(sv[i],sv[i+1],js) or injoint(tv[k],tv[k+1],jt)) else 0
bm.normal_update()
for f in bm.faces:
    if f.normal.z<0: f.normal_flip()
ring=[idx[i,0] for i in range(len(sv))]+[idx[len(sv)-1,k] for k in range(1,len(tv))]+[idx[i,len(tv)-1] for i in range(len(sv)-2,-1,-1)]+[idx[0,k] for k in range(len(tv)-2,0,-1)]
low=[bm.verts.new((v.co.x,v.co.y,v.co.z-0.12)) for v in ring]
cen=Vector((*(O+u*7+n*1.5),0))
for a in range(len(ring)):
    b=(a+1)%len(ring); f=bm.faces.new((ring[a],low[a],low[b],ring[b])); f.material_index=0
    f.normal_update()
    mid=(ring[a].co+ring[b].co)/2; out=Vector((mid.x-cen.x,mid.y-cen.y,0))
    if f.normal.dot(out)<0: f.normal_flip()
me=bpy.data.meshes.new('WS209_CCOM_apron_crossing_slab'); bm.to_mesh(me); bm.free()
ob=bpy.data.objects.new('WS209_CCOM_walk_apron_crossing_slab_OSM_ortho_UNVERIFIED',me)
for mn in ('WS4_Concrete_walk_broom_nogrid','Paving_joint_groove'): me.materials.append(bpy.data.materials[mn])
fp=bpy.data.objects['Footpaths_OSM']; (fp.users_collection[0] if fp.users_collection else bpy.context.scene.collection).objects.link(ob)
for p in me.polygons: p.use_smooth=False
print('F209 slab verts',len(me.vertices),'faces',len(me.polygons),flush=True)
# --- GN delete of the walk span (appended last)
ng=bpy.data.node_groups.new('WS209_walk_apron_span_delete','GeometryNodeTree')
ng.interface.new_socket('Geometry',in_out='INPUT',socket_type='NodeSocketGeometry'); ng.interface.new_socket('Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
N=ng.nodes; L=ng.links; gi=N.new('NodeGroupInput'); go=N.new('NodeGroupOutput'); pos=N.new('GeometryNodeInputPosition')
sub=N.new('ShaderNodeVectorMath'); sub.operation='SUBTRACT'; sub.inputs[1].default_value=(O[0],O[1],0); L.new(pos.outputs[0],sub.inputs[0])
def dot(vec):
    d=N.new('ShaderNodeVectorMath'); d.operation='DOT_PRODUCT'; d.inputs[1].default_value=(vec[0],vec[1],0); L.new(sub.outputs[0],d.inputs[0]); return d.outputs['Value']
def rng(sock,lo,hi):
    a=N.new('FunctionNodeCompare'); a.data_type='FLOAT'; a.operation='GREATER_THAN'; L.new(sock,a.inputs[0]); a.inputs[1].default_value=lo
    b=N.new('FunctionNodeCompare'); b.data_type='FLOAT'; b.operation='LESS_THAN'; L.new(sock,b.inputs[0]); b.inputs[1].default_value=hi
    x=N.new('FunctionNodeBooleanMath'); x.operation='AND'; L.new(a.outputs[0],x.inputs[0]); L.new(b.outputs[0],x.inputs[1]); return x.outputs[0]
both=N.new('FunctionNodeBooleanMath'); both.operation='AND'
L.new(rng(dot(u),S0+0.15,S1-0.15),both.inputs[0]); L.new(rng(dot(n),-0.6,TW+0.6),both.inputs[1])
dl=N.new('GeometryNodeDeleteGeometry'); dl.domain='FACE'; L.new(gi.outputs[0],dl.inputs['Geometry']); L.new(both.outputs[0],dl.inputs['Selection']); L.new(dl.outputs[0],go.inputs[0])
md=fp.modifiers.new('WS209_walk_apron_span_delete','NODES'); md.node_group=ng
print('F209 GN added; stack',[m.name for m in fp.modifiers][-3:],flush=True)
# --- 3h joint faces in span
jo=bpy.data.objects['Footpath control + expansion joints (3h)']; bm=bmesh.new(); bm.from_mesh(jo.data); mw=jo.matrix_world; dele=[]
for f in bm.faces:
    cc=mw@f.calc_center_median(); r=np.array([cc.x,cc.y])-O; s,t=r@u,r@n
    if -0.05<s<S1+0.05 and -0.4<t<TW+0.4: dele.append(f)
bmesh.ops.delete(bm,geom=dele,context='FACES'); bm.to_mesh(jo.data); bm.free(); print('F209 3h joint faces removed',len(dele),flush=True)
# --- tuck apron + fill under the slab
for o in (ap,fl):
    mw=o.matrix_world; inv=mw.inverted(); k=0
    for v in o.data.vertices:
        g=mw@v.co; r=np.array([g.x,g.y])-O; s,t=r@u,r@n
        if -0.02<=s<=S1+0.02 and -0.02<=t<=TW+0.02:
            zt=ztop(min(max(s,0),S1),min(max(t,0),TW))-0.015
            if g.z>zt: g.z=zt; v.co=inv@g; k+=1
    o.data.update(); print('F209 tucked',o.name,k,flush=True)
