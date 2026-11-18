# Session jh diag3 (read-only): faces near a cheek at the stage-front wall (env AI, SG), any material except flat stage.
import bpy, bmesh, math, os
CX,CY,AW=-167.322,0.669,1.3; ATH=(1.5911,2.2578); H=AW/2
AI=int(os.environ.get('AI',1)); SG=int(os.environ.get('SG',-1))
ob=bpy.data.objects['Kasser_amphitheater_bowl_hl']; me=ob.data
names=[s.material.name if s.material else '' for s in ob.material_slots]
bm=bmesh.new(); bm.from_mesh(me); bm.normal_update()
def fr(co,ai):
    a=ATH[ai]; dx,dy=co.x-CX,co.y-CY; return dx*math.cos(a)+dy*math.sin(a), -dx*math.sin(a)+dy*math.cos(a)
a=ATH[AI]
for f in bm.faces:
    s,d=fr(f.calc_center_median(),AI)
    if not (8.3<s<9.3 and abs(d*SG-H)<0.35): continue
    n=f.normal
    if n.z>0.97: continue
    if max(v.co.z for v in f.verts)>133.39: continue
    ns=n.x*math.cos(a)+n.y*math.sin(a); nd=-n.x*math.sin(a)+n.y*math.cos(a)
    print('JHD3 f%d %s n(s%.2f d%.2f z%.2f) A%.1f %s'%(f.index,names[f.material_index][:12],ns,nd,n.z,f.calc_area()*1e4,' '.join('(%.3f,%.3f,%.3f)'%(*fr(v.co,AI),v.co.z) for v in f.verts)))
