import bpy, bmesh, json
from mathutils import Vector
col=bpy.data.collections['QS_Richardson_walks_UNVERIFIED']
out={}
for o in col.objects:
    if o.type!='MESH': continue
    bm=bmesh.new(); bm.from_mesh(o.data); bm.verts.ensure_lookup_table()
    # top faces: normal z>0.7; find boundary edges of top faces belonging to short "end" edges
    tops=[f for f in bm.faces if f.normal.z>0.7]
    isl=[]; seen=set()
    for f in tops:
        if f.index in seen: continue
        st=[f]; comp=[]; seen.add(f.index)
        while st:
            g=st.pop(); comp.append(g)
            for e in g.edges:
                for h in e.link_faces:
                    if h.normal.z>0.7 and h.index not in seen: seen.add(h.index); st.append(h)
        vs=[v.co for g in comp for v in g.verts]
        isl.append(dict(n=len(comp),x=[round(min(v.x for v in vs),1),round(max(v.x for v in vs),1)],y=[round(min(v.y for v in vs),1),round(max(v.y for v in vs),1)],z=[round(min(v.z for v in vs),2),round(max(v.z for v in vs),2)]))
    # end centres: top-face edges with only one top face that are short (~width)
    ends=[]
    for e in bm.edges:
        lf=[f for f in e.link_faces if f.normal.z>0.7]
        if len(lf)==1:
            L=e.calc_length()
            a,b=e.verts; 
            if abs(L-o.data.get('w',0))<9 and L>1.5 and L<5 and abs(a.co.z-b.co.z)<0.5:
                # end edge if the two verts are across-width: check the face's other edge parallel
                c=(a.co+b.co)/2; ends.append([round(c.x,1),round(c.y,1),round(c.z,2),round(L,2)])
    out[o.name]=dict(islands=isl,ends=ends,mat=o.material_slots[0].material.name if o.material_slots else None)
    bm.free()
json.dump(out,open('data/qw/probe.json','w'),indent=1)
for k,v in out.items(): print(k,v['islands'],'ENDS',v['ends'])
