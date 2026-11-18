import bpy,bmesh,math
CX,CY,AW=-167.322,0.669,1.3; ATH=(1.5911,2.2578)
ob=bpy.data.objects['Kasser_amphitheater_bowl_hl']; me=ob.data
names=[s.material.name if s.material else '' for s in ob.material_slots]; RIS=names.index('hn_amphi_riser_coursed_stone')
bm=bmesh.new(); bm.from_mesh(me); bm.normal_update()
def fr(co):
    b=None
    for ai,a in enumerate(ATH):
        dx,dy=co.x-CX,co.y-CY; s=dx*math.cos(a)+dy*math.sin(a); d=-dx*math.sin(a)+dy*math.cos(a)
        if b is None or abs(d)<abs(b[2]): b=(ai,s,d)
    return b
import collections; h=collections.Counter(); A=0
for f in bm.faces:
    if f.material_index!=RIS: continue
    fs=[fr(v.co) for v in f.verts]
    if not all(abs(d)<0.655 and s>0 for _,s,d in fs): continue
    a=ATH[fs[0][0]]; n=f.normal; ns=n.x*math.cos(a)+n.y*math.sin(a)
    h[(round(ns,1),round(n.z,1))]+=1
    if n.z>0.35 and ns<-0.4: A+=f.calc_area()
print('JE4',sorted(h.items(),key=lambda kv:-kv[1])[:25]); print('JE4 lean area m2',A)
