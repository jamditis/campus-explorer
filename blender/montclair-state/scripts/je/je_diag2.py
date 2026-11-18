# Session je diag2 (read-only): aisle-frame classification of faces touching the cheek planes |d|=AW/2 (iz axes).
import bpy, bmesh, math, os
CX,CY,AW=-167.322,0.669,1.3; ATH=(1.5911,2.2578)
ob=bpy.data.objects['Kasser_amphitheater_bowl_hl']; me=ob.data
names=[s.material.name if s.material else '' for s in ob.material_slots]
bm=bmesh.new(); bm.from_mesh(me); bm.normal_update()
CH=bm.faces.layers.int.get('jb_chamfer'); W=bm.faces.layers.int.get('iy_wedge')
def frame(co):
    best=None
    for ai,a in enumerate(ATH):
        dx,dy=co.x-CX,co.y-CY; s=dx*math.cos(a)+dy*math.sin(a); d=-dx*math.sin(a)+dy*math.cos(a)
        if best is None or abs(d)<abs(best[2]): best=(ai,s,d)
    return best
bad=[]
for f in bm.faces:
    if names[f.material_index] in ('hn_amphi_base_fieldstone','io_amphi_stage_concrete'): continue
    vi=[frame(v.co) for v in f.verts]
    if not any(abs(abs(d)-AW/2)<0.01 for ai,s,d in vi): continue
    ai=vi[0][0]; a=ATH[ai]; n=f.normal
    nd=-n.x*math.sin(a)+n.y*math.cos(a); ns=n.x*math.cos(a)+n.y*math.sin(a)
    if (abs(nd)>0.3 and (n.z>0.15 or n.z<-0.05)) or (W and f[W]):
        bad.append(f)
        c=f.calc_center_median()
        print('JEB f%d'%f.index,'ai',ai,'s %.2f'%frame(c)[1],'c',[round(x,3) for x in c],'n(s,d,z)',round(ns,2),round(nd,2),round(n.z,2),'A',round(f.calc_area()*1e4,1),'nv',len(f.verts),names[f.material_index][:14],'ch',f[CH],'w',f[W] if W else 0)
        if os.environ.get('V')=='1':
            for v in f.verts:
                _,s,d=frame(v.co); print('JEB   v%d'%v.index,[round(x,3) for x in v.co],'s %.3f d %.3f'%(s,d))
print('JEB total',len(bad))
