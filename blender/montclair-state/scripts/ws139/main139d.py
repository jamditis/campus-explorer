import bpy, os, numpy as np
from mathutils import Vector, kdtree
SAVE=os.environ.get('SAVE','0')=='1'
OB=bpy.data.objects
# (a) Terrain poking over the WS136a walk edges -> pushed down to walk top -3 cm (feather 0.6..1.2 m)
wk=[o for o in OB if o.name.startswith('WS136a_Skyline_W_walk_N_of_-248')][0]; wm=wk.matrix_world
tops=[wm@v.co for v in wk.data.vertices]
kd=kdtree.KDTree(len(tops))
for i,p in enumerate(tops): kd.insert(Vector((p.x,p.y,0)),i)
kd.balance()
def span(y):
    s=[p.x for p in tops if abs(p.y-y)<0.6]; return (min(s),max(s)) if s else None
T=OB['Terrain_LiDAR_DTM_1m']; mw=T.matrix_world; mi=mw.inverted(); n=0; mx=0
for v in T.data.vertices:
    p=mw@v.co
    if not(-76<p.x<-66 and -248.5<p.y<-202.5): continue
    co,i,d=kd.find(Vector((p.x,p.y,0)))
    if d>1.3: continue
    sp=span(p.y); inside= sp and sp[0]-0.05<p.x<sp[1]+0.05
    near=[tops[j].z for (_,j,_) in kd.find_range(Vector((p.x,p.y,0)),d+0.5)]
    tz=(max(near) if near else tops[i].z)-(0.08 if inside else 0.03)
    if p.z>tz:
        w=1.0 if (inside or d<=0.6) else max(0.0,1-(d-0.6)/0.7)
        nz=p.z+(tz-p.z)*w; mx=max(mx,p.z-nz); v.co=mi@Vector((p.x,p.y,nz)); n+=1
T.data.update(); print('TERRAIN down',n,'max',round(mx,2))
# (b) probe pale patches near the lot W end
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene; hits={}
for x in np.arange(-174,-158,1.0):
    for y in np.arange(-274,-256,1.0):
        h=sc.ray_cast(dg,Vector((x,y,200)),Vector((0,0,-1)))
        if h[0]:
            o=h[4]; mn='?'
            try: mn=o.data.materials[o.data.polygons[h[3]].material_index].name if o.type=='MESH' and h[3]<len(o.data.polygons) else '?'
            except Exception: pass
            k=(o.name[:50],mn); hits.setdefault(k,[]).append((float(x),float(y)))
for k,v in hits.items(): print('HIT',k,len(v),v[:3])
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
