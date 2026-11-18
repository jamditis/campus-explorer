# Session jh diag2 (read-only): non-horizontal faces in front of each aisle (stage-front wall region) incl. stage z.
import bpy, bmesh, math
CX,CY,AW=-167.322,0.669,1.3; ATH=(1.5911,2.2578); H=AW/2
ob=bpy.data.objects['Kasser_amphitheater_bowl_hl']; me=ob.data
names=[s.material.name if s.material else '' for s in ob.material_slots]
bm=bmesh.new(); bm.from_mesh(me); bm.normal_update()
CH=bm.faces.layers.int.get('jb_chamfer'); STG=names.index('io_amphi_stage_concrete')
def fr(co,ai):
    a=ATH[ai]; dx,dy=co.x-CX,co.y-CY; return dx*math.cos(a)+dy*math.sin(a), -dx*math.sin(a)+dy*math.cos(a)
for ai in (0,1):
    a=ATH[ai]
    for f in bm.faces:
        c=f.calc_center_median(); s,d=fr(c,ai)
        if not (7.5<s<9.56 and abs(d)<H+0.35): continue
        n=f.normal
        if n.z>0.97 and f.material_index!=STG: continue
        if f.material_index==STG and n.z>0.97 and not (abs(abs(d)-H)<0.3): continue
        ns=n.x*math.cos(a)+n.y*math.sin(a); nd=-n.x*math.sin(a)+n.y*math.cos(a)
        vs=' '.join('(%.3f,%.3f,%.3f)'%(fr(v.co,ai)[0],fr(v.co,ai)[1],v.co.z) for v in f.verts)
        print('JHD2 ai%d f%d %s ch%d n(s%.2f d%.2f z%.2f) A%.1f %s'%(ai,f.index,names[f.material_index][:14],f[CH],ns,nd,n.z,f.calc_area()*1e4,vs))
