import bpy
from mathutils import Vector
from mathutils.geometry import intersect_point_line
B=bpy.data.objects['WS27_CollegeAve_curb_left_UNVERIFIED']; MB=B.matrix_world
bk=[(k,MB@B.data.vertices[6*k+3].co) for k in range(0,20)]
for k,p in bk[:16]: print('P224 curb k%d back (%.3f,%.3f,%.3f)'%(k,p.x,p.y,p.z))
def dist(p):
    best=(9,None)
    for (k,a),(_,b) in zip(bk,bk[1:]):
        q,t=intersect_point_line(p.xy.to_3d(),a.xy.to_3d(),b.xy.to_3d())
        t=min(max(t,0),1); q=a.xy.to_3d().lerp(b.xy.to_3d(),t); d=(p.xy.to_3d()-q).length
        if d<best[0]: best=(d,k,q,a.z+(b.z-a.z)*t)
    return best
for nm in ('WS72_Kasser_SW_RHD_core_sidewalk_landing_UNVERIFIED_width','WS71_Kasser_S_sidewalk'):
    o=[o for o in bpy.data.objects if o.name.startswith(nm)][0]; M=o.matrix_world; me=o.data; R=M.to_3x3()
    cnt={}
    for p in me.polygons:
        if (R@p.normal).z>0.3:
            for e in p.edge_keys: cnt[e]=cnt.get(e,0)+1
    bv=set(i for e,c in cnt.items() if c==1 for i in e)
    for i in sorted(bv):
        w=M@me.vertices[i].co
        if -247.5<w.x<-239 and w.y<-52.6:
            d=dist(w)
            if d[0]<0.6: print('P224 %s v%d (%.3f,%.3f,%.3f) gap-to-curb-back %.3f m (k%d) curb z %.3f'%(nm[:4],i,w.x,w.y,w.z,d[0],d[1],d[3]))
