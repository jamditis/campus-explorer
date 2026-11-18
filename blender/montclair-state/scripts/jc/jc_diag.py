# Session jc diag: down-facing faces + overlaps in Kasser_amphitheater_bowl_hl
import bpy, bmesh, numpy as np, collections
ob=bpy.data.objects['Kasser_amphitheater_bowl_hl']; me=ob.data
names=[s.material.name if s.material else '' for s in ob.material_slots]
bm=bmesh.new(); bm.from_mesh(me); bm.normal_update()
lay=bm.faces.layers.int.get('jb_chamfer'); wl=bm.faces.layers.int.get('iy_wedge')
down=[f for f in bm.faces if f.normal.z<-0.05]
print('JC faces',len(bm.faces),'down',len(down),'has_custom',me.has_custom_normals)
c=collections.Counter(); ar=[]
for f in down:
    c[(names[f.material_index], f[lay] if lay else -1, len(f.verts))]+=1; ar.append(f.calc_area())
print('JC down by mat/chamfer/nverts',c.most_common(20))
ar=np.array(ar); print('JC area stats',ar.min(),np.median(ar),ar.max(),ar.sum())
# what neighbours do down faces have
nb=collections.Counter()
for f in down:
    for e in f.edges:
        for g in e.link_faces:
            if g is not f: nb[('ch' if g[lay] else 'n', 'up' if g.normal.z>0.9 else 'vt' if abs(g.normal.z)<0.35 else 'dn' if g.normal.z<-0.05 else 'oth')]+=1
print('JC down neighbours',nb)
mw=ob.matrix_world
for f in down[:12]:
    cc=mw@f.calc_center_median(); print('JC sample',[round(x,2) for x in cc],round(f.normal.z,2),f[lay],names[f.material_index],round(f.calc_area()*1e4,2),'cm2')
# non-manifold / wire
nm=sum(1 for e in bm.edges if len(e.link_faces)>2); bd=sum(1 for e in bm.edges if e.is_boundary)
print('JC edges >2 faces',nm,'boundary',bd)
# faces near closeup cam region: steep (risers) with odd normals
