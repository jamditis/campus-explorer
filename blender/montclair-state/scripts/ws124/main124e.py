# white WS117 frame member standing in front of the WS123 door glass (y≈-199.12) -> remove the island(s) inside the door opening
import bpy, bmesh, os
o=next(o for o in bpy.data.objects if o.name.startswith('WS117_Chapin_W_entrance_frame_canopy')); mw=o.matrix_world
bm=bmesh.new(); bm.from_mesh(o.data); bm.verts.ensure_lookup_table()
seen=set(); kill=[]
for v0 in bm.verts:
    if v0.index in seen: continue
    st=[v0]; isl=[]
    while st:
        v=st.pop()
        if v.index in seen: continue
        seen.add(v.index); isl.append(v)
        for e in v.link_edges: st.append(e.other_vert(v))
    ws=[mw@v.co for v in isl]
    bb=(min(w.x for w in ws),max(w.x for w in ws),min(w.y for w in ws),max(w.y for w in ws),min(w.z for w in ws),max(w.z for w in ws))
    inside= bb[0]>-209.35 and bb[2]>-200.32 and bb[3]<-197.94
    print('ISL',len(isl),[round(a,2) for a in bb],'KILL' if inside else '')
    if inside: kill+=isl
if os.environ.get('APPLY')=='1' and kill:
    bmesh.ops.delete(bm,geom=kill,context='VERTS'); bm.to_mesh(o.data); o.data.update(); bpy.ops.wm.save_mainfile(); print('M124e SAVED, removed verts',len(kill))
bm.free()
