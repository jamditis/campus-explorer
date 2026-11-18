"""wu fix2: (a) confirm WU GN reads wu_in; (b) recompute wu_in so building-hole
edges are not treated as open-to-skirt (only true skirt-facing edges gate the dip);
(c) snap x=80 verts onto WT's x=80 verts by matching y (ray at x=80 missed the boundary);
(d) re-check skirt poke."""
import bpy, json, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree
R='/workspace/nj-scenes/montclair-state'
O=bpy.data.objects
E=O['WU_richardson_reid_LiDAR_patch_UNVERIFIED']; WT=O['WT_richardson_west_LiDAR_patch_UNVERIFIED']
sk=O['Context_skirt_3DEP_ortho_4km']
ng=bpy.data.node_groups['WU_skirt_under_richardson_reid']
names=[]
for n in ng.nodes:
    if n.bl_idname=='GeometryNodeInputNamedAttribute':
        val=n.inputs['Name'].default_value
        names.append(val)
        if val in ('wt_in','wo_in',''):
            n.inputs['Name'].default_value='wu_in'
            print('FIXED attr name',val,'-> wu_in',flush=True)
print('NAMED ATTRS',names,flush=True)
# object info target
for n in ng.nodes:
    if n.bl_idname=='GeometryNodeObjectInfo':
        print('OBJINFO',n.inputs['Object'].default_value.name if n.inputs['Object'].default_value else None,flush=True)

def ss(t):
    t=min(max(t,0.0),1.0); return t*t*(3-2*t)
def bvh(o,ev=True):
    dg=bpy.context.evaluated_depsgraph_get()
    if ev:
        e=o.evaluated_get(dg); m=e.to_mesh(); b=BVHTree.FromPolygons([o.matrix_world@v.co for v in m.vertices],[tuple(p.vertices) for p in m.polygons]); e.to_mesh_clear(); return b
    return BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons])
def hz(b,x,y):
    h=b.ray_cast(Vector((x,y,500)),Vector((0,0,-1))); return h[0].z if h[0] is not None else None

me=E.data; mw=E.matrix_world; mi=mw.inverted()
# (c) snap x=80 to WT
wt_by_y={}
mwT=WT.matrix_world
for v in WT.data.vertices:
    c=mwT@v.co
    if abs(c.x-80)<0.08: wt_by_y.setdefault(round(c.y,2),[]).append(c.z)
nsh=0; mx=0.0; pairs=[]
for v in me.vertices:
    c=mw@v.co
    if abs(c.x-80)>0.01: continue
    ys=[y for y in wt_by_y if abs(y-c.y)<0.02]
    if not ys: continue
    zt=float(np.median(wt_by_y[min(ys,key=lambda y:abs(y-c.y))]))
    d=zt-c.z
    if abs(d)>1e-4:
        c.z=zt; v.co=mi@c; nsh+=1; mx=max(mx,abs(d)); pairs.append([round(c.y,2),round(d,4)])
me.update()
print('SNAP x80',nsh,'max',round(mx,4),'n_wt_y',len(wt_by_y),'eg',pairs[:8],flush=True)

# (b) wu_in
cnt={}
for p in me.polygons:
    for ek in p.edge_keys: cnt[ek]=cnt.get(ek,0)+1
bv=set()
for ek,c in cnt.items():
    if c==1: bv.update(ek)
kt=KDTree(max(1,len(bv)))
for i in bv: kt.insert(me.vertices[i].co,i)
kt.balance()
grounds=[bvh(O[n]) for n in ('WT_richardson_west_LiDAR_patch_UNVERIFIED','QW_DTM_north_edge_ramp_UNVERIFIED','WF_east_dorm_LiDAR_terrain_patch_UNVERIFIED','RZ2_SC_LiDAR_ground_patch_UNVERIFIED','Terrain_LiDAR_DTM_1m')]
FP=['QT_Richardson_base_plinth_UNVERIFIED','QP_Richardson_ground_storey_glass_piers_UNVERIFIED','QP_Richardson_white_corner_towers_UNVERIFIED','QU_G_floor_UNVERIFIED']
bld=[bvh(O[n],False) for n in FP]
BE=bvh(E,False)
opn=[]
for i in bv:
    c=mw@me.vertices[i].co
    for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)):
        x,y=c.x+0.7*dx,c.y+0.7*dy
        if hz(BE,x,y) is not None: continue
        if any(hz(b,x,y) is not None for b in grounds): continue
        if any(hz(b,c.x+d*dx,c.y+d*dy) is not None for d in (0.5,1.0,1.5,2.0,2.5,3.0) for b in bld):
            continue
        opn.append(i); break
print('OPEN skirt-facing',len(opn),'of',len(bv),flush=True)
ko=KDTree(max(1,len(opn)))
for i in opn: ko.insert(me.vertices[i].co,i)
ko.balance()
a=me.attributes['wu_in']
for v in me.vertices:
    _,_,d=kt.find(v.co); w=ss(d/0.8)
    if opn:
        _,_,do=ko.find(v.co); w=min(w,ss((do-4.5)/4.0))
    a.data[v.index].value=0.40*w
me.update()
bpy.context.view_layer.update()
dg=bpy.context.evaluated_depsgraph_get()
BE2=bvh(E); BS=bvh(sk)
pk=0; pkmax=0.0; hist={}
for p in me.polygons:
    c=p.center
    for fx,fy in ((0,0),(0.25,0.25),(-0.25,0.25),(0.25,-0.25),(-0.25,-0.25)):
        x,y=c.x+fx,c.y+fy
        h=BE2.ray_cast(Vector((x,y,500)),Vector((0,0,-1)))[0]
        s=BS.ray_cast(Vector((x,y,500)),Vector((0,0,-1)))[0]
        if h is not None and s is not None and s.z>h.z-0.003:
            pk+=1; d=s.z-h.z; pkmax=max(pkmax,d)
            k=int(x)//4*4; hist.setdefault(k,[0,0.0]); hist[k][0]+=1; hist[k][1]=max(hist[k][1],round(d,3))
print('POKE',pk,round(pkmax,3),sorted(hist.items()),flush=True)
r=json.load(open(f'{R}/data/wu/fix_report.json'))
r['fix2_named_attrs']=names
r['fix2_x80_snap']=[nsh,round(mx,4),len(wt_by_y)]
r['fix2_open']=[len(opn),len(bv)]
r['fix2_poke']=[pk,round(pkmax,3),sorted((k,v) for k,v in hist.items())]
json.dump(r,open(f'{R}/data/wu/fix_report.json','w'),indent=1)
bpy.ops.wm.save_mainfile(); print('SAVED',flush=True)
