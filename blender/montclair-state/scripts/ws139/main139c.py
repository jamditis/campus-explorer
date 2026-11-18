import bpy, os
from mathutils import Vector, kdtree
SAVE=os.environ.get('SAVE','0')=='1'
OB=bpy.data.objects
wk=[o for o in OB if o.name.startswith('WS136a_Skyline_W_walk_N_of_-248')][0]; wm=wk.matrix_world
tops=[wm@v.co for v in wk.data.vertices]
tops=[p for p in tops]
kd=kdtree.KDTree(len(tops))
for i,p in enumerate(tops): kd.insert(Vector((p.x,p.y,0)),i)
kd.balance()
def span(y):
    s=[p.x for p in tops if abs(p.y-y)<0.6]; return (min(s),max(s)) if s else None
T=OB['Terrain_LiDAR_DTM_1m']; mw=T.matrix_world; mi=mw.inverted(); n=0; mx=0
for v in T.data.vertices:
    p=mw@v.co
    if not(-76<p.x<-66 and -248<p.y<-203.5): continue
    sp=span(p.y)
    if not sp or sp[0]-0.05<p.x<sp[1]+0.05: continue
    co,i,d=kd.find(Vector((p.x,p.y,0)))
    if d>1.6: continue
    near=[tops[j].z for (_,j,_) in kd.find_range(Vector((p.x,p.y,0)),d+0.5)]
    tz=max(near)-0.04
    if p.z<tz:
        w=1.0 if d<=0.5 else max(0.0,1-(d-0.5)/1.1)
        nz=p.z+(tz-p.z)*w; mx=max(mx,nz-p.z); v.co=mi@Vector((p.x,p.y,nz)); n+=1
T.data.update(); print('TERRAIN lift',n,'max',round(mx,2))
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
