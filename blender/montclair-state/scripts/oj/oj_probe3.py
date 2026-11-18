import bpy
from mathutils import Vector
fr=bpy.data.objects['OG_Schmitt_E_entrance_storefront_frame']; la=bpy.data.objects['OG_Schmitt_E_entrance_landing']
fv=[fr.matrix_world@v.co for v in fr.data.vertices]; lb=[la.matrix_world@v.co for v in la.data.vertices]
cen=sum(fv,Vector())/len(fv); lc=sum(lb,Vector())/len(lb); cen.z=0
OUT=Vector(((lc-cen).x,(lc-cen).y,0)).normalized(); AL=Vector((-OUT.y,OUT.x,0))
def L(w): d=w-cen; return d.dot(AL),d.dot(OUT),w.z
for n in ['OI_Schmitt_wing_eave_brackets','Schmitt Hall eave soffit + fascia + rafter tails','OI_Schmitt_wing_arcade_head_band']:
    o=bpy.data.objects[n]; ws=[L(o.matrix_world@v.co) for v in o.data.vertices]
    sel=[w for w in ws if -60<w[0]<60 and -8<w[1]<2]
    if not sel: print(n,'none'); continue
    print(n,len(sel),'a',round(min(w[0] for w in sel),2),round(max(w[0] for w in sel),2),'o',round(min(w[1] for w in sel),2),round(max(w[1] for w in sel),2),'z',round(min(w[2] for w in sel),2),round(max(w[2] for w in sel),2))
    # o histogram for the eave
    import collections
    h=collections.Counter(round(w[1],1) for w in sel if abs(w[0])>6); print('  o hist',sorted(h.items())[:30])
    hz=collections.Counter(round(w[2],1) for w in sel if abs(w[0])>6); print('  z hist',sorted(hz.items())[:30])
