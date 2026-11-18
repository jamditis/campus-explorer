# Session je diag3 (read-only): vertex/neighbour dump of chosen bowl faces (env F=comma idx).
import bpy, bmesh, math, os
CX,CY,AW=-167.322,0.669,1.3; ATH=(1.5911,2.2578)
ob=bpy.data.objects['Kasser_amphitheater_bowl_hl']; me=ob.data
names=[s.material.name[:12] if s.material else '' for s in ob.material_slots]
bm=bmesh.new(); bm.from_mesh(me); bm.normal_update(); bm.faces.ensure_lookup_table()
CH=bm.faces.layers.int.get('jb_chamfer')
def fr(co,ai):
    a=ATH[ai]; dx,dy=co.x-CX,co.y-CY; return dx*math.cos(a)+dy*math.sin(a), -dx*math.sin(a)+dy*math.cos(a)
for i in [int(x) for x in os.environ['F'].split(',')]:
    f=bm.faces[i]; ai=int(os.environ.get('AI','0'))
    c=f.calc_center_median(); ai=min((0,1),key=lambda k:abs(abs(fr(c,k)[1])-AW/2))
    print('JE3 F',i,'ai',ai,'n',[round(x,2) for x in f.normal],names[f.material_index])
    for v in f.verts:
        s,d=fr(v.co,ai); print('JE3   v',v.index,'s %.3f |d| %.3f z %.3f'%(s,abs(d),v.co.z))
    for e in f.edges:
        for g in e.link_faces:
            if g!=f: print('JE3   nb',g.index,'via',[v.index for v in e.verts],'n',[round(x,2) for x in g.normal],names[g.material_index],'ch',g[CH],'nv',len(g.verts))
