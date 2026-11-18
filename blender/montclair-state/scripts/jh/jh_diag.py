# Session jh diag (read-only): faces at the aisle foot where each aisle's bottom step cuts into the plumb stage-front wall.
import bpy, bmesh, math
CX,CY,AW=-167.322,0.669,1.3; ATH=(1.5911,2.2578); H=AW/2
ob=bpy.data.objects['Kasser_amphitheater_bowl_hl']; me=ob.data
names=[s.material.name if s.material else '' for s in ob.material_slots]
bm=bmesh.new(); bm.from_mesh(me); bm.normal_update()
CH=bm.faces.layers.int.get('jb_chamfer')
STG=names.index('io_amphi_stage_concrete'); AIS={i for i,n in enumerate(names) if 'aisle' in n}
def fr(co,ai):
    a=ATH[ai]; dx,dy=co.x-CX,co.y-CY; return dx*math.cos(a)+dy*math.sin(a), -dx*math.sin(a)+dy*math.cos(a)
for ai in (0,1):
    # aisle faces touching the stage
    af=[f for f in bm.faces if f.material_index in AIS and any(g.material_index==STG for v in f.verts for g in v.link_faces)]
    af=[f for f in af if abs(fr(f.calc_center_median(),ai)[1])<H+0.05]
    smin=min(fr(v.co,ai)[0] for f in af for v in f.verts) if af else None
    print('JHD ai',ai,'aisle faces touching stage',len(af),'smin',smin)
    if smin is None: continue
    for f in bm.faces:
        c=f.calc_center_median(); s,d=fr(c,ai)
        if not (smin-0.4<s<smin+0.45 and abs(d)<H+0.4): continue
        if f.material_index==STG and f.normal.z>0.9: continue
        n=f.normal; a=ATH[ai]; ns=n.x*math.cos(a)+n.y*math.sin(a); nd=-n.x*math.sin(a)+n.y*math.cos(a)
        vs=' '.join('(%.3f,%.3f,%.3f)'%(fr(v.co,ai)[0],fr(v.co,ai)[1],v.co.z) for v in f.verts)
        print('JHD f%d %s ch%d n(s%.2f d%.2f z%.2f) A%.1fcm2 %s'%(f.index,names[f.material_index][:22],f[CH],ns,nd,n.z,f.calc_area()*1e4,vs))
