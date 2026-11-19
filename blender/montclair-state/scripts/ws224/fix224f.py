# ws224f (W46): between the Kasser S walk edge (WS72 landing v160..v250, WS71 S sidewalk) and the College Ave curb_left
# back there is a 0.1-0.5 m strip of bare LiDAR terrain sitting 25-35 cm BELOW both (a dark trench in the eye views).
# The ws71 walk was traced 0.30 m back from the curb (ortho 2020), so the strip is read as a narrow grass verge, the same
# lawn as the WS70 verge W of the return (UNVERIFIED: could be concrete to the curb). New object, nothing moved:
# a quad strip from each walk-edge vertex (2 cm under the slab) to its closest curb-back point (2 cm under the curb),
# top 1 cm under the slab edge on the walk side and 1 cm under the curb back on the curb side.
import bpy, bmesh
from mathutils import Vector
from mathutils.geometry import intersect_point_line
B=bpy.data.objects['WS27_CollegeAve_curb_left_UNVERIFIED']; MB=B.matrix_world
nr=len(B.data.vertices)//6
bk=[MB@B.data.vertices[6*k+3].co for k in range(nr)]; fr=[MB@B.data.vertices[6*k+1].co for k in range(nr)]
def proj(p):
    best=None
    for k in range(nr-1):
        a,b=bk[k],bk[k+1]; q,t=intersect_point_line(p.xy.to_3d(),a.xy.to_3d(),b.xy.to_3d()); t=min(max(t,0),1)
        q=a.lerp(b,t); d=(p.xy-q.xy).length
        if best is None or d<best[0]:
            n=(fr[k].lerp(fr[k+1],t)-q); n.z=0; best=(d,q,n.normalized())
    return best
def edge_verts(nm,xmin,xmax):
    o=[o for o in bpy.data.objects if o.name.startswith(nm)][0]; M=o.matrix_world; me=o.data; R=M.to_3x3()
    cnt={}
    for p in me.polygons:
        if (R@p.normal).z>0.3:
            for e in p.edge_keys: cnt[e]=cnt.get(e,0)+1
    bv=set(i for e,c in cnt.items() if c==1 for i in e)
    out=[]
    for i in bv:
        w=M@me.vertices[i].co
        if xmin<=w.x<=xmax and w.y<-52.6:
            pr=proj(w)
            if pr[0]<0.6: out.append((w.x,w,pr))
    return sorted(out,key=lambda t:t[0])
pts=edge_verts('WS72_Kasser_SW_RHD_core_sidewalk_landing',-247.51,-243.0)+edge_verts('WS71_Kasser_S_sidewalk',-243.0,-200.0)
pts=[p for p in pts if p[2][0]>0.03 or p[0]<-247.4]
print('F224F edge verts',len(pts),'x %.2f..%.2f'%(pts[0][0],pts[-1][0]),flush=True)
bm=bmesh.new(); ring=[]
for x,w,(d,q,n) in pts:
    inn=(w.xy-q.xy); inn=inn.normalized() if inn.length>1e-4 else -n.xy
    a=bm.verts.new(Vector((w.x+inn.x*0.02,w.y+inn.y*0.02,w.z-0.01)))
    b=bm.verts.new(Vector((q.x+n.x*0.02,q.y+n.y*0.02,q.z-0.01)))
    ring.append((a,b))
for (a0,b0),(a1,b1) in zip(ring,ring[1:]):
    f=bm.faces.new((a0,b0,b1,a1)); f.normal_update()
    if f.normal.z<0: f.normal_flip()
me=bpy.data.meshes.new('WS224_Kasser_S_verge_grass_fill'); bm.to_mesh(me); bm.free()
for p in me.polygons: p.use_smooth=False
o=bpy.data.objects.new('WS224_Kasser_S_verge_grass_fill_UNVERIFIED',me)
o.data.materials.append(bpy.data.materials['WS70_berm_lawn_ortho_matched'])
bpy.data.collections['WS27_CollegeAve_Kasser_carriageway_curbs_20261110ws27'].objects.link(o)
print('F224F strip faces',len(me.polygons),'area %.2f m2'%sum(p.area for p in me.polygons),flush=True)
