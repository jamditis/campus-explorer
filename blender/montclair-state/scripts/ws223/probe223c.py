import bpy
L=bpy.data.objects['WS72_Kasser_SW_RHD_core_sidewalk_landing_UNVERIFIED_width']; M=L.matrix_world
print('P223 nverts',len(L.data.vertices),'npoly',len(L.data.polygons),'mods',[m.name for m in L.modifiers])
up=set()
for p in L.data.polygons:
    if p.normal.z>0.7: up.update(p.vertices)
for i in sorted(up):
    w=M@L.data.vertices[i].co
    if -250.5<=w.x<=-246.8 and -54.6<=w.y<=-51.6: print('P223 t v%d (%.3f,%.3f,%.3f)'%(i,w.x,w.y,w.z))
