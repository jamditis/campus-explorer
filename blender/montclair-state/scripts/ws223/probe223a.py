import bpy
L=bpy.data.objects['WS72_Kasser_SW_RHD_core_sidewalk_landing_UNVERIFIED_width']; LM=L.matrix_world
r=bpy.data.objects['WS220_CollegeAve_curb_jog_return_UNVERIFIED']; RM=r.matrix_world
cl=bpy.data.objects['WS27_CollegeAve_curb_left_UNVERIFIED']; CM=cl.matrix_world
print('P223 return nverts',len(r.data.vertices))
for k in range(15,30):
    if 5*k+4>=len(r.data.vertices): break
    print('P223 ret k%d '%k+' '.join('%d:(%.3f,%.3f,%.3f)'%((j,)+tuple(RM@r.data.vertices[5*k+j].co)) for j in range(5)))
for i in range(0,12):
    print('P223 cl v%d (%.3f,%.3f,%.3f)'%((i,)+tuple(CM@cl.data.vertices[i].co)))
for i,v in enumerate(L.data.vertices):
    w=LM@v.co
    if -249.5<=w.x<=-246.5 and -54.2<=w.y<=-52.5: print('P223 L v%d (%.3f,%.3f,%.3f)'%(i,w.x,w.y,w.z))
