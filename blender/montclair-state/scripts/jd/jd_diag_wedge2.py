# Session jd diag (read-only): vertices of the front-row aisle-cheek wedge faces + local vertex cloud.
import bpy, bmesh
ob=bpy.data.objects['Kasser_amphitheater_bowl_hl']; me=ob.data; mw=ob.matrix_world
print('JDD mw identity', mw==mw.Identity(4) if hasattr(mw,'Identity') else mw)
names=[s.material.name if s.material else '' for s in ob.material_slots]
bm=bmesh.new(); bm.from_mesh(me); bm.faces.ensure_lookup_table(); bm.normal_update()
for i in [200241,200244,200245,200246,178716,200444,200240,200242,184416,178721,184417,200348,194105]:
    f=bm.faces[i]
    print('JDD F',i,names[f.material_index][:20],'n',[round(v,2) for v in f.normal],[(v.index,tuple(round(c,3) for c in (mw@v.co))) for v in f.verts])
# all verts in box
vs=[v for v in bm.verts if -168.65<(mw@v.co).x<-167.95 and 11.95<(mw@v.co).y<12.35 and 134.0<(mw@v.co).z<134.35]
print('JDD nverts box',len(vs))
for v in sorted(vs,key=lambda v:((mw@v.co).z,(mw@v.co).x)):
    c=mw@v.co; print('JDD V',v.index,tuple(round(x,3) for x in c),'nf',len(v.link_faces))
