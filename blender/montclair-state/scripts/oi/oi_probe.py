import bpy, json
from mathutils import Vector
fr=bpy.data.objects['OG_Schmitt_E_entrance_storefront_frame']; la=bpy.data.objects['OG_Schmitt_E_entrance_landing']
fv=[fr.matrix_world@v.co for v in fr.data.vertices]; lb=[la.matrix_world@v.co for v in la.data.vertices]
cen=sum(fv,Vector())/len(fv); lc=sum(lb,Vector())/len(lb)
out=Vector(((lc-cen).x,(lc-cen).y,0)).normalized(); al=Vector((-out.y,out.x,0))
print('cen',cen,'out',out,'front',max(v.dot(out) for v in fv),'alongspan',min(v.dot(al) for v in fv),max(v.dot(al) for v in fv),'z',min(v.z for v in fv),max(v.z for v in fv))
print('landing z',min(v.z for v in lb),max(v.z for v in lb), 'landing out span',min(v.dot(out) for v in lb)-cen.dot(out),max(v.dot(out) for v in lb)-cen.dot(out))
w=bpy.data.objects['Schmitt Hall walls']; wv=[w.matrix_world@v.co for v in w.data.vertices]
print('wall z',min(v.z for v in wv),max(v.z for v in wv))
for n in ('Schmitt Hall eave soffit + fascia + rafter tails','Schmitt Hall roof (LiDAR)'):
    o=bpy.data.objects.get(n)
    if o: vv=[o.matrix_world@v.co for v in o.data.vertices]; print(n,min(v.z for v in vv),max(v.z for v in vv))
# wall face planes near door
for p in w.data.polygons:
    c=w.matrix_world@p.center
    if abs((c-cen).dot(al))<15 and abs((c-cen).dot(out))<8 and abs(p.normal.z)<0.1:
        n=(w.matrix_world.to_3x3()@p.normal).normalized()
        if abs(n.dot(out))>0.9 or abs(n.dot(al))>0.9:
            pass
# wall verts near door: list distinct out-offsets / along of vertical edges
pts=sorted({(round((v-cen).dot(al),2),round((v-cen).dot(out),2)) for v in wv if abs((v-cen).dot(al))<20 and abs((v-cen).dot(out))<12 and v.z>148})
print('top wall verts (along,out) near door',pts)
wins=[]
for o in bpy.data.objects:
    if o.name.startswith('SCH_win_'):
        d=o.matrix_world.translation-cen
        if abs(d.dot(al))<30 and abs(d.dot(out))<10: wins.append((o.name,round(d.dot(al),2),round(d.dot(out),2),round(o.matrix_world.translation.z,2),o.get('run')))
for x in sorted(wins,key=lambda t:(t[4],t[1])): print(x)
print('sconces',[ (n,tuple(bpy.data.objects[n].location)) for n in ('OH_Schmitt_sconce_L','OH_Schmitt_sconce_R')])
print([o.name for o in bpy.data.objects if o.name.startswith('OG_Schmitt_E_entrance')])
