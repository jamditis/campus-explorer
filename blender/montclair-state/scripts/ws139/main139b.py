import bpy, bmesh, os, numpy as np
from mathutils import Vector
SAVE=os.environ.get('SAVE','0')=='1'
OB=bpy.data.objects
wk=[o for o in OB if o.name.startswith('WS136a_Skyline_W_walk_N_of_-248')][0]; wm=wk.matrix_world
tops=[wm@v.co for v in wk.data.vertices]
nn=[p for p in tops if -204.2<p.y<-202.8]
print('NX',round(min(p.x for p in nn),2),round(max(p.x for p in nn),2), round(max(p.z for p in nn),3))
b=OB['WS139_walk_N_bridge_to_old_walk_y-203_-199_UNVERIFIEDjoint']
xw0=min(v.co.x for v in b.data.vertices); xe0=max(v.co.x for v in b.data.vertices)
xw=min(p.x for p in nn); xe=max(p.x for p in nn)
for v in b.data.vertices:
    t=(v.co.x-xw0)/(xe0-xw0); v.co.x=xw+t*(xe-xw)
b.data.update()
fp=OB['Footpaths_OSM']; fm=fp.matrix_world
print('FPN', sorted(set((round((fm@v.co).x,2),round((fm@v.co).y,2),round((fm@v.co).z,2)) for v in fp.data.vertices if -73.5<(fm@v.co).x<-68.5 and -199.6<(fm@v.co).y<-198.0)))
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
for y in (-206,-215,-225,-235,-245):
    for x in (-74.0,-73.2,-69.2,-68.4):
        h=sc.ray_cast(dg,Vector((x,y,200)),Vector((0,0,-1)))
        wz=max([p.z for p in tops if abs(p.y-y)<0.6] or [0])
        print('PROBE',x,y,h[4].name[:45] if h[0] else None, round(h[1].z,2) if h[0] else None,'walktop',round(wz,2))
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
