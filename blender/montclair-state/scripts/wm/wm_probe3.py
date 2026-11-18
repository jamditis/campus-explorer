import bpy, bmesh, json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.geometry import intersect_point_line
dg=bpy.context.evaluated_depsgraph_get()
J=json.load(open('scripts/wm/stone_base.json'))
GN=['QW_DTM_north_edge_ramp_UNVERIFIED','WV_stone_west_LiDAR_patch_UNVERIFIED','Context_skirt_3DEP_ortho_4km','WN_south_wood_LiDAR_patch_ext_UNVERIFIED','WO_gully_head_LiDAR_patch_UNVERIFIED','Terrain_LiDAR_DTM_1m']
for n in GN:
    o=bpy.data.objects[n]; print('VIS',n,o.visible_get(),o.hide_render,len(o.data.vertices))
trees={}
for n in GN:
    o=bpy.data.objects[n]; e=o.evaluated_get(dg); m=e.to_mesh()
    bm=bmesh.new(); bm.from_mesh(m); bm.transform(o.matrix_world)
    trees[n]=BVHTree.FromBMesh(bm); bm.free(); e.to_mesh_clear()
hard=[o for o in bpy.data.objects if o.type=='MESH' and any(k in o.name for k in ('footway','service','soil_edge','walk','steps','Walk'))]
hv=[]
for o in hard:
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    if min(p.x for p in bb)>185 or max(p.x for p in bb)<125 or min(p.y for p in bb)>310 or max(p.y for p in bb)<205: continue
    for v in o.data.vertices: hv.append((o.name,o.matrix_world@v.co))
print('HARDV',len(hv))
for E in J['edges']:
    a=Vector(E['a']+[0]); b=Vector(E['b']+[0]); n=Vector(E['n']+[0])
    # top object stats along edge
    tops={}
    for i,t in enumerate([0.1,0.3,0.5,0.7,0.9]):
        p=a.lerp(b,t)+n*0.15
        best=None
        for nm,tr in trees.items():
            h=tr.ray_cast(Vector((p.x,p.y,200)),Vector((0,0,-1)))
            if h[0] is not None and (best is None or h[0].z>best[0]): best=(h[0].z,nm)
        if best: tops[best[1]]=tops.get(best[1],0)+1
    dmin=99;nm=None
    for name,v in hv:
        q=Vector((v.x,v.y,0)); c,f=intersect_point_line(q,a,b)
        if 0<=f<=1:
            d=(q-c).dot(n)
            if -0.2<d<dmin: dmin=d;nm=name
    pr=[v for v in E['prof'] if v is not None]
    k=8; sm=[sum(pr[max(0,i-k):i+k+1])/len(pr[max(0,i-k):i+k+1]) for i in range(len(pr))]
    dev=max(abs(pr[i]-sm[i]) for i in range(len(pr)))
    print('E',E['poly'],'L',E['L'],'tops',tops,'maxdev',round(dev,2),'hard',round(dmin,2),nm)
