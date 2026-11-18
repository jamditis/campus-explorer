"""wt fix2 (rev3: no dip within 4.5 m of an open skirt edge, then 4 m fade; first try 0.3+5 m left a 7-14 cm step at x=80): deepen the skirt dip in the patch interior (wt_in = 0.40*ss(dist_to_patch_boundary/0.8 m)); dip = wt_in + 0.02.
Fixes skirt (4.4 m eval triangles) poking through the 1 m patch in concave spots. Boundary keeps the 2 cm tuck."""
import bpy, json, math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree
R='/workspace/nj-scenes/montclair-state'
O=bpy.data.objects; E=O['WT_richardson_west_LiDAR_patch_UNVERIFIED']; sk=O['Context_skirt_3DEP_ortho_4km']; me=E.data
def ss(t):
    t=min(max(t,0.0),1.0); return t*t*(3-2*t)
cnt={}
for p in me.polygons:
    for ek in p.edge_keys: cnt[ek]=cnt.get(ek,0)+1
bv=set()
for ek,c in cnt.items():
    if c==1: bv.update(ek)
kt=KDTree(len(bv))
for i in bv: kt.insert(me.vertices[i].co,i)
kt.balance()
# review fix: boundary verts open to bare skirt (east feather x=80, other skirt-facing edges) need the skirt dip faded over ~5 m
# (skirt eval triangles ~4.4 m), otherwise the dipped skirt drops away under the open edge and shows a dark step (eye-from-E view).
dg0=bpy.context.evaluated_depsgraph_get()
def bvh0(o):
    e=o.evaluated_get(dg0); mm=e.to_mesh(); b=BVHTree.FromPolygons([o.matrix_world@v.co for v in mm.vertices],[tuple(p.vertices) for p in mm.polygons]); e.to_mesh_clear(); return b
NB=[bvh0(O[n]) for n in ('RZ2_SC_LiDAR_ground_patch_UNVERIFIED','QW_DTM_north_edge_ramp_UNVERIFIED','WF_east_dorm_LiDAR_terrain_patch_UNVERIFIED','Terrain_LiDAR_DTM_1m','QT_Richardson_base_plinth_UNVERIFIED','QP_Richardson_ground_storey_glass_piers_UNVERIFIED','QP_Richardson_white_corner_towers_UNVERIFIED','QU_G_floor_UNVERIFIED','MO Health Drop-In Center walls+parapet+roof (best-effort; UNVER')]
BE0=bvh0(E)
def hit(b,x,y): return b.ray_cast(Vector((x,y,500)),Vector((0,0,-1)))[0] is not None
opn=[]
for i in bv:
    c=E.matrix_world@me.vertices[i].co
    for dx,dy in ((0.7,0),(-0.7,0),(0,0.7),(0,-0.7)):
        x,y=c.x+dx,c.y+dy
        if not hit(BE0,x,y) and not any(hit(b,x,y) for b in NB): opn.append(i); break
ko=KDTree(max(1,len(opn)))
for i in opn: ko.insert(me.vertices[i].co,i)
ko.balance()
a=me.attributes['wt_in']
for v in me.vertices:
    _,_,d=kt.find(v.co); w=ss(d/0.8)
    if opn:
        _,_,do=ko.find(v.co); w=min(w,ss((do-4.5)/4.0))
    a.data[v.index].value=0.40*w
me.update()
print('OPEN boundary verts',len(opn),'of',len(bv))
me.update()
ng=bpy.data.node_groups['WT_skirt_under_richardson_west']; m=ng.nodes['Math.001']
print('MATH001 before',[ (i.is_linked, round(i.default_value,3)) for i in m.inputs])
m.inputs[1].default_value=1.0; m.inputs[2].default_value=0.02
print('MATH001 after',[ (i.is_linked, round(i.default_value,3)) for i in m.inputs])
bpy.context.view_layer.update(); dg=bpy.context.evaluated_depsgraph_get()
def bvh(o):
    e=o.evaluated_get(dg); mm=e.to_mesh(); b=BVHTree.FromPolygons([o.matrix_world@v.co for v in mm.vertices],[tuple(p.vertices) for p in mm.polygons]); e.to_mesh_clear(); return b
BE=bvh(E); BS=bvh(sk)
hist={}; tot=0; PTS=[]
for p in me.polygons:
    c=p.center
    for fx,fy in ((0,0),(0.25,0.25),(-0.25,0.25),(0.25,-0.25),(-0.25,-0.25)):
        x,y=c.x+fx,c.y+fy
        h=BE.ray_cast(Vector((x,y,500)),Vector((0,0,-1)))[0]; s=BS.ray_cast(Vector((x,y,500)),Vector((0,0,-1)))[0]
        if h is not None and s is not None and s.z>h.z-0.003:
            tot+=1; PTS.append((round(x,1),round(y,1),round(s.z-h.z,2),round(kt.find(Vector((x,y,h.z)))[2],1))); k=int(x)//4*4; hist.setdefault(k,[0,0.0]); hist[k][0]+=1; hist[k][1]=max(hist[k][1],round(s.z-h.z,3))
print("POKE total",tot,sorted(hist.items())); print("PTS",PTS[:60])
r=json.load(open(f'{R}/data/wt/fix_report.json')); r['fix2_poke']=[tot,sorted(hist.items())]; json.dump(r,open(f'{R}/data/wt/fix_report.json','w'),indent=1)
bpy.ops.wm.save_mainfile(); print('SAVED')
