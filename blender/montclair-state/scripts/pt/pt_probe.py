import bpy
from mathutils import Vector
o=bpy.data.objects['PR_Calcia_slot_surrounds_UNVERIFIED']; me=o.data
print('PRS V',len(me.vertices),'F',len(me.polygons),'per140',len(me.vertices)/140)
w=bpy.data.objects['Feliciano School of Business walls']; m=w.data; mw=w.matrix_world
cen=sum((mw@v.co for v in m.vertices),Vector())/len(m.vertices)
for fi in (139,140,141,142,143):
    p=m.polygons[fi]; n=mw.to_3x3()@p.normal; c=mw@p.center
    print('OLD',fi,'n',tuple(round(x,3) for x in n),'c',tuple(round(x,2) for x in c),'out',round((c-cen).dot(n),2),'area',round(p.area,2),'verts',[tuple(round(x,2) for x in mw@m.vertices[i].co) for i in p.vertices])
print('TIERS',[x.name for x in bpy.data.objects if '156' in x.name or x.name.startswith('PN_Fel')][:30])
t=[x for x in bpy.data.objects if '156.6' in x.name][0]; tm=t.data; tw=t.matrix_world
p=tm.polygons[55]; print('TIER55 n',tuple(round(x,3) for x in tw.to_3x3()@p.normal),[tuple(round(x,2) for x in tw@tm.vertices[i].co) for i in p.vertices])
print('NFLIP old faces inward count',sum(1 for p in m.polygons if abs(p.normal.z)<0.3 and ((mw@p.center)-cen).dot(mw.to_3x3()@p.normal)<0))
for ob in bpy.data.objects:
    if 'utter' in ob.name or 'eave' in ob.name.lower() or 'Calcia' in ob.name:
        print('OBJ',ob.name,ob.type,len(ob.data.vertices) if ob.type=='MESH' else '',ob.hide_render)
print('CAMS',[c.name for c in bpy.data.objects if c.type=='CAMERA' and ('PK' in c.name or 'PO' in c.name or 'PE' in c.name or 'PF' in c.name)])
