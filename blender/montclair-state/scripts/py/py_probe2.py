import bpy, collections, math
from mathutils import Vector
def inwing(p): return p.x<-157.5 and 77.0<p.y<160.5
r=bpy.data.objects['Dickson Hall roof (LiDAR)']; W=[r.matrix_world@v.co for v in r.data.vertices]
hi=[c for c in W if inwing(c) and c.z>151.2]
cl=collections.Counter((round(c.x/2)*2,round(c.y/2)*2) for c in hi)
print('ROOFHI',len(hi),sorted(cl.items())[:60])
zs=sorted(c.z for c in W if inwing(c)); print('ROOFZ pct',[round(zs[int(len(zs)*q)],2) for q in (0.05,0.25,0.5,0.75,0.95)])
# roof material per face in wing, faces above 151.3
fm=collections.Counter()
for p in r.data.polygons:
    c=r.matrix_world@p.center
    if inwing(c) and c.z>151.0: fm[(r.data.materials[p.material_index].name,round(c.z,1))]+=1
print('ROOFFACES',sorted(fm.items())[:40])
for o in bpy.data.objects:
    if o.type=='MESH' and any(m and m.name=='PE_Dickson_coping_dark_bronze_UNVERIFIED' for m in o.data.materials): 
        W2=[o.matrix_world@v.co for v in o.data.vertices]; print('PECOP',o.name,len(W2),'z %.2f..%.2f'%(min(c.z for c in W2),max(c.z for c in W2)),o.hide_render)
for n in ('PV_CAM_closeup_dickson_north_toprow','PE_CAM_eye_dickson_west','PE_CAM_oblique_dickson_from_SW','PV_CAM_eye_dickson_north'):
    c=bpy.data.objects[n]; d=c.matrix_world.to_3x3()@Vector((0,0,-1)); print('CAM',n,tuple(round(x,1) for x in c.location),tuple(round(x,2) for x in d),round(math.degrees(c.data.angle),1))
w=bpy.data.objects['Dickson Hall walls']; W=[w.matrix_world@v.co for v in w.data.vertices]
lv=collections.Counter(round(c.z,2) for c in W if inwing(c) and c.z>150.5); print('WALLTOPZ',sorted(lv.items()))
