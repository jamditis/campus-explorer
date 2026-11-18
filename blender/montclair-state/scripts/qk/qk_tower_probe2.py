import bpy, numpy as np
dg=bpy.context.evaluated_depsgraph_get(); t=np.array([0.4,0.92]); n=np.array([0.92,-0.4])
for nm in ('Center for Computing and Information Science roof (LiDAR)','QF_CCIS_stucco_skin_recessed_openings_photo','QF_qe_cover_wall_windows_kept_red_UNVERIFIED','QE_CCIS_drape_cover_wall_east_UNVERIFIED'):
    o=bpy.data.objects.get(nm)
    if not o: print('missing',nm); continue
    e=o.evaluated_get(dg); me=e.to_mesh(); W=o.matrix_world; R=[]
    for p in me.polygons:
        c=W@p.center; T=c.x*0.4+c.y*0.92; N=c.x*0.92-c.y*0.4
        if 213<T<226 and -60<N<-53 and c.z>140.5: R.append((round(T,2),round(N,2),round(c.z,2),round(p.normal.z,2),p.material_index))
    zs=[r[2] for r in R]; print(nm,'faces',len(R),'zmax',max(zs) if zs else None,'mats',[m.name for m in o.data.materials][:4])
    vert=[r for r in R if abs(r[3])<0.5]; print('  vertical',len(vert)); 
    for r in sorted(vert,key=lambda r:r[2])[::max(1,len(vert)//12)]: print('   ',r)
    e.to_mesh_clear()
