# ws172: UNIFY #77 — S of Normal Ave W beyond the WS110 lawn patch the dark 3DEP skirt showed (hard diagonal near y -290; skirt up to
# 0.64 m below the 2023 LiDAR DTM under yard trees; sliver at the S walk back lip). Fix: front-yard ground patch on a NEW class-2 DTM
# (prep/ws172_s77/dtm172.npy from the J5D5 2023 tile, 0.5 m, x -360..-270, y -315..-255), from the S walk back edge (s-0.3) south to the
# house fronts (LiDAR class-6 footprints dilated 1.2 m are left OUT: houses are beyond the modelling edge, not invented) and to y -301;
# soft 3 m alpha fade toward houses / outer edges (not toward the walk); z = min(DTM-0.03, WS110 patch-0.03) so WS110 stays on top;
# hidden target + skirt GN drop (WS163 group copy) so the skirt sinks under it. Idempotent.
import bpy, bmesh, math, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
OB=bpy.data.objects; R0='/workspace/nj-scenes/montclair-state/prep/ws172_s77/'
D=np.load(R0+'dtm172.npy')[0]; X0,Y0,R=-360.0,-315.0,0.5
def dz(x,y):
    fi=(x-X0)/R-0.5; fj=(y-Y0)/R-0.5
    i=int(min(max(math.floor(fi),0),D.shape[1]-2)); j=int(min(max(math.floor(fj),0),D.shape[0]-2)); tx=min(max(fi-i,0),1); ty=min(max(fj-j,0),1)
    return float(D[j,i]*(1-tx)*(1-ty)+D[j,i+1]*tx*(1-ty)+D[j+1,i]*(1-tx)*ty+D[j+1,i+1]*tx*ty)
P=np.load(R0+'las172.npy'); H=P[(P[:,3]==6)][:,:2]
HM=np.zeros((120,180),bool); hi=((H[:,0]-X0)/R).astype(int).clip(0,179); hj=((H[:,1]-Y0)/R).astype(int).clip(0,119); HM[hj,hi]=True
# dilate 1.2 m (close small holes first)
from itertools import product
K=3
M=HM.copy()
for a,b in product(range(-K,K+1),repeat=2):
    if a*a+b*b<=K*K: M|=np.roll(np.roll(HM,a,0),b,1)
def house(x,y):
    i=int((x-X0)/R); j=int((y-Y0)/R); return bool(M[min(max(j,0),119),min(max(i,0),179)])
import os
NOHOUSE=os.environ.get('NOHOUSE','1')=='1'  # ws172d: footprints filled (the hole read as a dark pit at eye level); houses = UNIFY #78
for o in [o for o in OB if o.name.startswith('WS172_')]: OB.remove(o)
A=np.array([-268.8,-262.9]); N=np.array([0.236,1.0]); N/=np.linalg.norm(N)
sw=OB['WS163_NormalAve_W_S_sidewalk_1p6m_UNVERIFIED']
sback=min(float(np.dot(np.array(((sw.matrix_world@v.co).x,(sw.matrix_world@v.co).y))-A,N)) for v in sw.data.vertices)
p110=OB['WS110_ground_patch_S_of_y-238_DTM2023_1m_lawn_UNVERIFIED']
V=[p110.matrix_world@v.co for v in p110.data.vertices]; T110=BVHTree.FromPolygons(V,[list(pp.vertices) for pp in p110.data.polygons])
XS=np.arange(-346.0,-283.99,1.0); YS=np.arange(-301.0,-261.99,1.0); nx,ny=len(XS),len(YS)
valid=np.zeros((ny,nx),bool); outer=np.zeros((ny,nx),bool)
for j,y in enumerate(YS):
    for i,x in enumerate(XS):
        s=float(np.dot(np.array((x,y))-A,N))
        if s>sback-0.05: continue   # ws172b: reach the walk back edge (sliver at the lip)
        if house(x,y) and not NOHOUSE: outer[j,i]=True; continue
        valid[j,i]=True
# distance (in m) to outer invalid (houses or rect S/E/W edge), via BFS-ish chamfer
dist=np.full((ny,nx),99.0)
src=outer.copy(); src[0,:]=True; src[:,0]=True; src[:,-1]=True
dist[src]=0
for it in range(6):
    for j in range(ny):
        for i in range(nx):
            if dist[j,i]==0: continue
            m=dist[j,i]
            for a,b,c in ((-1,0,1),(1,0,1),(0,-1,1),(0,1,1),(-1,-1,1.41),(1,1,1.41),(-1,1,1.41),(1,-1,1.41)):
                jj,ii=j+a,i+b
                if 0<=jj<ny and 0<=ii<nx: m=min(m,dist[jj,ii]+c)
            dist[j,i]=m
fade=np.clip((dist-1.0)/3.0,0,1)  # edge verts fully transparent (ws172 review: 33% hard rim)
bm=bmesh.new(); G={}; fl=bm.verts.layers.float.new('fade172'); nlow=0
for j,y in enumerate(YS):
    for i,x in enumerate(XS):
        if not valid[j,i]: continue
        z=dz(x,y)-0.03
        h=T110.ray_cast(Vector((x,y,300)),Vector((0,0,-1)))
        if h[0] is not None and h[0].z-0.03<z: z=h[0].z-0.03; nlow+=1
        v=bm.verts.new((x,y,z)); v[fl]=float(fade[j,i]); G[(j,i)]=v
for j in range(ny-1):
    for i in range(nx-1):
        q=[(j,i),(j,i+1),(j+1,i+1),(j+1,i)]
        if all(k in G for k in q): bm.faces.new([G[k] for k in q])
for v in [v for v in bm.verts if not v.link_faces]: bm.verts.remove(v)
for f in bm.faces:
    f.normal_update()
    if f.normal.z<0: f.normal_flip()
me=bpy.data.meshes.new('WS172_frontyards_S_of_NormalAve_W_DTM2023_J5D5'); bm.to_mesh(me); bm.free()
src_mat=p110.data.materials[0] if p110.data.materials else None
mat=bpy.data.materials.get('WS172_lawn_fade')
if mat is None and src_mat is not None:
    mat=src_mat.copy(); mat.name='WS172_lawn_fade'; nt=mat.node_tree
    out=[n for n in nt.nodes if n.type=='OUTPUT_MATERIAL' and n.is_active_output][0]
    l=out.inputs['Surface'].links[0]; srcsock=l.from_socket; nt.links.remove(l)
    at=nt.nodes.new('ShaderNodeAttribute'); at.attribute_name='fade172'; at.attribute_type='GEOMETRY'
    tr=nt.nodes.new('ShaderNodeBsdfTransparent'); mx=nt.nodes.new('ShaderNodeMixShader')
    nt.links.new(at.outputs['Fac'],mx.inputs[0]); nt.links.new(tr.outputs[0],mx.inputs[1]); nt.links.new(srcsock,mx.inputs[2]); nt.links.new(mx.outputs[0],out.inputs['Surface'])
    try: mat.blend_method='HASHED'
    except Exception: pass
me.materials.append(mat)
uv=me.uv_layers.new(name='UVMap')
for lp in me.loops:
    pp=me.vertices[lp.vertex_index].co; uv.data[lp.index].uv=(pp.x*0.25,pp.y*0.25)
col=p110.users_collection[0]
ob=OB.new('WS172_frontyards_S_of_NormalAve_W_DTM2023_J5D5',me); col.objects.link(ob)
print('FIX172 patch faces',len(me.polygons),'verts',len(me.vertices),'lowered-under-WS110',nlow,'sback',round(sback,2),'src mat',src_mat.name if src_mat else None,flush=True)
print('FIX172 WS110 modifiers',[m.type+':'+m.name for m in p110.modifiers],flush=True)
# hidden skirt target + GN drop
tb=bmesh.new()
for pg in me.polygons: tb.faces.new([tb.verts.new(me.vertices[k].co.copy()) for k in pg.vertices])
tm=bpy.data.meshes.new('WS172_skirt_target_hidden'); tb.to_mesh(tm); tb.free()
a=tm.attributes.new('wv_in','FLOAT','POINT'); a.data.foreach_set('value',[0.10]*len(tm.vertices))
tgt=OB.new('WS172_skirt_target_hidden',tm); col.objects.link(tgt); tgt.hide_render=True; tgt.hide_viewport=True
xs_=[v.co.x for v in tm.vertices]; ys_=[v.co.y for v in tm.vertices]
sk=OB['Context_skirt_3DEP_ortho_4km']
for m_ in [m_ for m_ in sk.modifiers if m_.name.startswith('WS172_')]: sk.modifiers.remove(m_)
ng=bpy.data.node_groups['WS163_skirt_under_normalave_W'].copy(); ng.name='WS172_skirt_under_frontyards_S_NormalAve_W'; Nn=ng.nodes
Nn['Compare'].inputs[1].default_value=min(xs_)-1; Nn['Compare.001'].inputs[1].default_value=max(xs_)+1
Nn['Compare.002'].inputs[1].default_value=min(ys_)-1; Nn['Compare.003'].inputs[1].default_value=max(ys_)+1
Nn['Object Info'].inputs['Object'].default_value=tgt; Nn['Subdivide Mesh'].inputs['Level'].default_value=3
mod=sk.modifiers.new('WS172_skirt_under_frontyards_S_NormalAve_W','NODES'); mod.node_group=ng
print('FIX172 GN bounds',round(min(xs_),1),round(max(xs_),1),round(min(ys_),1),round(max(ys_),1),'skirt mods',[m.name for m in sk.modifiers][-4:],flush=True)
bpy.context.view_layer.update(); dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
for (x,y) in [(-310,-280),(-296,-270),(-320,-290),(-300,-295),(-335,-285),(-290,-288),(-340,-272),(-286,-298),(-315,-268),(-326,-296)]:
    hit,loc,nor,idx,o,_=sc.ray_cast(dg,Vector((x,y,170)),Vector((0,0,-1)))
    k=0
    while hit and k<4 and ('tree' in o.name.lower() or 'Tree' in o.name or 'UTIL' in o.name.upper()):
        hit,loc,nor,idx,o,_=sc.ray_cast(dg,Vector((x,y,loc.z-0.02)),Vector((0,0,-1))); k+=1
    print('PROBE172',x,y,o.name[:44] if hit else None,round(loc.z-dz(x,y),2) if hit else None,flush=True)
