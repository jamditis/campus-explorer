# Session jf diag: dump remaining bad aisle-corner faces (je's count_bad rule) in the aisle frame (s, d, z).
import bpy, bmesh, math
CX,CY,AW=-167.322,0.669,1.3; ATH=(1.5911,2.2578); H=AW/2
ob=bpy.data.objects['Kasser_amphitheater_bowl_hl']; me=ob.data
names=[s.material.name if s.material else '' for s in ob.material_slots]
SKIP={names.index(n) for n in ('hn_amphi_base_fieldstone','io_amphi_stage_concrete')}
bm=bmesh.new(); bm.from_mesh(me); bm.normal_update()
CH=bm.faces.layers.int.get('jb_chamfer'); WL=bm.faces.layers.int.get('iy_wedge')
def fr(co,ai):
    a=ATH[ai]; dx,dy=co.x-CX,co.y-CY; return dx*math.cos(a)+dy*math.sin(a), -dx*math.sin(a)+dy*math.cos(a)
def isbad(f,ai):
    if f.material_index in SKIP or f[CH]: return False
    a=ATH[ai]; n=f.normal; nd=-n.x*math.sin(a)+n.y*math.cos(a)
    return (WL and f[WL]) or (abs(nd)>0.3 and (n.z>0.15 or n.z<-0.05))
mw=ob.matrix_world
print('JF mw identity?', mw.is_identity if hasattr(mw,'is_identity') else mw)
for f in bm.faces:
    if f.material_index in SKIP: continue
    cc=f.calc_center_median(); ai=min((0,1),key=lambda k:abs(abs(fr(cc,k)[1])-H))
    if fr(cc,ai)[0]<=0: continue
    ds=[fr(v.co,ai)[1] for v in f.verts]
    if any(abs(abs(d)-H)<0.01 for d in ds) and any(abs(d)<H-0.01 for d in ds) and all(abs(d)<=H+0.015 for d in ds) and isbad(f,ai):
        a=ATH[ai]; n=f.normal; ns=n.x*math.cos(a)+n.y*math.sin(a); nd=-n.x*math.sin(a)+n.y*math.cos(a)
        print('JFBAD idx',f.index,'ai',ai,'c',[round(x,2) for x in cc],'mat',names[f.material_index],'A cm2',round(f.calc_area()*1e4,1),'n(s,d,z)',round(ns,2),round(nd,2),round(n.z,2),'wedge',f[WL] if WL else None)
        print('   verts(s,d,z)',[(v.index,round(fr(v.co,ai)[0],3),round(fr(v.co,ai)[1],3),round(v.co.z,3)) for v in f.verts])
        for e in f.edges:
            for g in e.link_faces:
                if g is f: continue
                gn=g.normal
                print('     nb',g.index,names[g.material_index][:22],'n(s,d,z)',round(gn.x*math.cos(a)+gn.y*math.sin(a),2),round(-gn.x*math.sin(a)+gn.y*math.cos(a),2),round(gn.z,2),'ch',g[CH],'v',[(round(fr(v.co,ai)[0],3),round(fr(v.co,ai)[1],3),round(v.co.z,3)) for v in g.verts])
