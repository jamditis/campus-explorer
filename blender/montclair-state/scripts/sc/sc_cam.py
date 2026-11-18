# sc: re-aim SC_CAM_closeup_promenade_joints onto a stretch where the SB promenade ribbon is the top surface (midpoint was on OZ/Footpaths walk).
import bpy,json,math
from mathutils import Vector
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
F={str(f['id']):f for f in json.load(open('data/scene_data.json'))['features']}
pts=[tuple(p) for p in F['313023297']['pts']]
S=[]
for (ax,ay),(bx,by) in zip(pts[:-1],pts[1:]):
    L=math.hypot(bx-ax,by-ay); n=max(1,int(L/1.0))
    for i in range(n): t=i/n; S.append((ax+(bx-ax)*t,ay+(by-ay)*t))
def top(x,y):
    r=sc.ray_cast(dg,Vector((x,y,400)),Vector((0,0,-1)))
    return (r[4].name,r[1].z) if r[0] else (None,None)
ok=[top(x,y)[0]=='SB_pedestrian_313023297_UNVERIFIED' for x,y in S]
best=None
for i in range(len(S)-14):
    if all(ok[i:i+14]):
        best=i; break
print('SCCAM run start',best,'of',len(S),'ok',sum(ok))
cam=bpy.data.objects['SC_CAM_closeup_promenade_joints']
if best is not None:
    (ax,ay),(bx,by)=S[best],S[best+12]; L=math.hypot(bx-ax,by-ay); dx,dy=(bx-ax)/L,(by-ay)/L
    cx,cy=ax+dy*1.0,ay-dx*1.0; z0=top(cx,cy)[1]
    cam.location=(cx,cy,z0+1.3); tx,ty=ax+dx*7,ay+dy*7; tz=top(tx,ty)[1]
    cam.rotation_euler=(Vector((tx,ty,tz))-cam.location).to_track_quat('-Z','Y').to_euler()
    print('SCCAM',tuple(round(c,2) for c in cam.location),'->',round(tx,2),round(ty,2))
    bpy.ops.wm.save_mainfile(); print('SAVED')
