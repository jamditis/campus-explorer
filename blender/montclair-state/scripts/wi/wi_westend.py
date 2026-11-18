"""wi part 3: walk 1132693523 dead-ends on lawn at its W end (OSM) with a ~4 cm lip.
Raise patch verts (raise-only) within 1.5 m W/N/S of the W end (x<210.3) to walk_z-0.015, smoothstep out by 2.5 m."""
import bpy, os, json
from mathutils import Vector
os.chdir('/workspace/nj-scenes/montclair-state')
P=bpy.data.objects['WF_east_dorm_LiDAR_terrain_patch_UNVERIFIED']
W=bpy.data.objects['WD_walk_1132693523_UNVERIFIED']
wv=[W.matrix_world@v.co for v in W.data.vertices]
west=[c for c in wv if c.x<210.3]
xs=[c.x for c in west]; ys=[c.y for c in west]
bx0,bx1,by0,by1=min(xs),210.3,min(ys),max(ys)
zt=max(c.z for c in west)-0.015
mw=P.matrix_world; inv=mw.inverted()
rep=[]
for v in P.data.vertices:
    c=mw@v.co
    dx=max(bx0-c.x,0,c.x-bx1); dy=max(by0-c.y,0,c.y-by1)
    d=(dx*dx+dy*dy)**0.5
    if c.x>bx1 or d>2.5: continue
    w=1.0 if d<=1.5 else 1-((d-1.5))**2*(3-2*(d-1.5))
    if zt<=c.z: continue
    nz=c.z+w*(zt-c.z); rep.append([round(c.x,2),round(c.y,2),round(c.z,3),round(nz,3)])
    c.z=nz; v.co=inv@c
P.data.update()
json.dump({'zt':zt,'box':[bx0,bx1,by0,by1],'raised':rep},open('data/wi/westend_report.json','w'))
print('REP',zt,len(rep),rep)
bpy.ops.wm.save_mainfile(compress=True); print('SAVED')
