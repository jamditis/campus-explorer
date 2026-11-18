import bpy,numpy as np
A=np.array([-244.8,-239.3]);B=np.array([-256.1,-271.6]);d=(B-A)/np.linalg.norm(B-A);n=np.array([d[1],-d[0]])
def st(x,y): return (x-A[0])*d[0]+(y-A[1])*d[1],(x-A[0])*n[0]+(y-A[1])*n[1]
o=bpy.data.objects['WS110_CollegeAve_S_end_to_NormalAve_flare6m_ortho2020_DTM2023_U']; me=o.data
for mi in range(len(o.material_slots)):
    cs=[o.matrix_world@f.center for f in me.polygons if f.material_index==mi]
    if not cs: continue
    S=[st(c.x,c.y) for c in cs]; s=[a for a,b in S]; t=[b for a,b in S]
    print('Q111 mat',o.material_slots[mi].name,len(cs),'s',round(min(s),2),round(max(s),2),'t',round(min(t),2),round(max(t),2),'y',round(min(c.y for c in cs),2),round(max(c.y for c in cs),2))
for nm in ('WS110_CollegeAve_S_end_curb_W_return6m_UNVERIFIED','WS110_CollegeAve_S_end_curb_E_return6m_UNVERIFIED'):
    c=bpy.data.objects[nm]; co=np.array([c.matrix_world@v.co for v in c.data.vertices])
    print('Q111',nm[:40]); 
    for i in range(0,len(co),4*5): print('  R',i//4,[ (round(p[0],2),round(p[1],2),round(p[2],2)) for p in co[i:i+4]])
    print('  R last',[ (round(p[0],2),round(p[1],2),round(p[2],2)) for p in co[-4:]])
for nm in ('Footpaths_OSM','WS102_CollegeAve_S_carriageway_brickband_table_ortho2020_LiDAR_','WS110_NormalAve_sidewalk_ws85prep_ortho2020_UNVERIFIED','WS110_NormalAve_verge_ws85prep_ortho2020_UNVERIFIED','WS103_CollegeAve_S_W_sidewalk_concrete_LiDAR2023_UNVERIFIEDwidt'):
    ob=bpy.data.objects[nm]
    for f in ob.data.polygons:
        c=ob.matrix_world@f.center
        if -268<c.x<-232 and -270<c.y<-236:
            pass
    cs=[(ob.matrix_world@f.center,f.material_index) for f in ob.data.polygons]
    sel=[(c,m) for c,m in cs if -268<c.x<-232 and -268<c.y<-236]
    if sel:
        xs=[c.x for c,m in sel]; ys=[c.y for c,m in sel]
        print('Q111 near',nm[:40],len(sel),'x',round(min(xs),1),round(max(xs),1),'y',round(min(ys),1),round(max(ys),1),'mats',set(m for c,m in sel))
        if 'sidewalk_ws85' in nm or 'Footpaths' in nm or 'verge' in nm:
            for c,m in sel[:400:max(1,len(sel)//25)]: print('   f',round(c.x,1),round(c.y,1),round(c.z,2),m)
# WS103 end row
ob=bpy.data.objects['WS103_CollegeAve_S_W_sidewalk_concrete_LiDAR2023_UNVERIFIEDwidt']
co=np.array([ob.matrix_world@v.co for v in ob.data.vertices]); s,t=st(co[:,0],co[:,1])
m=s>s.max()-0.3; print('Q111 WS103 end', [(round(a,2),round(b,2),round(c,2),round(ss,2),round(tt,2)) for (a,b,c),ss,tt in zip(co[m],s[m],t[m])])
