# wf (Nov 7 2026): east-dorm 1 m LiDAR terrain patch (x50-300,y320-520) from 2017 B17 J5D6 ground class 2.
# Visible mesh WF_east_dorm_LiDAR_terrain_patch_UNVERIFIED; skirt dipped 6 cm under it via GN (mesh unedited);
# WD stair cutter also applied to the patch so the N landing opening is preserved; trees reseated at -0.25 m;
# WD walks re-draped; dense grass hidden if mostly floating/buried. REVERT=1 undoes.
import bpy, bmesh, os, json, math, time
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from collections import deque

t0=time.time()
ROOT='/workspace/nj-scenes/montclair-state'
os.chdir(ROOT)
REV=os.environ.get('REVERT')=='1'
SAVE=os.environ.get('SAVE')=='1'
PN='WF_east_dorm_LiDAR_terrain_patch_UNVERIFIED'
MODN='WF_skirt_under_east_dorm_patch'
BAK='data/wf/drape_bak.npz'
X0,X1,Y0,Y1=50.,300.,320.,520.
FEATHER=4.0
SINK_TREE=-0.25

def rm_wf():
    sk=bpy.data.objects.get('Context_skirt_3DEP_ortho_4km')
    if sk:
        m=sk.modifiers.get(MODN)
        if m:
            ng=m.node_group; sk.modifiers.remove(m)
            if ng and ng.users==0: bpy.data.node_groups.remove(ng)
        if 'UNVERIFIED_wf' in sk: del sk['UNVERIFIED_wf']
    o=bpy.data.objects.get(PN)
    if o:
        me=o.data; bpy.data.objects.remove(o, do_unlink=True); bpy.data.meshes.remove(me)
    for o in bpy.data.objects:
        if 'wf_dz' in o:
            o.location.z -= o['wf_dz']; del o['wf_dz']
    if os.path.exists(BAK):
        z=np.load(BAK)
        for k in z.files:
            o=bpy.data.objects.get(k)
            if o and o.type=='MESH' and o.get('wf_drape'):
                o.data.vertices.foreach_set('co', z[k].ravel()); o.data.update(); del o['wf_drape']
    gh='data/wf/grass_hidden.json'
    if os.path.exists(gh):
        for n in json.load(open(gh)).get('hidden',[]):
            o=bpy.data.objects.get(n)
            if o:
                o.hide_render=False; o.hide_viewport=False
                if 'wf_grass_hide' in o: del o['wf_grass_hide']

rm_wf()
if REV:
    print('WF reverted')
    if SAVE: bpy.ops.wm.save_mainfile()
    raise SystemExit(0)

D=np.load('data/wf/east_dorm_dtm_1m.npz')
filled=D['dtm_filled']; gc=D['count'].astype(np.int32)
ny,nx=filled.shape
MASK=np.load('data/wf/patch_mask.npz')
mark=MASK['mark'].astype(bool); inside_b=MASK['inside_b'].astype(bool)
print('MARK cells',int(mark.sum()),'/',nx*ny,'buildings_masked',int(inside_b.sum()))

sk=bpy.data.objects['Context_skirt_3DEP_ortho_4km']
dg=bpy.context.evaluated_depsgraph_get()
sv=[sk.matrix_world@v.co for v in sk.data.vertices]
bs_base=BVHTree.FromPolygons(sv, [tuple(p.vertices) for p in sk.data.polygons])
ske=sk.evaluated_get(dg)
sme=ske.to_mesh(); sev=[sk.matrix_world@v.co for v in sme.vertices]
bs_eval=BVHTree.FromPolygons(sev, [tuple(p.vertices) for p in sme.polygons]); ske.to_mesh_clear()

def skirt_z(x,y):
    h=bs_eval.ray_cast(Vector((x,y,400)), Vector((0,0,-1)))
    if h[0] is not None: return h[0].z
    h=bs_base.ray_cast(Vector((x,y,400)), Vector((0,0,-1)))
    return h[0].z if h[0] is not None else None

def hcell(i,j):
    zs=[]
    for jj in (j-1,j):
        for ii in (i-1,i):
            if 0<=ii<nx and 0<=jj<ny and np.isfinite(filled[jj,ii]):
                zs.append(filled[jj,ii])
    return float(np.mean(zs)) if zs else None

# distance-to-edge of mark
dist=np.full((ny,nx), 99.0)
edge=np.zeros_like(mark)
for j in range(ny):
    for i in range(nx):
        if not mark[j,i]: continue
        if i==0 or j==0 or i==nx-1 or j==ny-1 or (not mark[j,i-1]) or (not mark[j,i+1]) or (not mark[j-1,i]) or (not mark[j+1,i]):
            edge[j,i]=True; dist[j,i]=0.0
q=deque([(j,i) for j,i in zip(*np.nonzero(edge))])
while q:
    j,i=q.popleft()
    for dj,di in ((-1,0),(1,0),(0,-1),(0,1)):
        jj,ii=j+dj,i+di
        if 0<=jj<ny and 0<=ii<nx and mark[jj,ii] and dist[jj,ii]>dist[j,i]+1:
            dist[jj,ii]=dist[j,i]+1; q.append((jj,ii))
print('edge cells',int(edge.sum()),'max inward dist',float(dist[mark].max()) if mark.any() else 0)

# ortho UV fit from skirt
uvL=sk.data.uv_layers.active or sk.data.uv_layers[0]
A=[]; U=[]; V=[]; n_uv=0
for p in sk.data.polygons:
    c=sk.matrix_world@p.center
    if not (X0-50<=c.x<=X1+50 and Y0-50<=c.y<=Y1+50): continue
    for li in p.loop_indices:
        v=sk.matrix_world@sk.data.vertices[sk.data.loops[li].vertex_index].co
        uv=uvL.data[li].uv
        A.append([v.x,v.y,1]); U.append(uv[0]); V.append(uv[1])
    n_uv+=1
    if n_uv>=2500: break
A=np.array(A); cu=np.linalg.lstsq(A,np.array(U),rcond=None)[0]; cv=np.linalg.lstsq(A,np.array(V),rcond=None)[0]
print('UV faces',n_uv)

bm=bmesh.new(); vid={}
def vert(i,j):
    if (i,j) in vid: return vid[(i,j)]
    x=X0+i; y=Y0+j
    z=hcell(i,j)
    if z is None: z=130.0
    dd=99.0
    for jj in (j-1,j):
        for ii in (i-1,i):
            if 0<=ii<nx and 0<=jj<ny and mark[jj,ii]:
                dd=min(dd, dist[jj,ii])
            else:
                dd=min(dd, 0.0)
    if dd < FEATHER:
        w = dd / FEATHER
        w = w*w*(3-2*w)
        sz=skirt_z(x,y)
        if sz is not None and sz > 125 and abs(sz-z)<8.0:
            z = sz*(1-w) + z*w
    v=bm.verts.new((x,y,z)); vid[(i,j)]=v; return v

nfaces=0
for j in range(ny):
    for i in range(nx):
        if not mark[j,i]: continue
        try:
            f=bm.faces.new([vert(i,j), vert(i+1,j), vert(i+1,j+1), vert(i,j+1)])
            f.smooth=True; nfaces+=1
        except ValueError:
            pass
print('PATCH faces',nfaces,'verts',len(bm.verts))
uvlayer=bm.loops.layers.uv.new('ortho')
for f in bm.faces:
    for l in f.loops:
        co=l.vert.co
        l[uvlayer].uv=(cu[0]*co.x+cu[1]*co.y+cu[2], cv[0]*co.x+cv[1]*co.y+cv[2])
    if f.normal.z<0: f.normal_flip()

me=bpy.data.meshes.new(PN); bm.to_mesh(me); bm.free()
mat=sk.data.materials[0] if sk.data.materials else None
if mat: me.materials.append(mat)
P=bpy.data.objects.new(PN, me)
P['wf_obj']=1
P['UNVERIFIED']='east-dorm 1m LiDAR DTM patch from 2017 B17 J5D6 class 2; feathered 4m into skirt; buildings masked'
sk.users_collection[0].objects.link(P)

cut=bpy.data.objects.get('WD_skirt_cutter_Bohn_N_steps')
if cut:
    md=P.modifiers.new('WF_cut_Bohn_N_steps','BOOLEAN')
    md.operation='DIFFERENCE'; md.object=cut; md.solver='EXACT'
    print('PATCH boolean WD cutter applied')

# GN: dip skirt 6 cm under patch (QD-style)
ng=bpy.data.node_groups.new(MODN,'GeometryNodeTree')
ng.interface.new_socket('Geometry',in_out='INPUT',socket_type='NodeSocketGeometry')
ng.interface.new_socket('Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
N=ng.nodes; Lnk=ng.links
gi=N.new('NodeGroupInput'); go=N.new('NodeGroupOutput')
pos=N.new('GeometryNodeInputPosition'); sxyz=N.new('ShaderNodeSeparateXYZ'); Lnk.new(pos.outputs[0],sxyz.inputs[0])
def cmp(sock,val,op):
    c=N.new('FunctionNodeCompare'); c.data_type='FLOAT'; c.operation=op; Lnk.new(sock,c.inputs[0]); c.inputs[1].default_value=val; return c.outputs[0]
def band(a,b):
    n=N.new('FunctionNodeBooleanMath'); n.operation='AND'; Lnk.new(a,n.inputs[0]); Lnk.new(b,n.inputs[1]); return n.outputs[0]
MARG=6.0
sel=band(band(cmp(sxyz.outputs[0],X0-MARG,'GREATER_THAN'),cmp(sxyz.outputs[0],X1+MARG,'LESS_THAN')),
         band(cmp(sxyz.outputs[1],Y0-MARG,'GREATER_THAN'),cmp(sxyz.outputs[1],Y1+MARG,'LESS_THAN')))
oi=N.new('GeometryNodeObjectInfo'); oi.transform_space='RELATIVE'; oi.inputs['Object'].default_value=P
gp=N.new('GeometryNodeProximity'); gp.target_element='FACES'; Lnk.new(oi.outputs['Geometry'],gp.inputs[0])
sel=band(sel, cmp(gp.outputs['Distance'], 8.0, 'LESS_THAN'))
sep=N.new('GeometryNodeSeparateGeometry'); sep.domain='FACE'
Lnk.new(gi.outputs[0],sep.inputs[0]); Lnk.new(sel,sep.inputs[1])
sub=N.new('GeometryNodeSubdivideMesh'); sub.inputs['Level'].default_value=2
Lnk.new(sep.outputs[0],sub.inputs[0])
oi2=N.new('GeometryNodeObjectInfo'); oi2.transform_space='RELATIVE'; oi2.inputs['Object'].default_value=P
rc=N.new('GeometryNodeRaycast'); Lnk.new(oi2.outputs['Geometry'],rc.inputs['Target Geometry'])
pos2=N.new('GeometryNodeInputPosition')
add=N.new('ShaderNodeVectorMath'); add.operation='ADD'; Lnk.new(pos2.outputs[0],add.inputs[0]); add.inputs[1].default_value=(0,0,50)
Lnk.new(add.outputs[0],rc.inputs['Source Position']); rc.inputs['Ray Direction'].default_value=(0,0,-1); rc.inputs['Ray Length'].default_value=200
hz=N.new('ShaderNodeSeparateXYZ'); Lnk.new(rc.outputs['Hit Position'],hz.inputs[0])
pz=N.new('ShaderNodeSeparateXYZ'); Lnk.new(pos2.outputs[0],pz.inputs[0])
d=N.new('ShaderNodeMath'); d.operation='SUBTRACT'; Lnk.new(pz.outputs[2],d.inputs[0]); Lnk.new(hz.outputs[2],d.inputs[1])
c1=cmp(d.outputs[0], -0.5, 'GREATER_THAN'); c2=cmp(d.outputs[0], 6.0, 'LESS_THAN')
s=band(band(c1,c2), rc.outputs['Is Hit'])
tz=N.new('ShaderNodeMath'); tz.operation='SUBTRACT'; Lnk.new(hz.outputs[2],tz.inputs[0]); tz.inputs[1].default_value=0.06
cxyz=N.new('ShaderNodeCombineXYZ'); Lnk.new(pz.outputs[0],cxyz.inputs[0]); Lnk.new(pz.outputs[1],cxyz.inputs[1]); Lnk.new(tz.outputs[0],cxyz.inputs[2])
sp=N.new('GeometryNodeSetPosition'); Lnk.new(sub.outputs[0],sp.inputs['Geometry']); Lnk.new(s,sp.inputs['Selection']); Lnk.new(cxyz.outputs[0],sp.inputs['Position'])
jo=N.new('GeometryNodeJoinGeometry'); Lnk.new(sp.outputs[0],jo.inputs[0]); Lnk.new(sep.outputs[1],jo.inputs[0])
Lnk.new(jo.outputs[0],go.inputs[0])
md=sk.modifiers.new(MODN,'NODES'); md.node_group=ng
bpy.context.view_layer.objects.active=sk
# move modifier to end
for _ in range(12):
    if sk.modifiers[-1]==md: break
    try: bpy.ops.object.modifier_move_down(modifier=MODN)
    except Exception: break
sk['UNVERIFIED_wf']='wf: skirt dipped 6cm under WF east-dorm LiDAR patch where overlapping (GN, mesh unedited)'
print('SKIRT GN applied, mods',[m.name for m in sk.modifiers])

bpy.context.view_layer.update()
dg=bpy.context.evaluated_depsgraph_get()

Pe=P.evaluated_get(dg)
pme=Pe.to_mesh(); pvs=[P.matrix_world@v.co for v in pme.vertices]; pfs=[tuple(p.vertices) for p in pme.polygons]
print('PATCH eval faces',len(pfs),'verts',len(pvs))
bp=BVHTree.FromPolygons(pvs,pfs); Pe.to_mesh_clear()
ske=sk.evaluated_get(dg); sme=ske.to_mesh(); svs=[sk.matrix_world@v.co for v in sme.vertices]
bs=BVHTree.FromPolygons(svs,[tuple(p.vertices) for p in sme.polygons]); ske.to_mesh_clear()

def ground_z(x,y):
    h=bp.ray_cast(Vector((x,y,400)), Vector((0,0,-1)))
    if h[0] is not None: return h[0].z, 'patch'
    h=bs.ray_cast(Vector((x,y,400)), Vector((0,0,-1)))
    if h[0] is not None: return h[0].z, 'skirt'
    return None, None

Lobj=bpy.data.objects['TK_Bohn_landing_N_steps_UNVERIFIED']
LV=[Lobj.matrix_world@v.co for v in Lobj.data.vertices]
land_dz=[]; top_dz=[]
for p in LV:
    gz,_=ground_z(p.x,p.y)
    if gz is not None:
        land_dz.append(gz-p.z)
        if p.z>132.3: top_dz.append(gz-p.z)
stair_decision='leave_stair_door_fixed'
valid=[d for d in top_dz if abs(d)<3.0]
if valid:
    med=float(np.median(valid))
    stair_decision=f'leave (|med_dz|={round(abs(med),3)} {"OK" if abs(med)<=0.15 else "gt0.15_but_door_fixed"})'
print('STAIR_DECISION',stair_decision,'top_dz',[round(d,3) for d in top_dz])

reseat=[]
for o in bpy.data.objects:
    if not o.name.startswith('TL_tree') or o.type!='MESH': continue
    p=o.matrix_world.translation
    if not (X0<=p.x<X1 and Y0<=p.y<Y1): continue
    mw=o.matrix_world
    bases=[(mw@v.co).z for v in o.data.vertices if ((mw@v.co).xy-p.xy).length<0.3]
    tb=min(bases) if bases else p.z
    gz,src=ground_z(p.x,p.y)
    if gz is None: continue
    d=(gz+SINK_TREE)-tb
    if abs(d)>0.08:
        o.location.z += d
        o['wf_dz']=round(float(o.get('wf_dz',0.0))+d,3)
        reseat.append([o.name, round(d,3), src])
print('RESEAT trees',len(reseat))

bak={}; draped=[]
for nm in ['WD_walk_1132693523_UNVERIFIED','WD_walk_600258640_UNVERIFIED','TK_Bohn_landing_W_walk_UNVERIFIED']:
    o=bpy.data.objects.get(nm)
    if not o or o.type!='MESH': continue
    n=len(o.data.vertices); co=np.zeros(n*3,np.float32); o.data.vertices.foreach_get('co',co); co=co.reshape(n,3)
    M=np.array(o.matrix_world); Wco=co@M[:3,:3].T+M[:3,3]
    dz=np.zeros(n); ok=np.zeros(n,bool)
    for i in range(n):
        x,y,z=Wco[i]
        gz,src=ground_z(x,y)
        if gz is None: continue
        d=(gz+0.05)-z
        if abs(d)>0.02 and abs(d)<2.5:
            dz[i]=d; ok[i]=True
    if ok.sum()<3: continue
    bak[nm]=co.copy()
    W2=Wco.copy(); W2[ok,2]+=dz[ok]
    invR=np.linalg.inv(M[:3,:3]).T
    co2=(W2-M[:3,3])@invR
    o.data.vertices.foreach_set('co', co2.astype(np.float32).ravel()); o.data.update()
    o['wf_drape']=1
    draped.append([nm,int(ok.sum()),round(float(dz[ok].min()),3),round(float(dz[ok].max()),3),round(float(dz[ok].mean()),3)])
print('DRAPED',draped)

hidden=[]
for o in bpy.data.objects:
    if o.type!='MESH': continue
    if 'grass' not in o.name.lower() and 'Grass' not in o.name: continue
    if o.hide_render: continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    if max(p.x for p in bb)<X0 or min(p.x for p in bb)>X1 or max(p.y for p in bb)<Y0 or min(p.y for p in bb)>Y1: continue
    n=len(o.data.vertices)
    if n==0: continue
    step=max(1,n//200)
    bad=0; tot=0; mw=o.matrix_world
    for vi in range(0,n,step):
        p=mw@o.data.vertices[vi].co
        if not (X0<=p.x<X1 and Y0<=p.y<Y1): continue
        gz,src=ground_z(p.x,p.y)
        if gz is None or src!='patch': continue
        tot+=1
        if p.z > gz+0.45 or p.z < gz-0.35: bad+=1
    if tot>=5 and bad/tot > 0.35:
        if n < 50:
            p=mw.translation; gz,src=ground_z(p.x,p.y)
            if gz is not None:
                d=(gz+0.02)-min((mw@Vector(c)).z for c in o.bound_box)
                if abs(d)>0.05:
                    o.location.z+=d; o['wf_dz']=round(d,3)
        else:
            o.hide_render=True; o.hide_viewport=True; o['wf_grass_hide']=1; hidden.append(o.name)
print('GRASS_HIDDEN',len(hidden))

if bak: np.savez(BAK, **bak)
json.dump(dict(hidden=hidden), open('data/wf/grass_hidden.json','w'), indent=1)

checks=[]
for x,y,lab in [(212,405,'W_door'),(228.8,412.7,'N_land'),(250,400,'east'),(180,380,'west'),(100,350,'SW'),(280,450,'NE')]:
    gz,src=ground_z(x,y)
    checks.append(dict(lab=lab,x=x,y=y,gz=round(gz,3) if gz else None,src=src))
print('CHECKS',checks)

off=0
for o in bpy.data.objects:
    if not o.name.startswith('TL_tree') or o.type!='MESH': continue
    p=o.matrix_world.translation
    if not (X0<=p.x<X1 and Y0<=p.y<Y1): continue
    mw=o.matrix_world
    bases=[(mw@v.co).z for v in o.data.vertices if ((mw@v.co).xy-p.xy).length<0.3]
    tb=min(bases) if bases else p.z
    gz,_=ground_z(p.x,p.y)
    if gz is None: continue
    if abs((gz+SINK_TREE)-tb)>0.15: off+=1
print('TREES still off>0.15m',off)

rep=dict(mark_cells=int(mark.sum()), patch_faces=nfaces, patch_eval_faces=len(pfs),
         reseat_n=len(reseat), reseat_sample=reseat[:20], draped=draped,
         grass_hidden=len(hidden), stair_decision=stair_decision,
         landing_dz=[round(d,3) for d in land_dz], top_dz=[round(d,3) for d in top_dz],
         checks=checks, trees_off=off, elapsed=round(time.time()-t0,1),
         objs=len(bpy.data.objects))
json.dump(rep, open('data/wf/apply.json','w'), indent=1)
print('APPLY', {k:rep[k] for k in ('mark_cells','patch_faces','reseat_n','stair_decision','trees_off','elapsed','objs')})

if SAVE:
    bpy.ops.wm.save_mainfile()
    print('SAVED',len(bpy.data.objects))
print('WF_DONE',round(time.time()-t0,1),'s')
