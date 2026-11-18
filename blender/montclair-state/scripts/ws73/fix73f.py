# ws73f: terrain 1 m triangles still poked through the College Ave gutter beside the north curb at the bend (41 probe hits) ->
# rebuild WS73_curb_back_clamp_helper_hidden with 2 extra points 1 m and 2 m into the road (z = curb face foot -7/-8 cm)
import bpy,bmesh,os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
dg=bpy.context.evaluated_depsgraph_get()
o=bpy.data.objects['Terrain_LiDAR_DTM_1m']; oe=o.evaluated_get(dg); m=oe.to_mesh(); bm=bmesh.new(); bm.from_mesh(m); bm.transform(o.matrix_world); T0=BVHTree.FromBMesh(bm); bm.free(); oe.to_mesh_clear()
dn=lambda x,y:T0.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))[0]
hc=bpy.data.objects['WS73_curb_back_clamp_helper_hidden']; me=hc.data
bm=bmesh.new(); prev={}
for cn in ('WS27_CollegeAve_curb_right_UNVERIFIED','WS27_CollegeAve_curb_left_UNVERIFIED'):
    V=bpy.data.objects[cn].data.vertices
    for r in range(len(V)//6):
        v=[V[6*r+k].co for k in range(6)]
        if not (-252<v[0].x<-193 and v[0].y>-95): continue
        d=Vector((v[4].x-v[1].x,v[4].y-v[1].y,0)); d.normalize(); f0=v[0]; b4=v[4]
        pts=[(f0.x-d.x*2.0,f0.y-d.y*2.0,f0.z-0.08),(f0.x-d.x*1.0,f0.y-d.y*1.0,f0.z-0.07),(f0.x-d.x*0.3,f0.y-d.y*0.3,f0.z-0.06),(f0.x,f0.y,f0.z-0.05),(b4.x,b4.y,b4.z-0.04)]
        for s in (0.4,0.8,1.2,1.6):
            x=b4.x+d.x*s; y=b4.y+d.y*s; h=dn(x,y); tz=h.z if h else b4.z
            w=s/1.6; z=(b4.z-0.04)*(1-w)+tz*w if tz>b4.z-0.04 else tz
            pts.append((x,y,z))
        row=[bm.verts.new(p) for p in pts]
        if (cn,r-1) in prev:
            p=prev[(cn,r-1)]
            for k in range(len(row)-1): bm.faces.new((p[k],row[k],row[k+1],p[k+1]))
        prev[(cn,r)]=row
bm.to_mesh(me); bm.free(); me.update()
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws73/fix73e.py').read().replace("if os.environ.get('SAVE')","if False"))
dg=bpy.context.evaluated_depsgraph_get(); dg.update()
oe=o.evaluated_get(dg); m=oe.to_mesh(); bm=bmesh.new(); bm.from_mesh(m); bm.transform(o.matrix_world); T=BVHTree.FromBMesh(bm); bm.free(); oe.to_mesh_clear()
bad=0;c=0
for cn in ('WS27_CollegeAve_curb_right_UNVERIFIED','WS27_CollegeAve_curb_left_UNVERIFIED'):
    V=bpy.data.objects[cn].data.vertices
    for r in range(len(V)//6):
        v=[V[6*r+k].co for k in range(6)]
        if not (-252<v[0].x<-193 and v[0].y>-95): continue
        d=Vector((v[4].x-v[1].x,v[4].y-v[1].y,0)); d.normalize()
        for s in (0.1,0.3,0.6,1.0,1.5):
            p=v[0]-d*s; h=T.ray_cast(Vector((p.x,p.y,400)),Vector((0,0,-1)))[0]; c+=1
            if h and h.z>v[0].z-0.02: bad+=1
print('W73f terrain within 2cm of gutter level road-side',bad,'/',c,flush=True)
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('W73f SAVED',flush=True)
