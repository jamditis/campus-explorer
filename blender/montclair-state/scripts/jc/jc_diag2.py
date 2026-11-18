# Session jc diag2: faces in the close-up's lower aisle region
import bpy, bmesh, numpy as np, collections
ob=bpy.data.objects['Kasser_amphitheater_bowl_hl']; me=ob.data; mw=ob.matrix_world
print('JC2 mw identity', [round(x,3) for x in mw.translation], ob.rotation_euler[:], ob.scale[:])
names=[s.material.name if s.material else '' for s in ob.material_slots]
bm=bmesh.new(); bm.from_mesh(me); bm.normal_update(); bm.faces.ensure_lookup_table()
lay=bm.faces.layers.int.get('jb_chamfer'); uv=bm.loops.layers.uv.active
reg=[f for f in bm.faces if -170.5<(mw@f.calc_center_median()).x<-164 and 8<(mw@f.calc_center_median()).y<13]
c=collections.Counter()
for f in reg:
    nz=f.normal.z; t='up' if nz>0.9 else 'vt' if abs(nz)<0.35 else 'dn' if nz<-0.05 else 'tilt'
    c[(t,names[f.material_index][:20],f[lay])]+=1
print('JC2 region faces',len(reg),c.most_common())
# vertical faces: nonplanarity and normal xy direction spread among same-step risers
np_=[]
for f in reg:
    if abs(f.normal.z)<0.35 and len(f.verts)>3:
        d=max(abs((v.co-f.verts[0].co).dot(f.normal)) for v in f.verts); np_.append((d,f.index))
np_.sort(reverse=True); print('JC2 max nonplanar vt',[(round(d*1000,1),i) for d,i in np_[:8]])
# tilt faces details
for f in reg:
    nz=f.normal.z
    if (0.35<=abs(nz)<=0.9) or nz<-0.05:
        cc=mw@f.calc_center_median(); print('JC2 odd',f.index,[round(x,2) for x in cc],'nz',round(nz,2),names[f.material_index][:22],'ch',f[lay],'A cm2',round(f.calc_area()*1e4,1),'nv',len(f.verts))
# UV stretch on vertical riser faces: ratio of uv area to area
st=[]
for f in reg:
    if abs(f.normal.z)<0.35 and f.calc_area()>1e-4:
        u=[l[uv].uv.copy() for l in f.loops]; a=0
        for i in range(1,len(u)-1): a+=abs((u[i]-u[0]).cross(u[i+1]-u[0]))/2
        st.append(a/f.calc_area())
st=np.array(st); print('JC2 uv/area ratio pct',[round(float(np.percentile(st,q)),3) for q in (1,10,50,90,99)])
