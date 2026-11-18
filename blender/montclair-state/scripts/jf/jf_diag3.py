# jf diag3: dump the remaining iy_wedge faces inside the aisles (verts in aisle frame + neighbours)
import bpy, bmesh, math
CX,CY,AW=-167.322,0.669,1.3; ATH=(1.5911,2.2578); H=AW/2
ob=bpy.data.objects['Kasser_amphitheater_bowl_hl']; me=ob.data
names=[s.material.name if s.material else '' for s in ob.material_slots]
bm=bmesh.new(); bm.from_mesh(me); bm.normal_update()
CH=bm.faces.layers.int.get('jb_chamfer'); WL=bm.faces.layers.int.get('iy_wedge')
def fr(co,ai):
    a=ATH[ai]; dx,dy=co.x-CX,co.y-CY; return dx*math.cos(a)+dy*math.sin(a), -dx*math.sin(a)+dy*math.cos(a)
P=lambda v,ai:(round(fr(v.co,ai)[0],3),round(fr(v.co,ai)[1],3),round(v.co.z,3))
for f in bm.faces:
    if not f[WL]: continue
    cc=f.calc_center_median(); ai=min((0,1),key=lambda k:abs(fr(cc,k)[1]))
    s,d=fr(cc,ai)
    if abs(d)>H: continue
    a=ATH[ai]; n=f.normal
    print('JF3 W',f.index,'ai',ai,names[f.material_index][:20],'n(s,d,z)',round(n.x*math.cos(a)+n.y*math.sin(a),2),round(-n.x*math.sin(a)+n.y*math.cos(a),2),round(n.z,2),[P(v,ai) for v in f.verts])
    for e in f.edges:
        for g in e.link_faces:
            if g is f: continue
            gn=g.normal
            print('JF3   nb',g.index,names[g.material_index][:20],'ch',g[CH],'n',round(gn.x*math.cos(a)+gn.y*math.sin(a),2),round(-gn.x*math.sin(a)+gn.y*math.cos(a),2),round(gn.z,2),[P(v,ai) for v in g.verts])
