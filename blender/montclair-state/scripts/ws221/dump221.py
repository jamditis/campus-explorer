import bpy,bmesh
ld=bpy.data.objects['WS72_Kasser_SW_RHD_core_sidewalk_landing_UNVERIFIED_width']; M=ld.matrix_world
print('P221 WS72 nv',len(ld.data.vertices),'mods',[m.type for m in ld.modifiers])
bm=bmesh.new(); bm.from_mesh(ld.data)
B=[v for v in bm.verts if v.is_boundary]
zs=[(M@v.co).z for v in bm.verts]
for v in bm.verts:
    w=M@v.co
    if -254<=w.x<=-247.5 and -56<=w.y<=-52.5: print('P221 V',v.index,'%.3f %.3f %.3f'%tuple(w),'B' if v.is_boundary else '-',len(v.link_faces))
w=bpy.data.objects['WS69_CollegeAve_gap_strip_curbs_UNVERIFIED']; M=w.matrix_world
for v in w.data.vertices:
    p=M@v.co
    if -256<=p.x<=-249 and -57<=p.y<=-53.5 and p.z>125.5: print('P221 C69 %.3f %.3f %.3f'%tuple(p))
c=bpy.data.objects['WS220_CollegeAve_curb_jog_return_UNVERIFIED']; M=c.matrix_world
for v in c.data.vertices[:30]:
    p=M@v.co; print('P221 CR %.3f %.3f %.3f'%tuple(p))
