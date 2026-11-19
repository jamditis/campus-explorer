import bpy, bmesh
from mathutils import Vector
P=Vector((-255.1,-53.1))
for on in ['WS69_CollegeAve_gap_strip_curbs_UNVERIFIED','WS70_gap_strip_grass_berms','WS72_Kasser_SW_RHD_core_sidewalk_landing_UNVERIFIED_width','WS214_N_berm_tip_gap_asphalt_underfill_ortho2020','WS67_CollegeAve_gap_asphalt (bridges WS27 to north-file KY carr']:
    o=next((x for x in bpy.data.objects if x.name.startswith(on[:40])),None)
    if not o: print('P219',on,'missing'); continue
    M=o.matrix_world; bm=bmesh.new(); bm.from_mesh(o.data)
    seen=set(); isl=[]
    for v in bm.verts:
        if v in seen or ((M@v.co).xy-P).length>1.2: continue
        s={v}; st=[v]
        while st:
            a=st.pop()
            for e in a.link_edges:
                b=e.other_vert(a)
                if b not in s: s.add(b); st.append(b)
        seen|=s
        ws=[M@x.co for x in s]
        isl.append((len(s),round(min(w.x for w in ws),2),round(max(w.x for w in ws),2),round(min(w.y for w in ws),2),round(max(w.y for w in ws),2),round(min(w.z for w in ws),2),round(max(w.z for w in ws),2)))
    near=[M@v.co for v in bm.verts if ((M@v.co).xy-P).length<0.8]
    print('P219',o.name[:40],'mods',[m.type for m in o.modifiers],'islands',isl[:6],'near z',sorted(round(w.z,2) for w in near)[-8:],flush=True)
